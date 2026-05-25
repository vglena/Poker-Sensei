/**
 * PokerTable.tsx
 * --------------
 * Renders the poker felt area: community cards, hole cards, pot size, stacks.
 */

import React from 'react'
import type { PokerScenario, CardCode } from '../types'
import { SUIT_SYMBOLS, SUIT_COLORS, STREET_LABELS } from '../types'

interface PlayingCardProps {
  code: CardCode
  size?: 'normal' | 'small'
}

export function PlayingCard({ code, size = 'normal' }: PlayingCardProps) {
  if (!code || code.length < 2) {
    return <div className="card placeholder">?</div>
  }

  const rank = code.slice(0, -1)
  const suit = code.slice(-1).toLowerCase()
  const symbol = SUIT_SYMBOLS[suit] ?? suit
  const color = SUIT_COLORS[suit] ?? '#000'
  const isRed = suit === 'h' || suit === 'd'

  if (size === 'small') {
    return (
      <span className={`mini-card ${isRed ? 'red' : 'black'}`} style={{ color }}>
        {rank}{symbol}
      </span>
    )
  }

  return (
    <div className={`card ${isRed ? 'red' : 'black'}`} style={{ color }}>
      <span className="card-rank">{rank}</span>
      <span className="card-suit">{symbol}</span>
    </div>
  )
}

interface PokerTableProps {
  scenario: PokerScenario
}

export default function PokerTable({ scenario }: PokerTableProps) {
  const {
    street,
    hole_cards,
    community_cards,
    pot_size,
    hero_stack,
    villain_stack,
    hero_position,
    villain_position,
  } = scenario

  // Pad community cards to expected count for the street
  const expectedCommunity: Record<string, number> = {
    preflop: 0,
    flop: 3,
    turn: 4,
    river: 5,
  }
  const expected = expectedCommunity[street] ?? community_cards.length
  const communitySlots = Array.from({ length: 5 }, (_, i) =>
    i < community_cards.length ? community_cards[i] : null
  )

  return (
    <div className="panel">
      <div className="panel-title">
        {STREET_LABELS[street]} &nbsp;·&nbsp;
        <span className="position-badge">{hero_position}</span>
      </div>

      <div className="poker-table">
        {/* Community cards */}
        <div>
          <div className="cards-label">Board</div>
          <div className="cards-row">
            {communitySlots.map((code, i) =>
              code ? (
                <PlayingCard key={i} code={code} />
              ) : (
                <div key={i} className="card placeholder">
                  {i < expected ? '?' : ''}
                </div>
              )
            )}
          </div>
        </div>

        {/* Pot info */}
        <div className="poker-table-info">
          <span>Pot: <strong>{pot_size}</strong></span>
          <span>Hero ({hero_position}): <strong>{hero_stack}</strong></span>
          <span>Villain ({villain_position}): <strong>{villain_stack}</strong></span>
        </div>

        {/* Hole cards */}
        <div>
          <div className="cards-label">Your Hand</div>
          <div className="cards-row">
            {hole_cards.map((code, i) => (
              <PlayingCard key={i} code={code} />
            ))}
          </div>
        </div>
      </div>

      {/* Action history */}
      {scenario.action_history.length > 0 && (
        <div style={{ marginTop: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          <strong style={{ color: 'var(--text-primary)' }}>Action so far:</strong>{' '}
          {scenario.action_history.map((a, i) => (
            <span key={i}>
              {a.player} {a.action}{a.amount ? ` ${a.amount}` : ''}
              {i < scenario.action_history.length - 1 ? ' → ' : ''}
            </span>
          ))}
        </div>
      )}

      {/* Learning objective */}
      {scenario.learning_objective && (
        <div style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--gold)', opacity: 0.85 }}>
          🎯 {scenario.learning_objective}
        </div>
      )}
    </div>
  )
}
