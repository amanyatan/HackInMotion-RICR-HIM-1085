'use client';

import { motion, useReducedMotion } from 'framer-motion';
import Image from 'next/image';
import Spline from '@splinetool/react-spline';

export default function LandingPage() {
  const shouldReduceMotion = useReducedMotion();

  return (
    <div className="min-h-screen overflow-x-hidden bg-[#000000] text-[#FFFFFF]">
      <header className="relative z-20">
        <nav className="mx-auto flex max-w-[1280px] items-center justify-between px-4 pt-6 sm:px-6 lg:px-8">
          <div className="flex items-center gap-3">
            <div className="relative h-10 w-10 shrink-0">
              <Image src="/Comus.svg" alt="Comuse logo" fill className="object-contain" priority />
            </div>
            <span className="font-jakarta text-lg font-medium tracking-[-0.02em] text-white">Comuse</span>
          </div>

          <button
            type="button"
            className="inline-flex h-12 items-center justify-center rounded-[10px] bg-[#1693A7] px-5 text-sm font-bold text-white shadow-[0_0_0_1px_rgba(22,147,167,0.2)] transition-all duration-200 ease-out hover:-translate-y-[1px] hover:bg-[#1BAFC5] hover:shadow-[0_8px_24px_rgba(22,147,167,0.35)] active:translate-y-0 active:bg-[#117C8D] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-[#1693A7] focus-visible:ring-offset-2 focus-visible:ring-offset-black disabled:cursor-not-allowed disabled:opacity-45 disabled:hover:translate-y-0 sm:h-[48px] sm:px-6"
          >
            Get Started
          </button>
        </nav>
      </header>

      <main className="relative mx-auto flex min-h-[calc(100vh-72px)] max-w-[1280px] items-center px-4 pb-10 pt-4 sm:px-6 lg:px-8 lg:pb-12">
        <div className="grid w-full grid-cols-1 items-center gap-8 lg:grid-cols-12 lg:gap-6">
          <motion.div
            initial={shouldReduceMotion ? false : { opacity: 0, y: 24 }}
            animate={shouldReduceMotion ? { opacity: 1 } : { opacity: 1, y: 0 }}
            transition={{ duration: shouldReduceMotion ? 0 : 0.7, ease: [0.22, 1, 0.36, 1] }}
            className="relative z-10 lg:col-span-6 lg:pr-4"
          >
            <p className="font-jakarta text-sm uppercase tracking-[0.32em] text-[#B3B3B3]">Trust me.</p>

            <h1 className="mt-5 max-w-[620px] text-[clamp(2.75rem,5vw,4.75rem)] font-sora font-semibold leading-[0.95] tracking-[-0.06em] text-white">
              OUR AI CAN{' '}
              <span className="font-serif italic text-[#1693A7]">UNDERSTAND</span>
              <br />
              YOUR STUDIES
            </h1>
          </motion.div>

          <motion.div
            initial={shouldReduceMotion ? false : { opacity: 0, scale: 0.98, y: 20 }}
            animate={shouldReduceMotion ? { opacity: 1 } : { opacity: 1, scale: 1, y: 0 }}
            transition={{
              duration: shouldReduceMotion ? 0 : 0.8,
              ease: [0.22, 1, 0.36, 1],
              delay: shouldReduceMotion ? 0 : 0.12,
            }}
            className="relative lg:col-span-6"
          >
            <div className="pointer-events-none absolute inset-x-10 top-1/2 h-32 -translate-y-1/2 rounded-full bg-[rgba(22,147,167,0.12)] blur-[90px]" />
            <div className="relative mx-auto w-full max-w-[620px]">
              <div className="relative flex items-center justify-center overflow-hidden rounded-[32px] lg:min-h-[620px]">
                <Spline scene="/scene-splinecode.splinecode" className="h-[420px] w-full md:h-[520px] lg:h-[680px]" />
              </div>
            </div>
          </motion.div>
        </div>
      </main>
    </div>
  );
}
