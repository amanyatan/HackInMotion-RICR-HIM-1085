"use client";

import { motion, useReducedMotion } from "framer-motion";
import Image from "next/image";
import Link from "next/link";
import Spline from "@splinetool/react-spline";

const MotionLink = motion(Link);

export default function LandingPage() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <main className="relative min-h-screen overflow-hidden bg-black text-white">
      {/* =========================================================
          SPLINE — FULL HERO BACKGROUND
      ========================================================= */}
      <div className="absolute inset-0 z-0">
        <Spline
          scene="/scene-splinecode.splinecode"
          className="h-full w-full"
        />
      </div>

      {/* =========================================================
          READABILITY OVERLAY
          Keeps the Spline visible while making the left text readable.
      ========================================================= */}
      <div
        className="
          pointer-events-none
          absolute inset-0 z-[1]
          bg-[linear-gradient(90deg,rgba(0,0,0,0.98)_0%,rgba(0,0,0,0.88)_28%,rgba(0,0,0,0.45)_52%,rgba(0,0,0,0.08)_78%,rgba(0,0,0,0)_100%)]
        "
      />

      {/* Subtle bottom protection for mobile / viewport edges */}
      <div
        className="
          pointer-events-none
          absolute inset-x-0 bottom-0 z-[1]
          h-40
          bg-[linear-gradient(0deg,rgba(0,0,0,0.65),transparent)]
        "
      />

      {/* =========================================================
          NAVBAR
      ========================================================= */}
      <header className="absolute inset-x-0 top-0 z-30">
        <nav
          className="
            mx-auto flex
            h-20
            max-w-[1280px]
            items-center
            justify-between
            px-5
            sm:px-6
            lg:px-8
          "
        >
          {/* LOGO */}
          <motion.div
            initial={shouldReduceMotion ? false : { opacity: 0, y: -10 }}
            animate={
              shouldReduceMotion
                ? { opacity: 1 }
                : { opacity: 1, y: 0 }
            }
            transition={{
              duration: shouldReduceMotion ? 0 : 0.5,
              ease: [0.22, 1, 0.36, 1],
            }}
            className="flex items-center gap-3"
          >
            <div className="relative h-9 w-9 shrink-0 sm:h-10 sm:w-10">
              <Image
                src="/Comus.svg"
                alt="Cosmos"
                fill
                priority
                className="object-contain"
              />
            </div>

            <span
              className="
                font-jakarta
                text-[17px]
                font-semibold
                tracking-[-0.02em]
                text-white
                sm:text-lg
              "
            >
              Cosmos
            </span>
          </motion.div>

          {/* GET STARTED */}
          <div className="flex items-center gap-3">
            <MotionLink
              href="/study"
              initial={shouldReduceMotion ? false : { opacity: 0, y: -10 }}
              animate={shouldReduceMotion ? { opacity: 1 } : { opacity: 1, y: 0 }}
              transition={{
                duration: shouldReduceMotion ? 0 : 0.5,
                delay: shouldReduceMotion ? 0 : 0.05,
                ease: [0.22, 1, 0.36, 1],
              }}
              className="
                inline-flex h-11 items-center justify-center rounded-[10px]
                border border-border px-5 font-jakarta text-sm font-semibold
                tracking-[-0.01em] text-white transition-all duration-200 ease-out
                hover:border-border-hover hover:bg-surface-hover sm:h-12 sm:px-6
              "
            >
              Study Mode
            </MotionLink>

            <MotionLink
              href="/login"
              initial={shouldReduceMotion ? false : { opacity: 0, y: -10 }}
              animate={
                shouldReduceMotion
                  ? { opacity: 1 }
                  : { opacity: 1, y: 0 }
              }
              transition={{
                duration: shouldReduceMotion ? 0 : 0.5,
                delay: shouldReduceMotion ? 0 : 0.1,
                ease: [0.22, 1, 0.36, 1],
              }}
              className="
                inline-flex
                h-11
                items-center
                justify-center
                rounded-[10px]
                bg-[#1693A7]
                px-5
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

                sm:h-12
                sm:px-6
              "
            >
              Get Started
            </MotionLink>
          </div>
        </nav>
      </header>

      {/* =========================================================
          HERO CONTENT
      ========================================================= */}
      <section
        className="
          relative
          z-10
          flex
          min-h-screen
          items-center
        "
      >
        <div
          className="
            mx-auto
            w-full
            max-w-[1280px]
            px-5
            pb-16
            pt-28
            sm:px-6
            lg:px-8
          "
        >
          <motion.div
            initial={
              shouldReduceMotion
                ? false
                : {
                    opacity: 0,
                    y: 24,
                  }
            }
            animate={
              shouldReduceMotion
                ? { opacity: 1 }
                : {
                    opacity: 1,
                    y: 0,
                  }
            }
            transition={{
              duration: shouldReduceMotion ? 0 : 0.8,
              delay: shouldReduceMotion ? 0 : 0.15,
              ease: [0.22, 1, 0.36, 1],
            }}
            className="
              w-full
              lg:max-w-[700px]
            "
          >
            {/* EYEBROW */}
            <p
              className="
                font-jakarta
                text-xs
                font-medium
                uppercase
                tracking-[0.34em]
                text-[#B3B3B3]
                sm:text-sm
              "
            >
              Trust me.
            </p>

            {/* HERO HEADING */}
            <h1
              className="
                mt-5
                max-w-[760px]
                font-sora
                text-[clamp(3rem,7vw,6.5rem)]
                font-semibold
                leading-[0.88]
                tracking-[-0.065em]
                text-white
              "
            >
              OUR AI CAN{" "}
              <span
                className="
                  font-serif
                  italic
                  font-normal
                  tracking-[-0.055em]
                  text-[#1693A7]
                "
              >
                UNDERSTAND
              </span>{" "}
              YOUR STUDIES
            </h1>

            {/* SUPPORTING COPY */}
            <p
              className="
                mt-7
                max-w-[480px]
                font-jakarta
                text-sm
                leading-6
                text-[#B3B3B3]
                sm:text-base
              "
            >
              A learning companion that understands how you study,
              adapts to your weaknesses, and helps you stay on track.
            </p>
          </motion.div>
        </div>
      </section>
    </main>
  );
}