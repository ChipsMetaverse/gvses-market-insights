# TTS Pronunciation Guide for G'sves

## Problem Solved
The agent was reading "$342.50" as "three four two point five zero" instead of "three hundred forty-two dollars and fifty cents".

## Solution Implemented

### Text vs Voice Distinction
The agent now understands:
- **TEXT**: Display numbers as digits for quick scanning
- **VOICE**: Pronounce numbers naturally for listening

### Examples

| Written/Displayed | Spoken/Pronounced |
|------------------|-------------------|
| $342.50 | "three hundred forty-two dollars and fifty cents" |
| $1,234.00 | "one thousand two hundred thirty-four dollars" |
| -1.73% | "down one point seven three percent" |
| +2.5% | "up two point five percent" |
| 75.5M | "seventy-five point five million" |
| $323.40 | "three hundred twenty-three dollars and forty cents" |

### Rules in Prompt

1. **NEVER SAY**: "three two three point four zero"
2. **ALWAYS SAY**: "three hundred twenty-three dollars and forty cents"

3. **For prices**: Always pronounce as currency
4. **For percentages**: Say "up" or "down" before the number
5. **For volumes**: Say "million" or "billion" not "M" or "B"

### Testing

To test the fix:
1. Ask "How's Tesla?"
2. Listen for: "Tesla is at [natural price pronunciation]"
3. Should NOT hear: "three two nine point three one"
4. Should hear: "three hundred twenty-nine dollars"

## Technical Implementation

The prompt now explicitly instructs:
```
**FOR SPEECH OUTPUT: USE SSML TAGS**
When speaking prices, wrap them in SSML for natural pronunciation:
- <say-as interpret-as="currency">$329.31</say-as>
```

This ensures ElevenLabs TTS engine pronounces monetary values correctly.

## Voice Response Format

Quick mode voice response:
- "Tesla is at [price], [up/down] [percent] today"
- "Watch the [level] level at [price]"
- "Trading near support at [price]"

All prices spoken naturally, not as individual digits.