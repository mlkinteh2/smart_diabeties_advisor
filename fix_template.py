
import os

content = """{% extends 'base.html' %}
{% load static %}

{% block title %}Doctor Dashboard - MedPredict AI{% endblock %}

{% block content %}
<style>
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        transition: transform 0.2s;
    }

    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    .stat-icon {
        width: 48px;
        height: 48px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }

    .avatar-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #f1f5f9;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        color: #64748b;
        font-size: 0.875rem;
    }

    .search-input-group {
        position: relative;
        min-width: 300px;
    }

    .search-input-group i {
        position: absolute;
        left: 1rem;
        top: 50%;
        transform: translateY(-50%);
        color: #94a3b8;
    }

    .search-input-group input {
        padding-left: 2.5rem;
        border-radius: 8px;
        border-color: #e2e8f0;
    }

    .table> :not(caption)>*>* {
        padding: 1rem 1.5rem;
    }

    .btn-create-prediction {
        background-color: #2563eb;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.2s;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
    }

    .btn-create-prediction:hover {
        background-color: #1d4ed8;
        color: white;
        transform: translateY(-1px);
    }
</style>

<div class="row mb-4">
    <div class="col-md-4">
        <div class="stat-card">
            <div>
                <p class="text-muted mb-1">Total Predictions</p>
                <h2 class="fw-bold mb-0">{{ total_predictions }}</h2>
            </div>
            <div class="stat-icon bg-primary bg-opacity-10 text-primary"><i class="bi bi-file-earmark-text"></i></div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="stat-card">
            <div>
                <p class="text-muted mb-1">Today's Predictions</p>
                <h2 class="fw-bold mb-0">{{ todays_predictions }}</h2>
            </div>
            <div class="stat-icon bg-success bg-opacity-10 text-success"><i class="bi bi-calendar-check"></i></div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="stat-card">
            <div>
                <p class="text-muted mb-1">Patients Monitored</p>
                <h2 class="fw-bold mb-0">{{ patients_monitored }}</h2>
            </div>
            <div class="stat-icon bg-danger bg-opacity-10 text-danger"><i class="bi bi-people"></i></div>
        </div>
    </div>
</div>

<div class="card border-0 shadow-sm mb-4">
    <div class="card-header bg-white border-0 py-3 d-flex justify-content-between align-items-center flex-wrap gap-3">
        <h5 class="mb-0 fw-bold"><i class="bi bi-people-fill me-2 text-primary"></i>Registered Patients</h5>
        <div class="search-input-group">
            <i class="bi bi-search"></i>
            <input type="text" id="patientSearch" class="form-control"
                placeholder="Search by name, username or phone...">
        </div>
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover align-middle mb-0" id="patientTable">
                <thead class="bg-light">
                    <tr>
                        <th class="ps-4 border-0 text-muted small text-uppercase fw-bold">Patient Name</th>
                        <th class="border-0 text-muted small text-uppercase fw-bold">Age</th>
                        <th class="border-0 text-muted small text-uppercase fw-bold">Gender</th>
                        <th class="border-0 text-muted small text-uppercase fw-bold">Phone</th>
                        <th class="text-end pe-4 border-0 text-muted small text-uppercase fw-bold">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for patient in patients %}
                    <tr>
                        <td class="ps-4">
                            <div class="d-flex align-items-center">
                                <div class="avatar-circle me-3">{{ patient.user.first_name.0|default:patient.user.username.0|upper }}{{ patient.user.last_name.0|default:""|upper }}</div>
                                <div>
                                    <h6 class="mb-0 fw-bold text-dark">{{ patient.user.get_full_name|default:patient.user.username }}</h6>
                                    <small class="text-muted">@{{ patient.user.username }}</small>
                                </div>
                            </div>
                        </td>
                        <td class="text-dark">{{ patient.age|default:"-" }}</td>
                        <td class="text-dark">{{ patient.gender|default:"-" }}</td>
                        <td class="text-dark">{{ patient.phone|default:"-" }}</td>
                        <td class="text-end pe-4">
                            <a href="{% url 'create_prediction' patient.id %}"
                                class="btn-create-prediction text-decoration-none">
                                <i class="bi bi-plus-circle"></i> Create Prediction
                            </a>
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="5" class="text-center py-5 text-muted">
                            <i class="bi bi-people display-4 mb-3 d-block opacity-50"></i>
                            No patients registered yet.
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
</div>

{% endblock %}

{% block extra_js %}
<script>
    document.getElementById('patientSearch').addEventListener('keyup', function () {
        const searchText = this.value.toLowerCase();
        const table = document.getElementById('patientTable');
        const rows = table.getElementsByTagName('tr');
        for (let i = 1; i < rows.length; i++) {
            const row = rows[i];
            const nameCol = row.getElementsByTagName('td')[0];
            const phoneCol = row.getElementsByTagName('td')[3];
            if (nameCol && phoneCol) {
                const nameText = nameCol.textContent || nameCol.innerText;
                const phoneText = phoneCol.textContent || phoneCol.innerText;
                if (nameText.toLowerCase().indexOf(searchText) > -1 || phoneText.toLowerCase().indexOf(searchText) > -1) {
                    row.style.display = "";
                } else {
                    row.style.display = "none";
                }
            }
        }
    });
</script>
{% endblock %}
"""

path = r"d:\Projects\Final_Project\medpredict\dashboard\templates\dashboard\doctor_dashboard.html"
with open(path, "w", encoding="utf-8") as f:
    f.write(content)
print("Successfully overwrote file:", path)
