-- Extract from 001_chat_and_market_history.sql
-- Create user_drawings table if it doesn't exist

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
