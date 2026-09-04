package com.miniproject.healthrisk.repository;

import com.miniproject.healthrisk.model.Patient;
import org.springframework.data.jpa.repository.JpaRepository;

public interface PatientRepository extends JpaRepository<Patient, Long> {
}

