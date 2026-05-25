/**
 * FeedbackPanel.tsx
 * -----------------
 * Displays the coaching analysis after a player decision.
 *
 * Layout hierarchy:
 *   1. Verdict        — score + rating badge + mistake tag
 *   2. Coach Summary  — 1–2 sentence takeaway (derived from explanation)
 *   3. Your action
 *   4. Best play / Better play
 *   5. Why this matters (mistakes only)
 *   6. Context details (hand strength, position, risk)
 *   7. Key Lesson     — teaching sentence from key_concept
 *   8. Recommended Practice
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

/** Returns the first 1–2 sentences of a text blob. */
function firstSentences(text: string, max = 2): string {
  const parts = text.match(/[^.!?]+[.!?]*/g) ?? [text]
  return parts.slice(0, max).join(' ').trim()
}

/** Derives a coach summary from available fields. */
function deriveCoachSummary(analysis: DecisionAnalysis): string {
  if (analysis.explanation) return firstSentences(analysis.explanation, 2)
  if (analysis.best_alternative) return firstSentences(analysis.best_alternative, 2)
  return ''
}

/** Expands a short concept tag into a teaching sentence. */
function expandKeyConcept(concept: string): string {
  const map: Record<string, string> = {
    'preflop aggression':    'Premium hands should usually be played aggressively in position.',
    'position advantage':    'Acting last gives you more information — use that to your advantage.',
    'pot odds':              'Compare the price you are getting to your odds of winning before calling.',
    'value betting':         'When you have a strong hand, bet to build the pot and get paid by worse hands.',
    'bluff catching':        'A good bluff catcher has enough showdown value to call when the pot odds justify it.',
    'c-bet':                 'A continuation bet on the flop represents the range you opened with preflop.',
    'hand selection':        'Playing fewer, stronger hands from early position reduces costly spots.',
    'fold equity':           'Aggressive bets put pressure on opponents and can win pots without a showdown.',
  }
  const lower = concept.toLowerCase()
  if (map[lower]) return map[lower]
  // Capitalise and add a period if it looks like a label, not a sentence
  if (!concept.includes('.') && concept.length < 60) {
    return concept.charAt(0).toUpperCase() + concept.slice(1) + '.'
  }
  return concept
}

export default function FeedbackPanel({ analysis, onNextHand }: FeedbackPanelProps) {
  const ratingColor = RATING_COLORS[analysis.rating]
  const ratingLabel = RATING_LABELS[analysis.rating]
  const mistakeLabel = analysis.mistake_category
    ? (MISTAKE_LABELS[analysis.mistake_category] ?? analysis.mistake_category.replace(/_/g, ' '))
    : null
  const isMistake = analysis.rating === 'mistake' || analysis.rating === 'blunder'
  const coachSummary = deriveCoachSummary(analysis)
  const keyLesson = analysis.key_concept ? expandKeyConcept(analysis.key_concept) : null

  return (
    <div className="panel feedback-panel">
      <div className="panel-title">Sensei Guidance</div>

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

      {/* ── 2. Coach Summary ── */}
      {coachSummary && (
        <div className="coach-summary">
          {coachSummary}
        </div>
      )}

      <hr className="feedback-divider" />

      {/* ── 3. Your action ── */}
      <div className="feedback-section">
        <div className="feedback-section-title">Your action</div>
        <div className="feedback-section-body" style={{ textTransform: 'capitalize' }}>
          {analysis.user_action}
          {analysis.bet_amount ? ` — ${analysis.bet_amount} chips` : ''}
        </div>
      </div>

      {/* ── 4. Best play ── */}
      {analysis.best_alternative && (
        <div className="feedback-section">
          <div className="feedback-section-title">
            {analysis.rating === 'ok' ? 'Correct discipline (more optimal)' : 'Correct discipline'}
          </div>
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

      {/* ── 5. Why this matters (mistakes only) ── */}
      {isMistake && analysis.risk_analysis && (
        <div className="why-matters-box">
          <div className="why-matters-title">Why it matters</div>
          <div className="why-matters-body">{analysis.risk_analysis}</div>
        </div>
      )}

      <hr className="feedback-divider" />

      {/* ── 6. Context details ── */}
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

      {!isMistake && analysis.risk_analysis && (
        <div className="feedback-section">
          <div className="feedback-section-title">Risk</div>
          <div className="feedback-section-body" style={{ color: 'var(--text-muted)' }}>
            {analysis.risk_analysis}
          </div>
        </div>
      )}

      <div className="feedback-section">
        <div className="feedback-section-title">Luck vs. strategy</div>
        <div className="feedback-section-body">{analysis.luck_vs_strategy}</div>
      </div>

      {/* ── 7. Key Lesson (single block, no duplicate) ── */}
      {keyLesson && (
        <div className="key-lesson-box">
          <div className="key-lesson-title">Lesson to remember</div>
          <div className="key-lesson-body">{keyLesson}</div>
        </div>
      )}

      {/* ── 8. Recommended Practice ── */}
      <div className="feedback-section">
        <div className="feedback-section-title">Next practice</div>
        <div className="drill-box">{analysis.recommended_drill}</div>
      </div>
    </div>
  )
}

