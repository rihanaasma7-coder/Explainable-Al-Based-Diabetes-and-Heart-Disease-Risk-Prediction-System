# Grafana SQL Queries

## Dashboard 1: Disease Risk Trends
```sql
SELECT
  $__timeGroupAlias(prediction_date, '1d'),
  AVG(diabetes_probability) AS diabetes_probability,
  AVG(heart_probability) AS heart_probability
FROM predictions
WHERE $__timeFilter(prediction_date)
GROUP BY 1
ORDER BY 1;
```

## Dashboard 2: Prediction Count
```sql
SELECT COUNT(*) AS prediction_count
FROM predictions;
```

## Dashboard 3: Average Glucose
```sql
SELECT AVG(glucose) AS average_glucose
FROM patients;
```

## Dashboard 4: Average BMI
```sql
SELECT AVG(bmi) AS average_bmi
FROM patients;
```

## Dashboard 5: High-Risk Patient Percentage
```sql
SELECT
  ROUND(
    100 * SUM(CASE WHEN diabetes_risk = 'High' OR heart_risk = 'High' THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0),
    2
  ) AS high_risk_percentage
FROM predictions;
```

