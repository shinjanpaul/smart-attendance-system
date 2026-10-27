import React, { useState } from 'react';
import { Header } from './components/Header';
import { BottomNav, NavTab } from './components/BottomNav';
import { LoginScreen } from './pages/LoginScreen';
import { TeacherDashboard } from './pages/TeacherDashboard';
import { TakeAttendanceScreen } from './pages/TakeAttendanceScreen';
import { AttendanceReviewScreen } from './pages/AttendanceReviewScreen';
import { HistoryScreen } from './pages/HistoryScreen';
import { FaceRegistryScreen } from './pages/FaceRegistryScreen';
import { DraftResult, Role } from './types/attendance';

export const App: React.FC = () => {
  const [user, setUser] = useState<{ username: string; role: Role } | null>(null);
  const [currentTab, setCurrentTab] = useState<NavTab>('dashboard');

  // Default initial draft matching user's mockup
  const [draftData, setDraftData] = useState<DraftResult>({
    total_photos_processed: 2,
    total_faces_detected: 4,
    unmatched_faces_count: 0,
    present_count: 3,
    absent_count: 2,
    class_id: 1,
    subject_id: 1,
    date: new Date().toISOString().split('T')[0],
    present_students: [
      {
        id: 3,
        username: 'shinjan_paul',
        name: 'Shinjan Paul',
        roll_number: 'IT202601',
        has_registered_face: true,
      },
      {
        id: 4,
        username: 'biswajit_sinha',
        name: 'Biswajit Sinha',
        roll_number: 'IT202602',
        has_registered_face: true,
      },
      {
        id: 5,
        username: 'priya_sharma',
        name: 'Priya Sharma',
        roll_number: 'IT202603',
        has_registered_face: true,
      },
    ],
    absent_students: [
      {
        id: 6,
        username: 'ayush_nyas',
        name: 'Ayush Nyas',
        roll_number: 'IT202604',
        has_registered_face: true,
      },
      {
        id: 7,
        username: 'rohan_sen',
        name: 'Rohan Sen',
        roll_number: 'IT202605',
        has_registered_face: false,
      },
    ],
    match_details: [
      {
        photo_index: 1,
        student_id: 3,
        student_name: 'Shinjan Paul',
        roll_number: 'IT202601',
        distance: 0.3812,
        confidence: 0.865,
      },
      {
        photo_index: 1,
        student_id: 4,
        student_name: 'Biswajit Sinha',
        roll_number: 'IT202602',
        distance: 0.3204,
        confidence: 0.912,
      },
      {
        photo_index: 2,
        student_id: 5,
        student_name: 'Priya Sharma',
        roll_number: 'IT202603',
        distance: 0.3541,
        confidence: 0.89,
      },
    ],
  });

  if (!user) {
    return <LoginScreen onLoginSuccess={(u) => setUser(u)} />;
  }

  const getScreenTitle = () => {
    switch (currentTab) {
      case 'dashboard':
        return 'Faculty Portal';
      case 'take-attendance':
        return 'Take Attendance';
      case 'attendance-review':
        return 'Attendance Review';
      case 'history':
        return 'Attendance History';
      case 'face-id':
        return 'Face ID Registry';
      default:
        return 'VeriFace AI';
    }
  };

  return (
    <div className="min-h-screen bg-surface flex flex-col font-body-md text-on-surface antialiased">
      <Header title={getScreenTitle()} />

      <div className="flex-1">
        {currentTab === 'dashboard' && (
          <TeacherDashboard
            onStartScan={() => setCurrentTab('take-attendance')}
            onNavigateTab={(tab) => setCurrentTab(tab)}
          />
        )}

        {currentTab === 'take-attendance' && (
          <TakeAttendanceScreen
            onProcessComplete={(draft) => {
              setDraftData(draft);
              setCurrentTab('attendance-review');
            }}
          />
        )}

        {currentTab === 'attendance-review' && (
          <AttendanceReviewScreen
            draftData={draftData}
            onRetake={() => setCurrentTab('take-attendance')}
            onConfirmedSuccess={() => setCurrentTab('history')}
          />
        )}

        {currentTab === 'history' && <HistoryScreen />}

        {currentTab === 'face-id' && <FaceRegistryScreen />}
      </div>

      <BottomNav currentTab={currentTab} onSelectTab={(tab) => setCurrentTab(tab)} />
    </div>
  );
};

export default App;
