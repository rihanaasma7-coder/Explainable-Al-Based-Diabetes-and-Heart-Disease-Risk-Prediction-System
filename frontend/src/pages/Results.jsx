import React from "react";
import { Link } from "react-router-dom";
import RiskBadge from "../components/RiskBadge";
import { latestPrediction } from "../state";

export default function Results() {
  const result = latestPrediction();
  if (!result) return <Empty />;
  return (
    <section className="space-y-6">
      <div><h2 className="text-2xl font-semibold text-[#3a0f23]">Prediction Results</h2><p className="mt-1 text-sm text-[#873a6c]">Prediction ID #{result.id}</p></div>
      <div className="grid gap-4 md:grid-cols-2">
        <ResultCard title="Diabetes Risk" risk={result.diabetesRisk} probability={result.diabetesProbability} />
        <ResultCard title="Heart Disease Risk" risk={result.heartRisk} probability={result.heartProbability} />
      </div>
      <div className="flex gap-3">
        <Link className="rounded bg-[#7c2b5e] px-4 py-2 font-semibold text-white hover:bg-[#6b2353]" to="/explainability">View Explainability</Link>
        <Link className="rounded border border-[#c47e8a] px-4 py-2 font-semibold text-[#491734] hover:bg-[#f2d6d0]" to="/recommendations">Recommendations</Link>
      </div>
    </section>
  );
}

function ResultCard({ title, risk, probability }) {
  const displayProbability = Number(probability).toFixed(1).replace(/\.0$/, "");
  const progress = Math.min(Math.max(Number(probability) || 0, 0), 100);
  return <div className="rounded border border-[#e0999a] bg-white p-6 shadow-sm"><div className="flex items-center justify-between"><h3 className="font-semibold text-[#3a0f23]">{title}</h3><RiskBadge risk={risk} /></div><p className="mt-6 text-5xl font-semibold text-[#491734]">{displayProbability}%</p><div className="mt-4 h-2 rounded bg-[#f2d6d0]"><div className="h-2 rounded bg-[#7c2b5e]" style={{ width: `${progress}%` }} /></div></div>;
}

function Empty() {
  return <div className="rounded border border-[#e0999a] bg-white p-6 text-[#491734]">No prediction found. Run a new prediction first.</div>;
}
