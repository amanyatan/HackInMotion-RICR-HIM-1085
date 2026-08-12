"use client";

export default function GlobalError({ error, reset }: { error: Error & { digest?: string }; reset: () => void }) {
  return (
    <html lang="en">
      <body style={{ backgroundColor: "#000000", color: "#FFFFFF" }}>
        <main className="flex min-h-screen flex-col items-center justify-center bg-black px-6 text-center text-white">
          <p className="font-jakarta text-xs uppercase tracking-[0.34em] text-[#1693A7]">Something went wrong</p>
          <h1 className="mt-4 font-sora text-4xl font-semibold tracking-[-0.04em]">Oops! An unexpected error occurred.</h1>
          <p className="mt-3 max-w-md font-jakarta text-sm leading-6 text-text-secondary">{error.message}</p>
          <button
            type="button"
            onClick={reset}
            className="mt-8 inline-flex h-12 items-center rounded-xl bg-[#1693A7] px-6 font-jakarta text-sm font-extrabold text-white transition-colors duration-200 hover:bg-[#1BAFC5]"
          >
            Try again
          </button>
        </main>
      </body>
    </html>
  );
}