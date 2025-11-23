# GVSES Comprehensive Stock Analysis Widget - Detailed Specification

## Widget Purpose
Create an all-in-one comprehensive stock analysis widget that serves as a conversational bookmark, capturing a complete point-in-time snapshot of market data when the user asks "Analyze [SYMBOL]". This widget combines price data, technical analysis, chart visualization, pattern detection, news, and upcoming events into a single, cohesive card that can be referenced later in conversation history.

---

## Widget Structure (Top to Bottom)

### 1. HEADER SECTION
**Layout**: Horizontal row, center-aligned, with gap spacing of 3

**Components**:
- **Left**: Large title displaying `{company_name} ({symbol})` (e.g., "Apple Inc. (AAPL)")
- **Middle**: Spacer to push content to edges
- **Right**: Small caption showing `{timestamp}` in secondary color (e.g., "Nov 16, 2025 2:30 PM")

---

### 2. PRICE DISPLAY SECTION
**Layout**: Horizontal row, baseline-aligned, with gap spacing of 2

**Components**:
- **Current Price**: Extra-large bold text showing `${price}` (e.g., "$272.41")
- **Price Change**: Semibold text showing `{price_change} ({price_change_percent}%)` (e.g., "+2.15 (+0.79%)")
  - Color: Dynamic based on `{price_change_color}` field
    - Green/success for positive
    - Red/danger for negative
    - Gray/secondary for unchanged
- **Spacer**: Pushes refresh button to right edge
- **Refresh Button**: Ghost variant, small size, with refresh icon
  - Action: `analysis.refresh` with payload `{symbol: symbol}`

**Divider**: 12px spacing

---

### 3. CHART SECTION
**Layout**: Vertical column, gap spacing of 3

**Header Row** (horizontal, center-aligned):
- **Left**: "Price Chart" caption (small, semibold, secondary color)
- **Spacer**: Pushes buttons to right
- **Timeframe Buttons**: Pill-shaped, extra-small size
  - "1D" button - color: `{chart_1d_color}`, variant: `{chart_1d_variant}`
  - "1W" button - color: `{chart_1w_color}`, variant: `{chart_1w_variant}`
  - "1M" button - color: `{chart_1m_color}`, variant: `{chart_1m_variant}`
  - "3M" button - color: `{chart_3m_color}`, variant: `{chart_3m_variant}`
  - "1Y" button - color: `{chart_1y_color}`, variant: `{chart_1y_variant}`
  - Each button action: `chart.setTimeframe` with payload `{symbol: symbol, timeframe: "1D"|"1W"|"1M"|"3M"|"1Y"}`
  - Active button: solid variant with info/primary color
  - Inactive buttons: outline variant with secondary color

**Chart Image**:
- Component: Image with source `{chart_image_url}`
- Alt text: `{symbol} price chart ({chart_timeframe})`
- Aspect ratio: 16:9 (widescreen)
- Border radius: medium (rounded corners)

**Divider**: 12px spacing

---

### 4. QUICK STATS SECTION
**Layout**: Vertical column, gap spacing of 2

**Header**: "Quick Stats" caption (small, semibold, secondary color)

**Stats Row** (horizontal, gap spacing of 4):
- **Open**:
  - Vertical column, gap 1
  - Label: "Open" (extra-small caption, secondary)
  - Value: `${open}` (small text)
- **Volume**:
  - Vertical column, gap 1
  - Label: "Volume" (extra-small caption, secondary)
  - Value: `{volume}` (small text, formatted with commas)
- **Day Range**:
  - Vertical column, gap 1
  - Label: "Day Range" (extra-small caption, secondary)
  - Value: `${day_low} - ${day_high}` (small text)

**Divider**: 12px spacing

---

### 5. TECHNICAL POSITION SECTION
**Layout**: Vertical column, gap spacing of 2

**Header Row** (horizontal, center-aligned):
- **Left**: "Technical Position" caption (small, semibold, secondary)
- **Right**: Badge displaying `{technical_position_label}` (e.g., "Bullish", "Bearish", "Neutral")
  - Color: `{technical_position_color}` (success for bullish, danger for bearish, warning for neutral)
  - Variant: soft (subtle background)
  - Size: small

