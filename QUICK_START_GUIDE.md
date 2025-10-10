# Quick Start Guide - Agent Builder Implementation

## 🎯 What You Have Now

✅ **Complete Agent Builder Instructions** created (GPT-5 powered, high reasoning)
✅ **Existing workflow** ready for configuration: `wf_68e474d14d28819085`
✅ **Backend** running and ready for integration
✅ **Voice system** fixed with server_vad

---

## 🚀 Immediate Next Steps (5 minutes)

### Step 1: Open Agent Builder

1. Go to: https://platform.openai.com/agent-builder
2. Open your existing workflow: `wf_68e474d14d28819085`
3. You should see your "G'sves Agent" node already there

### Step 2: Copy Instructions

1. Open file: `AGENT_BUILDER_ASSISTANT_INSTRUCTIONS.md`
2. Scroll to the section starting with the ━ lines
3. **Copy everything** between the first ━ line and the last ━ line (the entire workflow specification)

### Step 3: Paste to Assistant

1. In Agent Builder, look for **"Do it for me"** assistant panel (right side or bottom)
2. **Paste the complete instructions** you just copied
3. Press Enter or click Send

### Step 4: Wait for Implementation

The assistant will:
- Add 4 new nodes (Intent Classifier, Branch, Chart Command, Transform)
- Fix your existing G'sves Agent node (model change: o4-mini → gpt-4o)
- Configure all connections
- Set up structured outputs
- Add branching logic

**Time:** 2-5 minutes

---

## 📚 Step 5: Upload Knowledge Base Files

### If You Have the Files:

1. In Agent Builder, click on G'sves Agent node
2. Look for **Knowledge** section
3. Click **Add Knowledge** → **File Search**
4. Create new store: "gvses_kb"
5. Upload these 4 files:
   - gvses_methodology.md
   - gvses_options_guide.md
   - gvses_analysis_checklist.md
   - AGENT_BUILDER_INSTRUCTIONS.md

### If You DON'T Have the Files:

**Option A:** Skip for now, test without knowledge base first

**Option B:** Create placeholder files:

```bash
# In your project directory
cd knowledge_base  # or create this directory

# Create minimal versions
echo "# G'sves Methodology
LTB (Long-Term Bias): Weekly/daily trend levels
ST (Short-Term): Actionable intraday/daily levels
QE (Qualifying Events): Earnings, macro catalysts
2% Risk Rule: Never risk more than 2% per trade" > gvses_methodology.md

echo "# Options Guide
Focus on liquid options with tight spreads
Prefer weekly options for tactical plays
Analyze Greeks: Delta, Theta, Vega, Gamma" > gvses_options_guide.md

echo "# Analysis Checklist
1. Identify trend (LTB)
2. Mark key levels (ST)
3. Note catalysts (QE)
4. Calculate risk (2% rule)
5. Define entry/stop/target" > gvses_analysis_checklist.md

echo "# G'sves Personality
30 years trading experience
Trained under Buffett, Tudor Jones, Dalio
Focus: Risk management, discipline, education" > AGENT_BUILDER_INSTRUCTIONS.md
```

Then upload these files to gvses_kb in Agent Builder.

---

## 🧪 Step 6: Test in Preview Mode

1. Click **Preview** button (top right in Agent Builder)
2. Run these 4 test cases:

**Test 1 - Chart Command:**
```
Input: "Show 15m TSLA with RSI and VWAP"
Expected: Fast response with chart commands
Check: Should route through Intent Classifier → Chart Command → Transform
```

**Test 2 - Indicator Toggle:**
```
Input: "Turn off MACD"
Expected: Indicator removal command
Check: Should route through chart path (not G'sves)
```

**Test 3 - Trading Analysis:**
```
Input: "Give me a trade plan for NVDA this week"
Expected: Detailed analysis with LTB/ST/QE levels
Check: Should route through G'sves Agent, call tools, use knowledge base
```

