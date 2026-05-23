// app/dashboard/page.tsx
"use client"
import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import {
  PieChart, Pie, Cell,
  BarChart, Bar,
  XAxis, YAxis, Tooltip, ResponsiveContainer,
  CartesianGrid
} from "recharts"
import { useAuth } from "../context/AuthContext"
import { setAuthTokenGetter } from "../services/api"
import {
  fetchDashboardStats,
  fetchMetrics,
  DashboardStats,
  MetricEntry,
  evaluateMetrics,
} from "../services/api"

export default function DashboardPage() {
  const { user, loading, getIdToken } = useAuth()
  const router = useRouter()

  const [stats, setStats]       = useState<DashboardStats | null>(null)
  const [metrics, setMetrics]   = useState<MetricEntry[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isEvaluating, setIsEvaluating] = useState(false)
  const [evalMessage, setEvalMessage]   = useState("")



  // ── Wire auth token ───────────────────────────
  useEffect(() => {
    setAuthTokenGetter(getIdToken)
  }, [getIdToken])

  // ── Redirect if not logged in ─────────────────
  useEffect(() => {
    if (!loading && !user) {
      router.push("/login")
    }
  }, [user, loading, router])

  // ── Load dashboard data ───────────────────────
  useEffect(() => {
    const loadData = async () => {
      if (!user) return
      setIsLoading(true)
      const [statsData, metricsData] = await Promise.all([
        fetchDashboardStats(),
        fetchMetrics(50)
      ])
      setStats(statsData)
      setMetrics(metricsData)
      setIsLoading(false)
    }
    
    if (user) loadData()
  }, [user])

  if (loading || isLoading) {
    return (
      <div className="loading-screen">
        <div className="loading-spinner">📊</div>
        <p>Loading dashboard...</p>
      </div>
    )
  }

  if (!stats || stats.total_queries === 0) {
    return (
      <div className="dashboard-empty">
        <div className="dashboard-empty-icon">📊</div>
        <h1>No Data Yet!</h1>
        <p>Start chatting to generate metrics.</p>
        <Link href="/" className="dashboard-back-btn">
          ← Back to Chat
        </Link>
      </div>
    )
  }

  // ── Chart Data ────────────────────────────────
  const levelData = [
    { name: "Beginner", value: stats.beginner_count },
    { name: "Expert", value: stats.expert_count }
  ]

  const topicData = [
    { name: "On-Topic", value: stats.total_queries - stats.off_topic_count },
    { name: "Off-Topic", value: stats.off_topic_count }
  ]

  const COLORS = ["#2563eb", "#8b5cf6", "#10b981", "#f59e0b"]

  // ── Latency over recent queries ───────────────
  const latencyData = [...metrics]
    .reverse()
    .slice(-15)
    .map((m, i) => ({
      name: `Q${i + 1}`,
      latency: Math.round(m.latency_ms)
    }))

  // ── Run Evaluation ────────────────────────────
  const handleEvaluate = async () => {
    setIsEvaluating(true)
    setEvalMessage("Evaluating... this may take a few minutes ⏳")

    const result = await evaluateMetrics()

    if (result) {
      setEvalMessage(`✅ ${result.message}`)
      // Reload stats to show new scores
      const [statsData, metricsData] = await Promise.all([
        fetchDashboardStats(),
        fetchMetrics(50)
      ])
      setStats(statsData)
      setMetrics(metricsData)
    } else {
      setEvalMessage("❌ Evaluation failed. Check backend logs.")
    }

    setIsEvaluating(false)
    // Clear message after 5 seconds
    setTimeout(() => setEvalMessage(""), 5000)
  }



  return (
    <div className="dashboard-container">

      {/* ── Header ────────────────────────────── */}
      <div className="dashboard-header">
        <div>
          <h1 className="dashboard-title">📊 RAG Quality Dashboard</h1>
          <p className="dashboard-subtitle">
            Performance metrics for your interior design assistant
          </p>
        </div>
        <div className="dashboard-header-actions">
          <button
            onClick={handleEvaluate}
            disabled={isEvaluating}
            className="evaluate-btn"
          >
            {isEvaluating ? "⏳ Evaluating..." : "🔬 Evaluate Quality"}
          </button>
          <Link href="/" className="dashboard-back-btn">
            ← Back to Chat
          </Link>
        </div>
      </div>

      {/* ── Eval Message ──────────────────────── */}
      {evalMessage && (
        <div className="eval-message">
          {evalMessage}
        </div>
      )}



      {/* ── Stat Cards ────────────────────────── */}
      <div className="stat-cards">
        <div className="stat-card">
          <div className="stat-value">{stats.total_queries}</div>
          <div className="stat-label">Total Queries</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.off_topic_rate}%</div>
          <div className="stat-label">Off-Topic Rate</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.avg_latency_ms}ms</div>
          <div className="stat-label">Avg Response Time</div>
        </div>
        <div className="stat-card">
          <div className="stat-value">{stats.avg_retrieved_count}</div>
          <div className="stat-label">Avg Docs Retrieved</div>
        </div>
      </div>


      {/* ── RAGAS Quality Scores ──────────────── */}
      {(stats.avg_faithfulness !== null ||
        stats.avg_answer_relevancy !== null ||
        stats.avg_context_precision !== null) && (
        <div className="quality-section">
          <h2 className="quality-heading">🔬 RAG Quality Scores</h2>
          <div className="quality-cards">
            <div className="quality-card">
              <div className="quality-value">
                {stats.avg_faithfulness !== null
                  ? `${(stats.avg_faithfulness * 100).toFixed(0)}%`
                  : "—"}
              </div>
              <div className="quality-label">Faithfulness</div>
              <div className="quality-desc">Answer grounded in docs</div>
            </div>
            <div className="quality-card">
              <div className="quality-value">
                {stats.avg_answer_relevancy !== null
                  ? `${(stats.avg_answer_relevancy * 100).toFixed(0)}%`
                  : "—"}
              </div>
              <div className="quality-label">Answer Relevancy</div>
              <div className="quality-desc">Addresses the question</div>
            </div>
            <div className="quality-card">
              <div className="quality-value">
                {stats.avg_context_precision !== null
                  ? `${(stats.avg_context_precision * 100).toFixed(0)}%`
                  : "—"}
              </div>
              <div className="quality-label">Context Precision</div>
              <div className="quality-desc">Retrieved docs relevant</div>
            </div>
          </div>
        </div>
      )}



      {/* ── Charts Row ────────────────────────── */}
      <div className="dashboard-charts">

        {/* User Level Distribution */}
        <div className="chart-box">
          <h3 className="chart-title">User Level Distribution</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={levelData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                {levelData.map((_, i) => (
                  <Cell key={i} fill={COLORS[i]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Topic Distribution */}
        <div className="chart-box">
          <h3 className="chart-title">On-Topic vs Off-Topic</h3>
          <ResponsiveContainer width="100%" height={250}>
            <PieChart>
              <Pie
                data={topicData}
                cx="50%"
                cy="50%"
                outerRadius={80}
                dataKey="value"
                label={({ name, value }) => `${name}: ${value}`}
              >
                <Cell fill="#10b981" />
                <Cell fill="#ef4444" />
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* ── Latency Chart ─────────────────────── */}
      <div className="chart-box-wide">
        <h3 className="chart-title">Response Time (Last 15 Queries)</h3>
        <ResponsiveContainer width="100%" height={250}>
          <BarChart data={latencyData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#2a2a2a" />
            <XAxis dataKey="name" stroke="#888" />
            <YAxis stroke="#888" />
            <Tooltip
              contentStyle={{
                backgroundColor: "#1a1a1a",
                border: "1px solid #2a2a2a",
                borderRadius: "8px"
              }}
            />
            <Bar dataKey="latency" fill="#2563eb" radius={[4, 4, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      {/* ── Recent Queries Table ──────────────── */}
      <div className="chart-box-wide">
        <h3 className="chart-title">Recent Queries</h3>
        <div className="metrics-table-wrapper">
          <table className="metrics-table">
            <thead>
              <tr>
                <th>Question</th>
                <th>Level</th>
                <th>Docs</th>
                <th>Latency</th>
                <th>Rating</th>
              </tr>
            </thead>
            <tbody>
              {metrics.slice(0, 20).map((m) => (
                <tr key={m.id}>
                  <td className="table-question">
                    {m.question.slice(0, 50)}
                    {m.question.length > 50 ? "..." : ""}
                  </td>
                  <td>
                    <span className={`level-tag ${
                      m.is_off_topic ? "tag-offtopic" :
                      m.user_level === "EXPERT" ? "tag-expert" : "tag-beginner"
                    }`}>
                      {m.is_off_topic ? "OFF-TOPIC" : m.user_level}
                    </span>
                  </td>
                  <td>{m.retrieved_count}</td>
                  <td>{Math.round(m.latency_ms)}ms</td>
                  <td>
                    {m.user_rating === 1 ? "👍" :
                     m.user_rating === -1 ? "👎" : "—"}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

    </div>
  )
}

