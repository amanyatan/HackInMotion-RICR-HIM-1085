import type { Metadata } from 'next';
import { Sora, Plus_Jakarta_Sans, Instrument_Serif } from 'next/font/google';
import StyledComponentsRegistry from '@/lib/styled-components-registry';
import '@/app/globals.css';

const sora = Sora({
  subsets: ['latin'],
  variable: '--font-sora',
  weight: ['400', '500', '600', '700'],
});

const plusJakartaSans = Plus_Jakarta_Sans({
  subsets: ['latin'],
  variable: '--font-jakarta',
  weight: ['400', '500', '600', '700'],
});

const instrumentSerif = Instrument_Serif({
  subsets: ['latin'],
  variable: '--font-serif',
  weight: ['400'],
  style: 'normal',
});

export const metadata: Metadata = {
  title: 'COSMOS',
  description: 'COSMOS — AI Learning Companion',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className={`${sora.variable} ${plusJakartaSans.variable} ${instrumentSerif.variable}`}>
      <body>
        <StyledComponentsRegistry>{children}</StyledComponentsRegistry>
      </body>
    </html>
  );
}