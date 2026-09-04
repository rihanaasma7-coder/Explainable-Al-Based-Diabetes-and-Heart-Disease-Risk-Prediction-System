import { Loader2, Send } from "lucide-react";
import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api";
import { savePrediction } from "../state";

const fieldConfig = {
  age: { min: 1, max: 120, integer: true, step: 1 },
  gender: {},
  glucose: { min: 40, max: 600, integer: true, step: 1 },
  bmi: { min: 10, max: 80, integer: false, step: 0.1 },
  cholesterol: { min: 50, max: 600, integer: true, step: 1 },
  bloodPressure: { min: 50, max: 300, integer: true, step: 1 },
  heartRate: { min: 30, max: 250, integer: true, step: 1 }
};

const initial = { age: "", gender: "", glucose: "", bmi: "", cholesterol: "", bloodPressure: "", heartRate: "" };

const normalizeNumberValue = (value) => {
  if (value === "") return "";
  const normalized = value.replace(/^0+(?=\d)/, "");
  return normalized === "" ? "0" : normalized;
};

const validateField = (name, value) => {
  if (name === "gender") {
    return value ? "" : "Required";
  }
  const config = fieldConfig[name];
  if (!config) return "";
  if (value === "") return "Required";
  if (config.integer && !/^\d+$/.test(value)) return "Must be a whole number";
  if (!config.integer && !/^\d+(\.\d+)?$/.test(value)) return "Must be a valid number";
  const numeric = Number(value);
  if (Number.isNaN(numeric)) return "Must be a valid number";
  if (numeric < config.min || numeric > config.max) return `Must be between ${config.min} and ${config.max}`;
  return "";
};

export default function Predict() {
  const [form, setForm] = useState(initial);
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const change = (event) => {
    const { name, value } = event.target;
    setForm({ ...form, [name]: value });
    setErrors((prev) => ({ ...prev, [name]: "" }));
  };

  const blur = (event) => {
    const { name, value, type } = event.target;
    if (type !== "number") return;
    const normalized = normalizeNumberValue(value);
    setForm({ ...form, [name]: normalized });
    setErrors((prev) => ({ ...prev, [name]: validateField(name, normalized) }));
  };

  const validateAll = () => {
    return Object.keys(fieldConfig).reduce((acc, key) => {
      const error = validateField(key, form[key]);
      if (error) acc[key] = error;
      return acc;
    }, {});
  };

  async function submit(event) {
    event.preventDefault();
    const validationErrors = validateAll();
    if (Object.keys(validationErrors).length > 0) {
      setErrors(validationErrors);
      alert("Please fill all required fields");
      return;
    }

    setLoading(true);
    try {
      const payload = {
        age: Number(form.age),
        gender: form.gender,
        glucose: Number(form.glucose),
        bmi: Number(form.bmi),
        cholesterol: Number(form.cholesterol),
        bloodPressure: Number(form.bloodPressure),
        heartRate: Number(form.heartRate)
      };
      const { data } = await api.post("/predict", payload);
      savePrediction(data);
      navigate("/results");
    } finally {
      setLoading(false);
    }
  }

  return (
    <section className="space-y-6">
      <div><h2 className="text-2xl font-semibold text-[#3a0f23]">Patient Risk Prediction</h2><p className="mt-1 text-sm text-[#873a6c]">Enter current clinical indicators to classify diabetes and heart disease risk.</p></div>
      <form onSubmit={submit} className="rounded border border-[#e0999a] bg-white p-6 shadow-sm">
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          <Field label="Age (years)" name="age" value={form.age} onChange={change} onBlur={blur} error={errors.age} config={fieldConfig.age} />
          <label className="space-y-1 text-sm font-medium">
            Gender
            <select name="gender" value={form.gender} onChange={change} className="input">
              <option value="">Select gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
            {errors.gender && <p className="text-xs text-[#873a6c]">{errors.gender}</p>}
          </label>
          <Field label="Glucose (mg/dL)" name="glucose" value={form.glucose} onChange={change} onBlur={blur} error={errors.glucose} config={fieldConfig.glucose} />
          <Field label="BMI (kg/m²)" name="bmi" value={form.bmi} onChange={change} onBlur={blur} error={errors.bmi} config={fieldConfig.bmi} />
          <Field label="Cholesterol (mg/dL)" name="cholesterol" value={form.cholesterol} onChange={change} onBlur={blur} error={errors.cholesterol} config={fieldConfig.cholesterol} />
          <Field label="Blood Pressure (mmHg)" name="bloodPressure" value={form.bloodPressure} onChange={change} onBlur={blur} error={errors.bloodPressure} config={fieldConfig.bloodPressure} />
          <Field label="Heart Rate (bpm)" name="heartRate" value={form.heartRate} onChange={change} onBlur={blur} error={errors.heartRate} config={fieldConfig.heartRate} />
        </div>
        <button className="mt-6 inline-flex items-center gap-2 rounded bg-[#7c2b5e] px-4 py-2.5 font-semibold text-white hover:bg-[#6b2353] active:bg-[#5a1c46]" disabled={loading}>
          {loading ? <Loader2 className="animate-spin" size={18} /> : <Send size={18} />} Predict Risk
        </button>
      </form>
    </section>
  );
}

function Field({ label, error, config, ...props }) {
  return (
    <label className="space-y-1 text-sm font-medium">
      {label}
      <input
        type="number"
        step={config.step}
        min={config.min}
        max={config.max}
        inputMode={config.integer ? "numeric" : "decimal"}
        className={`input ${error ? "border-[#873a6c] ring-[#873a6c]/20" : ""}`}
        {...props}
      />
      {error && <p className="text-xs text-[#873a6c]">{error}</p>}
    </label>
  );
}