**Test 4 - Clarification:**
```
Input: "Analyze AAPL"
Expected: G'sves asks for timeframe
Check: Should ask ONE clarifying question
```

---

## ✅ Step 7: Publish Workflow

If all tests pass:

1. Click **Publish** (top right)
2. Version name: `v1.0 - Initial G'sves Workflow`
3. Description: `Trading assistant with intent classification and risk management`
4. Click **Publish**
5. **Copy the workflow ID** (should still be wf_68e474d14d28819085)

---

## 🔌 Step 8: Connect to Backend (Next Phase)

Once workflow is published:

```bash
# backend/.env

# Enable workflow with 10% A/B test
WORKFLOW_PERCENTAGE=10
GVSES_WORKFLOW_ID=wf_68e474d14d28819085

# Existing settings (keep these)
GVSES_ASSISTANT_ID=asst_FgdYMBvUvKUy0mxX5AF7Lmyg
USE_GVSES_ASSISTANT=true
```

Then:
1. Implement WorkflowProvider (see IMPLEMENTATION_ROADMAP.md Day 3-5)
2. Test backend integration
3. Monitor metrics
4. Gradually increase to 100%

---

## 📊 Success Criteria

### After Agent Builder Implementation:
- [x] 5 nodes visible in workflow canvas
- [x] G'sves Agent model changed to gpt-4o
- [x] Intent Classifier using gpt-4o-mini
- [x] All test cases pass in preview
- [x] Workflow published successfully

### After Backend Integration:
- [ ] Adapter switching between Responses and Workflow
- [ ] 10% of traffic going through workflow
- [ ] Latency comparable to Responses API
- [ ] No errors in logs
- [ ] Metrics visible in Langfuse

---

## 🆘 Troubleshooting

### "Do it for me" assistant not responding
- Make sure you pasted the COMPLETE instructions (all ━ lines)
- Try clicking the assistant panel again
- Refresh the Agent Builder page

### Model "o4-mini" still showing
- Manually click G'sves Agent node
- Change model dropdown to "gpt-4o"
- Save changes

### Test cases failing
- Check node connections are correct
- Verify Intent Classifier has structured output enabled
- Ensure G'sves Agent has tools enabled (File Search + MCP)
- Check branch condition is correct

### Can't upload knowledge base files
- Create placeholder files (see Step 5 Option B)
- Or skip knowledge base for initial testing
- G'sves will work but won't cite methodology

---

## 📝 Summary

**You're doing:** Configure Agent Builder workflow visually

**What happens:**
1. Paste instructions → Assistant configures 5 nodes
2. Upload knowledge base → G'sves gets expertise
3. Test in preview → Verify all paths work
4. Publish → Get workflow ID
5. Connect to backend → Enable A/B testing

**Time estimate:**
- Agent Builder config: **10-15 minutes**
- Backend integration: **1-2 hours** (later)
- Full testing: **30 minutes** (later)

---

## 🎓 What You've Accomplished

✅ Fixed voice with server_vad turn detection
✅ Created G'sves assistant programmatically
✅ Designed complete workflow architecture
✅ Generated GPT-5 powered implementation instructions
✅ Ready to deploy visual workflow in Agent Builder

**Next milestone:** Workflow published and running in Agent Builder ✨

---

## 📚 Reference Documents

- **AGENT_BUILDER_ASSISTANT_INSTRUCTIONS.md** ← **COPY FROM THIS FILE**
- IMPLEMENTATION_ROADMAP.md - Full 6-day implementation plan
- AGENT_BUILDER_WORKFLOW_DESIGN.md - Detailed workflow design
- GPT5_ANALYSIS_SUMMARY.md - GPT-5's analysis of all 3 paths
- AGENT_ARCHITECTURE_GUIDE.md - System architecture
- VOICE_TEST_CHECKLIST.md - Voice testing procedure

---

**Created:** October 7, 2025
**Status:** Ready for immediate use
**Next Action:** Open Agent Builder and paste instructions ⚡
