# 🌟 VeriFace AI — Smart Classroom Attendance Frontend Application

> **Production-grade, accessible, and type-safe frontend application for automated AI face recognition attendance.**  
> Built with **React 19**, **TypeScript 5.7**, **Vite**, **Tailwind CSS**, and **Vitest**.

---

## 🚀 Key Architectural Pillars & Skills

This application fulfills all 5 core competency criteria requested for modern frontend engineering:

### 1. 🛡️ Strict TypeScript
- **100% Type-Safe:** Zero `any` types.
- Centralized contracts in [`src/types/attendance.ts`](./src/types/attendance.ts) matching Django REST Framework serializers:
  - `Student`, `StudentClass`, `Subject`, `AttendanceLog`
  - `DraftResult`, `MatchDetail`, `ConfirmPayload`, `ConfirmResponse`
- Strongly-typed API client in [`src/api/attendanceApi.ts`](./src/api/attendanceApi.ts) with full type-inference on request and response bodies.

### 2. ♿ Comprehensive Accessibility (a11y)
- **Semantic Structure:** Full utilization of `<main>`, `<header>`, `<nav>`, `<table>`, and `<label>`.
- **WAI-ARIA Attributes:**
  - `role="tab"` and `aria-selected` for segmented filters and role selection.
  - `role="switch"` and `aria-checked` with explicit `aria-label` on all student presence toggle switches.
  - `aria-live="polite"` regions for feedback toasts and AI processing status announcements.
- **Colorblind-Safe Design:** Statuses are never communicated by color alone. Every student card pairs distinct color pills (emerald/error) with explicit text labels (`Present`, `Absent`) and status icons (`check`, `close`).
- **Keyboard Navigability:** Full tab-order navigation across all student cards with Space/Enter toggle triggers.

### 3. 🧪 Robust Testing Suite (Vitest + React Testing Library)
- Located in [`src/tests/AttendanceReview.test.tsx`](./src/tests/AttendanceReview.test.tsx):
  1. **Render Test:** Verifies that the student roster and Bento summary counts (Present, Absent, Photos, Faces) render accurately.
  2. **Interactive Toggle Test:** Simulates clicking a toggle switch on an absent student and verifies the state flips to `Present (Manual 1.0)`.
  3. **Quick Mark Test:** Verifies the one-click quick mark button updates presence and accessibility attributes.
  4. **Filter Test:** Asserts that clicking segmented filter tabs (`All`, `Present`, `Absent`) correctly filters the visible list.
- Run tests anytime with `npm run test`.

### 4. ⚡ Two-Step AI Workflow & Local State Persistence
- **Step 1 (Scan & Capture):** Multi-angle classroom capture dropzone supporting multiple image uploads or simulated live camera viewfinder with bounding box HUD.
- **Step 2 (Review & Override):** Prevents premature database writes. The AI generates an unpersisted draft roster, allowing teachers to review, flip switches for obstructed students, and commit only verified records to Supabase PostgreSQL.

### 5. 🌐 Cloud Database & API Synchronization
- Fully integrated with the Django backend at `http://127.0.0.1:8000/api/`.
- Automatic sync with Supabase PostgreSQL cloud database on attendance confirmation.
- Resilient fallback mechanism for offline demo presentation.

---

## 📱 Application Screens

| Screen | File | Description |
| :--- | :--- | :--- |
| **Login & Identity** | [`src/pages/LoginScreen.tsx`](./src/pages/LoginScreen.tsx) | Portal selection (Teacher / Student) with Quick Dev Auth presets and live API status. |
| **Teacher Dashboard** | [`src/pages/TeacherDashboard.tsx`](./src/pages/TeacherDashboard.tsx) | Faculty profile, active cohort scope, Bento metrics (42 enrolled, 90% bio indexed), and lecture log. |
| **Take Attendance (Scan)** | [`src/pages/TakeAttendanceScreen.tsx`](./src/pages/TakeAttendanceScreen.tsx) | Multi-photo staged angle dropzone, live camera viewfinder HUD, and AI execution. |
| **Review & Override** | [`src/pages/AttendanceReviewScreen.tsx`](./src/pages/AttendanceReviewScreen.tsx) | Core review grid, Bento diagnostics, override toggles, and Supabase commit. |
| **Attendance History** | [`src/pages/HistoryScreen.tsx`](./src/pages/HistoryScreen.tsx) | Filterable attendance table with real-time CSV export. |
| **Face ID Registry** | [`src/pages/FaceRegistryScreen.tsx`](./src/pages/FaceRegistryScreen.tsx) | Biometric enrolment modal to upload 1-5 photos for centroid extraction. |

---

## 🛠️ Getting Started

### 1. Install Dependencies
```bash
npm install
```

### 2. Start Local Development Server
```bash
npm run dev
```
Open **`http://localhost:5173`** in your browser.

### 3. Run Unit Tests
```bash
npm run test
```

### 4. Production Build
```bash
npm run build
```
cd backend && venv\Scripts\python.exe manage.py runserver 0.0.0.0:8000