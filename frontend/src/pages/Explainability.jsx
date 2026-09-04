import React from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { latestPrediction } from "../state";
import { chartPalette } from "../theme";

export default function Explainability() {
  const result = latestPrediction();
  if (!result) return <div className="rounded border border-[#e0999a] bg-white p-6 text-[#491734]">No explanation available yet.</div>;
  const diabetes = result.explanation.diabetes;
  const heart = result.explanation.heart;
  return (
    <section className="space-y-6">
      <div><h2 className="text-2xl font-semibold text-[#3a0f23]">Explainable AI</h2><p className="mt-1 text-sm text-[#873a6c]">SHAP-style importance and LIME local factors for the latest prediction.</p></div>
      <Explain title="Diabetes" data={diabetes} />
      <Explain title="Heart Disease" data={heart} />
    </section>
  );
}

function Explain({ title, data }) {
  return (
    <div className="grid gap-4 lg:grid-cols-2">
      <div className="rounded border border-[#e0999a] bg-white p-5 shadow-sm">
        <h3 className="font-semibold text-[#3a0f23]">{title} SHAP Feature Importance</h3>
        <div className="mt-4 h-72">
          <ResponsiveContainer>
            <BarChart data={data.shapFactors}>
              <CartesianGrid strokeDasharray="3 3" stroke="#e0999a" /><XAxis dataKey="feature" stroke="#491734" /><YAxis stroke="#491734" /><Tooltip /><Bar dataKey="impact" fill={chartPalette[0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      <div className="rounded border border-[#e0999a] bg-white p-5 shadow-sm">
        <h3 className="font-semibold text-[#3a0f23]">{title} LIME Top Features</h3>
        <div className="mt-4 space-y-3">
          {data.limeFactors.map((item, index) => <div key={`${item.feature}-${index}`} className="flex items-center justify-between rounded border border-[#e0999a]/70 bg-[#f2d6d0]/50 px-3 py-2 text-[#491734]"><span>{item.feature}</span><span className="font-semibold text-[#7c2b5e]">{item.weight ?? item.impact}</span></div>)}
        </div>
      </div>
    </div>
  );
}
