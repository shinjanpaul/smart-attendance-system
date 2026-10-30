# VeriFace AI • Flutter Mobile App (Supabase Cloud)

The mobile application for **VeriFace AI Smart Attendance**, built with Flutter and powered by **Supabase Cloud** (100% Free Forever Tier).

---

## 🚀 Key Features

1. **Exact UI/UX Match with Web**:
   - Signature Indigo/Purple theme (`#3525CD`), Material 3 clean surface cards, and rounded typography.
   - Dynamic 75% Safety Margin Bar (`+14.5% Above 75% Criteria` in emerald green).
   - Selected Professor pinned at Index 0 (`Selected Professor` badge, `100.0% Verified`).
2. **Role-Based Architecture**:
   - **Student Portal**: 100% passwordless single-tap access with real profile pictures (Ayush Nyas, Shinjan Paul, etc.).
   - **Faculty Portal**: Schedule cards, multi-photo classroom camera scanning, attendance review with manual override switches, and biometric registry.
3. **100% Free Cloud Infrastructure**:
   - Powered by Supabase Free Tier (PostgreSQL database, storage for face photos, real-time sync).
   - Zero hosting fees, zero monthly costs.
4. **Offline Resilient**:
   - Cached locally with 0ms instant display even without internet connection.

---

## 🛠️ Step-by-Step Setup Guide

### Step 1: Set up Supabase Cloud Database (3 Clicks)
1. Go to [https://supabase.com](https://supabase.com) and log in to your project (`ymcakklhzkuylowlhzms`).
2. In the left sidebar, click **SQL Editor**.
3. Open [`supabase_schema.sql`](../supabase_schema.sql) in this repository, copy all contents, paste into the SQL Editor, and click **Run**.
   - *This creates all tables (`profiles`, `attendance_logs`, `subjects`, `student_classes`) and seeds the exact 19-session baseline.*

### Step 2: Configure Supabase API Key
1. In Supabase Dashboard, navigate to **Project Settings** (gear icon) -> **API**.
2. Copy the `anon` / `public` API key.
3. Open `lib/services/supabase_service.dart`:
   ```dart
   static const String supabaseUrl = 'https://ymcakklhzkuylowlhzms.supabase.co';
   static const String supabaseAnonKey = 'YOUR_COPIED_ANON_KEY_HERE';
   ```

### Step 3: Run the Flutter App
In your terminal, navigate to the `mobile_app` folder:
```bash
cd mobile_app
flutter pub get
flutter run
```
You can run it on:
- **Android Phone / Emulator** (`flutter run -d android`)
- **iPhone / iOS Simulator** (`flutter run -d ios`)
- **Chrome / Web Browser** (`flutter run -d chrome`)
