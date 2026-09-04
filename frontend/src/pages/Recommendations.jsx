import React from "react";
import { CheckCircle2 } from "lucide-react";
import { latestPrediction } from "../state";

export default function Recommendations() {
  const result = latestPrediction();
  const items = result?.recommendations || [];
  return (
    <section className="space-y-6">
      <div><h2 className="text-2xl font-semibold text-[#3a0f23]">Personalized Recommendations</h2><p className="mt-1 text-sm text-[#873a6c]">Rule-based guidance generated from the submitted health parameters.</p></div>
      <div className="rounded border border-[#e0999a] bg-white p-6 shadow-sm">
        {items.length === 0 ? <p className="text-[#491734]">No recommendations available.</p> : <div className="space-y-3">{items.map((item) => <div key={item} className="flex gap-3 rounded border border-[#c47e8a]/60 bg-[#f2d6d0]/60 px-4 py-3 text-[#491734]"><CheckCircle2 size={20} className="mt-0.5 shrink-0 text-[#7c2b5e]" /><span>{item}</span></div>)}</div>}
      </div>
    </section>
  );
}
