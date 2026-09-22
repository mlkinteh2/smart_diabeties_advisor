# Smart Diabetes Advisor
<img width="1871" height="838" alt="image" src="https://github.com/user-attachments/assets/92b2971a-3afd-4f41-a9d9-6a7ef7bf30e5" />
<img width="1862" height="819" alt="image" src="https://github.com/user-attachments/assets/edca264b-0590-4350-85b5-eca687c01989" />



A comprehensive clinical decision support system that assists healthcare professionals in the early detection and management of diabetes mellitus and chronic kidney disease (CKD). The system integrates machine learning models with SHAP-based explainability and implements a mandatory "doctor-in-the-loop" approval workflow to ensure patient safety.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Django](https://img.shields.io/badge/Django-5.2.8-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 📋 Table of Contents

- [Features](#features)
- [System Architecture](#system-architecture)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Screenshots](#screenshots)
- [Model Performance](#model-performance)
- [Security \u0026 Privacy](#security--privacy)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### 🏥 Core Functionality

- **Dual-Disease Risk Assessment**: Simultaneous prediction for both diabetes and chronic kidney disease
- **Explainable AI**: SHAP (SHapley Additive exPlanations) integration for transparent, interpretable predictions
- **Personalized Recommendations**: Rule-based recommendation engine that adapts guidance based on specific risk combinations
- **Doctor-in-the-Loop Validation**: Mandatory physician review workflow ensures all AI predictions are verified before patient access
- **Real-time Visualizations**: Interactive SHAP plots showing feature contributions to predictions

### 👥 Role-Based Access Control

#### Administrator
- User management (create, edit, delete accounts)
- System configuration and monitoring
- View aggregate statistics (NO access to individual patient medical data)

#### Doctor
- Patient registration and data entry
- Generate predictions with explainability
- Review and approve/reject AI recommendations
- Monitor patient history and trends

#### Patient
- View approved predictions only
- Access personalized health recommendations
- Track historical risk trends
- Dashboard with visual risk indicators

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Presentation Layer                        │
│            (Django Templates, Bootstrap 5, Chart.js)        │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                    Application Layer                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │  Prediction  │  │Recommendation│  │Explainability│     │
│  │    Engine    │  │    Engine    │  │   Module     │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└───────────────────────┬─────────────────────────────────────┘
                        │
┌───────────────────────▼─────────────────────────────────────┐
│                      Data Layer                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   SQLite DB  │  │  ML Models   │  │ SHAP Plots   │     │
│  │  (User Data) │  │  (.pkl files)│  │   (Media)    │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

### Backend
- **Framework**: Django 5.2.8
- **Language**: Python 3.9+
- **ML Libraries**: 
  - scikit-learn 1.6+ (Random Forest models)
  - SHAP (Model explainability)
  - NumPy \u0026 Pandas (Data processing)
- **Serialization**: Joblib (Model persistence)

### Frontend
- **Templates**: Django Jinja2
- **CSS Framework**: Bootstrap 5
- **Visualizations**: Chart.js, Matplotlib
- **Icons**: Bootstrap Icons

### Database
- **Development**: SQLite3
- **Production Ready**: PostgreSQL/MySQL compatible

### Machine Learning Models
- **Diabetes Model**: Random Forest Classifier (74% accuracy)
- **Kidney Model**: Random Forest Classifier (100% test accuracy, 97.7% cross-validation)
- **Explainability**: SHAP TreeExplainer
- **Preprocessing**: RobustScaler

## 📦 Installation

### Prerequisites

- Python 3.9 or higher
- pip
- Virtual environment (recommended)

### Step-by-Step Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/smart-diabetes-advisor.git
   cd smart-diabetes-advisor
   ```

2. **Create and activate virtual environment**
   ```bash
   # Windows
   python -m venv venv
   venv\\Scripts\\activate

   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser (admin account)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Open your browser and navigate to: `http://127.0.0.1:8000`
   - Admin panel: `http://127.0.0.1:8000/admin/`

## 🚀 Usage

## ☁️ Deploying to Vercel

This repository includes a Vercel Python function configuration in `vercel.json`.
Before deploying, create a hosted PostgreSQL database. Vercel functions do not provide
persistent local SQLite or media storage, so the production `DATABASE_URL` must point to
PostgreSQL. Uploaded/generated media should be moved to an object-storage service before
using the application with real patient records.

1. Import `mlkinteh2/smart_diabeties_advisor` into Vercel with the root directory set to the directory containing `manage.py`.
2. Add `DJANGO_SECRET_KEY`, `DATABASE_URL`, `DJANGO_DEBUG=False`, and `DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-vercel-domain>` as environment variables.
3. Deploy. The configured build runs `python manage.py collectstatic --noinput`.
4. Run migrations against the hosted database from a trusted machine with the same `DATABASE_URL`:
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

The ML model files under `predictions/ml/` are bundled with the function. Vercel's function
size and build limits should be checked after the first deployment because NumPy, SciPy,
scikit-learn, pandas, SHAP, and Matplotlib are substantial dependencies.

### For Doctors

1. **Login** with your doctor credentials
2. **Register a patient** or select an existing patient
3. **Enter clinical data** (age, BMI, blood pressure, glucose, creatinine, etc.)
4. **Generate prediction** - system will:
   - Run ML models for diabetes and kidney disease
   - Generate SHAP explanations
   - Create personalized recommendations
5. **Review the prediction** on the review page
6. **Approve or reject** - only approved predictions are visible to patients

### For Patients

1. **Login** with your patient credentials
2. **View dashboard** showing:
   - Risk status (Low/Medium/High)
   - Risk trends over time
   - Latest prediction details
3. **Access recommendations** for:
   - Daily diet guidance
   - Physical activity suggestions
   - Clinical monitoring notes

## 📸 Screenshots



**To add screenshots to this README:**

### Login Page
<img width="1871" height="838" alt="image" src="https://github.com/user-attachments/assets/04827cb7-0fb4-438c-b6f3-b6d3fbe9a570" />




### Doctor Dashboard
<img width="1884" height="846" alt="image" src="https://github.com/user-attachments/assets/5e9ee55f-2fd5-4594-86e3-8a84c08c6911" />




### Prediction with SHAP Analysis
<img width="1850" height="865" alt="image" src="https://github.com/user-attachments/assets/df808b7a-df34-4b2c-87f8-98973f068108" />



### Patient Dashboard
<img width="1875" height="756" alt="image" src="https://github.com/user-attachments/assets/09bc4116-aeab-44f7-9d00-0d375250a961" />

```

## 📊 Model Performance

### Diabetes Prediction Model

| Metric              | Value  |
|---------------------|--------|
| Test Accuracy       | 74.03% |
| Precision (Positive)| 0.55   |
| Recall (Positive)   | 0.78   |
| F1-Score (Positive) | 0.64   |
| AUC-ROC             | 0.82   |

**Dataset**: PIMA Indians Diabetes Dataset (768 samples)  
**Features**: Age, BMI, Blood Pressure, Glucose

### Kidney Disease Prediction Model

| Metric              | Value  |
|---------------------|--------|
| Test Accuracy       | 100%   |
| Precision (CKD)     | 1.00   |
| Recall (CKD)        | 1.00   |
| F1-Score (CKD)      | 1.00   |
| Cross-Validation    | 97.7% ±2.9% |

**Dataset**: UCI Chronic Kidney Disease Dataset (400 samples)  
**Features**: Creatinine, Hemoglobin, Potassium, Sodium, Blood Pressure, RBC, Urea, Albumin

### External Validation

Tested with 30 anonymized patient records from a dialysis clinic:
- **Kidney Model**: 96.7% sensitivity in identifying CKD patients
- **Diabetes Model**: 60% flagged as high-risk (consistent with diabetic nephropathy prevalence)

## 🔒 Security \u0026 Privacy

- **HIPAA-Compliant Design**: Admins have NO access to individual patient medical data
- **Authentication**: Django session-based authentication with CSRF protection
- **Role-Based Access Control**: Strict separation of admin, doctor, and patient privileges
- **Input Validation**: Both frontend (HTML5) and backend validation with range clamping
- **Audit Trail**: All predictions logged with timestamp and reviewing doctor
- **Data Minimization**: Only medically necessary data is collected

## 🗂️ Project Structure

```
medpredict/
├── accounts/              # User management, authentication
├── dashboard/             # Role-specific dashboards
├── predictions/           # ML prediction engine
│   ├── ml/               # Trained models (.pkl files)
│   ├── views.py          # Prediction logic
│   └── explainability.py # SHAP integration
├── recommendations/       # Rule-based recommendation engine
├── media/                 # User-generated content (SHAP plots)
├── medpredict/           # Project settings
│   ├── static/          # CSS, JS, images
│   └── templates/       # Base templates
├── manage.py
└── requirements.txt
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some Amazing Feature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📧 Contact

For questions or support, please open an issue on GitHub.

## 🎓 Academic Context

This project was developed as a Final Year Project for [Your University Name]. For detailed methodology, results, and discussion, please refer to the [Full Project Report](Full_Project_Report.md).

## 🙏 Acknowledgments

- PIMA Indians Diabetes Dataset - National Institute of Diabetes and Digestive and Kidney Diseases
- UCI Chronic Kidney Disease Dataset - UCI Machine Learning Repository
- SHAP Library - Scott Lundberg and Su-In Lee
- Albukhary Dialysis Centre - External validation dataset

---


**⚠️ Medical Disclaimer**: This system is a clinical decision support tool and should not replace professional medical judgment. All predictions must be reviewed and approved by licensed healthcare professionals before being communicated to patients.


