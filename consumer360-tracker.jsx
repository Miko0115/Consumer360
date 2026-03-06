import { useState } from "react";

const weeks = [
  {
    week: 1,
    label: "Data Engineering & Schema",
    color: "#2DD4BF",
    tasks: [
      "Define Star Schema (Fact Sales, Dim Customer, Dim Product)",
      "Clean raw transaction logs (handle NULLs & negative return values)",
      "Create SQL View for the 'Single Customer View'",
    ],
    validation: "ER Diagram validation · SQL query execution < 2 seconds",
  },
  {
    week: 2,
    label: "Analytical Core (Python)",
    color: "#818CF8",
    tasks: [
      "Write production-grade Python script to pull data from SQL",
      "Calculate R, F, M scores and segment users (Champions / Loyalists / Hibernating)",
      "Run Association Rule algorithm via mlxtend to find product bundles",
    ],
    validation: "Statistical audit: Champions must show highest avg spend & LTV",
  },
  {
    week: 3,
    label: "Dashboard Construction",
    color: "#FB923C",
    tasks: [
      "Import processed datasets into Power BI",
      "Create Matrix Visual for Cohort Analysis",
      "Implement Row Level Security (RLS) for Regional Managers",
    ],
    validation: "UX Audit: clarity, efficiency, and 'Key Influencers' visual accuracy",
  },
  {
    week: 4,
    label: "Automation & Handoff",
    color: "#F472B6",
    tasks: [
      "Automate Python ETL script (Task Scheduler / Cron / Airflow simulation)",
      "Create Executive Presentation Deck with 'Churn Risk' customer list",
      "Run full automated pipeline test: raw data → published dashboard",
    ],
    validation: "Full end-to-end automated pipeline test",
  },
];

const enhancements = [
  {
    category: "Predictive Modeling",
    icon: "🧠",
    color: "#A78BFA",
    items: [
      {
        label: "CLV Prediction Model",
        desc: "Use Python's lifetimes library (BG/NBD + Gamma-Gamma) to forecast future revenue per customer — moves the project from descriptive to predictive.",
        impact: "HIGH",
        week: "Week 2",
      },
      {
        label: "Churn Probability Score",
        desc: "Logistic regression or XGBoost model that assigns each customer a churn risk % — pairs perfectly with CLV to prioritise retention spend.",
        impact: "HIGH",
        week: "Week 2",
      },
      {
        label: "Basket Analysis (Apriori / FP-Growth)",
        desc: "Surface product bundle recommendations per segment — Champions get upsell offers, Hibernating customers get win-back bundles.",
        impact: "MED",
        week: "Week 2",
      },
    ],
  },
  {
    category: "Dashboard Excellence",
    icon: "📊",
    color: "#34D399",
    items: [
      {
        label: "What-If Simulation Panel",
        desc: "Power BI slicer: 'What if we re-engage 20% of At Risk customers?' → projected revenue impact updates live. Turns reporting into decision-making.",
        impact: "HIGH",
        week: "Week 3",
      },
      {
        label: "Cohort Retention Heatmap",
        desc: "Month-on-month retention grid by signup cohort — visually striking and analytically deep. One of the most impressive visuals you can add.",
        impact: "MED",
        week: "Week 3",
      },
    ],
  },
  {
    category: "Engineering & Pipeline",
    icon: "⚙️",
    color: "#FBBF24",
    items: [
      {
        label: "Apache Airflow DAG",
        desc: "Replace basic Task Scheduler with a documented Airflow DAG (local simulation is fine). Shows you understand production-grade data pipelines.",
        impact: "MED",
        week: "Week 4",
      },
      {
        label: "Data Quality Gates (Great Expectations)",
        desc: "Add automated data quality checks at each pipeline stage — signals professional engineering thinking that most projects completely skip.",
        impact: "MED",
        week: "Week 1",
      },
    ],
  },
  {
    category: "Storytelling & Impact",
    icon: "📋",
    color: "#FB923C",
    items: [
      {
        label: "Executive Brief (1-pager)",
        desc: "Concrete business recommendation with numbers: e.g. 'Re-engaging 1,240 At Risk customers = £380K revenue opportunity.' Analysis → action.",
        impact: "HIGH",
        week: "Week 4",
      },
    ],
  },
];

