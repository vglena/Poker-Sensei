/**
 * FixtureSelector.tsx
 * -------------------
 * Displays training drills filtered by the current user level.
 *
 * White Belt  (5 lessons — 2 live, 3 coming soon)
 * Green Belt  (7 lessons — 3 live, 4 coming soon)
 * Black Belt  (7 advanced lessons — all coming soon  +  5 foundation review)
 *
 * Beginner path also shows a locked preview of 3 Green Belt lessons.
 *
 * Architecture: pure display component. No poker logic here.
 */

import React, { useEffect, useState } from 'react'
import type { FixtureItem, Difficulty, HandHistoryEntry } from '../types'
import { fetchFixturesList } from '../api/client'

interface FixtureSelectorProps {
  onSelectFixture: (name: string) => void
  onRandomScenario: () => void
  loading: boolean
  level: Difficulty
  handHistory: HandHistoryEntry[]
}

// ---------------------------------------------------------------------------
// Static data
// ---------------------------------------------------------------------------

const STREET_BADGE: Record<string, string> = {
  preflop: '#4c1d95',
  flop:    '#14532d',
  turn:    '#78350f',
  river:   '#7f1d1d',
}

// Maps fixture scenario_id → lesson name so progress can be tracked via handHistory
const SCENARIO_ID_TO_LESSON: Record<string, string> = {
  'fixture-preflop-raise-001':     'preflop_raise',
  'fixture-flop-cbet-001':         'flop_cbet',
  'fixture-turn-draw-001':         'turn_draw',
  'fixture-river-bluff-catch-001': 'river_bluff_catch',
  'fixture-value-bet-sizing-001':  'value_bet_sizing',
}

interface LessonDef {
  name: string
  label: string
  description: string
  street: string
  focus: string
  hasFixture: boolean
}

const WHITE_BELT_LESSONS: LessonDef[] = [
  {
    name: 'preflop_raise', label: 'Preflop Raise',
    description: 'Hero holds A♠K♠ on the button. CO opens. 3-bet, call, or fold?',
    street: 'preflop', focus: 'Aggression', hasFixture: true,
  },
  {
    name: 'flop_cbet', label: 'Flop C-Bet',
    description: 'Top pair on a dry K-8-3 board in position. Build the pot or trap?',
    street: 'flop', focus: 'Continuation betting', hasFixture: true,
  },
  {
    name: 'value_bet_basics', label: 'Value Bet Basics',
    description: 'Strong hand on a safe board. Learn to extract maximum value.',
    street: 'river', focus: 'Value sizing', hasFixture: false,
  },
  {
    name: 'position_basics', label: 'Position Basics',
    description: 'Preflop spot illustrating the power of acting last.',
    street: 'preflop', focus: 'Position', hasFixture: false,
  },
  {
    name: 'fold_top_pair', label: 'When to Fold Top Pair',
    description: 'You have top pair but face strong resistance. Recognise when to let go.',
    street: 'river', focus: 'Disciplined folds', hasFixture: false,
  },
]

const GREEN_BELT_LESSONS: LessonDef[] = [
  {
    name: 'turn_draw', label: 'Turn Draw',
    description: 'Open-ended straight draw on the turn. Is calling correct based on pot odds?',
    street: 'turn', focus: 'Pot odds & draws', hasFixture: true,
  },
  {
    name: 'river_bluff_catch', label: 'River Bluff Catch',
    description: 'Marginal hand facing a river overbet. Read the line and decide.',
    street: 'river', focus: 'Bluff catching', hasFixture: true,
  },
  {
    name: 'value_bet_sizing', label: 'Value Bet Sizing',
    description: 'Strong hand, multiple sizing options. Choose the bet that maximises EV.',
    street: 'river', focus: 'Value betting', hasFixture: true,
  },
  {
    name: 'pot_odds_call', label: 'Pot Odds Call',
    description: 'Drawing hand on the flop. Calculate the break-even call percentage.',
    street: 'flop', focus: 'Pot odds', hasFixture: false,
  },
  {
    name: 'thin_value_bet', label: 'Thin Value Bet',
    description: 'Marginal made hand. Bet thinly for value or check back to control the pot?',
    street: 'river', focus: 'Thin value', hasFixture: false,
  },
  {
    name: 'delayed_cbet', label: 'Delayed C-Bet',
    description: 'Checked back the flop in position. Which turn cards justify a delayed continuation?',
    street: 'turn', focus: 'Delayed aggression', hasFixture: false,
  },
  {
    name: 'check_raise_spot', label: 'Check-Raise Spot',
    description: 'Strong hand out of position. Build the pot with a check-raise or lead out?',
    street: 'flop', focus: 'Check-raising', hasFixture: false,
  },
]

