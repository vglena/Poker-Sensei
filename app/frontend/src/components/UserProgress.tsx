/**
 * UserProgress.tsx
 * ----------------
 * Displays session stats: hands played, average score, accuracy, level.
 */

import React from 'react'
import type { UserProfile } from '../types'

interface UserProgressProps {
  profile: UserProfile
  sessionDecisions: number
  sessionAvgScore: number
}

export default function UserProgress({ profile, sessionDecisions, sessionAvgScore }: UserProgressProps) {
  const sessionAccuracy = sessionDecisions > 0
    ? Math.round((sessionAvgScore / 10) * 100)
    : 0

  return (
    <div className="panel">
      <div className="panel-title">Session Progress</div>

      <div className="stats-grid">
        <div className="stat-box">
          <span className="stat-value">{sessionDecisions}</span>
          <span className="stat-label">Decisions</span>
        </div>
        <div className="stat-box">
          <span className="stat-value">{sessionDecisions > 0 ? sessionAvgScore.toFixed(1) : '—'}</span>
          <span className="stat-label">Avg Score</span>
        </div>
        <div className="stat-box">
          <span className="stat-value">{sessionDecisions > 0 ? `${sessionAccuracy}%` : '—'}</span>
          <span className="stat-label">Accuracy</span>
        </div>
        <div className="stat-box">
          <span className="stat-value" style={{ fontSize: '1rem', paddingTop: '4px', textTransform: 'capitalize' }}>
            {profile.level}
          </span>
          <span className="stat-label">Level</span>
        </div>
      </div>

      {/* All-time totals */}
      {profile.total_decisions > 0 && (
        <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)', borderTop: '1px solid var(--felt-border)', paddingTop: '0.75rem' }}>
          All time: {profile.total_sessions} sessions · {profile.total_decisions} decisions
          {profile.average_score > 0 && ` · avg ${profile.average_score.toFixed(1)}/10`}
        </div>
      )}
    </div>
  )
}
