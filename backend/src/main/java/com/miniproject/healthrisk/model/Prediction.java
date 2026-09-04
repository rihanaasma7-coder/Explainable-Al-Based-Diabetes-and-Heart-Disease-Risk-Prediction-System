package com.miniproject.healthrisk.model;

import jakarta.persistence.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "predictions")
public class Prediction {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    @ManyToOne(optional = false)
    @JoinColumn(name = "patient_id")
    private Patient patient;
    @Column(name = "diabetes_probability")
    private Double diabetesProbability;
    @Column(name = "heart_probability")
    private Double heartProbability;
    @Column(name = "diabetes_risk")
    private String diabetesRisk;
    @Column(name = "heart_risk")
    private String heartRisk;
    @Column(name = "prediction_date")
    private LocalDateTime predictionDate = LocalDateTime.now();
    @Lob
    @Column(columnDefinition = "TEXT")
    private String explanationJson;
    @Lob
    @Column(columnDefinition = "TEXT")
    private String recommendationsJson;

    public Long getId() { return id; }
    public Patient getPatient() { return patient; }
    public void setPatient(Patient patient) { this.patient = patient; }
    public Double getDiabetesProbability() { return diabetesProbability; }
    public void setDiabetesProbability(Double diabetesProbability) { this.diabetesProbability = diabetesProbability; }
    public Double getHeartProbability() { return heartProbability; }
    public void setHeartProbability(Double heartProbability) { this.heartProbability = heartProbability; }
    public String getDiabetesRisk() { return diabetesRisk; }
    public void setDiabetesRisk(String diabetesRisk) { this.diabetesRisk = diabetesRisk; }
    public String getHeartRisk() { return heartRisk; }
    public void setHeartRisk(String heartRisk) { this.heartRisk = heartRisk; }
    public LocalDateTime getPredictionDate() { return predictionDate; }
    public String getExplanationJson() { return explanationJson; }
    public void setExplanationJson(String explanationJson) { this.explanationJson = explanationJson; }
    public String getRecommendationsJson() { return recommendationsJson; }
    public void setRecommendationsJson(String recommendationsJson) { this.recommendationsJson = recommendationsJson; }
}

