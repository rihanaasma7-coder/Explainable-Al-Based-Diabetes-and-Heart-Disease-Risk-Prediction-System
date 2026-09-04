import React from "react";

export default function RiskBadge({ risk }) {
  const color = risk === "High" ? "bg-[#873a6c] text-white" : risk === "Medium" ? "bg-[#e0999a] text-[#3a0f23]" : "bg-[#c47e8a] text-[#3a0f23]";
  return <span className={`inline-flex rounded px-2.5 py-1 text-sm font-semibold ${color}`}>{risk || "Pending"}</span>;
}
