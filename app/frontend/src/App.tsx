/**
 * App.tsx
 * -------
 * Main application component.
 * Manages the top-level state machine: idle -> playing -> feedback -> (next hand)
 *
 * State:
 * - phase:           AppPhase -- controls which UI is shown
 * - currentScenario: PokerScenario | null -- the active hand
 * - currentAnalysis: DecisionAnalysis | null -- feedback after a decision
 * - handHistory:     HandHistoryEntry[] -- all decisions this session
 * - sessionId:       string -- UUID for this session
 * - userProfile:     UserProfile -- local (backend sync in v2)
 * - difficulty:      Difficulty -- scenario generation difficulty
 * - error:           string | null -- display backend errors
 */

import React, { useState, useCallback } from 'react'
import { v4 as uuidv4 } from 'uuid'

import type {
  AppPhase,
  PokerScenario,
  DecisionAnalysis,
  HandHistoryEntry,
  UserProfile,
  PlayerActionType,
  Difficulty,
} from './types'

import { fetchScenario, fetchFixtureScenario, submitDecision } from './api/client'
import PokerTable from './components/PokerTable'
import ActionButtons from './components/ActionButtons'
import FeedbackPanel from './components/FeedbackPanel'
import HandHistory from './components/HandHistory'
import UserProgress from './components/UserProgress'
import FixtureSelector from './components/FixtureSelector'
import SessionReportPanel from './components/SessionReportPanel'

// ---------------------------------------------------------------------------
// Default user profile (in-memory for v1)
// ---------------------------------------------------------------------------

const DEFAULT_PROFILE: UserProfile = {
  user_id: 'local_user',
  display_name: 'Player',
  level: 'beginner',
  goal: 'Improve fundamentals',
  preferred_format: 'cash',
  feedback_tone: 'direct',
  total_sessions: 0,
  total_decisions: 0,
  average_score: 0,
  accuracy_pct: 0,
}

// ---------------------------------------------------------------------------
// Helper: generate session id once per browser session
// ---------------------------------------------------------------------------

function getOrCreateSessionId(): string {
  const key = 'poker_session_id'
  let sid = sessionStorage.getItem(key)
  if (!sid) {
    sid = uuidv4()
    sessionStorage.setItem(key, sid)
  }
  return sid
}

// ---------------------------------------------------------------------------
// App
// ---------------------------------------------------------------------------

