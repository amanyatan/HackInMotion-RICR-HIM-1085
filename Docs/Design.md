# COMUSE Design System

> **Version:** 1.0.0  
> **Status:** Production  
> **Product:** COMUSE — AI Learning Companion   
> **Last Updated:** 2026-08-12

---

# 1. Design Direction

COMUSE is an AI learning companion, not a traditional EdTech dashboard.

The interface should feel:

- Intelligent
- Human
- Calm
- Premium
- Conversational
- Focused
- Slightly editorial
- Technically sophisticated

The visual identity is based on a **dark-first interface** with strong typography, restrained teal accents, subtle surfaces, and purposeful motion.

### Core Principle

> **The interface should disappear when the student needs to focus and become expressive when COMUSE needs to communicate.**

---

# 2. Brand System

## 2.1 Color Palette

### Core Colors

| Token | Value | Usage |
|---|---|---|
| `--color-bg` | `#000000` | Main application background |
| `--color-text` | `#FFFFFF` | Primary text |
| `--color-accent` | `#1693A7` | Primary brand/action color |

### Surface Colors

```css
--color-bg: #000000;
--color-surface-1: #080808;
--color-surface-2: #0D0D0D;
--color-surface-3: #141414;
--color-surface-hover: #181818;
Text Colors
--color-text: #FFFFFF;
--color-text-secondary: #B3B3B3;
--color-text-muted: #737373;
--color-text-disabled: #4A4A4A;
Accent Colors
--color-accent: #1693A7;
--color-accent-hover: #1BAFC5;
--color-accent-active: #117C8D;
--color-accent-soft: rgba(22, 147, 167, 0.12);
--color-accent-border: rgba(22, 147, 167, 0.45);
Semantic Colors
--color-success: #22C55E;
--color-warning: #F59E0B;
--color-error: #EF4444;
--color-info: #3B82F6;
Border Colors
--color-border: #222222;
--color-border-hover: #333333;
--color-border-subtle: #171717;
3. Color Usage Rules
Background

Use #000000 for:

Main pages
Study Mode
Full-screen AI experiences
Surface

Use dark surfaces to create hierarchy:

#000000
   ↓
#080808
   ↓
#0D0D0D
   ↓
#141414

Do not use random shades of gray.

Accent

#1693A7 is reserved for:

Primary CTA
Active navigation
Progress indicators
Focus states
Important AI states
Selected elements
Links where appropriate

Do not make every element teal.

4. Typography

COMUSE uses three typefaces.

4.1 Sora

Role: Headings and structural typography.

Use for:

Hero headings
Page titles
Section headings
Dashboard headings
Important numbers
Available weights
400 — Regular
500 — Medium
600 — SemiBold
700 — Bold

Default heading weight:

600

Hero/display weight:

600–700
5. Plus Jakarta Sans

Role: Interface and readable content.

Use for:

Body text
Buttons
Navigation
Forms
Cards
AI responses
Metadata
Labels
Available weights
400 — Regular
500 — Medium
600 — SemiBold
700 — Bold

Default body weight:

400

UI labels:

500–600
6. Instrument Serif

Role: Editorial emphasis and personality.

Use sparingly for:

Hero emphasis
Emotional statements
Important phrases
Brand storytelling
Selected words inside headings

Example:

Learn smarter.
Learn with COMUSE.

Only selected words should use Instrument Serif.

Rule
Sora
→ Structure

Plus Jakarta Sans
→ Interface + readability

Instrument Serif
→ Personality + emphasis

Never use Instrument Serif for:

Buttons
Navigation
Form labels
Body paragraphs
Dense data
Technical information
7. Typography Scale
Desktop
Element	Size	Line Height	Weight
Display	72px	76px	600
H1	56px	62px	600
H2	44px	50px	600
H3	32px	38px	600
H4	24px	30px	600
Body Large	20px	30px	400
Body	16px	26px	400
Body Small	14px	22px	400
Caption	12px	18px	500
Tablet
Element	Size
Display	60px
H1	48px
H2	38px
H3	28px
H4	22px
Body	16px
Mobile
Element	Size	Line Height
Display	44px	48px
H1	36px	42px
H2	30px	36px
H3	24px	30px
H4	20px	26px
Body Large	18px	28px
Body	16px	25px
Body Small	14px	21px
Caption	12px	18px
Mobile Rule

Never allow large headings to create horizontal overflow.

Use:

font-size: clamp(...);

for responsive display typography where appropriate.

8. Responsive Breakpoints

Use Tailwind-compatible breakpoints.

Mobile:
< 640px

Small Tablet:
640px – 767px

Tablet:
768px – 1023px

Desktop:
1024px – 1279px

Large Desktop:
1280px+
Tailwind
sm: 640px
md: 768px
lg: 1024px
xl: 1280px
2xl: 1536px
9. Container System
Desktop
Maximum width: 1280px
Horizontal padding: 32px
Tablet
Maximum width: 100%
Horizontal padding: 24px
Mobile
Horizontal padding: 16px
Large Screens

Content should not stretch indefinitely.

Use:

max-width: 1280px;
margin-inline: auto;
10. Spacing System

Use a 4px base unit.

4px   → 1
8px   → 2
12px  → 3
16px  → 4
20px  → 5
24px  → 6
32px  → 8
40px  → 10
48px  → 12
64px  → 16
80px  → 20
96px  → 24
128px → 32
Common Usage
Input padding:       12–16px
Card padding:        20–24px
Component gap:       12–24px
Section gap:         64–96px
Hero spacing:        96–160px
Mobile section gap:  48–64px

Do not introduce arbitrary spacing values without reason.

11. Grid
Desktop

Use a 12-column grid.

Columns: 12
Gap: 24px
Tablet
Columns: 8
Gap: 20px
Mobile
Columns: 4
Gap: 16px
12. Border Radius
--radius-sm: 8px;
--radius-md: 12px;
--radius-lg: 16px;
--radius-xl: 20px;
--radius-2xl: 24px;
--radius-pill: 9999px;
Usage
Inputs:       10–12px
Buttons:      10–12px
Cards:        16–20px
Large panels: 20–24px
Pills:        9999px

Do not round every element.

13. Borders

Default:

border: 1px solid #222222;

Hover:

border-color: #333333;

Active:

border-color: #1693A7;

Focus:

border-color: #1693A7;

Use subtle borders instead of heavy shadows whenever possible.

14. Shadows

COMUSE uses minimal shadows.

--shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.25);
--shadow-md: 0 8px 24px rgba(0, 0, 0, 0.35);
--shadow-lg: 0 16px 48px rgba(0, 0, 0, 0.45);

Use shadows for:

Dropdowns
Modals
Floating panels
Elevated interactive surfaces

Do not use shadows on every card.

15. Button System
Sizes
Small
Height: 36px
Horizontal padding: 14px
Font: 13px
Radius: 8px
Medium
Height: 44px
Horizontal padding: 18px
Font: 14px
Radius: 10px
Large
Height: 52px
Horizontal padding: 24px
Font: 16px
Radius: 12px
Mobile

Primary actions should generally use:

Height: 48px+
16. Button Variants
Primary
Background: #1693A7
Text: #FFFFFF
Hover
Background: #1BAFC5
Transform: translateY(-1px)
Active
Background: #117C8D
Transform: translateY(0)
Disabled
Opacity: 0.45
Cursor: not-allowed
Transform: none
Secondary
Background: transparent
Border: #333333
Text: #FFFFFF
Hover
Background: #0D0D0D
Border: #555555
Active
Background: #141414
Ghost
Background: transparent
Text: #A3A3A3
Hover
Background: #0D0D0D
Text: #FFFFFF
17. Button Interaction Rules

Every button must have:

Default
Hover
Focus
Active
Disabled
Loading
Loading

The button should maintain its width while loading.

Example:

Generate Plan
     ↓
[ Spinner ] Generating...

Do not cause layout shift.

18. Input System
Input Sizes
Small
Height: 36px
Medium
Height: 44px
Large
Height: 52px

Default application input:

Height: 48px
19. Input States
Default
Background: #080808
Border: #222222
Text: #FFFFFF
Hover
Border: #333333
Focus
Border: #1693A7
Box-shadow: 0 0 0 3px rgba(22,147,167,0.15)
Error
Border: #EF4444
Disabled
Opacity: 0.5
Cursor: not-allowed
20. Cards
Default Card
Background: #080808
Border: #222222
Radius: 16px
Padding: 24px
Hover

Only interactive cards should hover.

Border: #333333
Background: #0D0D0D
Transform: translateY(-2px)

Transition:

150–200ms

Do not animate static cards.

21. Navigation
Desktop

Height:

64–72px

Navigation should contain:

Logo
Primary navigation
Secondary actions
Profile
Nav Item

Default:

Color: #737373

Hover:

Color: #FFFFFF
Background: #0D0D0D

Active:

Color: #FFFFFF
Background: rgba(22,147,167,0.12)
22. Mobile Navigation

Mobile navigation should not attempt to replicate desktop navigation.

Recommended:

Top:
Logo + Profile/Menu

Bottom:
Primary navigation

Bottom navigation height:

64–72px

Touch targets:

Minimum 44px
23. Modal
Desktop
Width: 480–640px
Padding: 24–32px
Radius: 20–24px
Mobile
Width: calc(100% - 32px)
Padding: 20px
Radius: 20px
Overlay
background: rgba(0, 0, 0, 0.72);
backdrop-filter: blur(8px);

Modal animation:

Opacity: 0 → 1
Scale: 0.96 → 1
Duration: 180–220ms
24. Toast / Notification
Desktop

Position:

Top-right
24px from viewport edges
Mobile

Position:

Top
16px from edges

Width:

Desktop: 320–420px
Mobile: calc(100% - 32px)

States:

Success
Error
Warning
Info
25. AI Interface

COMUSE AI has five visual states.

Idle
Minimal presence
No distracting animation
Listening
Accent indicator
Subtle pulse
Microphone state visible
Thinking
Subtle loading animation
No excessive spinner
Speaking
Voice activity visualization
Playback controls
Error
Clear explanation
Retry action
Text fallback
26. Voice Interface

Voice controls should have a minimum:

44px × 44px

Recommended primary microphone control:

64px × 64px
Microphone states
Idle
Hover
Listening
Processing
Disabled
Error
Listening

Use the accent color:

#1693A7

with subtle animation.

Never use aggressive flashing animations.

27. Learning Interview

The Learning Interview is COMUSE's signature onboarding experience.

Instead of a long traditional form:

Login
 ↓
Meet COMUSE
 ↓
Conversation
 ↓
Learning Profile
 ↓
Assessment
 ↓
Personalized Plan
Question UI

Desktop:

Max width: 720px

Mobile:

Width: 100%
Padding: 16px

The question should remain the dominant element.

User response options:

Voice
Text
Quick choices
Skip
Edit
28. Study Dashboard

The dashboard must answer:

What should I study right now?

Priority
1. Today's session
2. Progress
3. Weak areas
4. Upcoming sessions
5. Recommendations
Desktop

Recommended layout:

┌───────────────────────────────┐
│ Today's Goal                  │
├───────────────────┬───────────┤
│ Next Session      │ Progress │
├───────────────────┴───────────┤
│ Study Plan                    │
├───────────────────────────────┤
│ Weak Areas / Insights         │
└───────────────────────────────┘
Mobile

Stack vertically:

Today's Goal
↓
Next Session
↓
Progress
↓
Weak Areas
↓
Study Plan
29. Progress System

Progress bars:

Height: 6–8px
Radius: 9999px

Track:

Background: #222222

Progress:

#1693A7
Progress states
0%
25%
50%
75%
100%

Avoid unnecessary animation on every page load.

Animate progress when the value actually changes.

30. Study Mode

Study Mode should be visually minimal.

Desktop
Current topic
      ↓
Main learning area
      ↓
Timer + progress
      ↓
Controls
Mobile

Prioritize:

Topic
Timer
Current task
AI action
Finish

Do not overload Study Mode with analytics.

31. Camera / Focus Monitoring

If MediaPipe monitoring is active:

Camera Active

must always be visible.

Provide:

Pause monitoring
Stop camera
Permission status

Never activate the camera silently.

Never imply that the system is monitoring something it cannot actually detect.

32. Assessment

Assessment should have a distraction-free layout.

Desktop
Max content width: 760px
Mobile
Full width
16px padding

Question:

24–28px desktop
20–24px mobile

Answer option minimum height:

48px
Answer states
Default
Hover
Selected
Correct
Incorrect
Disabled
33. Study Plan

Each session should display:

Date
Topic
Duration
Priority
Status

Status variants:

Upcoming
In Progress
Completed
Missed
Rescheduled

Interactive session hover:

Background: #0D0D0D
Border: #333333
34. Adaptive Replanning

When COMUSE changes a plan, the change should be visible.

Example:

Plan Updated

Your assessment showed difficulty
with Dynamic Programming.

Tomorrow's schedule has been adjusted.

Use a clear visual explanation.

Do not silently modify important learning plans.

35. Empty States

Every major screen needs an intentional empty state.

Example:

No learning goal yet.

Tell COMUSE what you want to learn
and we'll build your first plan.

[Start Learning]

Empty states should contain:

Context
Explanation
Primary action
36. Loading States

Use skeletons for content-heavy pages.

Skeleton rules
Match the final component dimensions.
Avoid excessive animation.
Use subtle opacity animation.
Do not show skeletons for extremely fast operations.
AI generation

Use meaningful states:

Understanding your goal...
Analyzing your knowledge...
Building your study plan...

This is preferable to a generic:

Loading...
37. Error States

Errors must be actionable.

Bad:

Error 500

Good:

We couldn't generate your study plan.

Your information is safe.
Try again in a moment.

[Retry]

Existing user data should never disappear because of an API failure.

38. Animation System
Duration Tokens
Fast:     100ms
Quick:    150ms
Standard: 200ms
Smooth:   300ms
Emphasis: 500ms
Complex:  700–1000ms
Easing

Default:

ease-out

For UI:

cubic-bezier(0.22, 1, 0.36, 1)

Avoid excessive bouncing.

39. Animation Responsibilities
GSAP

Use for:

Landing page hero
Scroll sequences
Complex timelines
Large visual transitions
Framer Motion

Use for:

Component transitions
Modals
Dropdowns
Presence animations
Micro interactions
Lenis

Use for:

Smooth scrolling
Rule

One animation should have one owner.

Do not unnecessarily animate the same property with GSAP and Framer Motion simultaneously.

40. Reduced Motion

Respect:

@media (prefers-reduced-motion: reduce)

When enabled:

Disable decorative animations.
Remove parallax.
Reduce transition duration.
Keep essential state changes visible.

Functionality must never depend on animation.

41. Z-Index System

Use a controlled scale.

Base:       0
Content:    1
Sticky:     10
Dropdown:   20
Header:     30
Overlay:    40
Modal:      50
Toast:      60
Critical:   70

Do not randomly use:

z-index: 99999;
42. Iconography

Use:

Lucide React

Rules:

Use consistent icon size.
Do not mix unrelated icon libraries.
Icons should support meaning, not replace labels where clarity is required.
Sizes
12px — metadata
16px — inline
20px — standard UI
24px — navigation
32px — feature icon

Default stroke:

1.75–2px
43. Mobile Touch Rules

Minimum interactive target:

44 × 44px

Preferred:

48 × 48px

Do not place critical controls too close together.

Minimum recommended spacing:

8px

between adjacent touch targets.

44. Accessibility

Required:

Semantic HTML
Keyboard navigation
Visible focus state
Screen reader labels
Sufficient contrast
Reduced-motion support
Accessible form labels
Text alternatives for voice
Camera/microphone permission clarity
Focus

Use:

outline: 2px solid #1693A7;
outline-offset: 2px;

Never remove focus indicators without replacement.

45. Performance Rules

Design decisions must not create unnecessary performance cost.

Avoid:

Huge background videos
Excessive blur
Hundreds of simultaneous animations
Unoptimized images
Continuous animation when idle
Heavy effects on mobile
Mobile Priority

If an effect significantly impacts mobile performance:

Desktop → full effect
Mobile → reduced effect

Visual quality should degrade gracefully.

46. Component Rules

Before creating a component:

Check existing components.
Reuse existing variants.
Use design tokens.
Follow responsive rules.
Add interaction states.
Add loading/error states where required.
Keep the component composable.

Do not duplicate components with slightly different styling.

47. Required Component States

Interactive components should support:

Default
Hover
Focus
Active
Disabled
Loading
Error
Success

Not every component requires every state, but state behavior must be intentionally defined.

48. Design Tokens

All reusable design values should be centralized.

Recommended implementation:

frontend/
└── src/
    └── styles/
        └── tokens.css

Example:

:root {
  --color-bg: #000000;
  --color-text: #FFFFFF;
  --color-accent: #1693A7;

  --color-surface-1: #080808;
  --color-surface-2: #0D0D0D;
  --color-surface-3: #141414;

  --color-border: #222222;

  --radius-sm: 8px;
  --radius-md: 12px;
  --radius-lg: 16px;
  --radius-xl: 20px;
  --radius-2xl: 24px;

  --transition-fast: 100ms;
  --transition-standard: 200ms;
  --transition-smooth: 300ms;
}

Components must consume these tokens.

49. Page-Specific Rules
Landing

Goal:

Create curiosity → Explain COMUSE → Drive interaction

Use stronger animation and editorial typography.

Login

Goal:

Fast → Clear → Trustworthy

Avoid unnecessary animation.

Learning Interview

Goal:

Conversation → Understanding

AI should be the primary visual focus.

Assessment

Goal:

Focus → Answer → Feedback

Minimize distractions.

Dashboard

Goal:

Understand → Decide → Study

The next recommended action should be obvious.

Study Mode

Goal:

Focus → Learn → Complete

Remove unnecessary navigation and analytics.

AI Tutor

Goal:

Ask → Understand → Continue Learning

Conversation should remain readable and contextual.

50. Design QA Checklist

Before shipping any screen:

Visual
 Correct background
 Correct typography
 Correct color tokens
 Correct spacing
 Correct radius
 Correct borders
 No random colors
 No random fonts
Interaction
 Hover state
 Focus state
 Active state
 Disabled state
 Loading state
 Error state
Responsive
 320px mobile
 375px mobile
 390px mobile
 430px mobile
 Tablet
 1024px desktop
 1280px desktop
 1440px desktop
 1536px+ desktop
Accessibility
 Keyboard navigation
 Focus indicators
 Accessible labels
 Contrast
 Reduced motion
 Voice fallback
Performance
 No unnecessary animation
 No layout shift
 Optimized images
 Mobile effects tested
 No excessive blur
 No unnecessary dependencies
51. Final Design Rule

COMUSE should not look like another generic AI dashboard.

It should feel like:

A dark, intelligent, personal learning companion that understands the student and adapts around them.

The design system prioritizes:

Human connection
      ↓
Clarity
      ↓
Learning focus
      ↓
AI intelligence
      ↓
Visual personality

Every design decision should reinforce these principles.