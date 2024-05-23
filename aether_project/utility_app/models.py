from django.db import models
from django.contrib.auth.models import User

class Project(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255)
    kWh_consumption = models.PositiveIntegerField()
    escalator = models.FloatField()

class ProposalUtility(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE)
    utility_id = models.CharField(max_length=255)
    tariff_name = models.CharField(max_length=255)
    pricing_matrix = models.JSONField()