# Quick A/B Test Integration Guide

## ✅ Step 1: Add ABTestSwitcher to Dashboard (2 minutes)

Add these 2 lines to `frontend/src/components/TradingDashboardSimple.tsx`:

### At the top (line 26, after `import { EconomicCalendar }...`):
```tsx
import { ABTestSwitcher } from './ABTestSwitcher';
```

### At the bottom (line 2795, before the closing `</div>`):
```tsx
      {/* A/B Test Switcher */}
      <ABTestSwitcher />
      </div>
```

**That's it!** The switcher will appear as a floating 🧪 button.

---

## ✅ Step 2: Test the Switcher (1 minute)

```bash
cd frontend
npm run dev
```

Open http://localhost:5174/demo and look for the 🧪 A button in bottom-right.

---

## ✅ Step 3: Add Variant Components (Done!)

I'm creating 3 new files:
- `EconomicCalendarVariantB.tsx` (Contextual Expansion)
- `EconomicCalendarVariantC.tsx` (Unified Split View)
- `EconomicCalendarVariantD.tsx` (Timeline Integration)

---

## ✅ Step 4: Add Variant Routing (5 minutes)

In `frontend/src/components/EconomicCalendar.tsx`, add this at the top:

```tsx
import { getTestConfig } from '../config/abTestConfig';
import { EconomicCalendarVariantB } from './EconomicCalendarVariantB';
import { EconomicCalendarVariantC } from './EconomicCalendarVariantC';
import { EconomicCalendarVariantD } from './EconomicCalendarVariantD';
```

Then wrap your existing component:

```tsx
export const EconomicCalendar: React.FC<...> = (props) => {
  const config = getTestConfig();

  // Variant routing
  switch (config.variant) {
    case 'B':
      return <EconomicCalendarVariantB {...props} />;
    case 'C':
      return <EconomicCalendarVariantC {...props} />;
    case 'D':
      return <EconomicCalendarVariantD {...props} />;
    default:
      // Variant A (current implementation)
      return (
        // Your existing JSX here
      );
  }
};
```

---

## 🎯 Testing Each Variant

1. Click the 🧪 button
2. Select a variant (A, B, C, or D)
3. Page reloads with new variant
4. Use the calendar naturally
5. Check metrics in the switcher panel

---

## 📊 View Results

Click the 🧪 button → "Show Detailed Metrics" to see:
- Sessions per variant
- Avg time to action
- Interaction rates
- Engagement scores

Winner = highest engagement score!

