---
name: Public Trust & Integrity
colors:
  surface: '#f8f9fa'
  surface-dim: '#d9dadb'
  surface-bright: '#f8f9fa'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f3f4f5'
  surface-container: '#edeeef'
  surface-container-high: '#e7e8e9'
  surface-container-highest: '#e1e3e4'
  on-surface: '#191c1d'
  on-surface-variant: '#424752'
  inverse-surface: '#2e3132'
  inverse-on-surface: '#f0f1f2'
  outline: '#727783'
  outline-variant: '#c2c6d4'
  surface-tint: '#165db2'
  primary: '#003e7f'
  on-primary: '#ffffff'
  primary-container: '#0055aa'
  on-primary-container: '#b3cdff'
  inverse-primary: '#aac7ff'
  secondary: '#b81d2d'
  on-secondary: '#ffffff'
  secondary-container: '#ff535a'
  on-secondary-container: '#5b000d'
  tertiary: '#043f7c'
  on-tertiary: '#ffffff'
  tertiary-container: '#2a5795'
  on-tertiary-container: '#b3ceff'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#d6e3ff'
  primary-fixed-dim: '#aac7ff'
  on-primary-fixed: '#001b3e'
  on-primary-fixed-variant: '#00458d'
  secondary-fixed: '#ffdad8'
  secondary-fixed-dim: '#ffb3b0'
  on-secondary-fixed: '#410007'
  on-secondary-fixed-variant: '#92001b'
  tertiary-fixed: '#d6e3ff'
  tertiary-fixed-dim: '#a8c8ff'
  on-tertiary-fixed: '#001b3d'
  on-tertiary-fixed-variant: '#134684'
  background: '#f8f9fa'
  on-background: '#191c1d'
  surface-variant: '#e1e3e4'
typography:
  headline-xl:
    fontFamily: Public Sans
    fontSize: 40px
    fontWeight: '700'
    lineHeight: 52px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Public Sans
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 42px
    letterSpacing: -0.01em
  headline-lg-mobile:
    fontFamily: Public Sans
    fontSize: 28px
    fontWeight: '700'
    lineHeight: 36px
  headline-md:
    fontFamily: Public Sans
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  headline-sm:
    fontFamily: Public Sans
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Public Sans
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Public Sans
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-md:
    fontFamily: Public Sans
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
  caption:
    fontFamily: Public Sans
    fontSize: 12px
    fontWeight: '400'
    lineHeight: 16px
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 8px
  sm: 16px
  md: 24px
  lg: 48px
  xl: 80px
  gutter: 24px
  margin-mobile: 16px
  container-max: 1200px
---

## Brand & Style

The design system is rooted in the principles of public service: reliability, transparency, and accessibility. It translates the official heritage of the Republic of Korea into a modern digital language that feels authoritative yet approachable. 

The aesthetic follows a **Corporate / Modern** direction with a focus on high-utility minimalism. It prioritizes clarity over decoration, ensuring that citizens of all demographics can navigate complex administrative tasks without cognitive friction. The interface leverages expansive white space to reduce visual noise, allowing critical data and instructions to take center stage.

## Colors

The palette is anchored by the "Government Symbol Blue" (#0055aa), representing trust and future-oriented stability. The "Government Symbol Red" (#cd2e3a) is used sparingly as a secondary accent to denote urgency or critical actions, maintaining a patriotic and official tone.

- **Backgrounds:** Use pure white (#ffffff) for primary content areas and Light Gray (#f8f9fa) for section backgrounds and surface grouping.
- **Contrast:** Strictly adhere to WCAG 2.1 Level AA standards. All text against colored backgrounds must maintain a minimum contrast ratio of 4.5:1.
- **Functional Colors:** Success (Green), Warning (Amber), and Error (Red) should be calibrated to remain distinct from the primary brand red.

## Typography

The design system utilizes **Public Sans** (as a high-accessibility substitute for Pretendard/NanumSquare styles) to ensure legibility across all digital touchpoints. It is a neutral, humanist sans-serif that excels in data-heavy environments.

- **Hierarchy:** Use bold weights (700) for primary headlines to establish clear entry points.
- **Paragraphs:** Standard body text should never fall below 16px to ensure accessibility for elderly users.
- **Optimization:** For Korean language implementation, use `-0.02em` letter-spacing for headlines to improve readability and visual density.

## Layout & Spacing

A disciplined **12-column fixed grid** is used for desktop layouts to create a sense of order and institutional reliability. 

- **Desktop (1200px+):** 12 columns with 24px gutters. Center the container to provide generous whitespace margins.
- **Tablet (768px - 1199px):** 8 columns with 20px gutters and 24px side margins.
- **Mobile (< 767px):** 4 columns with 16px gutters and 16px side margins.
- **Rhythm:** All vertical spacing should be a multiple of 4px. Use `lg` (48px) and `xl` (80px) spacing to separate major content sections, ensuring the layout feels open and uncrowded.

## Elevation & Depth

To maintain a professional and "flat" institutional look, the design system avoids heavy shadows. Instead, it uses **Tonal Layers** and **Low-Contrast Outlines**.

- **Surfaces:** Use subtle 1px borders (#dee2e6) to define cards and containers rather than shadows.
- **Elevation levels:**
    - **Level 0 (Base):** Light gray background (#f8f9fa).
    - **Level 1 (Card):** White background (#ffffff) with a 1px solid border.
    - **Level 2 (Interaction):** Very soft, diffused shadow (0px 4px 12px rgba(0, 0, 0, 0.05)) only used for floating elements like dropdowns or modals to indicate they sit above the base plane.

## Shapes

The shape language is **Soft (0.25rem / 4px)**. This subtle rounding provides a modern touch without sacrificing the formal, structured feel necessary for government communications.

- **Buttons & Inputs:** Use the 4px base radius for a crisp, professional look.
- **Large Containers:** Use `rounded-lg` (8px) for cards and modals to slightly soften the overall interface.
- **Icons:** Use 24px bounding boxes with a 2px stroke weight. Avoid filled shapes unless indicating an "active" state; use clean, open lines to maintain the "airy" layout philosophy.

## Components

### Buttons
- **Primary:** Solid #0055aa background with #ffffff text. 4px border radius.
- **Secondary:** White background with #0055aa 1px border and text.
- **States:** Hover states should darken the background by 10%. Focus states must show a 2px offset outline for accessibility.

### Input Fields
- **Style:** 1px border (#ced4da) with 4px radius. Labels must be placed above the field for maximum readability.
- **Active State:** Border color changes to Primary Blue (#0055aa) with a subtle 2px glow.

### Cards
- **Standard Card:** White background, 1px border, 8px corner radius. Used for grouping related content (e.g., news items, service links).
- **Interactive Card:** Includes a subtle hover lift or background color change to #f1f3f5.

### Chips & Tags
- Used for status indicators (e.g., "In Progress," "Completed"). Use high-contrast background tints with bold labels.

### Data Visualization
- **Charts:** Use a palette derived from the primary blue, supplemented by neutral grays. 
- **Maps:** Use simplified boundaries with the Primary Blue used for selected regions or data points. Ensure ample padding around visualization containers.