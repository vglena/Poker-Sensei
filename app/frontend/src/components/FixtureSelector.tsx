/**
 * FixtureSelector.tsx
 * -------------------
 * Displays a list of named, hand-crafted training scenarios.
 * The user can pick one to load it instead of getting a random generated scenario.
 *
 * Architecture: this component only renders data and fires callbacks.
 * All fetch logic lives in api/client.ts. No poker strategy here.
 */

import React, { useEffect, useState } from 'react'
import type { FixtureItem } from '../types'
import { fetchFixturesList } from '../api/client'

interface FixtureSelectorProps {
  onSelectFixture: (name: string) => void
  onRandomScenario: () => void
  loading: boolean
}

const STREET_BADGE: Record<string, string> = {
  preflop: '#4c1d95',
  flop:    '#14532d',
  turn:    '#78350f',
  river:   '#7f1d1d',
}

export default function FixtureSelector({ onSelectFixture, onRandomScenario, loading }: FixtureSelectorProps) {
  const [fixtures, setFixtures] = useState<FixtureItem[]>([])
  const [fetchError, setFetchError] = useState<string | null>(null)

  useEffect(() => {
    fetchFixturesList()
      .then(setFixtures)
      .catch(() => setFetchError('Could not load fixtures.'))
  }, [])

  return (
    <div className="fixture-selector">
      <div className="fixture-selector-header">
        <h2>Choose a Scenario</h2>
        <p className="fixture-selector-sub">
          Pick a specific training situation, or start with a random hand.
        </p>
      </div>

      <button
        className="btn btn-primary fixture-random-btn"
        onClick={onRandomScenario}
        disabled={loading}
      >
        ♠ Random Hand
      </button>

      <div className="fixture-divider">— or pick a drill —</div>

      {fetchError && (
        <p style={{ color: '#fecaca', fontSize: '0.85rem', textAlign: 'center' }}>{fetchError}</p>
      )}

      {fixtures.length === 0 && !fetchError && (
        <p className="empty-state">Loading drills…</p>
      )}

      <div className="fixture-list">
        {fixtures.map((f) => (
          <button
            key={f.name}
            className="fixture-item"
            onClick={() => onSelectFixture(f.name)}
            disabled={loading}
          >
            <div className="fixture-item-top">
              <span className="fixture-item-label">{f.label}</span>
              <span
                className="fixture-item-street"
                style={{ background: STREET_BADGE[f.street] ?? '#1a3a1a' }}
              >
                {f.street}
              </span>
              <span className="fixture-item-diff">{f.difficulty}</span>
            </div>
            <div className="fixture-item-desc">{f.description}</div>
          </button>
        ))}
      </div>
    </div>
  )
}