const stack = [
  { label: "SQL", desc: "Precise data extraction & window functions", icon: "🗄️" },
  { label: "Python", desc: "RFM logic, Lifetimes library, ML modeling", icon: "🐍" },
  { label: "Power BI", desc: "Dynamic visualization & segmentation mapping", icon: "📊" },
];

const segments = [
  { name: "Champions", color: "#2DD4BF", desc: "Highest R+F+M scores" },
  { name: "Loyalists", color: "#818CF8", desc: "High frequency, consistent spend" },
  { name: "At Risk", color: "#FB923C", desc: "Once high value, now fading" },
  { name: "Hibernating", color: "#64748B", desc: "Low recency, low engagement" },
];

const ImpactBadge = ({ level }) => {
  const colors = { HIGH: ["#FF6B6B", "#FF6B6B20"], MED: ["#FBBF24", "#FBBF2420"] };
  const [text, bg] = colors[level] || ["#94A3B8", "#94A3B820"];
  return (
    <span style={{ fontSize: 9, fontFamily: "monospace", letterSpacing: "0.15em", background: bg, color: text, border: `1px solid ${text}50`, borderRadius: 4, padding: "2px 6px", fontWeight: 700 }}>
      {level} IMPACT
    </span>
  );
};

export default function Consumer360Tracker() {
  const [checked, setChecked] = useState({});
  const [enhChecked, setEnhChecked] = useState({});
  const [activeWeek, setActiveWeek] = useState(1);
  const [activeTab, setActiveTab] = useState("plan");

  const toggle = (weekIdx, taskIdx) => {
    const key = `${weekIdx}-${taskIdx}`;
    setChecked((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const toggleEnh = (catIdx, itemIdx) => {
    const key = `${catIdx}-${itemIdx}`;
    setEnhChecked((prev) => ({ ...prev, [key]: !prev[key] }));
  };

  const totalTasks = weeks.reduce((s, w) => s + w.tasks.length, 0);
  const completedTasks = Object.values(checked).filter(Boolean).length;
  const totalEnh = enhancements.reduce((s, c) => s + c.items.length, 0);
  const completedEnh = Object.values(enhChecked).filter(Boolean).length;
  const overallTotal = totalTasks + totalEnh;
  const overallDone = completedTasks + completedEnh;
  const progress = Math.round((overallDone / overallTotal) * 100);
  const activeData = weeks[activeWeek - 1];

  return (
    <div style={{ fontFamily: "'Georgia', 'Times New Roman', serif", background: "#0A0F1E", minHeight: "100vh", color: "#E2E8F0", padding: "32px 24px" }}>
      <div style={{ maxWidth: 780, margin: "0 auto" }}>

        {/* Header */}
        <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", flexWrap: "wrap", gap: 16, marginBottom: 8 }}>
          <div>
            <div style={{ fontSize: 11, letterSpacing: "0.2em", color: "#2DD4BF", textTransform: "uppercase", marginBottom: 6, fontFamily: "monospace" }}>
              Infotact Solutions · Squadron Beta · Q4 2025
            </div>
            <h1 style={{ margin: 0, fontSize: 32, fontWeight: 700, color: "#fff", lineHeight: 1.1 }}>
              Consumer<span style={{ color: "#2DD4BF" }}>360</span>
            </h1>
            <div style={{ fontSize: 13, color: "#94A3B8", marginTop: 4 }}>
              Retail Analytics — Customer Segmentation & Lifetime Value Engine
            </div>
          </div>
          <div style={{ textAlign: "right" }}>
            <div style={{ fontSize: 11, color: "#64748B", fontFamily: "monospace", letterSpacing: "0.1em" }}>OVERALL PROGRESS</div>
            <div style={{ fontSize: 38, fontWeight: 700, color: "#2DD4BF", lineHeight: 1 }}>{progress}%</div>
            <div style={{ fontSize: 11, color: "#64748B", fontFamily: "monospace" }}>{overallDone}/{overallTotal} tasks</div>
          </div>
        </div>

        {/* Progress bar */}
        <div style={{ height: 4, background: "#1E293B", borderRadius: 2, margin: "20px 0 32px" }}>
          <div style={{ height: "100%", width: `${progress}%`, background: "linear-gradient(90deg, #2DD4BF, #818CF8, #F472B6)", borderRadius: 2, transition: "width 0.4s ease" }} />
        </div>

        {/* Objective */}
        <div style={{ background: "#111827", border: "1px solid #1E293B", borderLeft: "3px solid #2DD4BF", borderRadius: 8, padding: "16px 20px", marginBottom: 32 }}>
          <div style={{ fontSize: 11, color: "#2DD4BF", letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: 6, fontFamily: "monospace" }}>Business Objective</div>
          <p style={{ margin: 0, fontSize: 14, lineHeight: 1.7, color: "#CBD5E1" }}>
            A national retail chain is experiencing significant churn. Build an automated, scalable <strong style={{ color: "#E2E8F0" }}>RFM segmentation model</strong> to identify high-value "Whales" vs "Churn Risks" — enabling targeted marketing campaigns and strategic retention decisions.
          </p>
        </div>

        {/* Segments */}
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontSize: 11, color: "#94A3B8", letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: 12, fontFamily: "monospace" }}>RFM Segments to Produce</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 10 }}>
            {segments.map((s) => (
              <div key={s.name} style={{ background: "#111827", border: `1px solid ${s.color}30`, borderRadius: 8, padding: "12px 14px" }}>
                <div style={{ width: 8, height: 8, borderRadius: "50%", background: s.color, marginBottom: 8 }} />
                <div style={{ fontSize: 13, fontWeight: 600, color: "#E2E8F0", marginBottom: 3 }}>{s.name}</div>
                <div style={{ fontSize: 11, color: "#64748B" }}>{s.desc}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div style={{ marginBottom: 32 }}>
          <div style={{ fontSize: 11, color: "#94A3B8", letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: 12, fontFamily: "monospace" }}>Tech Stack</div>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            {stack.map((s, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 10, background: "#111827", border: "1px solid #1E293B", borderRadius: 8, padding: "10px 14px", flex: "1 1 180px" }}>
                <span style={{ fontSize: 20 }}>{s.icon}</span>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 700, color: "#E2E8F0" }}>{s.label}</div>
                  <div style={{ fontSize: 11, color: "#64748B" }}>{s.desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tab Switcher */}
        <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
          {[
            { id: "plan", label: `📅  4-Week Plan  (${completedTasks}/${totalTasks})` },
            { id: "enhance", label: `⚡  Enhancements  (${completedEnh}/${totalEnh})` },
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              style={{
                background: activeTab === tab.id ? "#E2E8F0" : "#111827",
                color: activeTab === tab.id ? "#0A0F1E" : "#94A3B8",
                border: `1px solid ${activeTab === tab.id ? "#E2E8F0" : "#1E293B"}`,
                borderRadius: 8, padding: "10px 18px", cursor: "pointer",
                fontSize: 13, fontWeight: activeTab === tab.id ? 700 : 400,
                fontFamily: "monospace", transition: "all 0.2s",
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* ── 4-WEEK PLAN TAB ── */}
        {activeTab === "plan" && (
          <>
            <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap" }}>
              {weeks.map((w) => {
                const wDone = w.tasks.filter((_, ti) => checked[`${w.week - 1}-${ti}`]).length;
                const isActive = activeWeek === w.week;
                return (
                  <button key={w.week} onClick={() => setActiveWeek(w.week)} style={{
                    background: isActive ? w.color : "#111827", color: isActive ? "#0A0F1E" : "#94A3B8",
                    border: `1px solid ${isActive ? w.color : "#1E293B"}`, borderRadius: 6,
                    padding: "8px 14px", cursor: "pointer", fontSize: 12,
                    fontWeight: isActive ? 700 : 400, fontFamily: "monospace", transition: "all 0.2s", letterSpacing: "0.05em",
                  }}>
                    W{w.week} · {wDone}/{w.tasks.length}
                  </button>
                );
              })}
            </div>

            <div style={{ background: "#111827", border: `1px solid ${activeData.color}40`, borderRadius: 10, padding: "20px 24px", marginBottom: 32 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 18 }}>
                <div style={{ width: 32, height: 32, borderRadius: 6, background: activeData.color, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 12, fontWeight: 700, color: "#0A0F1E" }}>
                  W{activeData.week}
                </div>
                <div>
                  <div style={{ fontSize: 15, fontWeight: 600, color: "#E2E8F0" }}>{activeData.label}</div>
                  <div style={{ fontSize: 11, color: "#64748B", fontFamily: "monospace" }}>Week {activeData.week} of 4</div>
                </div>
              </div>

              <div style={{ display: "flex", flexDirection: "column", gap: 10, marginBottom: 18 }}>
                {activeData.tasks.map((task, ti) => {
                  const key = `${activeData.week - 1}-${ti}`;
                  const done = checked[key];
                  return (
                    <div key={ti} onClick={() => toggle(activeData.week - 1, ti)} style={{
                      display: "flex", alignItems: "flex-start", gap: 12, cursor: "pointer",
                      background: done ? `${activeData.color}15` : "#0A0F1E",
                      border: `1px solid ${done ? activeData.color + "50" : "#1E293B"}`,
                      borderRadius: 8, padding: "12px 14px", transition: "all 0.2s",
                    }}>
                      <div style={{
                        width: 18, height: 18, borderRadius: 4, border: `2px solid ${done ? activeData.color : "#334155"}`,
                        background: done ? activeData.color : "transparent", flexShrink: 0, marginTop: 1,
                        display: "flex", alignItems: "center", justifyContent: "center",
                        fontSize: 11, color: "#0A0F1E", fontWeight: 700, transition: "all 0.2s",
                      }}>
                        {done ? "✓" : ""}
                      </div>
                      <span style={{ fontSize: 13, color: done ? "#64748B" : "#CBD5E1", textDecoration: done ? "line-through" : "none", lineHeight: 1.5 }}>
                        {task}
                      </span>
                    </div>
                  );
                })}
              </div>

              <div style={{ background: "#0A0F1E", border: "1px solid #1E293B", borderRadius: 6, padding: "10px 14px" }}>
                <div style={{ fontSize: 10, color: "#64748B", letterSpacing: "0.15em", textTransform: "uppercase", fontFamily: "monospace", marginBottom: 4 }}>✦ Review / Validation Gate</div>
                <div style={{ fontSize: 12, color: "#94A3B8" }}>{activeData.validation}</div>
              </div>
            </div>
          </>
        )}

        {/* ── ENHANCEMENTS TAB ── */}
        {activeTab === "enhance" && (
          <div style={{ marginBottom: 32 }}>
            <div style={{ background: "#111827", border: "1px solid #A78BFA30", borderLeft: "3px solid #A78BFA", borderRadius: 8, padding: "14px 18px", marginBottom: 24 }}>
              <div style={{ fontSize: 13, color: "#CBD5E1", lineHeight: 1.6 }}>
                These additions move the project from <strong style={{ color: "#E2E8F0" }}>descriptive → predictive</strong> and from <strong style={{ color: "#E2E8F0" }}>analysis → action</strong>. Tick each off as you build it — <span style={{ color: "#FF6B6B", fontFamily: "monospace", fontSize: 11 }}>HIGH IMPACT</span> items are the most differentiating.
              </div>
            </div>

            {enhancements.map((cat, catIdx) => (
              <div key={catIdx} style={{ marginBottom: 28 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 12 }}>
                  <span style={{ fontSize: 18 }}>{cat.icon}</span>
                  <div style={{ fontSize: 12, fontWeight: 700, color: cat.color, letterSpacing: "0.1em", textTransform: "uppercase", fontFamily: "monospace" }}>
                    {cat.category}
                  </div>
                  <div style={{ flex: 1, height: 1, background: `${cat.color}30` }} />
                  <div style={{ fontSize: 11, color: "#64748B", fontFamily: "monospace" }}>
                    {cat.items.filter((_, ii) => enhChecked[`${catIdx}-${ii}`]).length}/{cat.items.length} done
                  </div>
                </div>

                <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                  {cat.items.map((item, itemIdx) => {
                    const key = `${catIdx}-${itemIdx}`;
                    const done = enhChecked[key];
                    return (
                      <div key={itemIdx} onClick={() => toggleEnh(catIdx, itemIdx)} style={{
                        display: "flex", alignItems: "flex-start", gap: 14, cursor: "pointer",
                        background: done ? `${cat.color}10` : "#111827",
                        border: `1px solid ${done ? cat.color + "50" : "#1E293B"}`,
                        borderRadius: 10, padding: "14px 16px", transition: "all 0.2s",
                      }}>
                        <div style={{
                          width: 20, height: 20, borderRadius: 5, border: `2px solid ${done ? cat.color : "#334155"}`,
                          background: done ? cat.color : "transparent", flexShrink: 0, marginTop: 2,
                          display: "flex", alignItems: "center", justifyContent: "center",
                          fontSize: 12, color: "#0A0F1E", fontWeight: 700, transition: "all 0.2s",
                        }}>
                          {done ? "✓" : ""}
                        </div>
                        <div style={{ flex: 1 }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 5 }}>
                            <span style={{ fontSize: 14, fontWeight: 600, color: done ? "#64748B" : "#E2E8F0", textDecoration: done ? "line-through" : "none" }}>
                              {item.label}
                            </span>
                            <ImpactBadge level={item.impact} />
                            <span style={{ fontSize: 10, color: "#475569", fontFamily: "monospace", background: "#1E293B", padding: "2px 6px", borderRadius: 4 }}>
                              {item.week}
                            </span>
                          </div>
                          <div style={{ fontSize: 12, color: done ? "#475569" : "#94A3B8", lineHeight: 1.6 }}>
                            {item.desc}
                          </div>
                        </div>
                      </div>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Final Deliverables */}
        <div style={{ background: "#111827", border: "1px solid #1E293B", borderRadius: 10, padding: "20px 24px" }}>
          <div style={{ fontSize: 11, color: "#94A3B8", letterSpacing: "0.15em", textTransform: "uppercase", marginBottom: 14, fontFamily: "monospace" }}>Final Submission Checklist</div>
          {[
            { icon: "📁", label: "Code Repository", desc: "All Python scripts & SQL files committed to GitHub" },
            { icon: "📊", label: "Dashboard Publication", desc: "Power BI dashboard published with functional link" },
            { icon: "📄", label: "Project Report", desc: "Max 5 pages: problem → architecture → findings → methodology" },
          ].map((d, i) => (
            <div key={i} style={{ display: "flex", gap: 12, padding: "10px 0", borderBottom: i < 2 ? "1px solid #1E293B" : "none" }}>
              <span style={{ fontSize: 18 }}>{d.icon}</span>
              <div>
                <div style={{ fontSize: 13, fontWeight: 600, color: "#E2E8F0" }}>{d.label}</div>
                <div style={{ fontSize: 12, color: "#64748B" }}>{d.desc}</div>
              </div>
            </div>
          ))}
        </div>

        <div style={{ textAlign: "center", marginTop: 24, fontSize: 11, color: "#334155", fontFamily: "monospace", letterSpacing: "0.15em" }}>
          INFOTACT SOLUTIONS · CONFIDENTIAL · Q4 2025
        </div>
      </div>
    </div>
  );
}
