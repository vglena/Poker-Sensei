/**
 * ActionButtons.tsx
 * -----------------
 * Renders fold/check/call/bet/raise buttons based on available actions.
 * Includes a bet slider for bet/raise actions.
 */

import React, { useState } from 'react'
import type { PokerScenario, PlayerActionType } from '../types'
import { ACTION_LABELS } from '../types'

interface ActionButtonsProps {
  scenario: PokerScenario
  onAction: (action: PlayerActionType, betAmount?: number) => void
  disabled?: boolean
}

const ACTION_CLASSES: Record<PlayerActionType, string> = {
  fold:  'btn btn-fold',
  check: 'btn btn-check',
  call:  'btn btn-call',
  bet:   'btn btn-bet',
  raise: 'btn btn-raise',
}

export default function ActionButtons({ scenario, onAction, disabled = false }: ActionButtonsProps) {
  const { available_actions, bet_sizing, pot_size } = scenario
  const showSlider = available_actions.includes('bet') || available_actions.includes('raise')

  const defaultBet = bet_sizing.common.length > 0
    ? bet_sizing.common[Math.floor(bet_sizing.common.length / 2)]
    : Math.round(pot_size * 0.5)

  const [betAmount, setBetAmount] = useState<number>(defaultBet)

  function handleAction(action: PlayerActionType) {
    if (action === 'bet' || action === 'raise') {
      onAction(action, betAmount)
    } else {
      onAction(action)
    }
  }

  return (
    <div className="panel">
      <div className="panel-title">What should Hero do?</div>

      <div className="action-buttons">
        {available_actions.map((action) => (
          <button
            key={action}
            className={ACTION_CLASSES[action] ?? 'btn btn-primary'}
            disabled={disabled}
            onClick={() => handleAction(action)}
          >
            {ACTION_LABELS[action]}
            {action === 'call' && scenario.action_history.length > 0 ? (
              <>
                {' '}
                {/* Show call amount if it appears in action history */}
                {(() => {
                  const lastBet = [...scenario.action_history]
                    .reverse()
                    .find(a => a.action === 'bet' || a.action === 'raise')
                  return lastBet?.amount ? ` (${lastBet.amount})` : ''
                })()}
              </>
            ) : null}
          </button>
        ))}

        {/* Bet / raise slider */}
        {showSlider && (
          <div className="bet-input-group">
            <label>Bet size</label>
            <input
              type="range"
              min={bet_sizing.min_bet}
              max={bet_sizing.max_bet}
              step={Math.max(1, Math.round(bet_sizing.min_bet / 2))}
              value={betAmount}
              onChange={(e) => setBetAmount(Number(e.target.value))}
              disabled={disabled}
            />
            <span className="bet-value">{betAmount} chips</span>
            {/* Quick size buttons */}
            <div style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
              {bet_sizing.common.map((size) => (
                <button
                  key={size}
                  className="btn btn-secondary"
                  style={{ fontSize: '0.7rem', padding: '2px 6px' }}
                  onClick={() => setBetAmount(size)}
                  disabled={disabled}
                >
                  {size}
                </button>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
