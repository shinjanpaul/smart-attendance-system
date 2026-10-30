-- ======================================================================
-- VeriFace AI • Supabase PostgreSQL Cloud Schema & Seed Data
-- 100% Free Forever on Supabase Cloud Free Tier
-- ======================================================================

-- 1. Enable UUID Extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. Create Enums
DO $$ BEGIN
    CREATE TYPE user_role AS ENUM ('ADMIN', 'TEACHER', 'STUDENT');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE attendance_status AS ENUM ('PRESENT', 'ABSENT', 'LATE');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE verification_method AS ENUM ('FACE_RECOGNITION', 'MANUAL');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- 3. Student Classes Table
CREATE TABLE IF NOT EXISTS student_classes (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    department VARCHAR(100) DEFAULT 'Information Technology',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Subjects Table
CREATE TABLE IF NOT EXISTS subjects (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(20) NOT NULL,
    name VARCHAR(100) NOT NULL,
    student_class_id BIGINT REFERENCES student_classes(id) ON DELETE CASCADE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. User Profiles (Teachers, Students, Admins)
CREATE TABLE IF NOT EXISTS profiles (
    id BIGSERIAL PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    first_name VARCHAR(150) DEFAULT '',
    last_name VARCHAR(150) DEFAULT '',
    role user_role DEFAULT 'STUDENT',
    department VARCHAR(100) DEFAULT 'Information Technology',
    roll_number VARCHAR(50) UNIQUE,
    student_class_id BIGINT REFERENCES student_classes(id) ON DELETE SET NULL,
    profile_picture_url TEXT,
    face_embedding JSONB, -- 128-D Euclidean Facial Landmark Vector
    has_registered_face BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Attendance Logs Table
CREATE TABLE IF NOT EXISTS attendance_logs (
    id BIGSERIAL PRIMARY KEY,
    student_id BIGINT REFERENCES profiles(id) ON DELETE CASCADE,
    student_class_id BIGINT REFERENCES student_classes(id) ON DELETE CASCADE,
    subject_id BIGINT REFERENCES subjects(id) ON DELETE CASCADE,
    date DATE NOT NULL DEFAULT CURRENT_DATE,
    timestamp TIMESTAMPTZ DEFAULT NOW(),
    status attendance_status DEFAULT 'PRESENT',
    verification_method verification_method DEFAULT 'FACE_RECOGNITION',
    confidence_score FLOAT DEFAULT 0.95,
    snapshot_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(student_id, student_class_id, subject_id, date)
);

-- 7. Tasks & Submissions (Homework / Assignments)
CREATE TABLE IF NOT EXISTS tasks (
    id BIGSERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT DEFAULT '',
    assigned_by_id BIGINT REFERENCES profiles(id) ON DELETE CASCADE,
    assigned_to_id BIGINT REFERENCES profiles(id) ON DELETE SET NULL, -- NULL means all students in class
    deadline TIMESTAMPTZ NOT NULL,
    priority VARCHAR(20) DEFAULT 'MEDIUM',
    status VARCHAR(20) DEFAULT 'PENDING',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS submissions (
    id BIGSERIAL PRIMARY KEY,
    task_id BIGINT REFERENCES tasks(id) ON DELETE CASCADE,
    student_id BIGINT REFERENCES profiles(id) ON DELETE CASCADE,
    submission_file_url TEXT,
    submitted_at TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20) DEFAULT 'PENDING',
    feedback TEXT,
    score FLOAT
);

-- ======================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES (Open read/write for free app usage)
-- ======================================================================
ALTER TABLE student_classes ENABLE ROW LEVEL SECURITY;
ALTER TABLE subjects ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE attendance_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE submissions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Allow public read access to classes" ON student_classes FOR SELECT USING (true);
CREATE POLICY "Allow public read access to subjects" ON subjects FOR SELECT USING (true);
CREATE POLICY "Allow public read access to profiles" ON profiles FOR SELECT USING (true);
CREATE POLICY "Allow public all access to attendance" ON attendance_logs FOR ALL USING (true);
CREATE POLICY "Allow public all access to tasks" ON tasks FOR ALL USING (true);
CREATE POLICY "Allow public all access to submissions" ON submissions FOR ALL USING (true);

-- Enable Realtime on attendance_logs
ALTER PUBLICATION supabase_realtime ADD TABLE attendance_logs;

-- ======================================================================
-- SEED DATA (Exact match with current 19-session curriculum & live status)
-- ======================================================================

-- Classes
INSERT INTO student_classes (id, name, department) VALUES
(1, 'B.Tech IT 4th Yr - Sec A', 'Information Technology'),
(2, 'B.Tech CSE - 3rd Year - Sec B', 'Computer Science & Engineering'),
(3, 'B.Tech AI & DS - 2nd Year', 'AI & Data Science')
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

-- Subjects
INSERT INTO subjects (id, code, name, student_class_id) VALUES
(1, 'IT801', 'Cloud Computing & Distributed Systems', 1),
(2, 'IT802', 'Machine Learning & Pattern Recognition', 1),
(3, 'IT803', 'Cyber & Information Security', 1),
(4, 'CS601', 'Computer Networks', 2),
(5, 'AD401', 'Deep Learning & Computer Vision', 3)
ON CONFLICT (id) DO UPDATE SET name = EXCLUDED.name;

-- Faculty Profiles
INSERT INTO profiles (id, username, first_name, last_name, role, department, profile_picture_url) VALUES
(1, 'prof_sudipta', 'Sudipta', 'Bhadra', 'TEACHER', 'Information Technology', NULL),
(2, 'prof_ananya', 'Ananya', 'Mukherjee', 'TEACHER', 'Information Technology', NULL),
(3, 'prof_rituparna', 'Rituparna', 'Sinha', 'TEACHER', 'Information Technology', NULL),
(4, 'prof_rajesh', 'Rajesh', 'Sharma', 'TEACHER', 'AI & Data Science', NULL),
(5, 'prof_debashis', 'Debashis', 'Roy', 'TEACHER', 'Computer Science & Engineering', NULL)
ON CONFLICT (id) DO UPDATE SET first_name = EXCLUDED.first_name, last_name = EXCLUDED.last_name;

-- Student Profiles (Including real Ayush & Shinjan photos hosted on GitHub / Cloud CDN)
INSERT INTO profiles (id, username, first_name, last_name, role, department, roll_number, student_class_id, profile_picture_url, has_registered_face) VALUES
(10, 'shinjan_paul', 'Shinjan', 'Paul', 'STUDENT', 'Information Technology', 'IT202601', 1, 'https://shinjanpaul.github.io/smart-attendance-system/media/profiles/ShinjanPaul.jpeg', true),
(11, 'Sourjya_Saha', 'Sourjya', 'Saha', 'STUDENT', 'Information Technology', 'IT2354016', 1, NULL, true),
(12, 'ayush_nyas', 'Ayush', 'Nyas', 'STUDENT', 'Information Technology', 'IT202604', 1, 'https://shinjanpaul.github.io/smart-attendance-system/media/profiles/Ayush.jpeg', true),
(13, 'hammad_akhter', 'Hammad', 'Akhter', 'STUDENT', 'Information Technology', 'IT202603', 1, NULL, true),
(14, 'biswajit_sinha', 'Biswajit', 'Sinha', 'STUDENT', 'Information Technology', 'IT202602', 1, 'https://shinjanpaul.github.io/smart-attendance-system/media/profiles/4.jpeg', true)
ON CONFLICT (id) DO UPDATE SET 
    first_name = EXCLUDED.first_name, 
    last_name = EXCLUDED.last_name, 
    profile_picture_url = EXCLUDED.profile_picture_url;

-- Baseline 19 Sessions Attendance Seed
-- Cloud Dates (10 sessions of IT801)
-- Cyber Dates (8 sessions of IT803)
-- 19th Session: 2026-10-26 IT802 (Machine Learning, Prof. Rituparna Sinha)

-- 1. Ayush Nyas (17 of 19 Sessions = 89.5% Attendance, IT802 1/1 100%)
INSERT INTO attendance_logs (student_id, student_class_id, subject_id, date, status, verification_method, confidence_score) VALUES
(12, 1, 1, '2026-09-21', 'PRESENT', 'FACE_RECOGNITION', 0.95),
(12, 1, 1, '2026-09-23', 'PRESENT', 'FACE_RECOGNITION', 0.96),
(12, 1, 1, '2026-09-25', 'PRESENT', 'FACE_RECOGNITION', 0.94),
(12, 1, 1, '2026-09-28', 'PRESENT', 'FACE_RECOGNITION', 0.97),
(12, 1, 1, '2026-09-30', 'PRESENT', 'FACE_RECOGNITION', 0.93),
(12, 1, 1, '2026-10-05', 'ABSENT',  'FACE_RECOGNITION', 0.0),
(12, 1, 1, '2026-10-07', 'PRESENT', 'FACE_RECOGNITION', 0.95),
(12, 1, 1, '2026-10-09', 'PRESENT', 'FACE_RECOGNITION', 0.98),
(12, 1, 1, '2026-10-14', 'PRESENT', 'FACE_RECOGNITION', 0.94),
(12, 1, 1, '2026-10-19', 'PRESENT', 'FACE_RECOGNITION', 0.96),
(12, 1, 3, '2026-09-22', 'PRESENT', 'FACE_RECOGNITION', 0.95),
(12, 1, 3, '2026-09-24', 'PRESENT', 'FACE_RECOGNITION', 0.97),
(12, 1, 3, '2026-09-29', 'PRESENT', 'FACE_RECOGNITION', 0.94),
(12, 1, 3, '2026-10-01', 'ABSENT',  'FACE_RECOGNITION', 0.0),
(12, 1, 3, '2026-10-06', 'PRESENT', 'FACE_RECOGNITION', 0.96),
(12, 1, 3, '2026-10-08', 'PRESENT', 'FACE_RECOGNITION', 0.95),
(12, 1, 3, '2026-10-13', 'PRESENT', 'FACE_RECOGNITION', 0.97),
(12, 1, 3, '2026-10-15', 'PRESENT', 'FACE_RECOGNITION', 0.98),
(12, 1, 2, '2026-10-26', 'PRESENT', 'FACE_RECOGNITION', 0.95)
ON CONFLICT (student_id, student_class_id, subject_id, date) DO NOTHING;

-- 2. Shinjan Paul (16 of 19 Sessions = 84.2% Attendance)
INSERT INTO attendance_logs (student_id, student_class_id, subject_id, date, status, verification_method, confidence_score) VALUES
(10, 1, 1, '2026-09-21', 'PRESENT', 'FACE_RECOGNITION', 0.97),
(10, 1, 1, '2026-09-23', 'PRESENT', 'FACE_RECOGNITION', 0.95),
(10, 1, 1, '2026-09-25', 'ABSENT',  'FACE_RECOGNITION', 0.0),
(10, 1, 1, '2026-09-28', 'PRESENT', 'FACE_RECOGNITION', 0.96),
(10, 1, 1, '2026-09-30', 'PRESENT', 'FACE_RECOGNITION', 0.94),
(10, 1, 1, '2026-10-05', 'PRESENT', 'FACE_RECOGNITION', 0.95),
(10, 1, 1, '2026-10-07', 'PRESENT', 'FACE_RECOGNITION', 0.98),
(10, 1, 1, '2026-10-09', 'PRESENT', 'FACE_RECOGNITION', 0.93),
(10, 1, 1, '2026-10-14', 'PRESENT', 'FACE_RECOGNITION', 0.97),
(10, 1, 1, '2026-10-19', 'PRESENT', 'FACE_RECOGNITION', 0.96),
(10, 1, 3, '2026-09-22', 'PRESENT', 'FACE_RECOGNITION', 0.94),
(10, 1, 3, '2026-09-24', 'PRESENT', 'FACE_RECOGNITION', 0.96),
(10, 1, 3, '2026-09-29', 'PRESENT', 'FACE_RECOGNITION', 0.98),
(10, 1, 3, '2026-10-01', 'PRESENT', 'FACE_RECOGNITION', 0.95),
(10, 1, 3, '2026-10-06', 'ABSENT',  'FACE_RECOGNITION', 0.0),
(10, 1, 3, '2026-10-08', 'PRESENT', 'FACE_RECOGNITION', 0.97),
(10, 1, 3, '2026-10-13', 'PRESENT', 'FACE_RECOGNITION', 0.96),
(10, 1, 3, '2026-10-15', 'PRESENT', 'FACE_RECOGNITION', 0.95),
(10, 1, 2, '2026-10-26', 'ABSENT',  'FACE_RECOGNITION', 0.0)
ON CONFLICT (student_id, student_class_id, subject_id, date) DO NOTHING;
