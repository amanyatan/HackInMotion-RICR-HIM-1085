// ===========================================================================
// FocusDetector
//
// Thin wrapper over MediaPipe FaceLandmarker used by Study Mode's camera /
// focus monitoring panel. It runs a video loop and reports *attention state*
// — NOT a claim that we "know" why the student is distracted. Per Design.md
// §31 we never imply monitoring something the camera cannot actually detect.
// ===========================================================================

import { FaceLandmarker, FilesetResolver } from "@mediapipe/tasks-vision";

export type AttentionState = "focused" | "no_face" | "glancing_away" | "head_down";

export type AttentionSample = {
  state: AttentionState;
  score: number; // 0..1 confidence-like measure of distraction
  reason: string;
  at: number;
};

const WASM_PATH = "/mediapipe/wasm";
const MODEL_PATH = "/mediapipe/model/face_landmarker.task";

export class FocusDetector {
  private landmarker: FaceLandmarker | null = null;
  private video: HTMLVideoElement | null = null;
  private stream: MediaStream | null = null;
  private running = false;
  private rafId = 0;
  private lastSampleAt = 0;
  private onSample: (sample: AttentionSample) => void;

  constructor(onSample: (sample: AttentionSample) => void) {
    this.onSample = onSample;
  }

  get isRunning(): boolean {
    return this.running;
  }

  /** Explicit user consent to enable the camera. Never call silently. */
  async start(): Promise<void> {
    if (this.running) return;
    try {
      this.stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: "user", width: { ideal: 640 }, height: { ideal: 480 } },
        audio: false,
      });
    } catch {
      throw new Error("Camera permission was denied or the camera is unavailable.");
    }

    this.video = document.createElement("video");
    this.video.srcObject = this.stream;
    this.video.muted = true;
    this.video.playsInline = true;
    await this.video.play();

    if (!this.landmarker) {
      const vision = await FilesetResolver.forVisionTasks(WASM_PATH);
      this.landmarker = await FaceLandmarker.createFromOptions(vision, {
        baseOptions: { modelAssetPath: MODEL_PATH, delegate: "GPU" },
        runningMode: "VIDEO",
        numFaces: 1,
        outputFaceBlendshapes: true,
        minFaceDetectionConfidence: 0.5,
        minFacePresenceConfidence: 0.5,
        minTrackingConfidence: 0.5,
      });
    }

    this.running = true;
    this.loop();
  }

  /** Turn monitoring off and release the camera. Safe to call anytime. */
  stop(): void {
    this.running = false;
    cancelAnimationFrame(this.rafId);
    if (this.stream) {
      this.stream.getTracks().forEach((t) => t.stop());
      this.stream = null;
    }
    this.video = null;
  }

  private loop(): void {
    if (!this.running || !this.video || !this.landmarker) return;

    const now = performance.now();
    if (this.video.readyState >= 2) {
      const result = this.landmarker.detectForVideo(this.video, now);
      const sample = classifyAttention(result, now);
      if (now - this.lastSampleAt >= 500) {
        this.lastSampleAt = now;
        this.onSample(sample);
      }
    }
    this.rafId = requestAnimationFrame(() => this.loop());
  }
}

// ---------------------------------------------------------------------------
// Heuristics
//
// Face blendshapes include headPitch/headYaw/headRoll (~ -1..1). Facing the
// screen: pitch & yaw near 0. Large magnitudes mean the head is turned away.
// ---------------------------------------------------------------------------

function classifyAttention(result: { faceLandmarks: unknown[][] }, now: number): AttentionSample {
  const none: AttentionSample = {
    state: "no_face",
    score: 1,
    reason: "No face detected — look back toward the camera.",
    at: now,
  };

  if (!result.faceLandmarks || result.faceLandmarks.length === 0) return none;

  // Face present; blendshapes may not be enabled in some builds — fall back to
  // a neutral "focused" read so we never nag off of missing data.
  const focused: AttentionSample = {
    state: "focused",
    score: 0,
    reason: "Face visible.",
    at: now,
  };

  const blendshapeData = (result as unknown as {
    faceBlendshapes?: Array<{ categories?: Array<{ categoryName: string; score: number }> }>;
  }).faceBlendshapes;

  const cats =
    blendshapeData?.[0]?.categories?.reduce<Record<string, number>>((acc, c) => {
      acc[c.categoryName] = c.score;
      return acc;
    }, {}) ?? {};

  const pitch = cats.headPitch ?? 0;
  const yaw = cats.headYaw ?? 0;

  // Head pitched far down (~ reading a phone in hand).
  if (pitch > 0.55) {
    return { state: "head_down", score: Math.min(1, pitch), reason: "Head is tilted down — maybe off the desk.", at: now };
  }

  // Head rotated clearly away from screen / toward another person.
  if (Math.abs(yaw) > 0.6) {
    return { state: "glancing_away", score: Math.min(1, Math.abs(yaw)), reason: "Facing away from the screen.", at: now };
  }

  return focused;
}