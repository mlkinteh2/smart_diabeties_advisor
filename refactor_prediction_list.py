
import os

content = """{% extends 'dashboard/doctor_base.html' %}

{% block title %}All Predictions - MedPredict{% endblock %}

{% block doctor_content %}
<style>
    .card {
        background: white;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
    .card-header {
        background: white;
        padding: 1.5rem;
        border-bottom: 1px solid #e2e8f0;
        font-weight: 700;
        color: #0f172a;
        border-radius: 12px 12px 0 0;
        font-size: 1.1rem;
    }
    .table {
        margin-bottom: 0;
        width: 100%;
        border-collapse: collapse;
    }
    .table th {
        background: #f8fafc;
        padding: 1rem 1.5rem;
        font-weight: 600;
        color: #64748b;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        text-align: left;
        border-bottom: 1px solid #e2e8f0;
    }
    .table td {
        padding: 1rem 1.5rem;
        vertical-align: middle;
        color: #334155;
        border-bottom: 1px solid #e2e8f0;
    }
    .btn-primary {
        background: #2563eb;
        color: white;
        text-decoration: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-size: 0.875rem;
        transition: background-color 0.2s;
        display: inline-block;
    }
    .btn-primary:hover {
        background: #1d4ed8;
        color: white;
    }
</style>

<div class="row mb-4">
    <div class="col-12">
        <h1 class="h3 mb-2 text-gray-800">Prediction History</h1>
        <p class="mb-4 text-muted">View all past patient predictions and their status.</p>
    </div>
</div>

<div class="card">
    <div class="card-header">
        <i class="bi bi-file-text me-2"></i> All Predictions
    </div>
    <div class="table-responsive">
        <table class="table">
            <thead>
                <tr>
                    <th>ID</th>
                    <th>Patient</th>
                    <th>Date</th>
                    <th>Diabetes Risk</th>
                    <th>Kidney Risk</th>
                    <th>Status</th>
                    <th>Action</th>
                </tr>
            </thead>
            <tbody>
                {% for p in predictions %}
                <tr>
                    <td>#{{ p.id }}</td>
                    <td>
                        <div class="fw-bold">{{ p.patient.user.get_full_name|default:p.patient.user.username }}</div>
                    </td>
                    <td>{{ p.created_at|date:"M d, Y" }}</td>
                    <td>
                        <span class="badge {% if p.diabetes_risk == 'High' %}bg-danger{% elif p.diabetes_risk == 'Moderate' %}bg-warning{% else %}bg-success{% endif %} bg-opacity-10 text-{% if p.diabetes_risk == 'High' %}danger{% elif p.diabetes_risk == 'Moderate' %}warning{% else %}success{% endif %} px-3 py-1 rounded-pill" style="font-size: 0.8em; font-weight: 600;">
                            {{ p.diabetes_risk }}
                        </span>
                    </td>
                    <td>
                        <span class="badge {% if p.kidney_risk == 'High' %}bg-danger{% elif p.kidney_risk == 'Moderate' %}bg-warning{% else %}bg-success{% endif %} bg-opacity-10 text-{% if p.kidney_risk == 'High' %}danger{% elif p.kidney_risk == 'Moderate' %}warning{% else %}success{% endif %} px-3 py-1 rounded-pill" style="font-size: 0.8em; font-weight: 600;">
                            {{ p.kidney_risk }}
                        </span>
                    </td>
                    <td>
                        {% if p.approval_status == 'Pending' %}
                        <span class="badge bg-secondary bg-opacity-10 text-secondary px-3 py-1 rounded-pill" style="font-size: 0.8em; font-weight: 600;">Pending</span>
                        {% elif p.approval_status == 'Approved' %}
                        <span class="badge bg-success bg-opacity-10 text-success px-3 py-1 rounded-pill" style="font-size: 0.8em; font-weight: 600;">Approved</span>
                        {% else %}
                        <span class="badge bg-danger bg-opacity-10 text-danger px-3 py-1 rounded-pill" style="font-size: 0.8em; font-weight: 600;">Rejected</span>
                        {% endif %}
                    </td>
                    <td>
                        <a href="{% url 'prediction_detail' p.id %}" class="btn-primary">
                            Details
                        </a>
                    </td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="7" class="text-center py-5 text-muted">
                        No predictions found.
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
"""

path = r"d:\Projects\Final_Project\medpredict\predictions\templates\predictions\prediction_list.html"
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Successfully overwrote file:", path)
