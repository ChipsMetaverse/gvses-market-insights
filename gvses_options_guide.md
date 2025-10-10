# Options Trading Quick Reference for G'sves

## The Greeks (Simplified)

**Delta (Δ)**: How much option price moves per $1 stock move
- Call delta: 0 to 1.0 (50 delta = $0.50 move per $1 stock move)
- Put delta: -1.0 to 0 (negative because puts gain when stock drops)
- ATM options: ~0.50 delta
- Deep ITM: ~1.0 delta (moves like stock)
- Far OTM: ~0.10 delta (barely moves)

**Theta (Θ)**: Time decay (money lost per day)
- Always negative for option buyers
- Accelerates near expiration
- Weekly options: High theta (lose value FAST)

**Vega (ν)**: Sensitivity to volatility changes
- High vega = price changes a lot with IV changes
- Earnings = high vega due to uncertainty

**Gamma (Γ)**: Rate of delta change
- Highest at-the-money near expiration
- Tells you how fast delta will change

## Common Strategies

**Covered Call**: Own stock + sell call (income generation)
**Cash-Secured Put**: Sell put + hold cash (get paid to buy stock lower)
**Vertical Spread**: Buy one strike, sell another (defined risk/reward)
**Iron Condor**: Sell OTM put spread + OTM call spread (range-bound income)

## G'sves Weekly Options Selection Process

1. **Find stock near LTB/ST/QE level**
2. **Check IV Rank** - prefer < 50 for buying options
3. **Select strike based on view**:
   - Aggressive: Slightly OTM (higher R/R, lower probability)
   - Conservative: ATM (balanced)
4. **Check Greeks**:
   - Delta > 0.40 for calls
   - Theta not too high (< $0.20/day for small positions)
   - Vega moderate
5. **Calculate risk/reward**: Max loss = premium paid
6. **Set profit target**: 50-100% gain typical for weeklies
7. **Position size**: 2-5% of portfolio max

## Risk Management

- Max 2-5% of portfolio per options trade
- Stop loss at 50% of premium paid (common)
- Close winners at 50-100% gain
- Exit losers when thesis invalidated
- Don't hold through expiration (theta accelerates)

## Common Mistakes to Avoid

1. Buying too far OTM (low delta needs huge move)
2. Holding through expiration (theta kills you)
3. Ignoring IV (buying high IV = overpaying)
4. Too much size (options can go to zero)
5. No stop loss (hope is not a strategy)
6. Trading earnings without understanding IV crush
