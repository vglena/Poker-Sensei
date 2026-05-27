/**
 * HandHistory.tsx
 * ---------------
 * Shows a scrollable list of past decisions in this session.
 */

import React from 'react'
import type { HandHistoryEntry } from '../types'
import { RATING_COLORS, ACTION_LABELS } from '../types'
import { PlayingCard } from './PokerTable'

interface HandHistoryProps {
  history: HandHistoryEntry[]
}

export default function HandHistory({ history }: HandHistoryProps) {
  if (history.length === 0) {
    return (
      <div className="panel">
        <div className="panel-title">Lesson History</div>
        <div className="empty-state">No lessons yet. Begin a drill to start.</div>
      </div>
    )
  }

  return (
    <div className="panel">
      <div className="panel-title">Lesson History ({history.length})</div>
      <ul className="hand-history-list">
        {[...history].reverse().map((entry) => {
          const color = RATING_COLORS[entry.rating]
          return (
            <li
              key={entry.hand_id}
              className="hand-history-item"
              style={{ borderLeftColor: color }}
            >
              {/* Hole cards mini */}
              <div className="cards-mini">
                {entry.hole_cards.map((code, i) => (
                  <PlayingCard key={i} code={code} size="small" />
                ))}
              </div>

              {/* Action vs best */}
              <div className="history-actions">
                <span className="history-your-action" style={{ textTransform: 'capitalize' }}>
                  {entry.street} · You: {ACTION_LABELS[entry.user_action]}
                </span>
                {entry.best_action_note && entry.best_action_note !== 'This is the recommended play.' && entry.best_action_note !== 'This is correct.' && (
                  <span className="history-best-action">
                    {entry.best_action_note.length > 50
                      ? entry.best_action_note.slice(0, 50) + '…'
                      : entry.best_action_note}
                  </span>
                )}
              </div>

              {/* Score */}
              <span className="score-text" style={{ color }}>
                {entry.rating_score}/10
              </span>
            </li>
          )
        })}
      </ul>
    </div>
  )
}
