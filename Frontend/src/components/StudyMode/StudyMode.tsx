"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import {
  AlertTriangle,
  Camera,
  CameraOff,
  Check,
  Pause,
  Play,
  Sparkles,
  Target,
  Timer as TimerIcon,
  Trophy,
} from "lucide-react";

import { authApi, communicationApi, studyApi, studyPlanApi } from "@/lib/api";
import { FocusDetector, type AttentionSample } from "@/lib/focusDetector";

type Phase = "boot" | "setup" | "focus" | "done";

type MarkMessage = {
  id: string;
  from: "mark" | "user";
  text: string;
};

type DistractionLog = {
  id: string;
  time: string;
  reason: string;
  nudge: string;
};

const MARK_SPEAK_STATE: Record<string, "idle" | "listening" | "thinking" | "speaking"> = {
  idle: "idle",
  thinking: "thinking",
  speaking: "speaking",
};

function toHHMMSS(seconds: number): string {
  const s = Math.max(0, Math.floor(seconds));
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  return `${h > 0 ? `${h}:` : ""}${String(m).padStart(2, "0")}:${String(sec).padStart(2, "0")}`;
}

export default function StudyMode() {
  const router = useRouter();

  const [phase, setPhase] = useState<Phase>("boot");
  const [userName, setUserName] = useState("friend");

  // Setup chat (Mark asks hours/breaks)
  const [messages, setMessages] = useState<MarkMessage[]>([]);
  const [input, setInput] = useState("");
  const [markBusy, setMarkBusy] = useState(false);

  // Plan
  const [plan, setPlan] = useState<Awaited<ReturnType<typeof studyPlanApi.generate>>["plan"] | null>(null);

  // Focus timer
  const [remaining, setRemaining] = useState(0);
  const [totalSeconds, setTotalSeconds] = useState(0);
  const [elapsed, setElapsed] = useState(0);
  const [timerRunning, setTimerRunning] = useState(false);
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Camera / focus
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const detectorRef = useRef<FocusDetector | null>(null);
  const [cameraStatus, setCameraStatus] = useState<"off" | "requesting" | "active" | "denied" | "error">("off");
  const [attention, setAttention] = useState<AttentionSample | null>(null);
  const attentionRef = useRef<AttentionSample | null>(null);
  const [logs, setLogs] = useState<DistractionLog[]>([]);
  const lastNudgeRef = useRef(0);
  const sustainedAwayRef = useRef(0);
  const sessionIdRef = useRef<string | null>(null);

  // ---------------- Boot: identify the user ----------------
  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const me = await authApi.me();
        if (!mounted) return;
        setUserName(me.user.name || "friend");
        setMessages([
          {
            id: "m1",
            from: "mark",
            text: `Hey ${me.user.name || "there"}! I'm Mark. Let's plan your study session. How many hours do you want to study — and how many breaks?`,
          },
        ]);
        setPhase("setup");
      } catch {
        if (mounted) router.replace("/login");
      }
    })();
    return () => {
      mounted = false;
    };
  }, [router]);

  // ---------------- Timer: countdown + break markers ----------------
  useEffect(() => {
    if (phase !== "focus") return;
    setTotalSeconds(Math.round(plan?.total_minutes ?? 0) * 60);
    setRemaining(Math.round(plan?.total_minutes ?? 0) * 60);
    setElapsed(0);
    setTimerRunning(true);
  }, [phase, plan]);

  useEffect(() => {
    if (!timerRunning || remaining <= 0) {
      if (timerRunning && remaining === 0) setTimerRunning(false);
      return;
    }
    timerRef.current = setInterval(() => {
      setRemaining((r) => (r > 0 ? r - 1 : 0));
      setElapsed((e) => e + 1);
    }, 1000);
    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [timerRunning, remaining]);

  const startedSession = useCallback(async () => {
    try {
      const s = await studyApi.start({ character: "mark" });
      sessionIdRef.current = s.session_id;
    } catch {
      // non-fatal: session events are best-effort
    }
  }, []);

  const nextBreak = useMemo(() => {
    if (!plan) return null;
    const minute = elapsed / 60;
    // only show the break while its window is still running
    return (
      plan.breaks.find((b) => minute >= b.after_minute && minute < b.after_minute + b.minutes) ?? null
    );
  }, [plan, elapsed]);

  const currentBlock = useMemo(() => {
    if (!plan) return 0;
    const minute = elapsed / 60;
    const idx = plan.breaks.filter((b) => b.after_minute <= minute).length;
    return Math.min(idx + 1, plan.sessions.length);
  }, [plan, elapsed]);

  // Auto-suspend the timer while a break is active so breaks stay real.
  useEffect(() => {
    if (nextBreak && timerRunning) setTimerRunning(false);
  }, [nextBreak, timerRunning]);

  // ---------------- Mark speaks (TTS, mark voice) ----------------
  const speak = useCallback(async (text: string) => {
    try {
      const blob = await communicationApi.speakBlob(text, "mark", "en");
      const url = URL.createObjectURL(blob);
      const audio = new Audio(url);
      audio.onended = () => {
        URL.revokeObjectURL(url);
      };
      await audio.play();
    } catch {
      // audio is best-effort; the message text still shows in the chat
    }
  }, []);

  // ---------------- Setup chat handler ----------------
  const handleSend = useCallback(async () => {
    const text = input.trim();
    if (!text || markBusy) return;
    setInput("");
    setMessages((m) => [...m, { id: crypto.randomUUID(), from: "user", text }]);
    setMarkBusy(true);

    try {
      const res = await studyPlanApi.generate(text, userName);
      setPlan(res.plan);
      const planText = `Great! ${res.plan.total_hours}h study with ${res.plan.breaks_count} break${
        res.plan.breaks_count === 1 ? "" : "s"
      }. Should I lock it in?`;
      setMessages((m) => [...m, { id: crypto.randomUUID(), from: "mark", text: planText }]);
      await speak(planText);
    } catch (e) {
      const err = e as { code?: string; message?: string };
      const msg =
        err.code === "MAX_8_HOURS"
          ? "Whoa, that's more than 8 hours! A study session can't go over 8 hours. How about we plan up to 8 hours — how many hours and how many breaks?"
          : err.code === "PLAN_AMBIGUOUS"
            ? "Hmm, I didn't catch that. Tell me the hours — like '4 hours with 2 breaks'."
            : err.message || "Something went wrong. Let's try again.";
      setMessages((m) => [...m, { id: crypto.randomUUID(), from: "mark", text: msg }]);
      await speak(msg);
    } finally {
      setMarkBusy(false);
    }
  }, [input, markBusy, userName, speak]);

  const confirmPlan = useCallback(async () => {
    setPhase("focus");
    await startedSession();
    setMessages((m) => [
      ...m,
      { id: crypto.randomUUID(), from: "mark", text: "Locked in! The timer is running. I'll keep you on track — and I'm watching for focus." },
    ]);
  }, [startedSession]);

  const restart = useCallback(() => {
    setPlan(null);
    setLogs([]);
    setAttention(null);
    setCameraStatus("off");
    detectorRef.current?.stop();
    detectorRef.current = null;
    if (sessionIdRef.current) studyApi.complete(sessionIdRef.current).catch(() => {});
    sessionIdRef.current = null;
    setPhase("setup");
  }, []);

  // ---------------- Camera / focus monitoring ----------------
  const handleDistraction = useCallback(
    async (sample: AttentionSample) => {
      const now = Date.now();
      if (now - lastNudgeRef.current < 60_000) return; // max 1 nudge / minute
      lastNudgeRef.current = now;

      if (sessionIdRef.current) {
        studyApi
          .addEvent(sessionIdRef.current, "distraction", { reason: sample.reason })
          .catch(() => {});
      }

      try {
        const res = await studyPlanApi.reminder(userName);
        const entry: DistractionLog = {
          id: crypto.randomUUID(),
          time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
          reason: sample.reason,
          nudge: res.text,
        };
        setLogs((l) => [entry, ...l]);
        await speak(res.text);
      } catch {
        // leave the visual card even if voice fails
      }
    },
    [userName, speak]
  );

  const enableCamera = useCallback(async () => {
    setCameraStatus("requesting");
    try {
      const video = videoRef.current;
      if (!video) throw new Error("video not mounted");

      const detector = new FocusDetector((sample) => {
        attentionRef.current = sample;
        setAttention(sample);

        if (sample.state !== "focused") {
          sustainedAwayRef.current += 1;
          if (sustainedAwayRef.current >= 6) {
            sustainedAwayRef.current = 0;
            void handleDistraction(sample);
          }
        } else {
          sustainedAwayRef.current = 0;
        }
      });

      await detector.start();
      const stream = (detector as unknown as { stream: MediaStream | null }).stream;
      if (stream) video.srcObject = stream;
      await video.play();
      detectorRef.current = detector;
      setCameraStatus("active");
    } catch (e) {
      const hasPermission =
        e instanceof DOMException &&
        (e.name === "NotAllowedError" || e.name === "PermissionDeniedError");
      setCameraStatus(hasPermission ? "denied" : "error");
    }
  }, [handleDistraction]);

  const disableCamera = useCallback(() => {
    detectorRef.current?.stop();
    detectorRef.current = null;
    const video = videoRef.current;
    if (video?.srcObject) {
      (video.srcObject as MediaStream).getTracks().forEach((t) => t.stop());
      video.srcObject = null;
    }
    setCameraStatus("off");
    setAttention(null);
    sustainedAwayRef.current = 0;
  }, []);

  // ---------------- Mark character card ----------------
  const markCard = (
    <div className="flex flex-col items-center gap-4 rounded-[2rem] border border-border bg-surface-1 p-6 text-center shadow-soft">
      <div className="relative">
        <div className="flex h-20 w-20 items-center justify-center rounded-full border border-accent-border bg-accent-soft">
          <Sparkles className="h-8 w-8 text-accent" />
        </div>
        <span className="absolute -bottom-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full border border-border bg-black">
          <span
            className={`h-2.5 w-2.5 rounded-full ${
              phase === "focus" ? "bg-emerald-400" : markBusy ? "animate-pulse bg-amber-400" : "bg-accent"
            }`}
          />
        </span>
      </div>
      <div>
        <p className="font-sora text-lg font-semibold tracking-[-0.02em] text-white">Mark</p>
        <p className="font-jakarta text-xs text-muted">Your focus companion</p>
      </div>
      {MARK_SPEAK_STATE[markBusy ? "thinking" : phase === "focus" ? "speaking" : "idle"] === "speaking" && (
        <p className="font-jakarta text-xs text-accent">Speaking…</p>
      )}
    </div>
  );

  // ---------------- Render: boot ----------------
  if (phase === "boot") {
    return (
      <main className="flex min-h-screen items-center justify-center bg-black text-white">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-border border-t-accent" />
      </main>
    );
  }

  // ---------------- Render: setup chat ----------------
  if (phase === "setup") {
    return (
      <main className="min-h-screen bg-black text-white">
        <header className="border-b border-border bg-surface-1/80 backdrop-blur-xl">
          <div className="mx-auto flex h-16 max-w-[1280px] items-center justify-between px-5 sm:px-6 lg:px-8">
            <div className="flex items-center gap-2 font-jakarta text-sm font-semibold tracking-[-0.02em]">
              <Target className="h-4 w-4 text-accent" />
              Study Mode
            </div>
            <button
              onClick={() => router.push("/")}
              className="font-jakarta text-xs text-muted transition-colors hover:text-white"
            >
              Exit
            </button>
          </div>
        </header>

        <div className="mx-auto grid max-w-[1280px] gap-8 px-5 py-10 sm:px-6 lg:grid-cols-[340px_1fr] lg:px-8">
          <aside className="space-y-6">
            {markCard}
            <ul className="space-y-3">
              {["Tell Mark how long you want to study", "He schedules breaks for you", "He keeps you focused with voice nudges"].map(
                (step, i) => (
                  <li key={step} className="flex items-start gap-3">
                    <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border border-accent-border bg-accent-soft font-jakarta text-xs font-bold text-accent">
                      {i + 1}
                    </span>
                    <p className="font-jakarta text-sm text-text-secondary">{step}</p>
                  </li>
                )
              )}
            </ul>
          </aside>

          <section className="flex min-h-[60vh] flex-col rounded-[2rem] border border-border bg-surface-1 p-6 shadow-soft">
            <h1 className="font-sora text-xl font-semibold tracking-[-0.02em] text-white sm:text-2xl">
              Plan your session
            </h1>

            <div className="mt-6 flex flex-1 flex-col gap-3 overflow-y-auto">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.from === "user" ? "justify-end" : "justify-start"}`}
                >
                  <div
                    className={`max-w-[85%] rounded-2xl px-4 py-3 font-jakarta text-sm leading-relaxed ${
                      msg.from === "user"
                        ? "rounded-br-md bg-[#1693A7] font-medium text-white"
                        : "rounded-bl-md border border-border bg-surface-2 text-white"
                    }`}
                  >
                    {msg.text}
                  </div>
                </div>
              ))}
              {markBusy && (
                <div className="flex items-center gap-1 px-4 py-2">
                  <span className="h-2 w-2 animate-pulse rounded-full bg-accent" />
                  <span className="h-2 w-2 animate-pulse rounded-full bg-accent [animation-delay:150ms]" />
                  <span className="h-2 w-2 animate-pulse rounded-full bg-accent [animation-delay:300ms]" />
                </div>
              )}
            </div>

            {!plan && (
              <form
                className="mt-6 flex gap-3"
                onSubmit={(e) => {
                  e.preventDefault();
                  void handleSend();
                }}
              >
                <input
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder='e.g. "4 hours with 2 breaks"'
                  className="h-12 flex-1 rounded-xl border border-border bg-surface-2 px-4 font-jakarta text-sm text-white outline-none transition-colors placeholder:text-muted focus:border-accent-border"
                />
                <button
                  type="submit"
                  disabled={markBusy || !input.trim()}
                  className="inline-flex h-12 items-center justify-center rounded-xl bg-[#1693A7] px-6 font-jakarta text-sm font-extrabold text-white shadow-[0_8px_30px_rgba(22,147,167,0.18)] transition-all hover:bg-[#1BAFC5] disabled:cursor-not-allowed disabled:opacity-50"
                >
                  Send
                </button>
              </form>
            )}

            {plan && (
              <div className="mt-6 space-y-4">
                <div className="rounded-2xl border border-accent-border bg-accent-soft p-5">
                  <p className="font-jakarta text-xs font-bold uppercase tracking-[0.2em] text-accent">Your plan</p>
                  <div className="mt-2 flex items-end gap-3">
                    <span className="font-sora text-4xl font-semibold tracking-[-0.04em] text-white">
                      {plan.total_hours}h
                    </span>
                    <span className="pb-1 font-jakarta text-sm text-text-secondary">
                      {plan.breaks_count} break{plan.breaks_count === 1 ? "" : "s"}
                    </span>
                  </div>
                  <ul className="mt-4 space-y-1.5 font-jakarta text-sm text-text-secondary">
                    {plan.sessions.map((s, i) => (
                      <li key={i} className="flex items-center gap-2">
                        <span className="h-1.5 w-1.5 rounded-full bg-accent" />
                        Study block {i + 1}: {s}
                      </li>
                    ))}
                  </ul>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={confirmPlan}
                    className="inline-flex h-12 flex-1 items-center justify-center gap-2 rounded-xl bg-[#1693A7] px-6 font-jakarta text-sm font-extrabold text-white shadow-[0_8px_30px_rgba(22,147,167,0.18)] transition-all hover:bg-[#1BAFC5]"
                  >
                    <Check className="h-4 w-4" />
                    Start studying
                  </button>
                  <button
                    onClick={() => {
                      setPlan(null);
                      setMessages((m) => [
                        ...m,
                        {
                          id: crypto.randomUUID(),
                          from: "mark",
                          text: "No problem — tell me the new hours and breaks.",
                        },
                      ]);
                    }}
                    className="inline-flex h-12 items-center justify-center rounded-xl border border-border px-6 font-jakarta text-sm font-semibold text-text-secondary transition-colors hover:border-border-hover hover:text-white"
                  >
                    Change
                  </button>
                </div>
              </div>
            )}
          </section>
        </div>
      </main>
    );
  }

  // ---------------- Render: focus session ----------------
  const progress = totalSeconds > 0 ? ((totalSeconds - remaining) / totalSeconds) * 100 : 0;

  return (
    <main className="min-h-screen bg-black text-white">
      <header className="border-b border-border bg-surface-1/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-[1280px] items-center justify-between px-5 sm:px-6 lg:px-8">
          <div className="flex items-center gap-2 font-jakarta text-sm font-semibold tracking-[-0.02em]">
            <Target className="h-4 w-4 text-accent" />
            Study Mode · {userName}
          </div>
          <div className="flex items-center gap-3">
            {cameraStatus === "active" && (
              <span className="flex items-center gap-1.5 rounded-full border border-emerald-500/40 bg-emerald-500/10 px-3 py-1 font-jakarta text-xs font-semibold text-emerald-400">
                <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
                Camera Active
              </span>
            )}
            <button
              onClick={restart}
              className="font-jakarta text-xs text-muted transition-colors hover:text-white"
            >
              New session
            </button>
          </div>
        </div>
      </header>

      <div className="mx-auto grid max-w-[1280px] gap-8 px-5 py-10 sm:px-6 lg:grid-cols-[1fr_340px] lg:px-8">
        {/* Main learning area */}
        <section className="space-y-6">
          {/* Timer + progress */}
          <div className="rounded-[2rem] border border-border bg-surface-1 p-8 text-center shadow-soft">
            <div className="flex items-center justify-center gap-4">
              <TimerIcon className="h-5 w-5 text-accent" />
              <span className="font-jakarta text-sm font-semibold uppercase tracking-[0.2em] text-muted">
                Study session
              </span>
            </div>

            <p className="mt-6 font-sora text-[clamp(3.5rem,10vw,7rem)] font-semibold leading-none tracking-[-0.05em] text-white tabular-nums">
              {toHHMMSS(remaining)}
            </p>

            <div className="mx-auto mt-6 h-2 w-full max-w-md overflow-hidden rounded-full bg-[#222222]">
              <div
                className="h-full rounded-full bg-[#1693A7] transition-[width] duration-1000 ease-linear"
                style={{ width: `${Math.min(100, progress)}%` }}
              />
            </div>

            <div className="mt-4 flex items-center justify-center gap-6 font-jakarta text-sm text-text-secondary">
              <span>Block {currentBlock} / {plan?.sessions.length ?? 0}</span>
              <span className="text-muted">·</span>
              <span>Total {plan?.total_hours}h</span>
            </div>

            {nextBreak ? (
              <div className="mt-6 mx-auto flex max-w-md items-center gap-3 rounded-2xl border border-amber-400/30 bg-amber-400/10 px-4 py-3 font-jakarta text-sm text-amber-300">
                <Coffee className="h-4 w-4 shrink-0" />
                Break time — {nextBreak.minutes} min. Stand up, stretch, hydrate!
              </div>
            ) : (
              <div className="mt-6 flex items-center justify-center gap-3">
                <button
                  onClick={() => {
                    setTimerRunning((r) => !r);
                    if (sessionIdRef.current) {
                      studyApi
                        .addEvent(sessionIdRef.current, timerRunning ? "pause" : "resume", {})
                        .catch(() => {});
                    }
                  }}
                  className="inline-flex h-12 items-center justify-center gap-2 rounded-xl bg-[#1693A7] px-6 font-jakarta text-sm font-extrabold text-white shadow-[0_8px_30px_rgba(22,147,167,0.18)] transition-all hover:bg-[#1BAFC5]"
                >
                  {timerRunning ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
                  {timerRunning ? "Pause" : "Resume"}
                </button>

                {remaining === 0 && (
                  <button
                    onClick={restart}
                    className="inline-flex h-12 items-center justify-center gap-2 rounded-xl border border-emerald-500/40 bg-emerald-500/10 px-6 font-jakarta text-sm font-extrabold text-emerald-400 transition-all hover:bg-emerald-500/20"
                  >
                    <Trophy className="h-4 w-4" />
                    Session complete
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Camera / focus monitoring */}
          <div className="rounded-[2rem] border border-border bg-surface-1 p-6 shadow-soft">
            <div className="flex items-center justify-between">
              <h2 className="font-sora text-lg font-semibold tracking-[-0.02em] text-white">
                Focus monitoring
              </h2>
              {cameraStatus === "active" && (
                <span className="flex items-center gap-2 font-jakarta text-xs">
                  <span
                    className={`h-2.5 w-2.5 rounded-full ${attention?.state === "focused" ? "bg-emerald-400" : "animate-pulse bg-amber-400"}`}
                  />
                  <span className="text-muted">
                    {attention ? attention.reason : "Detecting…"}
                  </span>
                </span>
              )}
            </div>

            {cameraStatus === "active" ? (
              <div className="mt-4 grid gap-4 sm:grid-cols-[minmax(0,240px)_1fr]">
                <div className="relative aspect-[4/3] overflow-hidden rounded-2xl border border-border bg-black">
                  <video
                    ref={videoRef}
                    autoPlay
                    muted
                    playsInline
                    className="h-full w-full -scale-x-100 object-cover"
                  />
                  <span className="absolute left-2 top-2 rounded-full bg-black/60 px-2.5 py-1 font-jakarta text-[10px] font-semibold uppercase tracking-[0.15em] text-emerald-400">
                    ● Live
                  </span>
                </div>
                <div className="flex flex-col justify-between gap-4">
                  <div>
                    <h3 className="font-jakarta text-sm font-semibold text-white">How this works</h3>
                    <p className="mt-1 font-jakarta text-sm leading-6 text-text-secondary">
                      The camera checks whether you&apos;re still looking at your work. When it sees
                      your head turn away or tilt down, I&apos;ll gently remind you to get back to
                      your studies. Monitoring runs only while this screen is open.
                    </p>
                  </div>
                  <button
                    onClick={disableCamera}
                    className="inline-flex h-11 items-center justify-center gap-2 rounded-xl border border-border px-5 font-jakarta text-sm font-semibold text-text-secondary transition-colors hover:border-border-hover hover:text-white"
                  >
                    <CameraOff className="h-4 w-4" />
                    Stop camera
                  </button>
                </div>
              </div>
            ) : (
              <div className="mt-4">
                <p className="font-jakarta text-sm leading-6 text-text-secondary">
                  {cameraStatus === "denied"
                    ? "Camera permission was denied. I can still run your timer, but I won't be able to watch for distractions. You can enable the camera in your browser settings, then click retry."
                    : cameraStatus === "requesting"
                      ? "Requesting camera access…"
                      : "Turn on the camera to let Mark watch for distractions while you study. The camera is never activated without your permission."}
                </p>
                {cameraStatus !== "requesting" && (
                  <button
                    onClick={enableCamera}
                    className="mt-4 inline-flex h-11 items-center justify-center gap-2 rounded-xl bg-[#1693A7] px-5 font-jakarta text-sm font-extrabold text-white shadow-[0_8px_30px_rgba(22,147,167,0.18)] transition-all hover:bg-[#1BAFC5]"
                  >
                    <Camera className="h-4 w-4" />
                    {cameraStatus === "denied" ? "Retry camera" : "Enable camera"}
                  </button>
                )}
              </div>
            )}
          </div>

          {/* Distraction log */}
          {logs.length > 0 && (
            <div className="rounded-[2rem] border border-border bg-surface-1 p-6 shadow-soft">
              <h2 className="mb-4 flex items-center gap-2 font-sora text-lg font-semibold tracking-[-0.02em] text-white">
                <AlertTriangle className="h-5 w-5 text-amber-400" />
                Focus nudges
              </h2>
              <ul className="space-y-3">
                {logs.map((log) => (
                  <li key={log.id} className="rounded-2xl border border-border bg-surface-2 p-4">
                    <div className="flex items-center justify-between font-jakarta text-xs text-muted">
                      <span>{log.time}</span>
                      <span>{log.reason}</span>
                    </div>
                    <p className="mt-1.5 font-jakarta text-sm text-white">&ldquo;{log.nudge}&rdquo;</p>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </section>

        {/* Side column: Mark + plan card */}
        <aside className="space-y-6">
          {markCard}

          <div className="rounded-2xl border border-border bg-surface-2 p-5">
            <p className="font-jakarta text-sm leading-6 text-text-secondary">
              <span className="font-semibold text-white">Focus check:</span>{" "}
              {cameraStatus === "off"
                ? "Camera is off — timer only. Mark won't speak focus nudges."
                : attention?.reason ?? "Watching…"}
            </p>
          </div>

          {/* Plan card ("card stays on the side") */}
          <div className="rounded-[2rem] border border-accent-border bg-accent-soft p-6 shadow-soft">
            <p className="font-jakarta text-xs font-bold uppercase tracking-[0.2em] text-accent">
              Today&apos;s plan
            </p>
            <p className="mt-2 font-sora text-3xl font-semibold tracking-[-0.03em] text-white">
              {plan?.total_hours}h
            </p>
            <ul className="mt-4 space-y-1.5 font-jakarta text-sm text-text-secondary">
              {plan?.sessions.map((s, i) => {
                const active = i + 1 === currentBlock && timerRunning;
                return (
                  <li
                    key={i}
                    className={`flex items-center justify-between rounded-xl px-3 py-2 ${
                      active ? "border border-accent-border bg-[#1693A7]/10 text-white" : ""
                    }`}
                  >
                    <span className="flex items-center gap-2">
                      <span className={`h-1.5 w-1.5 rounded-full ${active ? "bg-accent" : "bg-muted"}`} />
                      Block {i + 1}
                    </span>
                    <span className="tabular-nums">{s}</span>
                  </li>
                );
              })}
            </ul>
          </div>
        </aside>
      </div>
    </main>
  );
}

function Coffee({ className }: { className?: string }) {
  return (
    <svg
      className={className}
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M17 8h1a4 4 0 1 1 0 8h-1" />
      <path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z" />
      <line x1="6" x2="6" y1="2" y2="4" />
      <line x1="10" x2="10" y1="2" y2="4" />
      <line x1="14" x2="14" y1="2" y2="4" />
    </svg>
  );
}