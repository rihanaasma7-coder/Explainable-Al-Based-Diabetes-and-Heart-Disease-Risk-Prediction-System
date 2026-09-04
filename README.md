# Explainable AI-Based Diabetes and Heart Disease Risk Prediction System

Production-style final-year mini project for predicting diabetes and heart disease risk with Machine Learning, Explainable AI, Spring Boot, React, MySQL, Grafana, and Docker.

## Architecture

- `frontend/`: React, Tailwind CSS, Axios, Recharts
- `backend/`: Spring Boot 3, Java 17, Maven, MVC REST API, Swagger, MySQL persistence
- `ml-service/`: Flask ML service with preprocessing, model training, SHAP/LIME explanations, and recommendations
- `datasets/`: auto-loaded Kaggle CSVs
- `database/`: MySQL schema
- `grafana/`: datasource provisioning, dashboard JSON, and SQL queries

## Datasets

The application expects:

```text
datasets/
  diabetes.csv
  heart_disease.csv
```

These files have already been extracted from the provided archives. To replace them, keep the same filenames.

## Run With Docker

From the project root:

```bash
docker-compose up --build
```

Services:

- React UI: http://localhost:3000
- Spring Boot API: http://localhost:8080
- Swagger UI: http://localhost:8080/swagger-ui.html
- Flask ML service: http://localhost:5000/health
- Grafana: http://localhost:3001
- Grafana login: `admin` / `admin`
- MySQL: `localhost:3306`, database `health_risk_db`, user `root`, password `root`

On first startup, the ML service trains diabetes and heart models and stores:

```text
models/diabetes_model.pkl
models/heart_model.pkl
processed/diabetes_processed.csv
processed/heart_processed.csv
```

## API Examples

### Predict Risk

```http
POST /api/predict
Content-Type: application/json
```

```json
{
  "age": 45,
  "gender": "Male",
  "glucose": 180,
  "bmi": 31,
  "bloodPressure": 145,
  "cholesterol": 240,
  "heartRate": 88
}
```

Response includes stored prediction ID, risk labels, probabilities, SHAP/LIME factors, and recommendations.

### Explanation

```http
GET /api/explanation/{id}
```

### Recommendations

```http
GET /api/recommendation/{id}
```

## Local Development

### ML Service

```bash
cd ml-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Backend

Start MySQL first, then:

```bash
cd backend
mvn spring-boot:run
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Risk Classification

- Low Risk: `0-30%`
- Medium Risk: `31-70%`
- High Risk: `71-100%`

## Model Training

For both diabetes and heart disease, the ML service trains:

- Logistic Regression
- Random Forest
- XGBoost

It compares accuracy, precision, recall, and F1 score, then automatically saves the best model by F1 score using `joblib`.

## Grafana

Grafana is pre-provisioned with MySQL as a datasource and a dashboard containing:

- Disease risk trends
- Prediction count
- Average glucose
- Average BMI
- High-risk patient percentage

The SQL queries are also documented in `grafana/sql-queries.md`.

## Notes

This project is intended for academic demonstration and explainability study. It is not a medical device and should not be used as a substitute for professional clinical diagnosis.
