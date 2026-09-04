package com.miniproject.healthrisk.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.core.type.TypeReference;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.miniproject.healthrisk.dto.PredictionRequest;
import com.miniproject.healthrisk.dto.PredictionResponse;
import com.miniproject.healthrisk.model.Patient;
import com.miniproject.healthrisk.model.Prediction;
import com.miniproject.healthrisk.repository.PatientRepository;
import com.miniproject.healthrisk.repository.PredictionRepository;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;
import java.util.Map;

@Service
public class PredictionService {
    private final PatientRepository patientRepository;
    private final PredictionRepository predictionRepository;
    private final RestTemplate restTemplate;
    private final ObjectMapper mapper;
    private final String mlServiceUrl;

    public PredictionService(PatientRepository patientRepository, PredictionRepository predictionRepository,
                             RestTemplate restTemplate, ObjectMapper mapper,
                             @Value("${ml.service-url}") String mlServiceUrl) {
        this.patientRepository = patientRepository;
        this.predictionRepository = predictionRepository;
        this.restTemplate = restTemplate;
        this.mapper = mapper;
        this.mlServiceUrl = mlServiceUrl;
    }

    public PredictionResponse predict(PredictionRequest request) {
        Map<String, Object> mlResponse = restTemplate.postForObject(mlServiceUrl + "/predict", request, Map.class);
        Map<String, Object> diseases = (Map<String, Object>) mlResponse.get("diseases");
        Map<String, Object> diabetes = (Map<String, Object>) diseases.get("diabetes");
        Map<String, Object> heart = (Map<String, Object>) diseases.get("heart");
        List<String> recommendations = (List<String>) mlResponse.get("recommendations");

        Patient patient = new Patient();
        patient.setAge(request.age());
        patient.setGender(request.gender());
        patient.setGlucose(request.glucose());
        patient.setBmi(request.bmi());
        patient.setCholesterol(request.cholesterol());
        patient.setBloodPressure(request.bloodPressure());
        patient.setHeartRate(request.heartRate());
        patientRepository.save(patient);

        Prediction prediction = new Prediction();
        prediction.setPatient(patient);
        prediction.setDiabetesProbability(((Number) diabetes.get("probability")).doubleValue());
        prediction.setHeartProbability(((Number) heart.get("probability")).doubleValue());
        prediction.setDiabetesRisk((String) diabetes.get("risk"));
        prediction.setHeartRisk((String) heart.get("risk"));
        prediction.setExplanationJson(writeJson(Map.of("diabetes", diabetes.get("explanation"), "heart", heart.get("explanation"))));
        prediction.setRecommendationsJson(writeJson(recommendations));
        predictionRepository.save(prediction);

        return toResponse(prediction);
    }

    public Map<String, Object> explanation(Long id) {
        return readJson(findPrediction(id).getExplanationJson(), new TypeReference<>() {});
    }

    public List<String> recommendation(Long id) {
        return readJson(findPrediction(id).getRecommendationsJson(), new TypeReference<>() {});
    }

    public Map<String, Object> dashboard() {
        long total = predictionRepository.count();
        long high = predictionRepository.findAll().stream()
                .filter(p -> "High".equalsIgnoreCase(p.getDiabetesRisk()) || "High".equalsIgnoreCase(p.getHeartRisk()))
                .count();
        return Map.of("totalPredictions", total, "highRiskPredictions", high);
    }

    private PredictionResponse toResponse(Prediction prediction) {
        return new PredictionResponse(
                prediction.getId(),
                prediction.getDiabetesRisk(),
                prediction.getHeartRisk(),
                prediction.getDiabetesProbability(),
                prediction.getHeartProbability(),
                explanation(prediction.getId()),
                recommendation(prediction.getId())
        );
    }

    private Prediction findPrediction(Long id) {
        return predictionRepository.findById(id).orElseThrow(() -> new IllegalArgumentException("Prediction not found: " + id));
    }

    private String writeJson(Object value) {
        try {
            return mapper.writeValueAsString(value);
        } catch (JsonProcessingException ex) {
            throw new IllegalStateException("Unable to serialize prediction payload", ex);
        }
    }

    private <T> T readJson(String value, TypeReference<T> type) {
        try {
            return mapper.readValue(value, type);
        } catch (JsonProcessingException ex) {
            throw new IllegalStateException("Unable to parse stored prediction payload", ex);
        }
    }
}