const BLACK_BELT_LESSONS: LessonDef[] = [
  {
    name: 'exploitative_river_call', label: 'Exploitative River Call',
    description: 'Exploit a known over-bluffer. Adjust your calling threshold against a specific villain tendency.',
    street: 'river', focus: 'Exploitative play', hasFixture: false,
  },
  {
    name: 'multi_street_bluff', label: 'Multi-Street Bluff Line',
    description: 'Construct a credible 3-street bluff that tells a consistent story.',
    street: 'river', focus: 'Bluff construction', hasFixture: false,
  },
  {
    name: 'range_advantage_cbet', label: 'Range Advantage C-Bet',
    description: 'Board texture heavily favours the preflop aggressor. Bet range vs. check range.',
    street: 'flop', focus: 'Range advantage', hasFixture: false,
  },
  {
    name: 'polarized_river_bet', label: 'Polarized River Bet',
    description: 'River decision with a polarized range. Size to maximise EV across your value bets and bluffs.',
    street: 'river', focus: 'Polarization', hasFixture: false,
  },
  {
    name: 'blocker_bluff', label: 'Blocker-Based Bluff',
    description: 'Select the right bluffs using blockers. Which hands block the nuts most effectively?',
    street: 'river', focus: 'Blockers', hasFixture: false,
  },
  {
    name: 'overbet_turn', label: 'Overbet Turn Strategy',
    description: 'Overbetting the turn to charge draws and deny equity. When and why to size up.',
    street: 'turn', focus: 'Overbets', hasFixture: false,
  },
  {
    name: 'tournament_pressure', label: 'Tournament Pressure',
    description: 'ICM pressure near the money. Adjust your ranges when stack-preservation matters.',
    street: 'preflop', focus: 'ICM & tournament play', hasFixture: false,
  },
]

// Foundation lessons shown in Black Belt view (live fixtures from earlier belts)
const FOUNDATION_LESSONS: LessonDef[] = [
  WHITE_BELT_LESSONS[0], // preflop_raise
  WHITE_BELT_LESSONS[1], // flop_cbet
  GREEN_BELT_LESSONS[0], // turn_draw
  GREEN_BELT_LESSONS[1], // river_bluff_catch
  GREEN_BELT_LESSONS[2], // value_bet_sizing
]

// A few Green Belt lessons shown as locked preview on the beginner path
const LOCKED_PREVIEW: LessonDef[] = GREEN_BELT_LESSONS.slice(0, 3)

interface PathConfig {
  beltLabel: string
  beltCss: string
  title: string
  tagline: string
  description: string
  lessons: LessonDef[]
}