**Levels Display** (vertical column, gap 1):
Four horizontal rows, each baseline-aligned with gap 2:

1. **QE Level** (Target):
   - Label: "QE" (extra-small caption, secondary, width 40px)
   - Value: `${qe_level}` (small text)
   - Note: "(Target)" (extra-small caption, secondary)

2. **ST Level** (Resistance):
   - Label: "ST" (extra-small caption, secondary, width 40px)
   - Value: `${st_level}` (small text)
   - Note: "(Resistance)" (extra-small caption, secondary)

3. **Current Price** (highlighted):
   - Label: "Now" (extra-small caption, PRIMARY color, BOLD, width 40px)
   - Value: `${price}` (small text, BOLD, PRIMARY color)
   - Note: "(Current)" (extra-small caption, primary color)

4. **LTB Level** (Support):
   - Label: "LTB" (extra-small caption, secondary, width 40px)
   - Value: `${ltb_level}` (small text)
   - Note: "(Support)" (extra-small caption, secondary)

**Divider**: 12px spacing

---

### 6. PATTERN DETECTION SECTION
**Layout**: Vertical column, gap spacing of 2

**Header**: "Pattern Detection" caption (small, semibold, secondary)

**Patterns List**: ListView of `{patterns}` array, limit to top 3 patterns

**Each Pattern Item** (ListViewItem, gap 2, center-aligned):
- **Left**: Circular indicator box (size 8, full radius)
  - Background color: `{pattern_confidence_color}`
    - Green for high confidence (>70%)
    - Yellow/orange for medium (40-70%)
    - Red for low (<40%)
- **Right**: Vertical column (gap 0, flex 1)
  - **Pattern Name**: `{pattern_name}` (small text, medium weight) - e.g., "Ascending Triangle"
  - **Details**: `{pattern_confidence} confidence • {pattern_direction}` (extra-small caption, secondary)
    - Example: "High confidence • Bullish"

**Divider**: 12px spacing

---

### 7. MARKET NEWS SECTION
**Layout**: Vertical column, gap spacing of 2

**Header Row** (horizontal, center-aligned):
- **Left**: "Market News (Top 5)" caption (small, semibold, secondary)
- **Spacer**: Pushes filter buttons to right
- **Source Filter Buttons**: Pill-shaped, extra-small
  - "All Sources" button - color: `{news_filter_all_color}`, variant: `{news_filter_all_variant}`
    - Action: `news.setSource` with payload `{source: "all"}`
  - "CNBC" button - color: `{news_filter_cnbc_color}`, variant: `{news_filter_cnbc_variant}`
    - Action: `news.setSource` with payload `{source: "cnbc"}`
  - "Yahoo" button - color: `{news_filter_yahoo_color}`, variant: `{news_filter_yahoo_variant}`
    - Action: `news.setSource` with payload `{source: "yahoo"}`
  - Active button: solid variant with info color
  - Inactive buttons: outline variant with secondary color

**News List**: ListView of `{news}` array, limit to top 5 articles

**Each News Item** (ListViewItem, gap 2, start-aligned, clickable):
- Click action: `browser.openUrl` with payload `{url: news_url}`
- **Left**: Circular source indicator (size 8, full radius)
  - Background: `{news_source_color}`
    - Blue for CNBC articles
    - Orange for Yahoo Finance articles
- **Right**: Vertical column (gap 1, flex 1)
  - **Headline**: `{news_title}` (small text, semibold weight, max 2 lines)
  - **Metadata Row**: Horizontal, gap 2
    - Source: `{news_source}` (extra-small caption, secondary)
    - Bullet separator: "•" (extra-small caption, secondary)
    - Time: `{news_time_ago}` (extra-small caption, secondary) - e.g., "2 hours ago"

**Footer Row** (horizontal):
- **Spacer**: Pushes button to right
- **More Button**: "More News" label, small size, ghost variant
  - Action: `news.showMore` with payload `{symbol: symbol}`

**Divider**: 12px spacing

---

