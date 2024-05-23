import React, { useState } from 'react';
import { Form, Button } from 'react-bootstrap';

const InputForm = ({ onSubmit }) => {
    const [address, setAddress] = useState('');
    const [kWh, setKWh] = useState(1000);
    const [escalator, setEscalator] = useState(4);
    const [result, setResult] = useState(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        const response = await fetch('/api/get-utility-tariff/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken'),
            },
            body: JSON.stringify({ address, kWh, escalator }),
        });
        const data = await response.json();
        setResult(data);
    };

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    return (
        <Form onSubmit={handleSubmit}>
            <Form.Group controlId="formAddress">
                <Form.Label>Address</Form.Label>
                <Form.Control
                    type="text"
                    placeholder="Enter address"
                    value={address}
                    onChange={(e) => setAddress(e.target.value)}
                    required
                />
            </Form.Group>
            <Form.Group controlId="formKWh">
                <Form.Label>kWh Consumption (1000 - 10000)</Form.Label>
                <Form.Control
                    type="number"
                    value={kWh}
                    onChange={(e) => setKWh(Math.max(1000, Math.min(10000, e.target.value)))}
                    required
                />
            </Form.Group>
            <Form.Group controlId="formEscalator">
                <Form.Label>Percentage Escalator (4% - 10%)</Form.Label>
                <Form.Control
                    type="number"
                    value={escalator}
                    onChange={(e) => setEscalator(Math.max(4, Math.min(10, e.target.value)))}
                    required
                />
            </Form.Group>
            <Button variant="primary" type="submit">
                Submit
            </Button>
            {result && (
                <div className="mt-3">
                    <h3>Results</h3>
                    <p>Average ¢/kWh: {result.average_rate}</p>
                    <p>Most Likely Utility Tariff: {result.most_likely_tariff}</p>
                    <p>Cost for the First Year: ${result.cost_first_year}</p>
                    <h4>Tariffs</h4>
                    <ul>
                        {result.tariffs.map((tariff, index) => (
                            <li key={index}>{tariff.tariff_name} - Start Date: {tariff.startdate}</li>
                        ))}
                    </ul>
                </div>
            )}
        </Form>
    );
};

export default InputForm;
