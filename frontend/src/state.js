export function savePrediction(result) {
  localStorage.setItem("latestPrediction", JSON.stringify(result));
}

export function latestPrediction() {
  return JSON.parse(localStorage.getItem("latestPrediction") || "null");
}

