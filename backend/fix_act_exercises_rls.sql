-- Fix RLS policy for act_exercises to allow public read access
-- Educational content should be publicly accessible

DROP POLICY IF EXISTS "Authenticated users can view exercises" ON act_exercises;

CREATE POLICY "Anyone can view exercises"
    ON act_exercises FOR SELECT
    USING (true);