const PATH_CONFIG: Record<string, PathConfig> = {
  beginner: {
    beltLabel: 'White Belt', beltCss: 'belt-badge belt-white',
    title: 'White Belt Path', tagline: 'Core fundamentals',
    description: 'Learn clean fundamentals: position, aggression, value, and disciplined folds.',
    lessons: WHITE_BELT_LESSONS,
  },
  intermediate: {
    beltLabel: 'Green Belt', beltCss: 'belt-badge belt-green',
    title: 'Green Belt Path', tagline: 'Odds, ranges, and sizing',
    description: 'Handle odds, ranges, sizing, and pressure across later streets.',
    lessons: GREEN_BELT_LESSONS,
  },
  advanced: {
    beltLabel: 'Black Belt', beltCss: 'belt-badge belt-black',
    title: 'Black Belt Path', tagline: 'Deep strategy and exploitative play',
    description: 'Study exploitative adjustments, multi-street plans, and advanced range logic.',
    lessons: BLACK_BELT_LESSONS,
  },
  pro: {
    beltLabel: 'Black Belt', beltCss: 'belt-badge belt-black',
    title: 'Black Belt Path', tagline: 'Full line analysis',
    description: 'Study exploitative adjustments, multi-street plans, and advanced range logic.',
    lessons: BLACK_BELT_LESSONS,
  },
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function FixtureSelector({
  onSelectFixture, onRandomScenario, loading, level, handHistory,
}: FixtureSelectorProps) {
  const [fixtures, setFixtures] = useState<FixtureItem[]>([])
  const [fetchError, setFetchError] = useState<string | null>(null)

  useEffect(() => {
    fetchFixturesList()
      .then(setFixtures)
      .catch(() => setFetchError('Could not load drills.'))
  }, [])

  const path      = PATH_CONFIG[level] ?? PATH_CONFIG.intermediate
  const isBeginner = level === 'beginner'
  const isAdvanced = level === 'advanced' || level === 'pro'

  // Progress: unique lessons practiced this session for the active path
  const practicedSet = new Set(
    handHistory.map(h => SCENARIO_ID_TO_LESSON[h.scenario_id]).filter(Boolean)
  )

  // For black belt we track foundation progress separately
  const foundationPracticed = FOUNDATION_LESSONS.filter(l => practicedSet.has(l.name)).length

  const pathLessons     = path.lessons
  const pathPracticed   = pathLessons.filter(l => practicedSet.has(l.name)).length
  const pathTotal       = pathLessons.length

  // For non-advanced progress label
  const progressLabel = isAdvanced
    ? `${foundationPracticed}/${FOUNDATION_LESSONS.length} foundation ${foundationPracticed === 1 ? 'lesson' : 'lessons'} reviewed`
    : `${pathPracticed}/${pathTotal} ${pathPracticed === 1 ? 'lesson' : 'lessons'} practiced`

  const progressPracticed = isAdvanced ? foundationPracticed : pathPracticed
  const progressTotal     = isAdvanced ? FOUNDATION_LESSONS.length : pathTotal
  const progressPercent   = progressTotal > 0 ? (progressPracticed / progressTotal) * 100 : 0

  // First live fixture in the current path (for the primary Start button)
  const liveLessons = isAdvanced ? FOUNDATION_LESSONS : pathLessons.filter(l => l.hasFixture)
  const firstLiveLesson = isAdvanced ? FOUNDATION_LESSONS[0] : pathLessons.find(l => l.hasFixture)
  // First unpracticed live lesson → drives "Recommended" card and today's focus
  const recommendedLesson = liveLessons.find(l => !practicedSet.has(l.name)) ?? null
  const todayFocus = recommendedLesson?.focus ?? (liveLessons[0]?.focus ?? null)

  return (
    <div className="fixture-selector">

      {/* ── Hero section: title, continue note, CTA buttons ── */}
      <div className="fs-hero">
        <h2 className="fs-title">
          Enter the dojo.<br />
          <span className="fixture-selector-tagline">Study one decision at a time.</span>
        </h2>

        {fetchError && (
          <p className="fixture-fetch-warning">
            Sensei note: the dojo could not load all drills. You can still train with available lessons.
          </p>
        )}

        {progressPracticed > 0 && (
          <p className="continue-note">
            You have practiced {progressPracticed} {progressPracticed === 1 ? 'lesson' : 'lessons'}.{' '}
            Continue your {path.beltLabel} path.
          </p>
        )}

        <div className="start-buttons">
          {firstLiveLesson && (
            <button
              className="btn btn-primary fixture-start-btn"
              onClick={() => onSelectFixture(firstLiveLesson.name)}
              disabled={loading}
            >
              ▶ Start {path.beltLabel} Practice
            </button>
          )}
          <button
            className="btn btn-secondary fixture-random-btn"
            onClick={onRandomScenario}
            disabled={loading}
          >
            ♠ Random Lesson
          </button>
        </div>
      </div>

      {/* ── Path panel with enhanced progress ── */}
      <div className="path-panel">
        <div className="path-panel-left">
          <span className="path-panel-label">Current path</span>
          <div className="path-panel-title">{path.title}</div>
          <div className="path-panel-description">{path.description}</div>
          <div className="path-progress-row">
            <span>{path.beltLabel} progress</span>
            <strong>{progressPracticed} / {progressTotal}</strong>
          </div>
          <div className="progress-bar" role="progressbar" aria-valuenow={progressPercent} aria-valuemin={0} aria-valuemax={100}>
            <div className="progress-fill" style={{ width: `${progressPercent}%` }} />
          </div>
        </div>
        <span className={path.beltCss} style={{ alignSelf: 'flex-start', marginTop: '0.15rem' }}>
          {path.beltLabel}
        </span>
      </div>

      {/* ── Today's practice ── */}
      <p className="today-practice-label">
        <span className="jp">今日の稽古</span>
        <span className="en">Today's practice</span>
      </p>
      {todayFocus && (
        <p className="today-focus">Today's focus: <strong>{todayFocus}</strong></p>
      )}
      <ol className="how-it-works" aria-label="Training rhythm">
        <li><span className="hiw-step">1</span> Choose a spot</li>
        <li><span className="hiw-step">2</span> Make your decision</li>
        <li><span className="hiw-step">3</span> Receive guidance</li>
        <li><span className="hiw-step">4</span> Refine your discipline</li>
      </ol>

      {/* ── Recommended next lesson ── */}
      {recommendedLesson && recommendedLesson.hasFixture && (
        <div className="recommended-card">
          <p className="recommended-card-eyebrow">Recommended next lesson</p>
          <div className="recommended-card-body">
            <div className="recommended-card-info">
              <div className="recommended-card-title">{recommendedLesson.label}</div>
              <div className="recommended-card-desc">{recommendedLesson.description}</div>
              <span className="fixture-item-focus">Focus: {recommendedLesson.focus}</span>
            </div>
            <button
              className="btn btn-primary recommended-card-btn"
              onClick={() => onSelectFixture(recommendedLesson.name)}
              disabled={loading}
            >
              Start lesson →
            </button>
          </div>
        </div>
      )}

      {/* ── Black Belt: Foundation Review + Challenges ── */}
      {isAdvanced && (
        <>
          <div className="fixture-section-label" style={{ marginTop: '1.5rem' }}>Foundation Review</div>
          <p className="fixture-section-hint">Core spots studied with advanced-level guidance and deeper strategic reasoning.</p>
          <div className="fixture-list">
            {FOUNDATION_LESSONS.map((lesson) => (
              <button
                key={lesson.name}
                className="fixture-item fixture-item--foundation"
                onClick={() => onSelectFixture(lesson.name)}
                disabled={loading}
              >
                <div className="fixture-item-foundation-tag">Foundation lesson — advanced guidance enabled</div>
                <div className="fixture-item-top">
                  <span className="fixture-item-label">{lesson.label}</span>
                  <span className="fixture-item-street" style={{ background: STREET_BADGE[lesson.street] ?? '#1a3a1a' }}>
                    {lesson.street}
                  </span>
                  <span className="belt-badge belt-foundation">Foundation</span>
                </div>
                <div className="fixture-item-desc">{lesson.description}</div>
                <div className="fixture-item-footer">
                  <span className="fixture-item-focus">Focus: {lesson.focus}</span>
                  <span className="fixture-item-cta">Begin lesson →</span>
                </div>
              </button>
            ))}
          </div>

          <div className="fixture-section-label" style={{ marginTop: '1.75rem' }}>Black Belt Challenges</div>
          <p className="fixture-section-hint">Advanced scenarios in development. Check back soon.</p>
          <div className="fixture-list">
            {BLACK_BELT_LESSONS.map((lesson) => (
              <div key={lesson.name} className="fixture-item fixture-item--coming-soon" aria-disabled="true">
                <div className="fixture-item-top">
                  <span className="fixture-item-label">{lesson.label}</span>
                  <span className="fixture-item-street" style={{ background: STREET_BADGE[lesson.street] ?? '#1a3a1a' }}>
                    {lesson.street}
                  </span>
                  <span className="coming-soon-badge">Coming soon</span>
                </div>
                <div className="fixture-item-desc">{lesson.description}</div>
                <div className="fixture-item-footer">
                  <span className="fixture-item-focus">Focus: {lesson.focus}</span>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* ── White Belt / Green Belt: own catalogue ── */}
      {!isAdvanced && (
        <>
          <div className="fixture-section-label" style={{ marginTop: '1.5rem' }}>Dojo Drills</div>
          <p className="fixture-section-hint">Choose a lesson to practice a specific situation.</p>
          <div className="fixture-list">
            {pathLessons.map((lesson) =>
              lesson.hasFixture ? (
                <button
                  key={lesson.name}
                  className="fixture-item"
                  onClick={() => onSelectFixture(lesson.name)}
                  disabled={loading}
                >
                  <div className="fixture-item-top">
                    <span className="fixture-item-label">{lesson.label}</span>
                    <span className="fixture-item-street" style={{ background: STREET_BADGE[lesson.street] ?? '#1a3a1a' }}>
                      {lesson.street}
                    </span>
                    <span className={`belt-badge ${isBeginner ? 'belt-white' : 'belt-green'}`}>
                      {isBeginner ? 'White Belt' : 'Green Belt'}
                    </span>
                  </div>
                  <div className="fixture-item-desc">{lesson.description}</div>
                  <div className="fixture-item-footer">
                    <span className="fixture-item-focus">Focus: {lesson.focus}</span>
                    <span className="fixture-item-cta">Begin lesson →</span>
                  </div>
                </button>
              ) : (
                <div key={lesson.name} className="fixture-item fixture-item--coming-soon" aria-disabled="true">
                  <div className="fixture-item-top">
                    <span className="fixture-item-label">{lesson.label}</span>
                    <span className="fixture-item-street" style={{ background: STREET_BADGE[lesson.street] ?? '#1a3a1a' }}>
                      {lesson.street}
                    </span>
                    <span className="coming-soon-badge">Coming soon</span>
                  </div>
                  <div className="fixture-item-desc">{lesson.description}</div>
                  <div className="fixture-item-footer">
                    <span className="fixture-item-focus">Focus: {lesson.focus}</span>
                  </div>
                </div>
              )
            )}
          </div>
        </>
      )}

      {/* ── Locked preview (Beginner only: shows 3 Green Belt lessons) ── */}
      {isBeginner && (
        <div className="locked-section">
          <div className="locked-section-header">
            <span className="belt-badge belt-green" style={{ opacity: 0.65 }}>Green Belt</span>
            <span className="locked-section-label">Unlocks in Green Belt</span>
          </div>
          <div className="fixture-list fixture-list--locked">
            {LOCKED_PREVIEW.map((lesson) => (
              <div key={lesson.name} className="fixture-item fixture-item--locked" aria-disabled="true">
                <div className="locked-overlay">🔒 Complete White Belt lessons to unlock</div>
                <div className="fixture-item-top">
                  <span className="fixture-item-label">{lesson.label}</span>
                  <span className="fixture-item-street" style={{ background: STREET_BADGE[lesson.street] ?? '#1a3a1a', opacity: 0.5 }}>
                    {lesson.street}
                  </span>
                  <span className="belt-badge belt-green" style={{ opacity: 0.5 }}>Green Belt</span>
                </div>
                <div className="fixture-item-desc">{lesson.description}</div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
