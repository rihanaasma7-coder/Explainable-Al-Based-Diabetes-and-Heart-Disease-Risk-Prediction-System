import { useEffect, useState } from "react";
import { Cell, Pie, PieChart, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from "recharts";
import { api } from "../api";
import { chartPalette } from "../theme";

export default function Dashboard() {
  const [stats, setStats] = useState({ totalPredictions: 0, highRiskPredictions: 0 });
  useEffect(() => {
    api.get("/dashboard").then((res) => setStats(res.data)).catch(() => {});
  }, []);
  const riskData = [
    { name: "High Risk", value: stats.highRiskPredictions },
    { name: "Other", value: Math.max(stats.totalPredictions - stats.highRiskPredictions, 0) }
  ];
  const trend = [
    { name: "Diabetes", value: stats.totalPredictions },
    { name: "Heart", value: stats.totalPredictions },
    { name: "High Risk", value: stats.highRiskPredictions }
  ];
  return (
    <section className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-[#3a0f23]">Clinical Dashboard</h2>
        <p className="mt-1 text-sm text-[#873a6c]">Live operational summary from stored predictions.</p>
      </div>
      <div className="grid gap-4 md:grid-cols-3">
        <Metric label="Total predictions" value={stats.totalPredictions} />
        <Metric label="High-risk patients" value={stats.highRiskPredictions} />
        <Metric label="High-risk percentage" value={`${stats.totalPredictions ? Math.round((stats.highRiskPredictions / stats.totalPredictions) * 100) : 0}%`} />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded border border-[#e0999a] bg-white p-5 shadow-sm">
          <h3 className="font-semibold text-[#3a0f23]">Risk Summary</h3>
          <div className="h-72">
            <ResponsiveContainer>
              <PieChart>
                <Pie data={riskData} dataKey="value" nameKey="name" outerRadius={95}>
                  <Cell fill={chartPalette[0]} /><Cell fill={chartPalette[3]} />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
        <div className="rounded border border-[#e0999a] bg-white p-5 shadow-sm">
          <h3 className="font-semibold text-[#3a0f23]">Prediction Count</h3>
          <div className="h-72">
            <ResponsiveContainer>
              <BarChart data={trend}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e0999a" /><XAxis dataKey="name" stroke="#491734" /><YAxis allowDecimals={false} stroke="#491734" /><Tooltip /><Bar dataKey="value" fill={chartPalette[2]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>
    </section>
  );
}

function Metric({ label, value }) {
  return <div className="rounded border border-[#e0999a] bg-white p-5 shadow-sm"><p className="text-sm text-[#873a6c]">{label}</p><p className="mt-2 text-3xl font-semibold text-[#3a0f23]">{value}</p></div>;
}

