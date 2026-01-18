import { useState } from "react";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

export default function App() {
  const [resume, setResume] = useState(null);
  const [jd, setJd] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    if (!resume) return alert("Upload a resume PDF");
    if (!jd.trim()) return alert("Paste a job description");

    const fd = new FormData();
    fd.append("resume", resume);
    fd.append("job_description", jd);

    setLoading(true);
    setResult(null);

    try {
      const res = await fetch("http://localhost:5002/api/analyze-resume", {
        method: "POST",
        body: fd,
      });
      const data = await res.json();
      setResult(data);
    } catch (err) {
      alert("Something went wrong");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const confidence =
    result?.final_score >= 75
      ? { label: "Strong Match", color: "bg-indigo-600" }
      : result?.final_score >= 50
      ? { label: "Moderate Match", color: "bg-amber-600" }
      : { label: "Low Match", color: "bg-rose-600" };

  const comparisonData = result
    ? [
        { name: "TF-IDF (Keyword)", score: result.skill_match_score },
        { name: "Semantic (Embeddings)", score: result.semantic_similarity },
      ]
    : [];

  return (
    <div className="min-h-screen bg-[#0b1220] text-slate-200">

      {/* ================= DUSKY HEADER ================= */}
      <section
        className="relative"
        style={{
          background:
            "linear-gradient(135deg, #0b1026 0%, #1b1f3b 45%, #2a2f5a 100%)",
        }}
      >
        <div className="max-w-6xl mx-auto px-6 py-24">
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight">
            ProfileIQ{" "}
            <span className="text-indigo-300 font-semibold">Match</span>
          </h1>

          <p className="mt-5 max-w-2xl text-slate-300 leading-relaxed">
            An intelligent profile-matching platform that evaluates how well a
            candidate aligns with a role using explainable, multi-signal
            intelligence — not just keywords. Designed for thoughtful evaluation, not instant judgment.
          </p>

          <div className="mt-8 text-sm text-slate-400">
            Skill relevance • Semantic understanding • Role alignment •
            Experience signals
          </div>
        </div>
      </section>

      {/* ================= ANALYZER ================= */}
      <section className="max-w-4xl mx-auto px-6 py-16">
        <div className="bg-[#11162a] rounded-2xl p-8 border border-white/5 shadow-xl">

          {/* ================= PROCEDURE ================= */}
          <div className="mb-8 bg-[#0b1220] rounded-xl p-5 border border-white/5">
            <h3 className="text-lg font-semibold text-indigo-300 mb-3">
              How to use ProfileIQ Match
            </h3>

            <ol className="list-decimal pl-5 space-y-2 text-sm text-slate-300">
              <li>
                Upload your <span className="text-indigo-400 font-medium">resume (PDF)</span> so the system can extract skills, experience, and context.
              </li>
              <li>
                Paste the <span className="text-indigo-400 font-medium">job description</span> to define role expectations and required competencies.
              </li>
              <li>
                Click <span className="text-indigo-400 font-medium">Analyze Profile</span> to evaluate alignment using keyword, semantic, role, and experience signals.
              </li>
              <li>
                Review the <span className="text-indigo-400 font-medium">match score, confidence label</span>, and explainability insights to understand the result.
              </li>
            </ol>
          </div>

          <input
            type="file"
            accept=".pdf"
            onChange={(e) => setResume(e.target.files[0])}
            className="block w-full text-sm mb-4
                       file:mr-4 file:py-2 file:px-4
                       file:rounded-md file:border-0
                       file:bg-slate-700 file:text-slate-100
                       hover:file:bg-slate-600"
          />

          <textarea
            rows="5"
            placeholder="Paste Job Description"
            value={jd}
            onChange={(e) => setJd(e.target.value)}
            className="w-full p-3 rounded-md mb-4 bg-[#0b1220]
                       border border-white/10 focus:outline-none
                       focus:ring-2 focus:ring-indigo-600"
          />

          <button
            onClick={submit}
            disabled={loading}
            className="bg-indigo-600 hover:bg-indigo-700
                       px-6 py-2 rounded-md font-semibold
                       transition disabled:opacity-50"
          >
            {loading ? "Analyzing..." : "Analyze Profile"}
          </button>

          {result && (
            <div className="mt-10 space-y-10">

              {/* Final Score */}
              <div>
                <div className="flex items-center gap-4 mb-2">
                  <h3 className="text-lg font-semibold">
                    Final Match Score: {result.final_score}%
                  </h3>
                  <span
                    className={`px-3 py-1 text-sm rounded-full text-white ${confidence.color}`}
                  >
                    {confidence.label}
                  </span>
                </div>

                <div className="w-full bg-slate-700 rounded-full h-4">
                  <div
                    className="h-4 bg-indigo-500 rounded-full transition-all"
                    style={{ width: `${result.final_score}%` }}
                  />
                </div>
                <p className="mt-2 text-sm text-slate-400">
                  {confidence.label === "Strong Match" && "The profile demonstrates strong alignment across skills, intent, and role expectations."}
                  {confidence.label === "Moderate Match" && "The profile partially aligns with the role. Strengthening missing skills or clarifying experience could improve the match."}
                  {confidence.label === "Low Match" && "The profile currently shows limited alignment with the role requirements. Consider reviewing required skills and role focus."}
                </p>
              </div>

              {/* Explainability */}
              <div>
                <h3 className="text-lg font-semibold mb-4">
                  Why this score?
                </h3>
                <p className="text-sm text-slate-400 mb-3">
                  Skill coverage reflects how well the resume satisfies explicitly stated role requirements.
                </p>

                <div className="grid md:grid-cols-2 gap-4">
                  <ExplainCard title="Skill Match" value={result.skill_match_score} />
                  <ExplainCard title="Semantic Similarity" value={result.semantic_similarity} />
                  <ExplainCard title="Role Alignment" value={result.role_alignment_score} />
                  <ExplainCard title="Experience Signal" value={result.experience_score} />
                </div>
              </div>

              {/* Contribution Chart */}
              <div>
                <h3 className="text-lg font-semibold mb-2">
                  Score Contribution Breakdown
                </h3>
                <p className="text-sm text-slate-400 mb-4">
                  This chart shows how different evaluation signals contribute to the final
                  match score. Keyword matching captures explicit skills, while semantic
                  matching captures contextual alignment.
                </p>

                <div className="h-64 bg-[#0b1220] rounded-xl p-4 border border-white/5">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart
                      data={[
                        { name: "Keyword Match", value: 40 },
                        { name: "Semantic Match", value: 30 },
                        { name: "Role Alignment", value: 20 },
                        { name: "Experience Signal", value: 10 },
                      ]}
                    >
                      <XAxis dataKey="name" stroke="#cbd5e1" />
                      <YAxis unit="%" stroke="#cbd5e1" />
                      <Tooltip
                        contentStyle={{
                          backgroundColor: "#020617",
                          borderRadius: "8px",
                          border: "1px solid #334155",
                          color: "#e2e8f0",
                        }}
                      />
                      <Bar dataKey="value" fill="#818cf8" radius={[6, 6, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* Recommendations */}
              <div>
                <h3 className="font-semibold mb-2">
                  {confidence.label === "Strong Match" && "Next Steps"}
                  {confidence.label === "Moderate Match" && "Improvement Suggestions"}
                  {confidence.label === "Low Match" && "Guidance"}
                </h3>
                <ul className="list-disc pl-6 text-sm text-slate-300">
                  {result.recommendations.map((r, i) => (
                    <li key={i}>{r}</li>
                  ))}
                </ul>
              </div>

            </div>
          )}
        </div>
      </section>
    </div>
  );
}

/* ================= CARD ================= */
function ExplainCard({ title, value }) {
  return (
    <div className="bg-[#0b1220] p-5 rounded-xl border border-white/5 relative">
      <h4 className="text-slate-300 font-semibold flex items-center gap-2">
        {title}
        <span
          className="text-xs text-slate-500 cursor-help"
          title={
            title === "Skill Match"
              ? "Exact overlap between required skills in the job description and the resume"
              : title === "Semantic Similarity"
              ? "Contextual similarity using sentence embeddings, beyond exact keywords"
              : title === "Role Alignment"
              ? "Alignment between resume focus and role intent (intern, developer, engineer, etc.)"
              : "Estimated experience depth inferred from resume signals"
          }
        >ⓘ</span>
      </h4>
      <p className="text-2xl font-bold text-indigo-400">{value}%</p>
    </div>
  );
}