### 8. UPCOMING EVENTS SECTION
**Layout**: Vertical column, gap spacing of 2

**Header**: "Upcoming Events" caption (small, semibold, secondary)

**Events List**: ListView of `{events}` array, limit to top 2 events

**Each Event Item** (ListViewItem, gap 2, center-aligned):
- **Left**: Circular impact indicator (size 8, full radius)
  - Background: `{event_impact_color}`
    - Red for high-impact events (earnings, FDA decisions)
    - Yellow for medium-impact (conferences, analyst days)
    - Blue for low-impact (minor announcements)
- **Right**: Vertical column (gap 0, flex 1)
  - **Event Name**: `{event_name}` (small text, medium weight) - e.g., "Q4 Earnings Report"
  - **Timing**: `{event_date} ({event_countdown})` (extra-small caption, secondary)
    - Example: "Nov 28, 2025 (12 days away)"

---

## Data Schema Requirements

### Required Top-Level Fields:
- `symbol` (string): Stock ticker
- `company_name` (string): Full company name
- `timestamp` (string): Analysis timestamp
- `price` (string): Current price
- `price_change` (string): Price change amount
- `price_change_percent` (string): Price change percentage
- `price_change_color` (enum: "success" | "danger" | "secondary")
- `chart_image_url` (string, URI): URL to chart snapshot image
- `chart_timeframe` (string): Currently selected timeframe
- Chart button colors/variants (for each timeframe: 1d, 1w, 1m, 3m, 1y)
- `open`, `volume`, `day_low`, `day_high` (strings)
- `technical_position_label` (string: "Bullish" | "Bearish" | "Neutral")
- `technical_position_color` (enum: "success" | "danger" | "warning" | "secondary")
- `qe_level`, `st_level`, `ltb_level` (strings): Price levels

### Array Fields:
- `patterns` (array of objects):
  - `pattern_name` (string)
  - `pattern_confidence` (string: "High" | "Medium" | "Low")
  - `pattern_direction` (string: "Bullish" | "Bearish" | "Neutral")
  - `pattern_confidence_color` (string)

- `news` (array of objects):
  - `news_title` (string)
  - `news_source` (string)
  - `news_time_ago` (string)
  - `news_url` (string, URI)
  - `news_source_color` (string)

- `events` (array of objects):
  - `event_name` (string)
  - `event_date` (string)
  - `event_countdown` (string)
  - `event_impact_color` (string)

### Filter State Fields:
- `news_filter_all_color`, `news_filter_all_variant`
- `news_filter_cnbc_color`, `news_filter_cnbc_variant`
- `news_filter_yahoo_color`, `news_filter_yahoo_variant`

---

## Widget Styling Guidelines
- **Card**: Large size with status indicator ("GVSES Analysis" with chart-line icon)
- **Color Palette**:
  - Success/Green: Bullish indicators, positive price changes
  - Danger/Red: Bearish indicators, negative price changes
  - Warning/Yellow: Neutral positions, medium confidence
  - Info/Blue: Active selections, CNBC news source
  - Secondary/Gray: Inactive states, labels, captions
  - Primary: Current price highlight in technical levels
- **Typography**:
  - Extra-large (xl): Current price only
  - Large (lg): Widget title
  - Medium (md): Default for most content
  - Small (sm): Secondary content, values
  - Extra-small (xs): Labels, captions, metadata
- **Spacing**: Consistent 12px dividers between major sections
- **Interactive Elements**: All buttons use pill shape for modern look

---

## Use Case Example

**User Query**: "Analyze AAPL"

**Widget Output**: A single comprehensive card showing:
- Apple Inc. (AAPL) with timestamp
- Current price $272.41 (+0.79% in green)
- Chart image with 1D selected
- Open $270.50, Volume 52.3M, Range $269.80 - $273.15
- Technical: Bullish badge, price between ST ($275) and LTB ($265)
- Patterns: Ascending Triangle (High confidence, Bullish)
- News: Top 5 articles from CNBC and Yahoo with filtering
- Events: Q4 Earnings (12 days away, high impact)

**Value**: Complete analysis snapshot preserved in conversation history for future reference