export default function App() {
  const [phase, setPhase] = useState<AppPhase>('idle')
  const [currentScenario, setCurrentScenario] = useState<PokerScenario | null>(null)
  const [currentAnalysis, setCurrentAnalysis] = useState<DecisionAnalysis | null>(null)
  const [handHistory, setHandHistory] = useState<HandHistoryEntry[]>([])
  const [userProfile, setUserProfile] = useState<UserProfile>(DEFAULT_PROFILE)
  const [sessionId] = useState<string>(getOrCreateSessionId)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)
  // difficulty controls scenario complexity; userProfile.level controls coaching depth
  const [difficulty, setDifficulty] = useState<Difficulty>('beginner')

  const levels: Difficulty[] = ['beginner', 'intermediate', 'advanced', 'pro']

  // ---- Session stats ----
  const sessionDecisions = handHistory.length
  const sessionAvgScore = sessionDecisions > 0
    ? handHistory.reduce((sum, h) => sum + h.rating_score, 0) / sessionDecisions
    : 0

  // ---- Apply a loaded scenario ----
  function applyScenario(scenario: PokerScenario) {
    setCurrentScenario(scenario)
    setCurrentAnalysis(null)
    setPhase('playing')
  }

  // ---- Load a random generated hand ----
  const loadNewHand = useCallback(async () => {
    setError(null)
    setLoading(true)
    setCurrentAnalysis(null)
    setPhase('playing')
    try {
      const scenario = await fetchScenario({ difficulty })
      setCurrentScenario(scenario)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scenario.')
      setPhase('idle')
    } finally {
      setLoading(false)
    }
  }, [difficulty])

  // ---- Load a named fixture scenario ----
  const loadFixture = useCallback(async (name: string) => {
    setError(null)
    setLoading(true)
    try {
      const scenario = await fetchFixtureScenario(name)
      applyScenario(scenario)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load fixture.')
      setPhase('idle')
    } finally {
      setLoading(false)
    }
  }, [])

  // ---- Handle a player decision ----
  const handleAction = useCallback(async (action: PlayerActionType, betAmount?: number) => {
    if (!currentScenario) return
    setError(null)
    setLoading(true)
    try {
      const analysis = await submitDecision({
        session_id: sessionId,
        scenario_id: currentScenario.scenario_id,
        user_action: action,
        bet_amount: betAmount ?? null,
        user_level: userProfile.level,
        scenario_data: currentScenario,
      })
      setCurrentAnalysis(analysis)
      setPhase('feedback')
      const entry: HandHistoryEntry = {
        hand_id: analysis.decision_id,
        scenario_id: currentScenario.scenario_id,
        street: currentScenario.street,
        hole_cards: currentScenario.hole_cards,
        community_cards: currentScenario.community_cards,
        user_action: action,
        rating: analysis.rating,
        rating_score: analysis.rating_score,
        timestamp: new Date().toISOString(),
      }
      setHandHistory((prev) => [...prev, entry])
      setUserProfile((prev) => ({ ...prev, total_decisions: prev.total_decisions + 1 }))
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze decision.')
    } finally {
      setLoading(false)
    }
  }, [currentScenario, sessionId, userProfile.level])

  // ---- After feedback: next hand ----
  const handleNextHand = useCallback(() => {
    loadNewHand()
  }, [loadNewHand])

  // ---- Go back to fixture selector without losing session history ----
  function handleBackToHome() {
    setCurrentScenario(null)
    setCurrentAnalysis(null)
    setPhase('idle')
  }

  // ---- Change user level (coaching depth + scenario difficulty) ----
  function handleLevelChange(newLevel: Difficulty) {
    setDifficulty(newLevel)
    setUserProfile((prev) => ({ ...prev, level: newLevel }))
  }

  // ---- Render ----
  return (
    <div className="app-container">
      {/* Header */}
      <div className="header">
        <h1>♠ Poker Training</h1>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Level:{' '}
            <select
              value={userProfile.level}
              onChange={(e) => handleLevelChange(e.target.value as Difficulty)}
              style={{
                background: 'var(--felt-dark)',
                color: 'var(--text-primary)',
                border: '1px solid var(--felt-border)',
                borderRadius: 'var(--radius-sm)',
                padding: '2px 6px',
                fontFamily: 'inherit',
                marginLeft: '4px',
              }}
            >
              {levels.map((l) => (
                <option key={l} value={l}>
                  {l.charAt(0).toUpperCase() + l.slice(1)}
                </option>
              ))}
            </select>
          </label>
        </div>
      </div>

      {/* Error banner */}
      {error && (
        <div style={{
          background: '#7f1d1d',
          color: '#fecaca',
          padding: '0.75rem 1rem',
          borderRadius: 'var(--radius-sm)',
          marginBottom: '1rem',
          fontSize: '0.9rem',
        }}>
          ⚠ {error}
        </div>
      )}

      {/* ---- IDLE PHASE ---- */}
      {phase === 'idle' && (
        <div className="welcome-screen">
          <FixtureSelector
            onSelectFixture={loadFixture}
            onRandomScenario={loadNewHand}
            loading={loading}
          />
          {handHistory.length > 0 && (
            <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>
              Session: {handHistory.length} hands · avg {sessionAvgScore.toFixed(1)}/10
            </p>
          )}
        </div>
      )}

      {/* ---- PLAYING / FEEDBACK PHASES ---- */}
      {(phase === 'playing' || phase === 'feedback') && (
        <div className="main-grid">
          <div style={{ gridColumn: '1 / -1', marginBottom: '0.5rem' }}>
            <button className="secondary-button" onClick={handleBackToHome}>
              ← Back to scenarios
            </button>
          </div>
          <div className="left-column">
            {loading && !currentScenario && (
              <div className="loading">Loading scenario…</div>
            )}
            {currentScenario && (
              <>
                <PokerTable scenario={currentScenario} />
                {phase === 'playing' && (
                  <ActionButtons
                    scenario={currentScenario}
                    onAction={handleAction}
                    disabled={loading}
                  />
                )}
                {phase === 'feedback' && loading && (
                  <div className="loading">Analyzing your decision…</div>
                )}
                {phase === 'feedback' && currentAnalysis && (
                  <FeedbackPanel
                    analysis={currentAnalysis}
                    onNextHand={handleNextHand}
                  />
                )}
              </>
            )}
          </div>
          <div className="right-column">
            <UserProgress
              profile={userProfile}
              sessionDecisions={sessionDecisions}
              sessionAvgScore={sessionAvgScore}
            />
            <SessionReportPanel
              sessionId={sessionId}
              decisionCount={sessionDecisions}
            />
            <HandHistory history={handHistory} />
          </div>
        </div>
      )}
    </div>
  )
}
