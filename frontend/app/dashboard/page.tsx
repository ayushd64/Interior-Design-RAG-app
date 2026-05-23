// app/dashboard/page.tsx
"use client"

import { useState, useEffect } from "react"
import { useRouter } from "next/navigation"
import Link from "next/link"
import { useAuth } from "../context/AuthContext"
import { setAuthTokenGetter } from "../services/api"
import {
  fetchDashboardStats,
  fetchMetrics,
  evaluateMetrics,
  DashboardStats,
  MetricEntry
} from "../services/api"

export default function DashboardPage() {
  const { user, loading, getIdToken } = useAuth()
  const router = useRouter()

  const [stats, setStats]         = useState<DashboardStats | null>(null)
  const [metrics, setMetrics]     = useState<MetricEntry[]>([])
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
  const loadData = async () => {
    setIsLoading(true)
    const [statsData, metricsData] = await Promise.all([
      fetchDashboardStats(),
      fetchMetrics(50)
    ])
    setStats(statsData)
    setMetrics(metricsData)
    setIsLoading(false)
  }

  useEffect(() => {
    if (user) loadData()
  }, [user])

  // ── Run Evaluation ────────────────────────────
  const handleEvaluate = async () => {
    setIsEvaluating(true)
    setEvalMessage("Evaluating… this may take a few minutes ⏳")

    const result = await evaluateMetrics()

    if (result) {
      setEvalMessage(`✅ ${result.message}`)
      await loadData()
    } else {
      setEvalMessage("❌ Evaluation failed. Check backend logs.")
    }

    setIsEvaluating(false)
    setTimeout(() => setEvalMessage(""), 5000)
  }

  // ── Loading ───────────────────────────────────
  if (loading || isLoading) {
    return (
      <div className="dashboard-empty">
        <div className="dashboard-empty-icon">📊</div>
        <p>Loading dashboard…</p>
      </div>
    )
  }

  // ── Empty ─────────────────────────────────────
  if (!stats || stats.total_queries === 0) {
    return (
      <div className="dashboard-empty">
        <div className="dashboard-empty-icon">📊</div>
        <h1>No Data Yet!</h1>
        <p>Start chatting to generate metrics.</p>
        <Link href="/" className="dashboard-link" style={{ width: "auto", padding: "10px 20px" }}>
          ← Back to Chat
        </Link>
      </div>
    )
  }

  // ── Compute Overall Quality ───────────────────
  const qualityScores = [
    stats.avg_faithfulness,
    stats.avg_answer_relevancy,
    stats.avg_context_precision
  ].filter((s): s is number => s !== null)

  const overallQuality = qualityScores.length > 0
    ? Math.round(
        (qualityScores.reduce((a, b) => a + b, 0) /
         qualityScores.length) * 100
      )
    : null

  // ── Derived values ────────────────────────────
  const beginnerPct = stats.total_queries > 0
    ? Math.round((stats.beginner_count / stats.total_queries) * 100)
    : 0
  const expertPct = 100 - beginnerPct

  const onTopicCount = stats.total_queries - stats.off_topic_count
  const onTopicPct = stats.total_queries > 0
    ? Math.round((onTopicCount / stats.total_queries) * 100)
    : 0
  const offTopicPct = 100 - onTopicPct

  // ── Latency bars (last 12) ────────────────────
  const latencyData = [...metrics].reverse().slice(-12)
  const maxLatency = Math.max(
    ...latencyData.map(m => m.latency_ms), 1
  )

  // ── Helper: format score as % or — ────────────
  const pct = (v: number | null) =>
    v !== null ? `${Math.round(v * 100)}%` : "—"

  return (
    <div className="dashboard-container">

      {/* ── Hero Strip ────────────────────────── */}
      <div className="dash-hero">
        <div>
          <div className="dash-hero-label">RAG Quality Dashboard</div>
          <div className="dash-hero-value">
            {overallQuality !== null
              ? `${overallQuality}% overall quality`
              : "Not yet evaluated"}
          </div>
          <div className="dash-hero-sub">
            across {stats.total_queries} queries
            {overallQuality === null && " · click Evaluate to score quality"}
          </div>
        </div>
        <div className="dash-hero-actions">
          <button
            onClick={handleEvaluate}
            disabled={isEvaluating}
            className="evaluate-btn"
          >
            {isEvaluating ? "⏳ Evaluating…" : "🔬 Evaluate Quality"}
          </button>
          <Link href="/" className="dashboard-back-btn">
            ← Back to Chat
          </Link>
        </div>
      </div>

      {/* ── Eval Message ──────────────────────── */}
      {evalMessage && (
        <div className="eval-message">{evalMessage}</div>
      )}

      {/* ── Quality Cards ─────────────────────── */}
      <div className="quality-cards">
        <div className="quality-card qc-faith">
          <div className="quality-label">Faithfulness</div>
          <div className="quality-value">
            {pct(stats.avg_faithfulness)}
          </div>
          <div className="quality-desc">Answer grounded in docs</div>
        </div>
        <div className="quality-card qc-rel">
          <div className="quality-label">Answer Relevancy</div>
          <div className="quality-value">
            {pct(stats.avg_answer_relevancy)}
          </div>
          <div className="quality-desc">Addresses the question</div>
        </div>
        <div className="quality-card qc-prec">
          <div className="quality-label">Context Precision</div>
          <div className="quality-value">
            {pct(stats.avg_context_precision)}
          </div>
          <div className="quality-desc">Retrieved docs relevant</div>
        </div>
      </div>

      {/* ── Stat Cards ────────────────────────── */}
      <div className="stat-cards">
        <div className="stat-card">
          <div className="stat-label">Total Queries</div>
          <div className="stat-value">{stats.total_queries}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Off-Topic Rate</div>
          <div className="stat-value">{stats.off_topic_rate}%</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Response</div>
          <div className="stat-value">
            {(stats.avg_latency_ms / 1000).toFixed(1)}s
          </div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Avg Docs</div>
          <div className="stat-value">{stats.avg_retrieved_count}</div>
        </div>
      </div>

      {/* ── Split Bars ────────────────────────── */}
      <div className="dashboard-charts">
        <div className="chart-box">
          <div className="chart-title">User Level</div>
          <div className="split-bar">
            <div style={{
              width: `${beginnerPct}%`,
              background: "var(--accent)"
            }} />
            <div style={{
              width: `${expertPct}%`,
              background: "var(--accent-light)"
            }} />
          </div>
          <div className="split-bar-legend">
            <span>Beginner {beginnerPct}%</span>
            <span>Expert {expertPct}%</span>
          </div>
        </div>

        <div className="chart-box">
          <div className="chart-title">On-Topic vs Off-Topic</div>
          <div className="split-bar">
            <div style={{
              width: `${onTopicPct}%`,
              background: "#1D9E75"
            }} />
            <div style={{
              width: `${offTopicPct}%`,
              background: "#D85A30"
            }} />
          </div>
          <div className="split-bar-legend">
            <span>On-Topic {onTopicPct}%</span>
            <span>Off-Topic {offTopicPct}%</span>
          </div>
        </div>
      </div>

      {/* ── Response Time Bars ────────────────── */}
      <div className="chart-box-wide">
        <div className="chart-title">
          Response Time (Last {latencyData.length} Queries)
        </div>
        <div className="latency-bars">
          {latencyData.map((m, i) => (
            <div key={i} className="latency-bar-col">
              <div
                className="latency-bar"
                style={{
                  height: `${(m.latency_ms / maxLatency) * 100}%`
                }}
                title={`${Math.round(m.latency_ms)}ms`}
              />
              <span className="latency-bar-label">
                {(m.latency_ms / 1000).toFixed(0)}s
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Recent Queries Table ──────────────── */}
      <div className="chart-box-wide">
        <div className="chart-title">Recent Queries</div>
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
                  <td>
                    {m.question.slice(0, 50)}
                    {m.question.length > 50 ? "…" : ""}
                  </td>
                  <td>
                    <span className={`level-tag ${
                      m.is_off_topic ? "tag-offtopic" :
                      m.user_level === "EXPERT" ? "tag-expert" : "tag-beginner"
                    }`}>
                      {m.is_off_topic ? "Off-Topic" :
                       m.user_level === "EXPERT" ? "Expert" : "Beginner"}
                    </span>
                  </td>
                  <td>{m.retrieved_count}</td>
                  <td>{(m.latency_ms / 1000).toFixed(1)}s</td>
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

