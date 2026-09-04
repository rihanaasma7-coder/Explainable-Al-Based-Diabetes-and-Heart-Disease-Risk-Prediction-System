package com.miniproject.healthrisk.dto;

import jakarta.validation.constraints.*;

public record PredictionRequest(
        @NotNull @Min(1) @Max(120) Integer age,
        @NotBlank String gender,
        @NotNull @Positive Double glucose,
        @NotNull @Positive Double bmi,
        @NotNull @Positive Double cholesterol,
        @NotNull @Positive Double bloodPressure,
        @NotNull @Positive Double heartRate
) {
}

