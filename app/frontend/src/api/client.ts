/**
 * api/client.ts
 * -------------
 * Fetch-based API client for the poker training backend.
 * All endpoints proxy through Vite's /api prefix to the Vite proxy target.
 *
 * Canonical endpoint paths:
 *   GET  /api/scenario/new          — new training scenario
 *   GET  /api/scenario/fixture/:n   — stable named fixture
 *   POST /api/decision/analyze      — submit decision + get analysis
 *   POST /api/hand/review           — full hand review
 *   POST /api/session/save          — save session summary
 *   GET  /api/session/:id/summary   — rich session report
 *
 * NOTE: No authentication in v1 — this is a local training tool.
 */

import type { PokerScenario, DecisionAnalysis, HandReview, SessionReport, FixtureItem } from '../types'

const RAW_BASE = import.meta.env.VITE_API_BASE_URL?.trim()
const BASE = RAW_BASE ? RAW_BASE.replace(/\/$/, '') : '/api'

// ---------------------------------------------------------------------------
// Generic fetch helper
// ---------------------------------------------------------------------------

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${BASE}${path}`, {
      headers: { 'Content-Type': 'application/json' },
      ...options,
    })
  } catch {
    throw new Error('API_UNREACHABLE')
  }

  if (!response.ok) {
    const body = await response.text()
    throw new Error(`API error ${response.status}: ${body}`)
  }

  return response.json() as Promise<T>
}

// ---------------------------------------------------------------------------
// Scenario endpoints
// ---------------------------------------------------------------------------

export interface ScenarioRequestParams {
  difficulty?: string
  street?: string
  focus_area?: string
  seed?: number
}

/** Fetch a new generated training scenario (canonical). */
export async function fetchScenario(params?: ScenarioRequestParams): Promise<PokerScenario> {
  const qs = params
    ? '?' + new URLSearchParams(
        Object.fromEntries(
          Object.entries(params)
            .filter(([, v]) => v !== undefined)
            .map(([k, v]) => [k, String(v)])
        )
      ).toString()
    : ''
  return request<PokerScenario>(`/scenario/new${qs}`)
}

/** Fetch the list of all named fixtures with metadata for display in the UI. */
export async function fetchFixturesList(): Promise<FixtureItem[]> {
  return request<FixtureItem[]>('/scenario/fixtures')
}

/** Fetch a named, stable fixture scenario (e.g. 'flop_cbet', 'river_bluff_catch'). */
export async function fetchFixtureScenario(name: string): Promise<PokerScenario> {
  return request<PokerScenario>(`/scenario/fixture/${encodeURIComponent(name)}`)
}

export async function fetchExampleScenario(): Promise<PokerScenario> {
  return request<PokerScenario>('/scenario/example')
}

// ---------------------------------------------------------------------------
// Decision endpoints
// ---------------------------------------------------------------------------

export interface DecisionPayload {
  session_id: string
  scenario_id: string
  user_action: string
  bet_amount?: number | null
  user_level: string
  scenario_data: PokerScenario
}

/** Submit a decision for analysis and logging (canonical). */
export async function submitDecision(payload: DecisionPayload): Promise<DecisionAnalysis> {
  return request<DecisionAnalysis>('/decision/analyze', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

/** Analyze a decision without logging (stateless). */
export async function analyzeDecision(payload: DecisionPayload): Promise<DecisionAnalysis> {
  return request<DecisionAnalysis>('/analyze', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

// ---------------------------------------------------------------------------
// Hand review endpoint
// ---------------------------------------------------------------------------

export interface ShowdownResult {
  winner: string
  hero_cards_revealed: string[]
  villain_cards_revealed: string[]
  winning_hand_description: string
  pot_awarded: number
}

export interface HandReviewPayload {
  session_id: string
  hand_id: string
  decisions: DecisionPayload[]
  showdown_result?: ShowdownResult
}

/** Request a full hand review (canonical). */
export async function reviewHand(payload: HandReviewPayload): Promise<HandReview> {
  return request<HandReview>('/hand/review', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

// ---------------------------------------------------------------------------
// Session endpoints
// ---------------------------------------------------------------------------

export interface SessionSavePayload {
  session_id: string
  user_id: string
  total_decisions: number
  hands_played: number
  average_score: number
  accuracy_pct: number
  primary_lesson?: string
  notes?: string
}

/** Save a session summary (canonical). */
export async function saveSession(payload: SessionSavePayload): Promise<{ saved: boolean; message: string }> {
  return request<{ saved: boolean; message: string }>('/session/save', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

/** Get the rich session report including strongest/weakest decisions and recurring mistakes. */
export async function fetchSessionReport(sessionId: string): Promise<SessionReport> {
  return request<SessionReport>(`/session/${encodeURIComponent(sessionId)}/summary`)
}

// ---------------------------------------------------------------------------
// Health check
// ---------------------------------------------------------------------------

export async function healthCheck(): Promise<{ status: string; version: string }> {
  return request<{ status: string; version: string }>('/health')
}

export async function fetchSessionSummary(sessionId: string): Promise<unknown> {
  return request<unknown>(`/session/${sessionId}/summary`)
}
