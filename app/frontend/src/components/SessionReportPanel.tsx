/**
 * SessionReportPanel.tsx
 * ----------------------
 * Displays the rich end-of-session summary fetched from the backend.
 * Triggered by the user when they want to review their session.
 *
 * Data source: GET /api/session/{sessionId}/summary
 * Fetch function: fetchSessionReport() from api/client.ts
 *
 * Architecture: pure display component. No poker logic here.
 */

import React, { useState } from 'react'
import type { SessionReport } from '../types'
import { fetchSessionReport } from '../api/client'

interface SessionReportPanelProps {
  sessionId: string
  decisionCount: number
}

export default function SessionReportPanel({ sessionId, decisionCount }: SessionReportPanelProps) {
  const [report, setReport] = useState<SessionReport | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [loaded, setLoaded] = useState(false)

  if (decisionCount === 0) return null

  async function handleLoad() {
    setLoading(true)
    setError(null)
    try {
      const r = await fetchSessionReport(sessionId)
      setReport(r)
      setLoaded(true)
    } catch {
      setError('Could not load session report.')
    } finally {
      setLoading(false)
    }
  }

  const mistakeLabel = report?.recurring_mistake
    ? report.recurring_mistake.replace(/_/g, ' ')
    : null

  return (
    <div className="panel">
      <div className="panel-title">Training Reflection</div>

      {!loaded && (
        <button
          className="btn btn-secondary"
          style={{ width: '100%' }}
          onClick={handleLoad}
          disabled={loading}
        >
          {loading ? 'Loading…' : 'View Training Reflection'}
        </button>
      )}

      {error && (
        <p style={{ color: '#fca5a5', fontSize: '0.85rem', textAlign: 'center' }}>{error}</p>
      )}

      {report && (
        <div className="session-report">
          {/* Key stats */}
          <div className="session-report-stats">
            <div className="stat-box">
              <span className="stat-value">{report.total_decisions}</span>
              <span className="stat-label">Decisions</span>
            </div>
            <div className="stat-box">
              <span className="stat-value">{report.average_score.toFixed(1)}</span>
              <span className="stat-label">Avg Score</span>
            </div>
            <div className="stat-box">
              <span className="stat-value">{Math.round(report.accuracy_pct)}%</span>
              <span className="stat-label">Accuracy</span>
            </div>
          </div>

          {/* Best decision */}
          {report.strongest_decision && (
            <div className="session-report-block">
              <div className="session-report-block-title">Best decision</div>
              <div className="session-report-block-value" style={{ color: '#22c55e' }}>
                {report.strongest_decision.action} on the {report.strongest_decision.street} · {report.strongest_decision.score}/10
              </div>
            </div>
          )}

          {/* Worst decision */}
          {report.weakest_decision && (
            <div className="session-report-block">
              <div className="session-report-block-title">Weakest decision</div>
              <div className="session-report-block-value" style={{ color: '#f97316' }}>
                {report.weakest_decision.action} on the {report.weakest_decision.street} · {report.weakest_decision.score}/10
              </div>
            </div>
          )}

          {/* Recurring mistake */}
          {mistakeLabel && (
            <div className="session-report-block">
              <div className="session-report-block-title">Recurring pattern</div>
              <div className="session-report-block-value">
                <span className="mistake-tag">{mistakeLabel}</span>
              </div>
            </div>
          )}

          {/* Recommended drill */}
          {report.recommended_drill && (
            <>
              <div className="session-report-block-title">Next practice</div>
              <div className="session-report-drill">{report.recommended_drill}</div>
            </>
          )}

          {/* Progress note */}
          <p className="session-report-note">{report.progress_note}</p>
        </div>
      )}
    </div>
  )
}
