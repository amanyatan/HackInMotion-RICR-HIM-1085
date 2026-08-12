// ===========================================================================
// COSMOS API client
//
// Thin typed wrapper around the FastAPI backend. Always sends `credentials:
// include` so the HttpOnly session cookie is attached to every request. The
// backend returns a structured envelope: `{error:{code,message}}` on failure
// and domain payloads on success.
// ===========================================================================

export type ApiErrorPayload = { code: string; message: string };

const API_BASE: string =
  process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  code: string;
  status: number;

  constructor(status: number, code: string, message: string) {
    super(message);
    this.name = "ApiError";
    this.status = status;
    this.code = code;
  }
}

type RequestOptions = {
  method?: "GET" | "POST" | "PATCH" | "PUT" | "DELETE";
  body?: unknown;
  formData?: FormData;
  headers?: Record<string, string>;
};

async function request<T>(
  path: string,
  { method = "GET", body, formData, headers }: RequestOptions = {}
): Promise<T> {
  const init: RequestInit = {
    method,
    credentials: "include",
    headers: headers ?? {},
  };

  if (formData) {
    init.body = formData; // do NOT set Content-Type for FormData
  } else if (body !== undefined) {
    init.headers = { "Content-Type": "application/json", ...init.headers };
    init.body = JSON.stringify(body);
  }

  const res = await fetch(`${API_BASE}${path}`, init);

  if (!res.ok) {
    let code = "HTTP_ERROR";
    let message = "Something went wrong. Please try again.";
    try {
      const data = await res.json();
      code = data?.error?.code ?? code;
      message = data?.error?.message ?? message;
    } catch {
      // non-JSON response — fall back to defaults
    }
    // 204 no-content responses are valid successes
    if (res.status === 204) return undefined as T;
    throw new ApiError(res.status, code, message);
  }

  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

// ---------------------------------------------------------------------------
// Auth
// ---------------------------------------------------------------------------

export type AuthUser = { id: string; email: string; name?: string | null };
export type AuthSuccess = { message: string; user: AuthUser };
export type SignupPayload = {
  name: string;
  email: string;
  password: string;
  confirmPassword: string;
};
export type LoginPayload = { email: string; password: string };

export const authApi = {
  signup: (payload: SignupPayload) =>
    request<AuthSuccess>("/api/auth/signup", { method: "POST", body: payload }),
  login: (payload: LoginPayload) =>
    request<AuthSuccess>("/api/auth/login", { method: "POST", body: payload }),
  me: () => request<AuthSuccess>("/api/auth/me"),
  logout: () => request<void>("/api/auth/logout", { method: "POST" }),
};

// ---------------------------------------------------------------------------
// Onboarding
// ---------------------------------------------------------------------------

export type OnboardingStatus = {
  current_step: number;
  done: boolean;
  data?: Record<string, unknown> | null;
};

export const onboardingApi = {
  status: () => request<OnboardingStatus>("/api/onboarding/status"),
  saveStep: (payload: { step: number } & Record<string, unknown>) =>
    request<OnboardingStatus>("/api/onboarding/step", {
      method: "POST",
      body: payload,
    }),
  complete: (payload: Record<string, unknown>) =>
    request<OnboardingStatus>("/api/onboarding/complete", {
      method: "POST",
      body: payload,
    }),
};

// ---------------------------------------------------------------------------
// Communication (companion chat)
// ---------------------------------------------------------------------------

export type ChatMessage = {
  message_id: string;
  role: "user" | "assistant";
  content: string;
  emotion: string;
  character: string;
  language: string;
};

export type ChatPayload = {
  message: string;
  character?: string;
  language?: string;
};

export const communicationApi = {
  chat: (payload: ChatPayload) =>
    request<ChatMessage>("/api/communication/chat", {
      method: "POST",
      body: payload,
    }),
  history: () =>
    request<{ messages: Array<Record<string, unknown>> }>(
      "/api/communication/history"
    ),
  clearHistory: () =>
    request<void>("/api/communication/history", { method: "DELETE" }),
  transcribe: (audio: Blob, language = "en") => {
    const fd = new FormData();
    fd.append("audio", audio, "audio.wav");
    fd.append("language", language);
    return request<{ text: string; language: string; is_mock: boolean }>(
      "/api/communication/transcribe",
      { method: "POST", formData: fd }
    );
  },
  speakUrl: (text: string, voice = "kei", language = "en") =>
    `${API_BASE}/api/communication/speak?text=${encodeURIComponent(
      text
    )}&voice=${voice}&language=${language}`,
  speakBlob: async (text: string, voice = "kei", language = "en") => {
    const res = await fetch(`${API_BASE}/api/communication/speak`, {
      method: "POST",
      credentials: "include",
      body: (() => {
        const fd = new FormData();
        fd.append("text", text);
        fd.append("voice", voice);
        fd.append("language", language);
        return fd;
      })(),
    });
    if (!res.ok) throw new ApiError(res.status, "SPEAK_FAILED", "Voice playback failed");
    return res.blob();
  },
};

// ---------------------------------------------------------------------------
// Notes
// ---------------------------------------------------------------------------

export type Note = {
  id: string;
  subject: string;
  title: string;
  content: string;
  created_at?: string | null;
  updated_at?: string | null;
};

export const notesApi = {
  list: (subject?: string) =>
    request<{ notes: Note[] }>(
      `/api/notes${subject ? `?subject=${encodeURIComponent(subject)}` : ""}`
    ),
  create: (payload: { subject: string; title: string; content: string }) =>
    request<Note>("/api/notes", { method: "POST", body: payload }),
  update: (
    id: string,
    payload: Partial<{ subject: string; title: string; content: string }>
  ) => request<Note>(`/api/notes/${id}`, { method: "PATCH", body: payload }),
  remove: (id: string) =>
    request<void>(`/api/notes/${id}`, { method: "DELETE" }),
};

// ---------------------------------------------------------------------------
// Study room
// ---------------------------------------------------------------------------

export type SessionInfo = { session_id: string; status: string };

export const studyApi = {
  start: (payload: { character?: string; language?: string }) =>
    request<SessionInfo>("/api/study_room/session/start", {
      method: "POST",
      body: payload,
    }),
  pause: (sessionId: string) =>
    request<SessionInfo>("/api/study_room/session/pause", {
      method: "POST",
      body: { session_id: sessionId },
    }),
  resume: (sessionId: string) =>
    request<SessionInfo>("/api/study_room/session/resume", {
      method: "POST",
      body: { session_id: sessionId },
    }),
  complete: (sessionId: string) =>
    request<SessionInfo>("/api/study_room/session/complete", {
      method: "POST",
      body: { session_id: sessionId },
    }),
  current: (sessionId?: string) =>
    request<SessionInfo>(
      `/api/study_room/session/current${
        sessionId ? `?session_id=${sessionId}` : ""
      }`
    ),
  addEvent: (sessionId: string, type: string, payload: Record<string, unknown>) =>
    request<{ event_id: string; recorded: boolean }>("/api/study_room/event", {
      method: "POST",
      body: { session_id: sessionId, type, payload },
    }),
};

// ---------------------------------------------------------------------------
// Dashboard
// ---------------------------------------------------------------------------

export type DashboardSummary = {
  words_today: number;
  minutes_today: number;
  total_words: number;
  total_minutes: number;
  streak_days: number;
  subject_breakdown: Array<{ subject: string; sessions: number }>;
};

export const dashboardApi = {
  summary: () =>
    request<DashboardSummary>("/api/dashboard/summary"),
};

// ---------------------------------------------------------------------------
// Profile
// ---------------------------------------------------------------------------

export type Profile = {
  id: string;
  email: string;
  name?: string | null;
  character: string;
  language: string;
};

export const profileApi = {
  get: () => request<Profile>("/api/profile"),
  update: (payload: Partial<{ name: string; character: string; language: string }>) =>
    request<Profile>("/api/profile", { method: "PATCH", body: payload }),
};

// ---------------------------------------------------------------------------
// Study plan (Study Mode)
// ---------------------------------------------------------------------------

export type StudyPlan = {
  total_hours: number;
  total_minutes: number;
  sessions: string[];
  breaks: Array<{ after_minute: number; minutes: number }>;
  breaks_count: number;
};

export type StudyPlanResponse = { plan: StudyPlan };

export type ReminderResponse = {
  text: string;
  character: string;
  language: string;
};

export const studyPlanApi = {
  generate: (requestText: string, userName?: string) =>
    request<StudyPlanResponse>("/api/study_plan/generate", {
      method: "POST",
      body: { request_text: requestText, user_name: userName },
    }),
  reminder: (userName?: string) =>
    request<ReminderResponse>("/api/study_plan/reminder", {
      method: "POST",
      body: { user_name: userName },
    }),
};

const api = {
  auth: authApi,
  onboarding: onboardingApi,
  communication: communicationApi,
  notes: notesApi,
  study: studyApi,
  studyPlan: studyPlanApi,
  dashboard: dashboardApi,
  profile: profileApi,
  ApiError,
};

export default api;
