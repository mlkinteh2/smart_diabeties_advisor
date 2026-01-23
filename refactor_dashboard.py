
import os

content = """{% extends 'dashboard/doctor_base.html' %}
{% load static %}

{% block title %}Doctor Dashboard - MedPredict AI{% endblock %}

{% block doctor_content %}
<style>
    /* Dashboard specific styles */
    .dashboard-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 2rem;
    }

    .welcome-text h1 {
        font-size: 1.75rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.5rem;
    }

    .welcome-text p {
        color: #64748b;
        margin-bottom: 0;
    }

    .header-actions {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .action-btn {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background: white;
        border: 1px solid #e2e8f0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #64748b;
        cursor: pointer;
        transition: all 0.2s;
    }

    .action-btn:hover {
        background: #f1f5f9;
        color: #0f172a;
    }

    .doctor-profile {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding-left: 1rem;
        border-left: 1px solid #e2e8f0;
    }

    .profile-avatar {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        background-color: #2563eb;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
    }

    /* Stats Cards */
    .stat-card {
        background: white;
        border-radius: 1rem;
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        transition: transform 0.2s;
        height: 100%;
    }

    .stat-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    }

    .stat-info h3 {
        font-size: 1.875rem;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 0.25rem;
    }

    .stat-info p {
        color: #64748b;
        font-size: 0.875rem;
        margin-bottom: 0;
    }

    .stat-icon {
        width: 48px;
        height: 48px;
        border-radius: 0.75rem;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
    }

    /* Patient Table Styles */
    .card {
        border-radius: 1rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 2rem;
        background: white;
    }

    .card-header {
        padding: 1.5rem;
        background: white;
        border-bottom: 1px solid #e2e8f0;
        border-radius: 1rem 1rem 0 0 !important;
    }

    .section-title {
        font-size: 1.125rem;
        font-weight: 700;
        color: #0f172a;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0;
    }

    .search-input-group {
        position: relative;
        width: 300px;
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
        padding-top: 0.6rem;
        padding-bottom: 0.6rem;
        border-radius: 0.5rem;
        border-color: #e2e8f0;
        background-color: #f8fafc;
        width: 100%;
    }

    .search-input-group input:focus {
        background-color: white;
        box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
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

    .table td {
        vertical-align: middle;
        padding: 1rem 1.5rem;
    }

    .table th {
        padding: 1rem 1.5rem;
        background-color: #f8fafc;
        font-weight: 600;
        color: #64748b;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    .btn-create-prediction {
        background-color: #2563eb;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-weight: 500;
        transition: all 0.2s;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        text-decoration: none;
        font-size: 0.875rem;
    }

    .btn-create-prediction:hover {
        background-color: #1d4ed8;
        color: white;
        transform: translateY(-1px);
    }
</style>

<!-- Header -->
<header class="dashboard-header">
    <div class="welcome-text">
        <h1>Dashboard</h1>
        <p>Welcome back, Dr. {{ user.last_name|default:user.username }}</p>
    </div>
    
    <div class="header-actions">
        <button class="action-btn">
            <i class="bi bi-search"></i>
        </button>
        <button class="action-btn">
            <i class="bi bi-bell"></i>
        </button>
        <div class="doctor-profile">
            <div class="text-end d-none d-sm-block">
                <div class="fw-bold small">{{ user.get_full_name|default:user.username }}</div>
                <div class="text-muted small" style="font-size: 0.75rem;">Doctor</div>
            </div>
            <div class="profile-avatar">
                {{ user.first_name.0|default:'D'|upper }}{{ user.last_name.0|default:'R'|upper }}
            </div>
        </div>
    </div>
</header>

<!-- Stats Grid -->
<div class="row g-4 mb-5">
    <div class="col-md-4">
        <div class="stat-card">
            <div class="stat-info">
                <h3>{{ total_predictions }}</h3>
                <p>Total Predictions</p>
            </div>
            <div class="stat-icon bg-blue-50 text-primary" style="background-color: #eff6ff;">
                <i class="bi bi-file-earmark-text"></i>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="stat-card">
            <div class="stat-info">
                <h3>{{ todays_predictions }}</h3>
                <p>Today's Predictions</p>
            </div>
            <div class="stat-icon bg-green-50 text-success" style="background-color: #f0fdf4;">
                <i class="bi bi-calendar-check"></i>
            </div>
        </div>
    </div>
    <div class="col-md-4">
        <div class="stat-card">
            <div class="stat-info">
                <h3>{{ patients_monitored }}</h3>
                <p>Patients Monitored</p>
            </div>
            <div class="stat-icon bg-red-50 text-danger" style="background-color: #fef2f2;">
                <i class="bi bi-people"></i>
            </div>
        </div>
    </div>
</div>

<!-- Registered Patients Section -->
<div class="card shadow-sm border-0">
    <div class="card-header d-flex justify-content-between align-items-center">
        <h5 class="section-title">
            <i class="bi bi-people-fill text-primary"></i>
            Registered Patients
        </h5>
        <div class="search-input-group">
            <i class="bi bi-search"></i>
            <input type="text" id="patientSearch" placeholder="Search by name, username or phone...">
        </div>
    </div>
    <div class="card-body p-0">
        <div class="table-responsive">
            <table class="table table-hover mb-0" id="patientTable">
                <thead>
                    <tr>
                        <th class="ps-4">Patient Name</th>
                        <th>Age</th>
                        <th>Gender</th>
                        <th>Phone</th>
                        <th class="text-end pe-4">Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for patient in patients %}
                    <tr>
                        <td class="ps-4">
                            <div class="d-flex align-items-center">
                                <div class="avatar-circle me-3">{{ patient.user.first_name.0|default:patient.user.username.0|upper }}{{ patient.user.last_name.0|default:""|upper }}</div>
                                <div>
                                    <div class="fw-bold text-dark">{{ patient.user.get_full_name|default:patient.user.username }}</div>
                                    <div class="text-muted small">@{{ patient.user.username }}</div>
                                </div>
                            </div>
                        </td>
                        <td>{{ patient.age|default:"-" }}</td>
                        <td>{{ patient.gender|default:"-" }}</td>
                        <td>{{ patient.phone|default:"-" }}</td>
                        <td class="text-end pe-4">
                            <a href="{% url 'create_prediction' patient.id %}" class="btn-create-prediction">
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
