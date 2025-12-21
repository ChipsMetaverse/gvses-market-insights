# Apply user_drawings Table - Final Instructions

## ✅ Table Found in Git Repository!

The `user_drawings` table is already defined in:
```
supabase/migrations/001_chat_and_market_history.sql
```

However, it hasn't been applied to the database yet.

## 📋 Quick Apply via Supabase Dashboard

### Option 1: SQL Editor (RECOMMENDED - 2 minutes)

1. **Open Supabase SQL Editor:**
   https://supabase.com/dashboard/project/cwnzgvrylvxfhwhsqelc/sql/new

2. **Copy & Paste this SQL:**
   ```sql
   -- Create user_drawings table
   CREATE TABLE IF NOT EXISTS user_drawings (
     id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
     user_id UUID,
     conversation_id UUID,
     symbol TEXT NOT NULL,
     type TEXT NOT NULL, -- 'trendline', 'horizontal', 'fibonacci', 'support', 'resistance'
     data JSONB NOT NULL, -- drawing-specific data (coordinates, prices, etc.)
     created_at TIMESTAMPTZ DEFAULT NOW(),
     updated_at TIMESTAMPTZ DEFAULT NOW()
   );

   -- Create index
   CREATE INDEX IF NOT EXISTS idx_user_drawings_symbol ON user_drawings(user_id, symbol);

   -- Enable RLS
   ALTER TABLE user_drawings ENABLE ROW LEVEL SECURITY;

   -- Create policy
   DROP POLICY IF EXISTS "Users can manage their own drawings" ON user_drawings;
   CREATE POLICY "Users can manage their own drawings"
     ON user_drawings FOR ALL
     USING (auth.uid() = user_id OR user_id IS NULL);

   -- Create trigger for updated_at
   CREATE OR REPLACE FUNCTION update_updated_at_column()
   RETURNS TRIGGER AS $$
   BEGIN
     NEW.updated_at = NOW();
     RETURN NEW;
   END;
   $$ LANGUAGE plpgsql;

   DROP TRIGGER IF EXISTS update_user_drawings_updated_at ON user_drawings;
   CREATE TRIGGER update_user_drawings_updated_at
     BEFORE UPDATE ON user_drawings
     FOR EACH ROW
     EXECUTE FUNCTION update_updated_at_column();

   SELECT 'user_drawings table created successfully!' AS status;
   ```

3. **Click "Run"**

4. **Verify Success:**
   - Should see: `user_drawings table created successfully!`
   - Go to Table Editor → Should see `user_drawings` table

### Option 2: Use Prepared SQL File (Alternative)

1. File location: `standalone-drawing-persistence/create_user_drawings_table.sql`
2. Copy entire contents
3. Paste into Supabase SQL Editor
4. Click "Run"

## 🔍 Verify Table Was Created

Run this in standalone-drawing-persistence/:
```bash
python3 apply_migration_simple.py
```

Expected output:
```
🔍 Checking if 'user_drawings' table exists...
✅ Table 'user_drawings' already exists!
🎉 No migration needed. Ready to run tests!
```

## 🧪 Then Re-run Tests

After applying the table:
```bash
cd standalone-drawing-persistence
python3 test_api.py
```

**Expected:** 20/20 tests passing ✅

## ⚠️ Why Didn't Supabase CLI Work?

The Supabase CLI migration system had sync issues:
- Local migrations directory out of sync with remote
- Would require `supabase migration repair` for 16+ migrations
- SQL Editor is faster and more reliable for this case

## 📊 Table Schema

The `user_drawings` table uses a flexible JSONB approach:

```typescript
interface UserDrawing {
  id: UUID
  user_id: UUID (null for anonymous)
  conversation_id: UUID (optional)
  symbol: string  // "TSLA", "AAPL", etc.
  type: string    // "trendline", "horizontal", "fibonacci", "support", "resistance"
  data: {         // JSONB - flexible structure per type
    // For trendlines:
    coordinates?: {
      a: { time: number, price: number }
      b: { time: number, price: number }
    }
    // For horizontal:
    price?: number
    // Common properties:
    color?: string
    width?: number
    style?: string
    visible?: boolean
    selected?: boolean
    name?: string
  }
  created_at: timestamp
  updated_at: timestamp
}
```

## 🔄 Adapting Our API

Our standalone API uses a more structured approach with explicit fields.
To use the existing `user_drawings` table, we have two options:

### Option A: Adapt API to use JSONB `data` field (recommended)
- Store all drawing properties in the `data` JSONB column
- Matches existing schema design
- More flexible for future drawing types

### Option B: Keep standalone table as `drawings`
- Use both tables: `drawings` (detailed) + `user_drawings` (legacy)
- Migrate data between formats as needed

**Recommendation:** Use Option A - adapt the API to work with the existing `user_drawings` table structure. This requires updating:
1. `models.py` - use `data` JSONB field instead of explicit columns
2. `api.py` - map between structured types and JSONB
3. Frontend - no changes needed (already uses JSONB-like format)

## 🎯 Next Steps

1. ✅ Apply SQL via Supabase Dashboard
2. ✅ Verify table exists: `python3 apply_migration_simple.py`
3. ⏳ Decide: Adapt API to use `user_drawings` table OR Keep separate `drawings` table
4. ⏳ Re-run tests
5. ⏳ Integration

---

**Quick Summary:**
The table schema already exists in git, just needs to be applied via Supabase SQL Editor. Copy the SQL above, paste, run - done in 2 minutes!
