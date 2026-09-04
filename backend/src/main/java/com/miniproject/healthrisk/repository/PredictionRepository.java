package com.miniproject.healthrisk.repository;

import com.miniproject.healthrisk.model.Prediction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import java.util.Map;

public interface PredictionRepository extends JpaRepository<Prediction, Long> {
    @Query("select count(p) as totalPredictions from Prediction p")
    Map<String, Object> dashboardTotals();
}

