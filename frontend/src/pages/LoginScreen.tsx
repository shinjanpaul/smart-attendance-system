import React, { useState } from 'react';
import { Role } from '../types/attendance';

interface LoginScreenProps {
  onLoginSuccess: (user: { username: string; role: Role }) => void;
}

export const LoginScreen: React.FC<LoginScreenProps> = ({ onLoginSuccess }) => {
  const [role, setRole] = useState<'teacher' | 'student'>('teacher');
  const [username, setUsername] = useState('prof_sharma');
  const [isLoading, setIsLoading] = useState(false);
  const [toastMessage, setToastMessage] = useState<string | null>(null);
  const [toastIsError, setToastIsError] = useState(false);

  const showToast = (msg: string, isError = false) => {
    setToastMessage(msg);
    setToastIsError(isError);
    setTimeout(() => setToastMessage(null), 2800);
  };

  const handleRoleChange = (newRole: 'teacher' | 'student') => {
    setRole(newRole);
    if (newRole === 'teacher') {
      setUsername('prof_sharma');
    } else {
      setUsername('shinjan_paul');
    }
  };

  const fillPreset = (uname: string, userRole: 'teacher' | 'student') => {
    setRole(userRole);
    setUsername(uname);
    showToast(`Loaded ${userRole === 'teacher' ? 'Faculty' : 'Student'} preset: ${uname}`);
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (!username.trim()) {
      showToast('Please enter a username or select a quick dev account', true);
      return;
    }

    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      onLoginSuccess({
        username: username.trim(),
        role: role === 'teacher' ? 'TEACHER' : 'STUDENT',
      });
    }, 600);
  };

  return (
    <main className="flex flex-col relative w-full bg-surface min-h-screen pt-safe pb-safe items-center justify-center p-4">
      <div className="flex flex-col w-full max-w-md pb-space-xl">
        {/* Ambient Graphic Glow Layer */}
        <div className="relative w-full overflow-hidden rounded-2xl bg-gradient-to-b from-primary-fixed/40 via-surface-container-low to-surface p-space-md mb-space-md shadow-sm border border-outline-variant/30">
          <div className="absolute -top-12 -right-12 w-40 h-40 bg-primary-fixed-dim/30 rounded-full blur-2xl pointer-events-none"></div>
          <div className="absolute -bottom-8 -left-8 w-32 h-32 bg-secondary-fixed/40 rounded-full blur-xl pointer-events-none"></div>

          {/* Brand Header */}
          <div className="relative z-10 flex flex-col items-center text-center pt-space-xs pb-space-sm">
            <div className="relative mb-space-sm">
              <div className="w-20 h-20 rounded-2xl bg-surface-container-lowest shadow-md flex items-center justify-center p-2 transform active:scale-95 transition-transform duration-200">
                <span className="material-symbols-outlined text-primary text-[44px]">face</span>
              </div>
              <div className="absolute -bottom-1 -right-1 w-5 h-5 bg-surface-container-lowest rounded-full flex items-center justify-center shadow-sm">
                <span className="w-3 h-3 bg-primary-container rounded-full animate-pulse"></span>
              </div>
            </div>

            <h1 className="font-headline-lg-mobile text-headline-lg-mobile text-on-surface tracking-tight mb-1 font-bold">
              VeriFace
            </h1>
            <p className="font-body-sm text-body-sm text-secondary max-w-[260px] leading-relaxed">
              Smart Attendance Powered by <span className="font-label-sm text-primary font-semibold">dlib 128-D Deep ResNet</span>
            </p>

            {/* Architecture Tech Pill */}
            <div className="mt-space-sm inline-flex items-center gap-1.5 px-3 py-1 rounded-full bg-surface-container-high text-on-surface-variant text-center">
              <span className="material-symbols-outlined text-[14px] text-primary">terminal</span>
              <span className="font-label-sm text-label-sm text-xs truncate">Django 5 + DRF • Supabase PostgreSQL • AllowAny</span>
            </div>
          </div>
        </div>

        {/* Role Selector & Auth Card */}
        <form onSubmit={handleLogin} className="w-full bg-surface-container-lowest rounded-2xl p-space-md shadow-sm border border-outline-variant/30 flex flex-col gap-space-md">
          {/* Interactive Role Toggle */}
          <div className="flex flex-col gap-1.5">
            <label className="font-label-md text-label-md text-secondary">Select Active Identity</label>
            <div className="grid grid-cols-2 p-1 bg-surface-container rounded-xl relative" role="tablist">
              <button
                type="button"
                role="tab"
                aria-selected={role === 'teacher'}
                onClick={() => handleRoleChange('teacher')}
                className={`flex items-center justify-center gap-1.5 py-2.5 rounded-lg font-label-lg text-label-lg transition-all duration-200 ${
                  role === 'teacher'
                    ? 'bg-surface-container-lowest text-primary shadow-sm font-semibold'
                    : 'text-secondary hover:text-on-surface'
                }`}
              >
                <span className="material-symbols-outlined text-[18px]">school</span>
                <span>Teacher Portal</span>
              </button>

              <button
                type="button"
                role="tab"
                aria-selected={role === 'student'}
                onClick={() => handleRoleChange('student')}
                className={`flex items-center justify-center gap-1.5 py-2.5 rounded-lg font-label-lg text-label-lg transition-all duration-200 ${
                  role === 'student'
                    ? 'bg-surface-container-lowest text-primary shadow-sm font-semibold'
                    : 'text-secondary hover:text-on-surface'
                }`}
              >
                <span className="material-symbols-outlined text-[18px]">badge</span>
                <span>Student Portal</span>
              </button>
            </div>
          </div>

          {/* Username Field */}
          <div className="flex flex-col gap-1.5">
            <div className="flex justify-between items-center">
              <label className="font-label-md text-label-md text-on-surface font-medium" htmlFor="username-input">
                Portal Username
              </label>
              <span className="font-label-sm text-label-sm px-2 py-0.5 rounded-full bg-primary-fixed text-on-primary-fixed-variant text-xs font-semibold">
                {role === 'teacher' ? 'Faculty Mode' : 'Student Mode'}
              </span>
            </div>

            <div className="relative flex items-center">
              <div className="absolute left-3 flex items-center pointer-events-none text-secondary">
                <span className="material-symbols-outlined text-[20px]">account_circle</span>
              </div>
              <input
                id="username-input"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="e.g. shinjan_paul or prof_sharma"
                className="w-full pl-10 pr-10 py-3 bg-surface-container-low text-on-surface font-body-md text-body-md rounded-xl focus:outline-none focus:bg-surface-container-lowest focus:ring-2 focus:ring-primary/20 transition-all placeholder:text-outline-variant"
              />
              {username && (
                <button
                  type="button"
                  onClick={() => setUsername('')}
                  aria-label="Clear username input"
                  className="absolute right-3 flex items-center text-secondary hover:text-on-surface"
                >
                  <span className="material-symbols-outlined text-[18px]">cancel</span>
                </button>
              )}
            </div>
            <p className="font-body-sm text-body-sm text-secondary flex items-center gap-1 text-xs">
              <span className="material-symbols-outlined text-[14px]">info</span>
              <span>
                Enter registered username (e.g. <strong className="text-on-surface">shinjan_paul</strong> or <strong className="text-on-surface">prof_sharma</strong>)
              </span>
            </p>
          </div>

          {/* Quick Dev Login Presets */}
          <div className="flex flex-col gap-2 pt-1">
            <div className="flex items-center justify-between">
              <span className="font-label-sm text-label-sm text-outline uppercase tracking-wider text-xs font-semibold">
                Quick Dev Auth Fill
              </span>
              <span className="font-label-sm text-label-sm text-primary flex items-center gap-0.5 text-xs font-semibold">
                <span className="material-symbols-outlined text-[12px]">bolt</span> Ready
              </span>
            </div>

            <div className="flex flex-col sm:flex-row gap-2">
              <button
                type="button"
                onClick={() => fillPreset('prof_sharma', 'teacher')}
                className="flex-1 flex items-center justify-between p-2.5 rounded-xl bg-surface-container-low hover:bg-surface-container text-left transition-colors group"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <div className="w-7 h-7 rounded-full bg-primary-fixed flex items-center justify-center text-primary shrink-0">
                    <span className="material-symbols-outlined text-[16px]">psychology</span>
                  </div>
                  <div className="min-w-0">
                    <p className="font-label-md text-label-md text-on-surface text-xs font-semibold truncate">Teacher (Dr. R. Sharma)</p>
                    <p className="font-body-sm text-body-sm text-secondary text-xs truncate">prof_sharma</p>
                  </div>
                </div>
                <span className="material-symbols-outlined text-outline-variant group-hover:text-primary transition-colors text-[18px] ml-1 shrink-0">
                  input
                </span>
              </button>

              <button
                type="button"
                onClick={() => fillPreset('shinjan_paul', 'student')}
                className="flex-1 flex items-center justify-between p-2.5 rounded-xl bg-surface-container-low hover:bg-surface-container text-left transition-colors group"
              >
                <div className="flex items-center gap-2 min-w-0">
                  <div className="w-7 h-7 rounded-full bg-secondary-fixed flex items-center justify-center text-secondary shrink-0">
                    <span className="material-symbols-outlined text-[16px]">person</span>
                  </div>
                  <div className="min-w-0">
                    <p className="font-label-md text-label-md text-on-surface text-xs font-semibold truncate">Student (Shinjan Paul)</p>
                    <p className="font-body-sm text-body-sm text-secondary text-xs truncate">IT202601</p>
                  </div>
                </div>
                <span className="material-symbols-outlined text-outline-variant group-hover:text-primary transition-colors text-[18px] ml-1 shrink-0">
                  input
                </span>
              </button>
            </div>
          </div>

          {/* Primary CTA Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full mt-2 py-3.5 px-space-md rounded-xl bg-primary hover:bg-primary-container active:scale-[0.99] text-on-primary font-title-md text-title-md flex items-center justify-center gap-2 shadow-md transition-all duration-150 font-semibold"
          >
            {isLoading ? (
              <>
                <span className="material-symbols-outlined text-[20px] animate-spin">sync</span>
                <span>Authenticating...</span>
              </>
            ) : (
              <>
                <span>{role === 'teacher' ? 'Sign In to Teacher Portal' : 'Sign In to Student Portal'}</span>
                <span className="material-symbols-outlined text-[20px]">arrow_forward</span>
              </>
            )}
          </button>
        </form>

        {/* API Diagnostics Banner */}
        <div className="mt-space-md bg-surface-container-low rounded-2xl p-space-md flex flex-col gap-2 border border-outline-variant/20">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 shadow-sm animate-ping"></span>
              <span className="font-label-md text-label-md text-on-surface font-semibold ml-1">Live Backend Status</span>
            </div>
            <span className="font-label-sm text-label-sm px-2 py-0.5 rounded-full bg-surface-container-highest text-tertiary font-semibold text-xs">
              Django 5 + Supabase
            </span>
          </div>

          <div className="flex flex-col gap-1 text-on-surface-variant font-body-sm text-body-sm pt-1 text-xs">
            <div className="flex items-center justify-between bg-surface-container-lowest px-2.5 py-1.5 rounded-lg">
              <span className="text-secondary">Base API URL:</span>
              <code className="font-mono text-on-surface bg-surface-container px-1.5 py-0.5 rounded text-xs select-all">
                http://127.0.0.1:8000/api/
              </code>
            </div>
            <div className="flex items-center justify-between bg-surface-container-lowest px-2.5 py-1.5 rounded-lg">
              <span className="text-secondary">CORS Policy:</span>
              <span className="font-label-sm text-label-sm text-emerald-700 font-semibold flex items-center gap-1">
                <span className="material-symbols-outlined text-[14px]">lock_open</span> Open / Dev Unrestricted
              </span>
            </div>
          </div>
        </div>

        {/* Micro Toast Feedback */}
        {toastMessage && (
          <div
            role="status"
            aria-live="polite"
            className="fixed bottom-6 left-1/2 -translate-x-1/2 max-w-[90vw] px-4 py-2 bg-inverse-surface text-inverse-on-surface rounded-full shadow-xl flex items-center gap-2 z-50 animate-bounce"
          >
            <span className={`material-symbols-outlined text-[18px] ${toastIsError ? 'text-error' : 'text-primary-fixed'}`}>
              {toastIsError ? 'error' : 'check_circle'}
            </span>
            <span className="font-label-md text-label-md text-sm">{toastMessage}</span>
          </div>
        )}
      </div>
    </main>
  );
};
