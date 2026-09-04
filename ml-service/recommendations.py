from __future__ import annotations

from typing import Dict, List


def build_recommendations(patient: Dict) -> List[str]:
    recommendations: List[str] = []
    if patient.get("glucose", 0) > 140:
        recommendations.append("Reduce sugar intake and prefer low glycemic index meals.")
    if patient.get("bmi", 0) > 25:
        recommendations.append("Exercise regularly for at least 150 minutes per week.")
    if patient.get("bloodPressure", 0) > 130:
        recommendations.append("Follow a low sodium diet and monitor blood pressure weekly.")
    if patient.get("cholesterol", 0) > 200:
        recommendations.append("Limit saturated fats and increase fiber-rich foods.")
    if patient.get("heartRate", 0) > 100:
        recommendations.append("Consult a clinician if elevated resting heart rate persists.")
    if not recommendations:
        recommendations.append("Maintain current healthy habits and schedule routine checkups.")
    return recommendations

