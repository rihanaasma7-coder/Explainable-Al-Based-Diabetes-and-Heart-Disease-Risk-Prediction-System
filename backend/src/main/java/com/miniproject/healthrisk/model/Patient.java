package com.miniproject.healthrisk.model;

import jakarta.persistence.*;

@Entity
@Table(name = "patients")
public class Patient {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    private Integer age;
    private String gender;
    private Double glucose;
    private Double cholesterol;
    private Double bmi;
    @Column(name = "blood_pressure")
    private Double bloodPressure;
    @Column(name = "heart_rate")
    private Double heartRate;

    public Long getId() { return id; }
    public Integer getAge() { return age; }
    public void setAge(Integer age) { this.age = age; }
    public String getGender() { return gender; }
    public void setGender(String gender) { this.gender = gender; }
    public Double getGlucose() { return glucose; }
    public void setGlucose(Double glucose) { this.glucose = glucose; }
    public Double getCholesterol() { return cholesterol; }
    public void setCholesterol(Double cholesterol) { this.cholesterol = cholesterol; }
    public Double getBmi() { return bmi; }
    public void setBmi(Double bmi) { this.bmi = bmi; }
    public Double getBloodPressure() { return bloodPressure; }
    public void setBloodPressure(Double bloodPressure) { this.bloodPressure = bloodPressure; }
    public Double getHeartRate() { return heartRate; }
    public void setHeartRate(Double heartRate) { this.heartRate = heartRate; }
}

