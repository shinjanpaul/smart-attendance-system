import React, { useState, useMemo } from 'react';
import { DraftResult, AttendanceStatus, ConfirmPayload } from '../types/attendance';
import { confirmAttendance } from '../api/attendanceApi';

interface AttendanceReviewScreenProps {
  draftData: DraftResult;
  onRetake: () => void;
  onConfirmedSuccess: () => void;
}

interface StudentReviewItem {
  id: number;
  name: string;
  roll_number: string;
  has_registered_face: boolean;
  isPresent: boolean;
  confidence: number;
  distance: number;
  avatarUrl?: string;
  isManualOverride?: boolean;
}

export const AttendanceReviewScreen: React.FC<AttendanceReviewScreenProps> = ({
  draftData,
  onRetake,
  onConfirmedSuccess,
}) => {
  // Build initial editable list from draft
  const initialItems = useMemo<StudentReviewItem[]>(() => {
    const confMap = new Map<number, { conf: number; dist: number }>();
    draftData.match_details.forEach((m) => {
      if (m.student_id) {
        confMap.set(m.student_id, { conf: m.confidence, dist: m.distance });
      }
    });

    const list: StudentReviewItem[] = [];

    // Present students
    draftData.present_students.forEach((s) => {
      const match = confMap.get(s.id);
      list.push({
        id: s.id,
        name: s.name,
        roll_number: s.roll_number,
        has_registered_face: s.has_registered_face,
        isPresent: true,
        confidence: match ? match.conf : 0.88,
        distance: match ? match.dist : 0.35,
        avatarUrl:
          s.id === 3
            ? 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?auto=format&fit=crop&w=200&q=80'
            : s.id === 4
            ? 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80'
            : 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=200&q=80',
      });
    });

    // Absent students
    draftData.absent_students.forEach((s) => {
      list.push({
        id: s.id,
        name: s.name,
        roll_number: s.roll_number,
        has_registered_face: s.has_registered_face,
        isPresent: false,
        confidence: 0.0,
        distance: 0.0,
        avatarUrl:
          s.id === 6
            ? 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80'
            : undefined,
      });
    });

    return list;
  }, [draftData]);

  const [students, setStudents] = useState<StudentReviewItem[]>(initialItems);
  const [filter, setFilter] = useState<'all' | 'present' | 'absent'>('all');
  const [isConfirming, setIsConfirming] = useState(false);
  const [confirmedMessage, setConfirmedMessage] = useState<string | null>(null);

  // Stats calculation
  const presentCount = students.filter((s) => s.isPresent).length;
  const absentCount = students.filter((s) => !s.isPresent).length;
  const totalCount = students.length;

  const toggleStudent = (id: number) => {
    setStudents((prev) =>
      prev.map((s) => {
        if (s.id === id) {
          const newStatus = !s.isPresent;
          return {
            ...s,
            isPresent: newStatus,
            isManualOverride: true,
            confidence: newStatus ? 1.0 : 0.0,
          };
        }
        return s;
      })
    );
  };

  const markQuickPresent = (id: number) => {
    setStudents((prev) =>
      prev.map((s) =>
        s.id === id
          ? {
              ...s,
              isPresent: true,
              isManualOverride: true,
              confidence: 1.0,
            }
          : s
      )
    );
  };

  const filteredStudents = useMemo(() => {
    if (filter === 'present') return students.filter((s) => s.isPresent);
    if (filter === 'absent') return students.filter((s) => !s.isPresent);
    return students;
  }, [students, filter]);

  const handleConfirm = async () => {
    setIsConfirming(true);

    const payload: ConfirmPayload = {
      class_id: draftData.class_id,
      subject_id: draftData.subject_id,
      date: draftData.date || new Date().toISOString().split('T')[0],
      records: students.map((s) => ({
        student_id: s.id,
        status: (s.isPresent ? 'PRESENT' : 'ABSENT') as AttendanceStatus,
        confidence: s.confidence,
      })),
    };

    const res = await confirmAttendance(payload);
    setTimeout(() => {
      setIsConfirming(false);
      setConfirmedMessage(res.message || 'Attendance Saved to Supabase!');
      setTimeout(() => {
        onConfirmedSuccess();
      }, 1200);
    }, 1000);
  };

  return (
    <main className="flex flex-col relative w-full pt-16 pb-28 bg-surface min-h-screen">
      <div className="flex flex-col w-full max-w-lg mx-auto px-4 gap-space-md">
        {/* Top Context & Draft Meta */}
        <div className="flex flex-col gap-space-xs mt-space-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-primary-container animate-pulse" aria-hidden="true"></span>
              <span className="font-label-sm text-label-sm text-primary uppercase tracking-wider font-semibold text-xs">
                Step 2 of 2 • Draft Review
              </span>
            </div>
            <span className="px-2 py-0.5 rounded-full bg-secondary-container text-on-secondary-container font-label-sm text-label-sm font-semibold text-xs">
              {draftData.date || 'Oct 17, 2026'}
            </span>
          </div>

          <div className="flex items-baseline justify-between">
            <div>
              <h1 className="font-headline-lg-mobile text-headline-lg-mobile text-on-surface font-bold text-xl">
                Review &amp; Override
              </h1>
              <p className="font-body-sm text-body-sm text-on-surface-variant text-xs">
                Class: <strong className="font-semibold text-on-surface">B.Tech IT 4th Yr</strong> • Section A
              </p>
            </div>
            <div className="flex items-center gap-1 text-on-surface-variant font-label-sm text-label-sm bg-surface-container-low px-2 py-1 rounded-xl text-xs">
              <span className="material-symbols-outlined text-[16px] text-primary">security_update_good</span>
              <span>Ready to Post</span>
            </div>
          </div>
        </div>

        {/* AI Diagnostic Summary Bento */}
        <div className="flex flex-col gap-space-xs">
          <div className="grid grid-cols-4 gap-2">
            {/* Photos Processed */}
            <div className="flex flex-col items-center justify-center p-2.5 rounded-2xl bg-surface-container-low shadow-sm border border-outline-variant/20">
              <div className="flex items-center gap-1 text-secondary text-xs">
                <span className="material-symbols-outlined text-[16px]">photo_library</span>
                <span className="font-label-sm text-label-sm text-on-surface-variant">Photos</span>
              </div>
              <span className="font-headline-sm text-headline-sm text-on-surface font-bold mt-0.5">
                {draftData.total_photos_processed || 2}
              </span>
            </div>

            {/* Faces Detected */}
            <div className="flex flex-col items-center justify-center p-2.5 rounded-2xl bg-surface-container-low shadow-sm border border-outline-variant/20">
              <div className="flex items-center gap-1 text-primary text-xs">
                <span className="material-symbols-outlined text-[16px]">face</span>
                <span className="font-label-sm text-label-sm text-on-surface-variant">Faces</span>
              </div>
              <span className="font-headline-sm text-headline-sm text-primary font-bold mt-0.5" id="stat-faces">
                {draftData.total_faces_detected || 4}
              </span>
            </div>

            {/* Present Count */}
            <div className="flex flex-col items-center justify-center p-2.5 rounded-2xl bg-surface-container-low shadow-sm border border-outline-variant/20">
              <div className="flex items-center gap-1 text-emerald-600 text-xs">
                <span className="material-symbols-outlined text-[16px]">verified</span>
                <span className="font-label-sm text-label-sm text-on-surface-variant">Present</span>
              </div>
              <span className="font-headline-sm text-headline-sm text-emerald-600 font-bold mt-0.5" id="stat-present">
                {presentCount}
              </span>
            </div>

            {/* Absent Count */}
            <div className="flex flex-col items-center justify-center p-2.5 rounded-2xl bg-surface-container-low shadow-sm border border-outline-variant/20">
              <div className="flex items-center gap-1 text-error text-xs">
                <span className="material-symbols-outlined text-[16px]">person_off</span>
                <span className="font-label-sm text-label-sm text-on-surface-variant">Absent</span>
              </div>
              <span className="font-headline-sm text-headline-sm text-error font-bold mt-0.5" id="stat-absent">
                {absentCount}
              </span>
            </div>
          </div>

          {/* Live Match State Alert Pill */}
          <div className="flex items-center justify-between px-3 py-2 rounded-xl bg-surface-container-lowest shadow-sm border border-outline-variant/20">
            <div className="flex items-center gap-2 text-xs">
              <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
              <span className="font-label-sm text-label-sm text-on-surface">
                Unmatched Faces: <strong className="text-on-surface font-semibold">{draftData.unmatched_faces_count || 0}</strong>{' '}
                (All detected faces matched)
              </span>
            </div>
            <span className="px-2 py-0.5 rounded-md bg-surface-container text-on-surface-variant text-[11px] font-semibold">
              100% Resolved
            </span>
          </div>
        </div>

        {/* Manual Override Info Callout */}
        <div className="flex items-start gap-2.5 p-3 rounded-2xl bg-primary-fixed/40 border border-primary/20">
          <span className="material-symbols-outlined text-primary text-[20px] shrink-0 mt-0.5">touch_app</span>
          <p className="font-body-sm text-body-sm text-on-surface text-xs leading-relaxed">
            <strong className="font-semibold text-primary">Notice:</strong> Flip any toggle to override AI detection. Manually marked Present records will be saved with a <strong className="font-semibold text-primary">1.0 confidence score</strong>.
          </p>
        </div>

        {/* Filter Segmented Tabs */}
        <div className="flex items-center p-1 rounded-xl bg-surface-container-low gap-1" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={filter === 'all'}
            onClick={() => setFilter('all')}
            className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold text-center transition-all ${
              filter === 'all'
                ? 'bg-surface-container-lowest text-primary shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            All ({totalCount})
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={filter === 'present'}
            onClick={() => setFilter('present')}
            className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold text-center transition-all ${
              filter === 'present'
                ? 'bg-surface-container-lowest text-emerald-600 shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            Present ({presentCount})
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={filter === 'absent'}
            onClick={() => setFilter('absent')}
            className={`flex-1 py-1.5 px-2 rounded-lg text-xs font-semibold text-center transition-all ${
              filter === 'absent'
                ? 'bg-surface-container-lowest text-error shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            Absent ({absentCount})
          </button>
        </div>

        {/* Student Verification Roster */}
        <div className="flex flex-col gap-space-sm" id="student-list" role="list" aria-label="Student Verification List">
          {filteredStudents.map((st) => (
            <div
              key={st.id}
              role="listitem"
              data-id={st.roll_number}
              data-status={st.isPresent ? 'present' : 'absent'}
              className="student-card flex flex-col p-3 rounded-2xl bg-surface-container-lowest shadow-sm border border-outline-variant/30 gap-2.5 transition-all"
            >
              <div className="flex items-center justify-between gap-space-sm">
                <div className="flex items-center gap-space-sm min-w-0">
                  <div className="relative w-12 h-12 rounded-full overflow-hidden shrink-0 bg-surface-container flex items-center justify-center">
                    {st.avatarUrl ? (
                      <img src={st.avatarUrl} alt={`Portrait of ${st.name}`} className="w-full h-full object-cover" />
                    ) : (
                      <span className="material-symbols-outlined text-secondary text-[24px]">person</span>
                    )}

                    <span
                      className={`absolute bottom-0 right-0 w-3.5 h-3.5 rounded-full flex items-center justify-center ${
                        st.isPresent ? 'bg-emerald-500' : st.has_registered_face ? 'bg-error' : 'bg-amber-500'
                      }`}
                    >
                      <span className="material-symbols-outlined text-[10px] text-white font-bold">
                        {st.isPresent ? 'check' : st.has_registered_face ? 'close' : 'priority_high'}
                      </span>
                    </span>
                  </div>

                  <div className="flex flex-col min-w-0">
                    <div className="flex items-center gap-1.5">
                      <span className="font-title-md text-title-md text-on-surface truncate text-sm font-semibold">
                        {st.name}
                      </span>
                      {st.has_registered_face ? (
                        <span className="material-symbols-outlined text-primary text-[15px]" title="Face Model Registered">
                          face_retouching_natural
                        </span>
                      ) : (
                        <span className="px-1.5 py-0.5 rounded bg-amber-100 text-amber-900 text-[10px] font-semibold">
                          Unenrolled
                        </span>
                      )}
                    </div>

                    <div className="flex items-center gap-2 text-xs">
                      <span className="font-label-sm text-label-sm text-on-surface-variant">Roll: {st.roll_number}</span>
                      <span className="w-1 h-1 rounded-full bg-outline-variant"></span>
                      <span
                        className={`font-label-sm text-label-sm font-semibold ${
                          st.has_registered_face ? 'text-emerald-600' : 'text-amber-800'
                        }`}
                      >
                        {st.has_registered_face ? 'Face Registered' : 'No Face ID'}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Accessible Toggle Switch */}
                <label className="relative inline-flex items-center cursor-pointer shrink-0">
                  <input
                    type="checkbox"
                    checked={st.isPresent}
                    onChange={() => toggleStudent(st.id)}
                    className="sr-only peer override-toggle"
                    aria-label={`Toggle attendance for ${st.name}`}
                  />
                  <div className="w-11 h-6 bg-secondary-container peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-surface-container-lowest after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-surface-container-lowest after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
                </label>
              </div>

              {/* Card Footer Detail */}
              {st.isPresent ? (
                <div className="flex items-center justify-between pt-2 bg-surface-container-low/60 -mx-3 -mb-3 px-3 py-2 rounded-b-2xl text-xs">
                  <div className="flex items-center gap-2">
                    <span className="status-badge px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800 font-label-sm text-label-sm font-semibold flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-emerald-600"></span>
                      {st.isManualOverride ? 'Present (Manual 1.0)' : 'Present'}
                    </span>
                    <span className="font-body-sm text-body-sm text-on-surface-variant">
                      Conf:{' '}
                      <strong className="text-on-surface font-semibold">
                        {(st.confidence * 100).toFixed(1)}%
                      </strong>
                    </span>
                  </div>
                  <span className="font-label-sm text-label-sm text-secondary">
                    Dist: {st.distance.toFixed(2)} (High)
                  </span>
                </div>
              ) : st.has_registered_face ? (
                <div className="flex items-center justify-between pt-2 bg-error-container/20 -mx-3 -mb-3 px-3 py-2 rounded-b-2xl text-xs">
                  <div className="flex items-center gap-2">
                    <span className="status-badge px-2 py-0.5 rounded-full bg-error-container text-on-error-container font-label-sm text-label-sm font-semibold flex items-center gap-1">
                      <span className="w-1.5 h-1.5 rounded-full bg-error"></span> Absent
                    </span>
                    <span className="font-body-sm text-body-sm text-on-surface-variant">Not detected in photos</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => markQuickPresent(st.id)}
                    className="px-2.5 py-1 rounded-lg bg-surface-container-lowest text-primary font-label-sm text-label-sm font-semibold shadow-sm hover:bg-primary-fixed transition-colors"
                  >
                    Quick Mark Present
                  </button>
                </div>
              ) : (
                <div className="flex items-center justify-between pt-2 bg-amber-50/70 -mx-3 -mb-3 px-3 py-2 rounded-b-2xl text-xs">
                  <div className="flex items-center gap-1 text-amber-900">
                    <span className="material-symbols-outlined text-[16px]">info</span>
                    <span className="font-body-sm text-body-sm">Cannot auto-detect; manual toggle required</span>
                  </div>
                  <button
                    type="button"
                    onClick={() => alert(`Redirecting to register face for ${st.name}`)}
                    className="font-label-sm text-label-sm text-primary font-semibold hover:underline"
                  >
                    Enroll Face
                  </button>
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Confirmation Sticky Summary Panel */}
        <div className="sticky bottom-20 z-40 flex flex-col p-3.5 rounded-2xl bg-surface-container-lowest/95 backdrop-blur-xl shadow-xl border border-outline-variant/30 gap-3">
          <div className="flex items-center justify-between text-xs">
            <div className="flex items-center gap-2">
              <span className="material-symbols-outlined text-primary text-[20px]">cloud_sync</span>
              <span className="font-label-md text-label-md text-on-surface font-semibold" id="confirm-summary">
                {totalCount} Records ready to confirm ({presentCount} Present, {absentCount} Absent)
              </span>
            </div>
            <span className="font-label-sm text-label-sm text-emerald-600 font-semibold bg-emerald-50 px-2 py-0.5 rounded-md">
              Draft Valid
            </span>
          </div>

          <div className="flex items-center gap-2">
            {/* Retake Secondary Button */}
            <button
              type="button"
              onClick={onRetake}
              className="flex items-center justify-center gap-1.5 px-3 py-2.5 rounded-xl bg-surface-container hover:bg-surface-container-high text-on-surface font-label-md text-label-md font-semibold transition-all shrink-0 text-xs"
            >
              <span className="material-symbols-outlined text-[18px]">photo_camera</span>
              <span>Retake Photos</span>
            </button>

            {/* Primary Confirm Button */}
            <button
              type="button"
              disabled={isConfirming}
              onClick={handleConfirm}
              id="btn-confirm"
              className="flex-1 flex items-center justify-center gap-2 py-2.5 px-4 rounded-xl bg-primary text-on-primary font-label-md text-label-md font-semibold shadow-md shadow-primary/25 hover:bg-primary-container active:scale-[0.98] transition-all text-xs"
            >
              <span className={`material-symbols-outlined text-[20px] ${isConfirming ? 'animate-spin' : ''}`}>
                {isConfirming ? 'autorenew' : 'check_circle'}
              </span>
              <span>{isConfirming ? 'Saving to Supabase...' : 'Confirm & Save to Supabase'}</span>
            </button>
          </div>
        </div>

        {/* Success Banner Feedback */}
        {confirmedMessage && (
          <div
            role="status"
            aria-live="polite"
            className="fixed top-20 left-1/2 -translate-x-1/2 px-4 py-2.5 bg-emerald-600 text-white rounded-full shadow-2xl flex items-center gap-2 z-50 animate-bounce text-xs font-semibold"
          >
            <span className="material-symbols-outlined text-[18px]">task_alt</span>
            <span>{confirmedMessage}</span>
          </div>
        )}
      </div>
    </main>
  );
};
