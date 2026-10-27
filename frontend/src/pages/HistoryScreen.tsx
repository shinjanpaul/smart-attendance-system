import React, { useState } from 'react';
import { AttendanceLog } from '../types/attendance';

export const HistoryScreen: React.FC = () => {
  const [logs] = useState<AttendanceLog[]>([
    {
      id: 1,
      student: 3,
      student_name: 'shinjan_paul',
      student_roll: 'IT202601',
      student_class: 1,
      class_name: 'B.Tech IT • 4A',
      subject: 1,
      subject_name: 'Distributed Operating Systems',
      date: '2026-10-17',
      timestamp: '2026-10-17T10:15:00Z',
      status: 'PRESENT',
      verification_method: 'FACE_RECOGNITION',
      confidence_score: 0.865,
      snapshot: null,
    },
    {
      id: 2,
      student: 4,
      student_name: 'biswajit_sinha',
      student_roll: 'IT202602',
      student_class: 1,
      class_name: 'B.Tech IT • 4A',
      subject: 1,
      subject_name: 'Distributed Operating Systems',
      date: '2026-10-17',
      timestamp: '2026-10-17T10:15:00Z',
      status: 'PRESENT',
      verification_method: 'FACE_RECOGNITION',
      confidence_score: 0.912,
      snapshot: null,
    },
    {
      id: 3,
      student: 5,
      student_name: 'priya_sharma',
      student_roll: 'IT202603',
      student_class: 1,
      class_name: 'B.Tech IT • 4A',
      subject: 1,
      subject_name: 'Distributed Operating Systems',
      date: '2026-10-17',
      timestamp: '2026-10-17T10:15:00Z',
      status: 'PRESENT',
      verification_method: 'FACE_RECOGNITION',
      confidence_score: 0.89,
      snapshot: null,
    },
    {
      id: 4,
      student: 6,
      student_name: 'ayush_nyas',
      student_roll: 'IT202604',
      student_class: 1,
      class_name: 'B.Tech IT • 4A',
      subject: 1,
      subject_name: 'Distributed Operating Systems',
      date: '2026-10-17',
      timestamp: '2026-10-17T10:15:00Z',
      status: 'ABSENT',
      verification_method: 'FACE_RECOGNITION',
      confidence_score: 0.0,
      snapshot: null,
    },
  ]);

  const [search, setSearch] = useState('');

  const filteredLogs = logs.filter(
    (l) =>
      l.student_name.toLowerCase().includes(search.toLowerCase()) ||
      l.student_roll.toLowerCase().includes(search.toLowerCase())
  );

  const exportCSV = () => {
    const headers = ['Date', 'Student Name', 'Roll Number', 'Class', 'Subject', 'Status', 'Confidence'];
    const rows = filteredLogs.map((l) => [
      l.date,
      l.student_name,
      l.student_roll,
      l.class_name,
      l.subject_name,
      l.status,
      `${(l.confidence_score * 100).toFixed(1)}%`,
    ]);

    const csvContent =
      'data:text/csv;charset=utf-8,' + [headers.join(','), ...rows.map((e) => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement('a');
    link.setAttribute('href', encodedUri);
    link.setAttribute('download', `Attendance_Report_${new Date().toISOString().split('T')[0]}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <main className="flex flex-col relative w-full pt-16 pb-28 bg-surface min-h-screen">
      <div className="flex flex-col w-full max-w-lg mx-auto px-4 space-y-space-md">
        <div className="flex items-center justify-between mt-space-sm">
          <div>
            <h1 className="font-bold text-xl text-on-surface">Attendance History</h1>
            <p className="text-xs text-secondary">Verified records synced with Supabase</p>
          </div>
          <button
            type="button"
            onClick={exportCSV}
            className="px-3 py-2 rounded-xl bg-primary text-white text-xs font-semibold flex items-center gap-1.5 shadow-md active:scale-95 transition-all"
          >
            <span className="material-symbols-outlined text-[16px]">download</span>
            <span>Export CSV</span>
          </button>
        </div>

        {/* Search Bar */}
        <div className="relative">
          <span className="material-symbols-outlined absolute left-3 top-2.5 text-secondary text-[20px]">
            search
          </span>
          <input
            type="text"
            placeholder="Search by student name or roll..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 bg-surface-container-low rounded-xl text-xs text-on-surface focus:outline-none focus:ring-2 focus:ring-primary/20"
          />
        </div>

        {/* Records Table */}
        <div className="rounded-2xl bg-surface-container-lowest shadow-sm border border-outline-variant/30 overflow-hidden">
          <table className="w-full text-left text-xs" aria-label="Attendance History Table">
            <thead className="bg-surface-container-low text-secondary font-semibold text-[11px] border-b border-outline-variant/20">
              <tr>
                <th className="p-3">Student</th>
                <th className="p-3">Status</th>
                <th className="p-3">Confidence</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/20">
              {filteredLogs.map((log) => (
                <tr key={log.id} className="hover:bg-surface-container-low/50">
                  <td className="p-3">
                    <div className="font-bold text-on-surface">{log.student_name}</div>
                    <div className="text-[10px] text-secondary">
                      {log.student_roll} • {log.date}
                    </div>
                  </td>
                  <td className="p-3">
                    <span
                      className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                        log.status === 'PRESENT'
                          ? 'bg-emerald-100 text-emerald-800'
                          : 'bg-error-container text-on-error-container'
                      }`}
                    >
                      {log.status}
                    </span>
                  </td>
                  <td className="p-3 font-semibold text-secondary">
                    {log.confidence_score > 0 ? `${(log.confidence_score * 100).toFixed(1)}%` : '—'}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </main>
  );
};
