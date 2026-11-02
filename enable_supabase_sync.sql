-- ======================================================================
-- VeriFace AI • Supabase Cloud Full Biometric & Data Access Policy
-- Run this in your Supabase Dashboard -> SQL Editor (Click "New query" -> Run)
-- Guarantees that Django Admin and the Flutter app can read/write biometrics,
-- profiles, and attendance without RLS permission blocks.
-- ======================================================================

-- 1. Ensure profiles table allows full insert, update, select, delete
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow public read access to profiles" ON profiles;
DROP POLICY IF EXISTS "Allow public all access to profiles" ON profiles;
CREATE POLICY "Allow public all access to profiles" ON profiles FOR ALL USING (true) WITH CHECK (true);

-- 2. Ensure student_classes table allows full sync
ALTER TABLE student_classes ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow public read access to classes" ON student_classes;
DROP POLICY IF EXISTS "Allow public all access to classes" ON student_classes;
CREATE POLICY "Allow public all access to classes" ON student_classes FOR ALL USING (true) WITH CHECK (true);

-- 3. Ensure subjects table allows full sync
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow public read access to subjects" ON subjects;
DROP POLICY IF EXISTS "Allow public all access to subjects" ON subjects;
CREATE POLICY "Allow public all access to subjects" ON subjects FOR ALL USING (true) WITH CHECK (true);

-- 4. Ensure attendance_logs table allows full sync
ALTER TABLE attendance_logs ENABLE ROW LEVEL SECURITY;
DROP POLICY IF EXISTS "Allow public all access to attendance" ON attendance_logs;
CREATE POLICY "Allow public all access to attendance" ON attendance_logs FOR ALL USING (true) WITH CHECK (true);

-- 5. Enable Realtime broadcasting on profiles and attendance_logs
ALTER PUBLICATION supabase_realtime ADD TABLE profiles;
ALTER PUBLICATION supabase_realtime ADD TABLE attendance_logs;
