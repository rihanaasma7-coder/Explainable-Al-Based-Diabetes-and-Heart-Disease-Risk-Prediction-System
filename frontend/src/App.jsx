import React from "react";
import { Activity, BarChart3, BrainCircuit, HeartPulse, Lightbulb, Stethoscope } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";

const links = [
  { to: "/", label: "Dashboard", icon: BarChart3 },
  { to: "/predict", label: "Predict", icon: Stethoscope },
  { to: "/results", label: "Results", icon: Activity },
  { to: "/explainability", label: "Explainability", icon: BrainCircuit },
  { to: "/recommendations", label: "Recommendations", icon: Lightbulb }
];

export default function App() {
  return (
    <div className="min-h-screen bg-[#f2d6d0] text-[#491734]">
      <aside className="fixed inset-y-0 left-0 hidden w-72 border-r border-[#e0999a] bg-[#491734] px-5 py-6 text-white lg:block">
        <div className="flex items-center gap-3">
          <div className="grid h-11 w-11 place-items-center rounded bg-[#7c2b5e] text-white">
            <HeartPulse size={24} />
          </div>
          <div>
            <h1 className="text-lg font-semibold leading-tight">Health Risk AI</h1>
            <p className="text-sm text-[#e0999a]">Explainable predictions</p>
          </div>
        </div>
        <nav className="mt-8 space-y-1">
          {links.map(({ to, label, icon: Icon }) => (
            <NavLink key={to} to={to} className={({ isActive }) => `flex items-center gap-3 rounded px-3 py-2.5 text-sm font-medium ${isActive ? "bg-[#7c2b5e] text-white" : "text-[#f2d6d0] hover:bg-[#5a1c46]"}`}>
              <Icon size={18} />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="lg:pl-72">
        <div className="border-b border-[#e0999a] bg-[#3a0f23] px-4 py-3 text-white lg:hidden">
          <div className="flex items-center gap-2 font-semibold"><HeartPulse size={20} /> Health Risk AI</div>
          <nav className="mt-3 flex gap-2 overflow-x-auto pb-1">
            {links.map(({ to, label, icon: Icon }) => (
              <NavLink key={to} to={to} className={({ isActive }) => `flex shrink-0 items-center gap-2 rounded px-3 py-2 text-xs font-medium ${isActive ? "bg-[#7c2b5e] text-white" : "bg-[#491734] text-[#f2d6d0]"}`}>
                <Icon size={15} />
                {label}
              </NavLink>
            ))}
          </nav>
        </div>
        <div className="mx-auto max-w-7xl px-4 py-6 sm:px-6 lg:px-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
