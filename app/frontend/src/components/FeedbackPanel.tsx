/**
 * FeedbackPanel.tsx
 * -----------------
 * Displays the coaching analysis after a player decision.
 *
 * Layout hierarchy:
 *   1. Verdict  — score + rating badge + mistake tag (immediate outcome)
 *   2. Action   — what the user did
 *   3. Analysis — explanation + strategic reasoning
 *   4. Better play + sizing (if any)
 *   5. Context  — hand strength, position, risk
 *   6. Meta     — luck vs. strategy, key concept
 *   7. Drill    — recommended next practice
 *
 * Architecture: pure display component. No poker logic here.
 */

import React from 'react'
import type { DecisionAnalysis } from '../types'
import { RATING_COLORS, RATING_LABELS } from '../types'

interface FeedbackPanelProps {
  analysis: DecisionAnalysis
  onNextHand: () => void
}

const MISTAKE_LABELS: Record<string, string> = {
  passive_play:       'Passive play',
  missed_value:       'Missed value',
  hand_selection:     'Hand selection',
  over_bluff:         'Over-bluffing',
  calling_station:    'Calling station',
  sizing_error:       'Sizing error',
  general_mistake:    'Mistake',
}

export default function FeedbackPanel({ analysis, onNextHand }: FeedbackPanelProps) {
  const ratingColor = RATING_COLORS[analysis.rating]
  const ratingLabel = RATING_LABELS[analysis.rating]
  const mistakeLabel = analysis.mistake_category
    ? (MISTAKE_LABELS[analysis.mistake_category] ?? analysis.mistake_category.replace(/_/g, ' '))
    : null

  return (
    <div className="panel feedback-panel">
      <div className="panel-title">Coach Feedback</div>

      {/* ── 1. Verdict ── */}
      <div className="rating-row">
        <span className="rating-score" style={{ color: ratingColor }}>
          {analysis.rating_score}/10
        </span>
        <span
          className="rating-badge"
          style={{ background: ratingColor + '22', color: ratingColor, border: `1px solid ${ratingColor}` }}
        >
          {ratingLabel}
        </span>
        {mistakeLabel && (
          <span className="mistake-tag">{mistakeLabel}</span>
        )}
      </div>

      {/* ── 2. Your action ── */}
      <div className="feedback-section">
        <div className="feedback-section-title">Your action</div>
        <div className="feedback-section-body" style={{ textTransform: 'capitalize' }}>
          {analysis.user_action}
          {analysis.bet_amount ? ` — ${analysis.bet_amount} chips` : ''}
        </div>
      </div>

      <hr className="feedback-divider" />

      {/* ── 3. Analysis (explanation + strategic reasoning) ── */}
      <div className="feedback-section">
        <div className="feedback-section-title">Analysis</div>
        <div className="feedback-section-body">{analysis.explanation}</div>
      </div>

      {/* ── 4. Better play ── */}
      {analysis.best_alternative && (
        <div className="feedback-section">
          <div className="feedback-section-title">Better play</div>
          <div className="feedback-section-body" style={{ color: 'var(--gold-light)' }}>
            {analysis.best_alternative}
          </div>
        </div>
      )}

      {analysis.recommended_sizing && (
        <div className="feedback-section">
          <div className="feedback-section-title">Recommended sizing</div>
          <div className="feedback-section-body">{analysis.recommended_sizing}</div>
        </div>
      )}

      <hr className="feedback-divider" />

      {/* ── 5. Context ── */}
      {analysis.hand_strength && (
        <div className="feedback-section">
          <div className="feedback-section-title">Hand strength</div>
          <div className="feedback-section-body">{analysis.hand_strength}</div>
        </div>
      )}

      {analysis.position_note && (
        <div className="feedback-section">
          <div className="feedback-section-title">Position</div>
          <div className="feedback-section-body">{analysis.position_note}</div>
        </div>
      )}

      {analysis.risk_analysis && (
        <div className="feedback-section">
          <div className="feedback-section-title">Risk</div>
          <div className="feedback-section-body" style={{ color: 'var(--text-muted)' }}>
            {analysis.risk_analysis}
          </div>
        </div>
      )}

      <hr className="feedback-divider" />

      {/* ── 6. Meta ── */}
      <div className="feedback-section">
        <div className="feedback-section-title">Luck vs. strategy</div>
        <div className="feedback-section-body">{analysis.luck_vs_strategy}</div>
      </div>

      {analysis.key_concept && (
        <div className="feedback-section">
          <div className="feedback-section-title">Key concept</div>
          <div className="feedback-section-body" style={{ color: 'var(--gold)' }}>
            {analysis.key_concept}
          </div>
        </div>
      )}

      {/* ── 7. Drill ── */}
      <div className="feedback-section">
        <div className="feedback-section-title">Recommended drill</div>
        <div className="drill-box">{analysis.recommended_drill}</div>
      </div>

      <button
        className="btn btn-primary"
        style={{ marginTop: '1rem', width: '100%' }}
        onClick={onNextHand}
      >
        Next Hand →
      </button>
    </div>
  )
}
