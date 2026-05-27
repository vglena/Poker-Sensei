/**
 * types/index.ts
 * --------------
 * Re-exports shared types and adds UI-specific constants.
 * Mirrors app/shared/types.ts — keep both files in sync.
 */

// ---------------------------------------------------------------------------
// Core domain types
// ---------------------------------------------------------------------------

export type Street = 'preflop' | 'flop' | 'turn' | 'river'
export type PlayerActionType = 'fold' | 'check' | 'call' | 'bet' | 'raise'
export type Rating = 'good' | 'ok' | 'mistake' | 'blunder'
export type Difficulty = 'beginner' | 'intermediate' | 'advanced' | 'pro'
export type OutcomeClassification =
  | 'strategy_win'
  | 'strategy_loss'
  | 'luck_win'
  | 'luck_loss'
  | 'mixed'

export type AppPhase = 'idle' | 'playing' | 'feedback' | 'reviewing'

// ---------------------------------------------------------------------------
// Card
// ---------------------------------------------------------------------------

export type CardCode = string  // e.g. 'Ah', 'Kd', 'Tc'

// ---------------------------------------------------------------------------
// Game objects
// ---------------------------------------------------------------------------

export interface PlayerAction {
  player: string
  action: PlayerActionType
  amount: number | null
}

export interface BetSizing {
  min_bet: number
  max_bet: number
  common: number[]
}

export interface PokerScenario {
  scenario_id: string
  street: Street
  hole_cards: CardCode[]
  community_cards: CardCode[]
  pot_size: number
  hero_stack: number
  villain_stack: number
  hero_position: string
  villain_position: string
  action_history: PlayerAction[]
  available_actions: PlayerActionType[]
  bet_sizing: BetSizing
  difficulty: Difficulty
  tags: string[]
  learning_objective: string | null
}

// ---------------------------------------------------------------------------
// Decision analysis
// ---------------------------------------------------------------------------

export interface DecisionAnalysis {
  decision_id: string
  scenario_id: string
  user_action: PlayerActionType
  bet_amount: number | null
  rating: Rating
  rating_score: number
  hand_strength: string | null
  position_note: string | null
  explanation: string
  best_alternative: string
  best_action_label: string
  recommended_sizing: string | null
  risk_analysis: string
  luck_vs_strategy: string
  key_concept: string | null
  mistake_category: string | null
  recommended_drill: string
  learning_objective: string | null
}

// ---------------------------------------------------------------------------
// Hand review
// ---------------------------------------------------------------------------

export interface StreetGrade {
  rating: Rating
  score: number
  note: string
}

export interface KeyDecision {
  street: Street
  hero_action: string
  optimal_action: string
  sizing_recommendation: string | null
  explanation: string
}

export interface HandReview {
  hand_id: string
  session_id: string
  outcome: string
  outcome_classification: OutcomeClassification
  key_decision: KeyDecision
  street_grades: Record<string, StreetGrade>
  luck_vs_strategy: string
  primary_lesson: string
  recommended_drill: string
  overall_grade: Rating
  overall_score: number
}

// ---------------------------------------------------------------------------
// User profile
// ---------------------------------------------------------------------------

export interface UserProfile {
  user_id: string
  display_name: string
  level: Difficulty
  goal: string
  preferred_format: string
  feedback_tone: string
  total_sessions: number
  total_decisions: number
  average_score: number
  accuracy_pct: number
}

// ---------------------------------------------------------------------------
// Session report (end-of-session summary)
// ---------------------------------------------------------------------------

export interface DecisionSummary {
  action: string
  street: string
  score: number
}

export interface SessionReport {
  session_id: string
  total_decisions: number
  average_score: number
  accuracy_pct: number
  strongest_decision: DecisionSummary | null
  weakest_decision: DecisionSummary | null
  recurring_mistake: string | null
  recommended_drill: string | null
  progress_note: string
  streets_played: Record<string, number>
}

// ---------------------------------------------------------------------------
// Fixture metadata (for the fixture selector UI)
// ---------------------------------------------------------------------------

export interface FixtureItem {
  name: string
  label: string
  description: string
  street: Street
  difficulty: Difficulty
}

// ---------------------------------------------------------------------------
// Hand history entry (local state)
// ---------------------------------------------------------------------------

export interface HandHistoryEntry {
  hand_id: string
  scenario_id: string
  street: Street
  hole_cards: CardCode[]
  community_cards: CardCode[]
  user_action: PlayerActionType
  best_action_note: string
  rating: Rating
  rating_score: number
  timestamp: string
}

// ---------------------------------------------------------------------------
// UI constants
// ---------------------------------------------------------------------------

export const RATING_COLORS: Record<Rating, string> = {
  good:    '#22c55e',
  ok:      '#eab308',
  mistake: '#f97316',
  blunder: '#ef4444',
}

export const RATING_LABELS: Record<Rating, string> = {
  good:    'Good Play',
  ok:      'Acceptable',
  mistake: 'Needs Review',
  blunder: 'Incorrect',
}

/** Score-based label shown in the verdict row (overrides rating-based label). */
export function scoreLabel(score: number): string {
  if (score >= 9) return 'Excellent'
  if (score >= 7) return 'Good'
  if (score >= 5) return 'Needs Review'
  return 'Incorrect'
}

export const SUIT_SYMBOLS: Record<string, string> = {
  c: '♣',
  d: '♦',
  h: '♥',
  s: '♠',
}

export const SUIT_COLORS: Record<string, string> = {
  c: '#1a1a1a',
  d: '#cc0000',
  h: '#cc0000',
  s: '#1a1a1a',
}

export const STREET_LABELS: Record<Street, string> = {
  preflop: 'Preflop',
  flop:    'Flop',
  turn:    'Turn',
  river:   'River',
}

export const ACTION_LABELS: Record<PlayerActionType, string> = {
  fold:  'Fold',
  check: 'Check',
  call:  'Call',
  bet:   'Bet',
  raise: 'Raise',
}
