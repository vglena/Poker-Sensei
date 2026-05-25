/**
 * types.ts
 * --------
 * TypeScript type definitions for the Poker Training Application.
 *
 * These types mirror the Pydantic schemas in app/shared/schemas.py.
 * Keep both files in sync when modifying the data model.
 */

// ---------------------------------------------------------------------------
// Enums
// ---------------------------------------------------------------------------

export type Street = "preflop" | "flop" | "turn" | "river";

export type PlayerActionType = "fold" | "check" | "call" | "bet" | "raise";

export type Rating = "good" | "ok" | "mistake" | "blunder";

export type Difficulty = "beginner" | "intermediate" | "advanced" | "pro";

export type OutcomeClassification =
  | "strategy_win"
  | "strategy_loss"
  | "luck_win"
  | "luck_loss"
  | "mixed";

// ---------------------------------------------------------------------------
// Card
// ---------------------------------------------------------------------------

/**
 * A single playing card.
 * rank: 2 3 4 5 6 7 8 9 T J Q K A
 * suit: c (clubs) | d (diamonds) | h (hearts) | s (spades)
 */
export interface Card {
  rank: string;
  suit: string;
}

/** Compact card string, e.g. "Ah" = Ace of hearts */
export type CardCode = string;

// ---------------------------------------------------------------------------
// Player action
// ---------------------------------------------------------------------------

export interface PlayerAction {
  player: string;
  action: PlayerActionType;
  amount: number | null;
}

// ---------------------------------------------------------------------------
// Bet sizing
// ---------------------------------------------------------------------------

export interface BetSizing {
  min_bet: number;
  max_bet: number;
  common: number[];
}

// ---------------------------------------------------------------------------
// Poker scenario
// ---------------------------------------------------------------------------

/**
 * A structured poker training scenario.
 * Received from the backend when a new hand starts.
 */
export interface PokerScenario {
  scenario_id: string;
  street: Street;
  hole_cards: CardCode[];         // Always 2 items
  community_cards: CardCode[];    // 0–5 items depending on street
  pot_size: number;
  hero_stack: number;
  villain_stack: number;
  hero_position: string;
  villain_position: string;
  action_history: PlayerAction[];
  available_actions: PlayerActionType[];
  bet_sizing: BetSizing;
  difficulty: Difficulty;
  tags: string[];
  // Hidden until after the user acts — may be null in the initial response
  learning_objective: string | null;
}

// ---------------------------------------------------------------------------
// Decision analysis
// ---------------------------------------------------------------------------

/**
 * Coaching analysis of a single user decision.
 * Received from the backend after the user submits their action.
 */
export interface DecisionAnalysis {
  decision_id: string;
  scenario_id: string;
  user_action: PlayerActionType;
  bet_amount: number | null;

  // Rating
  rating: Rating;
  rating_score: number;             // 1–10

  // Coaching content
  hand_strength: string | null;
  position_note: string | null;
  explanation: string;
  best_alternative: string;
  recommended_sizing: string | null;
  risk_analysis: string;
  luck_vs_strategy: string;
  key_concept: string | null;
  recommended_drill: string;

  // Revealed post-action
  learning_objective: string | null;
}

// ---------------------------------------------------------------------------
// Hand review
// ---------------------------------------------------------------------------

export interface StreetGrade {
  rating: Rating;
  score: number;
  note: string;
}

export interface KeyDecision {
  street: Street;
  hero_action: string;
  optimal_action: string;
  sizing_recommendation: string | null;
  explanation: string;
}

/**
 * Full post-hand review covering all streets.
 * Received after a complete hand is played.
 */
export interface HandReview {
  hand_id: string;
  session_id: string;
  outcome: string;                          // "win" | "loss" | "fold"
  outcome_classification: OutcomeClassification;
  key_decision: KeyDecision;
  street_grades: Record<string, StreetGrade>;
  luck_vs_strategy: string;
  primary_lesson: string;
  recommended_drill: string;
  overall_grade: Rating;
  overall_score: number;
}

// ---------------------------------------------------------------------------
// User profile
// ---------------------------------------------------------------------------

export interface UserProfile {
  user_id: string;
  display_name: string;
  level: Difficulty;
  goal: string;
  preferred_format: string;
  feedback_tone: string;

  // Session stats
  total_sessions: number;
  total_decisions: number;
  average_score: number;
  accuracy_pct: number;
}

// ---------------------------------------------------------------------------
// API request / response types
// ---------------------------------------------------------------------------

export interface ScenarioRequest {
  user_level: Difficulty;
  street_preference?: Street;
  focus_area?: string;
  seed?: number;
}

export interface DecisionRequest {
  session_id: string;
  scenario_id: string;
  user_action: PlayerActionType;
  bet_amount?: number | null;
  user_level: Difficulty;
  scenario_data?: PokerScenario;
}

export interface SessionSummaryRequest {
  session_id: string;
  user_id: string;
  total_decisions: number;
  average_score: number;
  accuracy_pct: number;
  primary_lesson?: string;
  notes?: string;
}

export interface SessionSummaryResponse {
  session_id: string;
  saved: boolean;
  message: string;
}

// ---------------------------------------------------------------------------
// UI-specific types (not in the shared schema)
// ---------------------------------------------------------------------------

/** The main app phases / screens */
export type AppPhase =
  | "idle"        // No active scenario
  | "playing"     // User is making a decision
  | "feedback"    // Showing analysis after an action
  | "reviewing";  // Showing full hand review

/** Rating color for UI display */
export const RATING_COLORS: Record<Rating, string> = {
  good:    "#22c55e",   // green
  ok:      "#eab308",   // yellow
  mistake: "#f97316",   // orange
  blunder: "#ef4444",   // red
};

/** Rating label for UI display */
export const RATING_LABELS: Record<Rating, string> = {
  good:    "Good Play",
  ok:      "Acceptable",
  mistake: "Mistake",
  blunder: "Blunder",
};

/** Suit symbols for card display */
export const SUIT_SYMBOLS: Record<string, string> = {
  c: "♣",
  d: "♦",
  h: "♥",
  s: "♠",
};

/** Suit colors for card display */
export const SUIT_COLORS: Record<string, string> = {
  c: "#1a1a1a",   // black
  d: "#cc0000",   // red
  h: "#cc0000",   // red
  s: "#1a1a1a",   // black
};
