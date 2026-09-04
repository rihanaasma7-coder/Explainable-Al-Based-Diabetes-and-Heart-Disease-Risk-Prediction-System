CREATE DATABASE IF NOT EXISTS health_risk_db;
USE health_risk_db;

CREATE TABLE IF NOT EXISTS patients (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  age INT NOT NULL,
  gender VARCHAR(20) NOT NULL,
  glucose DOUBLE NOT NULL,
  cholesterol DOUBLE NOT NULL,
  bmi DOUBLE NOT NULL,
  blood_pressure DOUBLE NOT NULL,
  heart_rate DOUBLE NOT NULL
);

CREATE TABLE IF NOT EXISTS predictions (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  patient_id BIGINT NOT NULL,
  diabetes_probability DOUBLE NOT NULL,
  heart_probability DOUBLE NOT NULL,
  diabetes_risk VARCHAR(20) NOT NULL,
  heart_risk VARCHAR(20) NOT NULL,
  prediction_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  explanation_json TEXT,
  recommendations_json TEXT,
  CONSTRAINT fk_predictions_patient FOREIGN KEY (patient_id) REFERENCES patients(id)
);

CREATE INDEX idx_prediction_date ON predictions(prediction_date);
CREATE INDEX idx_prediction_risk ON predictions(diabetes_risk, heart_risk);

