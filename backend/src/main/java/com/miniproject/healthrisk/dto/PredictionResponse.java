package com.miniproject.healthrisk.dto;

import java.util.List;
import java.util.Map;

public record PredictionResponse(
        Long id,
        String diabetesRisk,
        String heartRisk,
        Double diabetesProbability,
        Double heartProbability,
        Map<String, Object> explanation,
        List<String> recommendations
) {
}

