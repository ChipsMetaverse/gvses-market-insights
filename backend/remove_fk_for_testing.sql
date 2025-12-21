-- Temporarily remove foreign key constraints for testing
-- This allows testing without creating actual auth.users

ALTER TABLE trade_journal DROP CONSTRAINT IF EXISTS trade_journal_user_id_fkey;
ALTER TABLE weekly_insights DROP CONSTRAINT IF EXISTS weekly_insights_user_id_fkey;
ALTER TABLE act_exercise_completions DROP CONSTRAINT IF EXISTS act_exercise_completions_user_id_fkey;
ALTER TABLE behavioral_patterns DROP CONSTRAINT IF EXISTS behavioral_patterns_user_id_fkey;
ALTER TABLE user_behavioral_settings DROP CONSTRAINT IF EXISTS user_behavioral_settings_user_id_fkey;
