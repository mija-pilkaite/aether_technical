from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm, SignUpForm
from .models import Project, ProposalUtility
from .services import get_lat_lon, get_utility_data
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus
from .serializers import ProjectSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.http import JsonResponse

WEBHOOK_URL = 'https://webhook.site/63c62839-c2e4-4331-9b5a-f3b9c462ae0d'

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_project(request):
    if request.method == 'POST':
        serializer = ProjectSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            project = serializer.save()
            webhook_data = {
                'event': 'Project Created',
                'data': serializer.data
            }
            requests.post(WEBHOOK_URL, json=webhook_data)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def landing_view(request):
    return render(request, 'utility_app/landing.html')

@login_required
def project_create_view(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.user = request.user
            project.save()
            data = get_utility_data(project.address)
            if data and 'items' in data and len(data['items']) > 0:
                item = data['items'][0]
                ProposalUtility.objects.create(
                    project=project,
                    utility_id=item['id'],
                    tariff_name=item['tariff_name'],
                    pricing_matrix=item['rates']
                )
            return redirect('project_detail', pk=project.pk)
    else:
        form = ProjectForm()
    return render(request, 'utility_app/project_form.html', {'form': form})

# @login_required
# def project_detail_view(request, pk):
#     project = get_object_or_404(Project, pk=pk)
#     proposal = ProposalUtility.objects.filter(project=project).first()
#     tariffs = json.loads(proposal.pricing_matrix) if proposal else []
#     return render(request, 'utility_app/project_detail.html', {
#         'project': project,
#         'proposal': proposal,
#         'tariffs': tariffs,
#     })
def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('landing')
    else:
        form = SignUpForm()
    return render(request, 'utility_app/signup.html', {'form': form})

api_key_maps = '664f58ed6a6b7822498850ridbda371'
api_key = 'R1srhBFi8lubuElt5xcCpNjwlkQBJdE53WA15ctC'


def get_lat_lon(address):
    address = quote_plus(address)
    url = f'https://geocode.maps.co/search?q={address}&api_key={api_key_maps}'
    response = requests.get(url)
    if response.status_code == 200:
        try:
            data = response.json()
            if data:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                return lat, lon
            else:
                return None, None
        except (json.JSONDecodeError, IndexError) as e:
            return None, None
    else:
        return None, None

def parse_html_for_rate(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    rates = []
    for row in soup.select('.strux_view_row'):
        rate_cell = row.select_one('.strux_view_cell:nth-child(5)')
        if rate_cell:
            try:
                rate = float(rate_cell.text.strip())
                rates.append(rate)
            except ValueError:
                continue
    if rates:
        average_rate = sum(rates) / len(rates)
    else:
        average_rate = 0
    return average_rate

def calculate_average_rate(uri):
    response = requests.get(uri)
    if response.status_code == 200:
        content_type = response.headers.get('Content-Type')
        if 'text/html' in content_type:
            try:
                return parse_html_for_rate(response.content)
            except Exception as e:
                return 0
        else:
            return 0
    else:
        return 0

def calculate_first_year_cost(kWh, average_rate, escalator):
    return kWh * average_rate 

def calculate_yearly_costs(kWh, average_rate, escalator):
    yearly_costs = []
    current_rate = average_rate
    for year in range(20):
        yearly_cost = kWh * current_rate
        yearly_costs.append(yearly_cost)
        current_rate *= (1 + escalator / 100)  # Increase the rate by the escalator for the next year
    return yearly_costs

def fetch_tariff_data(lat, lon, kWh, escalator):
    url = f'https://api.openei.org/utility_rates?version=3&format=json&api_key={api_key}&approved=true&lat={lat}&lon={lon}&Isdefault=true'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        items = data.get('items', [])

        tariff_dict = {}
        for item in items:
            startdate = item.get('startdate')
            if startdate and startdate > 1640995200:  # Timestamp for Jan 1, 2022
                uri = item.get('uri')
                if uri:
                    average_rate = calculate_average_rate(uri)
                    first_year_cost = calculate_first_year_cost(kWh, average_rate, escalator)
                    name = item.get('name')

                    if name in tariff_dict:
                        tariff_dict[name]['average_rate'] += average_rate
                        tariff_dict[name]['first_year_cost'] += first_year_cost
                        tariff_dict[name]['count'] += 1
                    else:
                        tariff_dict[name] = {
                            'name': name,
                            'startdate': item.get('startdate'),
                            'uri': uri,
                            'average_rate': average_rate,
                            'first_year_cost': first_year_cost,
                            'count': 1
                        }

        tariffs = []
        for name, data in tariff_dict.items():
            tariffs.append({
                'name': name,
                'startdate': data['startdate'],
                'uri': data['uri'],
                'average_rate': data['average_rate'] / data['count'],
                'first_year_cost': data['first_year_cost'] / data['count']
            })

        if tariffs:
            most_likely_tariff = tariffs[0]  # Assuming the first one is the most likely for simplicity
            return {
                'most_likely_tariff_name': most_likely_tariff['name'],
                'average_rate': most_likely_tariff['average_rate'],
                'cost_first_year': most_likely_tariff['first_year_cost'],
                'tariffs': tariffs
            }
        else:
            return {
                'most_likely_tariff_name': '',
                'average_rate': 0,
                'cost_first_year': 0,
                'tariffs': []
            }
    else:
        return {
            'most_likely_tariff_name': '',
            'average_rate': 0,
            'cost_first_year': 0,
            'tariffs': []
        }
    
@csrf_exempt
def get_utility_tariff(request):
    if request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        address = data.get('address')
        kWh = data.get('kWh')
        escalator = data.get('escalator')

        if (not address) or (kWh is None) or (escalator is None):
            print(f'Address: {address}, kWh: {kWh}, escalator: {escalator}')
            return JsonResponse({'error': 'Missing required parameters'}, status=400)

        lat, lon = get_lat_lon(address)
        if lat is None or lon is None:
            return JsonResponse({'error': 'Invalid address or unable to geocode address'}, status=400)

        result = fetch_tariff_data(lat, lon, kWh, escalator)
        return JsonResponse(result)

    return JsonResponse({'error': 'Invalid request method'}, status=405)

def utility_tariff_view(request):
    return render(request, 'utility_app/create_project.html')