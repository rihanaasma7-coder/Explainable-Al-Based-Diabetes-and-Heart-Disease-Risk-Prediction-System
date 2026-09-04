package com.miniproject.healthrisk.controller;

import com.miniproject.healthrisk.dto.PredictionRequest;
import com.miniproject.healthrisk.dto.PredictionResponse;
import com.miniproject.healthrisk.service.PredictionService;
import io.swagger.v3.oas.annotations.Operation;
import jakarta.validation.Valid;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.Map;

@RestController
@RequestMapping("/api")
@CrossOrigin(origins = "*")
public class PredictionController {
    private final PredictionService service;

    public PredictionController(PredictionService service) {
        this.service = service;
    }

    @PostMapping("/predict")
    @Operation(summary = "Predict diabetes and heart disease risk")
    public PredictionResponse predict(@Valid @RequestBody PredictionRequest request) {
        return service.predict(request);
    }

    @GetMapping("/explanation/{id}")
    public Map<String, Object> explanation(@PathVariable Long id) {
        return service.explanation(id);
    }

    @GetMapping("/recommendation/{id}")
    public List<String> recommendation(@PathVariable Long id) {
        return service.recommendation(id);
    }

    @GetMapping("/dashboard")
    public Map<String, Object> dashboard() {
        return service.dashboard();
    }
}

