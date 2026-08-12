"use client";

import { useState } from "react";
import Link from "next/link";
import { AnimatePresence, motion } from "framer-motion";
import {
  ArrowLeft,
  ArrowRight,
  Eye,
  EyeOff,
  Loader2,
  Lock,
  Mail,
  User,
} from "lucide-react";
import Authpagecomponent from "./authpagecomponent";

type Mode = "signin" | "signup";

const inputBase =
  "h-12 w-full rounded-xl border border-border bg-surface-2 pl-11 pr-12 font-jakarta text-sm text-white placeholder:text-muted outline-none transition-all duration-200 focus:border-[#1693A7] focus:ring-2 focus:ring-[#1693A7]/25";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

export default function Auth() {
  const [mode, setMode] = useState<Mode>("signin");
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const switchMode = (next: Mode) => {
    setMode(next);
    setError("");
    setSuccess("");
    setShowPassword(false);
    setShowConfirm(false);
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();

    if (isSubmitting) return;

    const form = new FormData(e.currentTarget);

    if (mode === "signup") {
      const password = String(form.get("password") ?? "");
      const confirm = String(form.get("confirmPassword") ?? "");

      if (password !== confirm) {
        setError("Passwords do not match.");
        return;
      }

      if (password.length < 8) {
        setError("Password must be at least 8 characters.");
        return;
      }
    }

    setError("");
    setSuccess("");
    setIsSubmitting(true);

    const body =
      mode === "signin"
        ? {
            email: String(form.get("email") ?? ""),
            password: String(form.get("password") ?? ""),
          }
        : {
            name: String(form.get("name") ?? ""),
            email: String(form.get("email") ?? ""),
            password: String(form.get("password") ?? ""),
            confirmPassword: String(form.get("confirmPassword") ?? ""),
          };

    try {
      const res = await fetch(
        `${API_BASE}/api/auth/${mode === "signin" ? "login" : "signup"}`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          credentials: "include",
          body: JSON.stringify(body),
        }
      );

      let data: { message?: string; error?: { code?: string; message?: string } } = {};
      try {
        data = await res.json();
      } catch {
        // non-JSON body — fall through to status-based handling
      }

      if (!res.ok) {
        const code = data.error?.code;
        if (code === "EMAIL_ALREADY_EXISTS" || res.status === 409) {
          setError("An account with this email already exists.");
        } else if (code === "INVALID_CREDENTIALS" || res.status === 401) {
          setError("Incorrect email or password.");
        } else if (code === "EMAIL_NOT_CONFIRMED") {
          setError("Please confirm your email address before signing in.");
        } else if (code === "RATE_LIMITED" || res.status === 429) {
          setError("Too many attempts. Please wait a moment and try again.");
        } else if (res.status === 422) {
          setError("Please check your details and try again.");
        } else if (data.error?.message) {
          setError(data.error.message);
        } else {
          setError("Something went wrong. Please try again.");
        }
        return;
      }

      setSuccess(
        mode === "signin"
          ? "Signed in successfully. Welcome back!"
          : "Account created — you're signed in. Welcome to COSMOS!"
      );
    } catch {
      setError("Could not reach the server. Please check your connection and try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  const fieldIconClass =
    "pointer-events-none absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-muted";

  return (
    <main className="relative min-h-screen overflow-hidden bg-black text-white">
      {/* =========================================================
          DESKTOP BACKGROUND SPLIT
          
          LEFT  = 50% BLACK
          RIGHT = 50% WHITE
          
          This is FULL viewport height/width.
          ========================================================= */}
      <div
        className="
          pointer-events-none
          absolute
          inset-y-0
          right-0
          z-0
          hidden
          w-1/2
          bg-white
          md:block
        "
      />

      {/* Ambient background — kept only on black side */}
      <div
        className="
          pointer-events-none
          absolute
          -top-40
          left-0
          z-0
          h-[480px]
          w-[480px]
          rounded-full
          bg-[rgba(22,147,167,0.10)]
          blur-[120px]
        "
      />

      <div
        className="
          pointer-events-none
          absolute
          bottom-[-20%]
          left-[-10%]
          z-0
          h-[420px]
          w-[420px]
          rounded-full
          bg-[rgba(22,147,167,0.07)]
          blur-[120px]
        "
      />

      {/* =========================================================
          PAGE CONTENT
          ========================================================= */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.5 }}
        className="
          relative
          z-10
          mx-auto
          flex
          min-h-screen
          w-full
          max-w-[1280px]
          flex-col
          px-5
          py-6
          sm:px-8
        "
      >
        {/* =======================================================
            TOP BAR
            ======================================================= */}
        <div className="flex items-center justify-between">
          <Link
            href="/"
            className="
              group
              inline-flex
              items-center
              gap-2
              font-jakarta
              text-sm
              text-text-secondary
              transition-colors
              duration-200
              hover:text-white
            "
          >
            <ArrowLeft className="h-4 w-4 transition-transform duration-200 group-hover:-translate-x-1" />
            Back home
          </Link>

          <span
            className="
              font-jakarta
              text-sm
              font-semibold
              tracking-[-0.02em]
              text-white
              md:text-black
            "
          >
            Cosmos
          </span>
        </div>

        {/* =======================================================
            MAIN LAYOUT
            ======================================================= */}
        <div
          className="
            grid
            flex-1
            grid-cols-1
            items-center
            py-10
            md:grid-cols-2
            md:gap-0
            lg:py-6
          "
        >
          {/* =====================================================
              LEFT — AUTH FORM
              ===================================================== */}
          <motion.section
            initial={{ opacity: 0, x: -32 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{
              duration: 0.7,
              ease: [0.22, 1, 0.36, 1],
              delay: 0.18,
            }}
            className="
              flex
              items-center
              justify-center
              md:pr-8
              lg:pr-12
            "
          >
            <div className="w-full max-w-[440px]">
              {/* Mode tabs */}
              <div
                className="
                  mb-8
                  grid
                  w-full
                  grid-cols-2
                  gap-1
                  rounded-xl
                  border
                  border-border
                  bg-surface-2
                  p-1
                "
              >
                {(["signin", "signup"] as const).map((m) => (
                  <button
                    key={m}
                    type="button"
                    onClick={() => switchMode(m)}
                    className={`h-10 rounded-[10px] font-jakarta text-sm font-semibold transition-all duration-200 ${
                      mode === m
                        ? "bg-[#1693A7] text-white shadow-[0_6px_20px_rgba(22,147,167,0.25)]"
                        : "text-text-secondary hover:text-white"
                    }`}
                  >
                    {m === "signin" ? "Sign In" : "Sign Up"}
                  </button>
                ))}
              </div>

              {/* Form */}
              <AnimatePresence mode="wait">
                <motion.form
                  key={mode}
                  onSubmit={handleSubmit}
                  initial={{ opacity: 0, y: 18 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -18 }}
                  transition={{
                    duration: 0.35,
                    ease: [0.22, 1, 0.36, 1],
                  }}
                  className="flex flex-col gap-4"
                  noValidate
                >
                  {mode === "signin" ? (
                    <>
                      {/* Email */}
                      <div>
                        <label
                          htmlFor="signin-email"
                          className="
                            mb-1.5
                            block
                            font-jakarta
                            text-sm
                            font-medium
                            text-text-secondary
                          "
                        >
                          Email
                        </label>

                        <div className="relative">
                          <Mail className={fieldIconClass} />

                          <input
                            id="signin-email"
                            name="email"
                            type="email"
                            autoComplete="email"
                            placeholder="you@example.com"
                            className={inputBase}
                            required
                          />
                        </div>
                      </div>

                      {/* Password */}
                      <div>
                        <label
                          htmlFor="signin-password"
                          className="
                            mb-1.5
                            block
                            font-jakarta
                            text-sm
                            font-medium
                            text-text-secondary
                          "
                        >
                          Password
                        </label>

                        <div className="relative">
                          <Lock className={fieldIconClass} />

                          <input
                            id="signin-password"
                            name="password"
                            type={showPassword ? "text" : "password"}
                            autoComplete="current-password"
                            placeholder="Enter your password"
                            className={inputBase}
                            required
                          />

                          <button
                            type="button"
                            onClick={() =>
                              setShowPassword((v) => !v)
                            }
                            aria-label={
                              showPassword
                                ? "Hide password"
                                : "Show password"
                            }
                            className="
                              absolute
                              right-3
                              top-1/2
                              -translate-y-1/2
                              rounded-md
                              p-1.5
                              text-muted
                              transition-colors
                              duration-200
                              hover:text-white
                            "
                          >
                            {showPassword ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </button>
                        </div>
                      </div>
                    </>
                  ) : (
                    <>
                      {/* Name */}
                      <div>
                        <label
                          htmlFor="signup-name"
                          className="
                            mb-1.5
                            block
                            font-jakarta
                            text-sm
                            font-medium
                            text-text-secondary
                          "
                        >
                          Name
                        </label>

                        <div className="relative">
                          <User className={fieldIconClass} />

                          <input
                            id="signup-name"
                            name="name"
                            type="text"
                            autoComplete="name"
                            placeholder="Enter your name"
                            className={inputBase}
                            required
                          />
                        </div>
                      </div>

                      {/* Email */}
                      <div>
                        <label
                          htmlFor="signup-email"
                          className="
                            mb-1.5
                            block
                            font-jakarta
                            text-sm
                            font-medium
                            text-text-secondary
                          "
                        >
                          Email
                        </label>

                        <div className="relative">
                          <Mail className={fieldIconClass} />

                          <input
                            id="signup-email"
                            name="email"
                            type="email"
                            autoComplete="email"
                            placeholder="you@example.com"
                            className={inputBase}
                            required
                          />
                        </div>
                      </div>

                      {/* Password */}
                      <div>
                        <label
                          htmlFor="signup-password"
                          className="
                            mb-1.5
                            block
                            font-jakarta
                            text-sm
                            font-medium
                            text-text-secondary
                          "
                        >
                          Password
                        </label>

                        <div className="relative">
                          <Lock className={fieldIconClass} />

                          <input
                            id="signup-password"
                            name="password"
                            type={showPassword ? "text" : "password"}
                            autoComplete="new-password"
                            placeholder="Create a password"
                            className={inputBase}
                            required
                          />

                          <button
                            type="button"
                            onClick={() =>
                              setShowPassword((v) => !v)
                            }
                            aria-label={
                              showPassword
                                ? "Hide password"
                                : "Show password"
                            }
                            className="
                              absolute
                              right-3
                              top-1/2
                              -translate-y-1/2
                              rounded-md
                              p-1.5
                              text-muted
                              transition-colors
                              duration-200
                              hover:text-white
                            "
                          >
                            {showPassword ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </button>
                        </div>
                      </div>

                      {/* Confirm password */}
                      <div>
                        <label
                          htmlFor="signup-confirm"
                          className="
                            mb-1.5
                            block
                            font-jakarta
                            text-sm
                            font-medium
                            text-text-secondary
                          "
                        >
                          Confirm Password
                        </label>

                        <div className="relative">
                          <Lock className={fieldIconClass} />

                          <input
                            id="signup-confirm"
                            name="confirmPassword"
                            type={showConfirm ? "text" : "password"}
                            autoComplete="new-password"
                            placeholder="Confirm your password"
                            className={inputBase}
                            required
                          />

                          <button
                            type="button"
                            onClick={() =>
                              setShowConfirm((v) => !v)
                            }
                            aria-label={
                              showConfirm
                                ? "Hide password"
                                : "Show password"
                            }
                            className="
                              absolute
                              right-3
                              top-1/2
                              -translate-y-1/2
                              rounded-md
                              p-1.5
                              text-muted
                              transition-colors
                              duration-200
                              hover:text-white
                            "
                          >
                            {showConfirm ? (
                              <EyeOff className="h-4 w-4" />
                            ) : (
                              <Eye className="h-4 w-4" />
                            )}
                          </button>
                        </div>
                      </div>
                    </>
                  )}

                  {/* Error */}
                  {error && (
                    <motion.p
                      initial={{ opacity: 0, y: -6 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="
                        rounded-lg
                        border
                        border-[#8B1E1E]/40
                        bg-[#2A1212]/60
                        px-3
                        py-2
                        font-jakarta
                        text-xs
                        text-[#FF8A8A]
                      "
                    >
                      {error}
                    </motion.p>
                  )}

                  {success && (
                    <motion.p
                      initial={{ opacity: 0, y: -6 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="
                        rounded-lg
                        border
                        border-[#22C55E]/40
                        bg-[#0A1F12]/60
                        px-3
                        py-2
                        font-jakarta
                        text-xs
                        text-[#86EFAC]
                      "
                    >
                      {success}
                    </motion.p>
                  )}

                  {/* Submit */}
                  <button
                    type="submit"
                    disabled={isSubmitting}
                    className="
                      group
                      mt-1
                      inline-flex
                      h-12
                      w-full
                      items-center
                      justify-center
                      gap-2
                      rounded-xl
                      bg-[#1693A7]
                      font-jakarta
                      text-sm
                      font-extrabold
                      tracking-[-0.01em]
                      text-white
                      shadow-[0_8px_30px_rgba(22,147,167,0.18)]
                      transition-all
                      duration-200
                      ease-out
                      hover:-translate-y-[1px]
                      hover:bg-[#1BAFC5]
                      hover:shadow-[0_10px_35px_rgba(22,147,167,0.30)]
                      active:translate-y-0
                      active:bg-[#117C8D]
                      focus-visible:outline-none
                      focus-visible:ring-2
                      focus-visible:ring-[#1693A7]
                      focus-visible:ring-offset-2
                      focus-visible:ring-offset-black
                      disabled:pointer-events-none
                      disabled:opacity-45
                      disabled:shadow-none
                    "
                  >
                    {isSubmitting
                      ? mode === "signin"
                        ? "Signing in…"
                        : "Creating…"
                      : mode === "signin"
                        ? "Sign In"
                        : "Create Account"}

                    {isSubmitting ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <ArrowRight className="h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
                    )}
                  </button>
                </motion.form>
              </AnimatePresence>

              {/* Switch auth mode */}
              <p className="mt-6 text-center font-jakarta text-sm text-text-secondary">
                {mode === "signin" ? (
                  <>
                    Don&apos;t have an account?{" "}
                    <button
                      type="button"
                      onClick={() => switchMode("signup")}
                      className="
                        font-semibold
                        text-[#1693A7]
                        transition-colors
                        duration-200
                        hover:text-[#1BAFC5]
                      "
                    >
                      Sign up
                    </button>
                  </>
                ) : (
                  <>
                    Already have an account?{" "}
                    <button
                      type="button"
                      onClick={() => switchMode("signin")}
                      className="
                        font-semibold
                        text-[#1693A7]
                        transition-colors
                        duration-200
                        hover:text-[#1BAFC5]
                      "
                    >
                      Sign in
                    </button>
                  </>
                )}
              </p>
            </div>
          </motion.section>

          {/* =====================================================
              RIGHT — LOADER
              
              Desktop:
              RIGHT HALF IS ALREADY WHITE FROM BACKGROUND SPLIT.
              
              Mobile:
              WHITE BACKGROUND APPEARS BELOW FORM.
              
              Authpagecomponent.tsx IS NOT MODIFIED.
              ===================================================== */}
          <motion.section
            initial={{ opacity: 0, x: 32 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{
              duration: 0.7,
              ease: [0.22, 1, 0.36, 1],
              delay: 0.1,
            }}
            className="
              flex
              min-h-[360px]
              w-full
              items-center
              justify-center
              bg-white
              px-6
              py-10
              md:min-h-[520px]
              md:bg-transparent
              md:px-8
              md:py-0
              lg:min-h-[600px]
              lg:px-12
            "
          >
            {/* Bigger loader */}
            <div
              className="
                flex
                items-center
                justify-center
                scale-[1.5]
                md:scale-[1.8]
                lg:scale-[2.2]
              "
            >
              <Authpagecomponent />
            </div>
          </motion.section>
        </div>
      </motion.div>
    </main>
  );
}