import React, { useState, useRef } from 'react';
import { DraftResult } from '../types/attendance';
import { processClassroomPhotos } from '../api/attendanceApi';

interface StagedPhoto {
  id: string;
  file: File;
  previewUrl: string;
  name: string;
  size: string;
  angleTag: string;
}

interface TakeAttendanceScreenProps {
  onProcessComplete: (draft: DraftResult) => void;
}

export const TakeAttendanceScreen: React.FC<TakeAttendanceScreenProps> = ({ onProcessComplete }) => {
  const [activeMode, setActiveMode] = useState<'photos' | 'live'>('photos');
  const [isProcessing, setIsProcessing] = useState(false);
  const [photos, setPhotos] = useState<StagedPhoto[]>([
    {
      id: '1',
      file: new File(['mock1'], 'classroom_angle_1.jpg', { type: 'image/jpeg' }),
      previewUrl:
        'https://images.unsplash.com/photo-1577896851231-70ef18881754?auto=format&fit=crop&w=400&q=80',
      name: 'classroom_angle_1.jpg',
      size: '4.2 MB',
      angleTag: 'Angle 35° W',
    },
    {
      id: '2',
      file: new File(['mock2'], 'classroom_center.jpg', { type: 'image/jpeg' }),
      previewUrl:
        'https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=400&q=80',
      name: 'classroom_center.jpg',
      size: '5.8 MB',
      angleTag: 'Direct frontal',
    },
    {
      id: '3',
      file: new File(['mock3'], 'front_row.jpg', { type: 'image/jpeg' }),
      previewUrl:
        'https://images.unsplash.com/photo-1516321318423-f06f85e504b3?auto=format&fit=crop&w=400&q=80',
      name: 'front_row.jpg',
      size: '3.9 MB',
      angleTag: 'Near focus',
    },
  ]);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files) return;
    const newFiles: StagedPhoto[] = Array.from(e.target.files).map((file, idx) => ({
      id: `${Date.now()}_${idx}`,
      file,
      previewUrl: URL.createObjectURL(file),
      name: file.name,
      size: `${(file.size / (1024 * 1024)).toFixed(1)} MB`,
      angleTag: `Angle #${photos.length + idx + 1}`,
    }));
    setPhotos((prev) => [...prev, ...newFiles]);
  };

  const removePhoto = (id: string) => {
    setPhotos((prev) => prev.filter((p) => p.id !== id));
  };

  const clearAll = () => {
    setPhotos([]);
  };

  const handleProcess = async () => {
    setIsProcessing(true);
    const filesToUpload = photos.map((p) => p.file);
    const draft = await processClassroomPhotos(1, 1, filesToUpload);
    setTimeout(() => {
      setIsProcessing(false);
      onProcessComplete(draft);
    }, 1200);
  };

  return (
    <main className="flex flex-col relative w-full pt-16 pb-24 bg-surface min-h-screen">
      <div className="flex flex-col w-full max-w-lg mx-auto px-4 space-y-space-md">
        {/* Step Indicator & Context Ribbon */}
        <div className="flex flex-col gap-space-xs mt-space-sm">
          <div className="flex items-center justify-between">
            <div className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-primary-fixed text-on-primary-fixed-variant shadow-sm">
              <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse" aria-hidden="true"></span>
              <span className="font-label-sm text-label-sm uppercase tracking-wider font-semibold text-xs">
                Step 1 of 2
              </span>
            </div>
            <span className="font-label-sm text-label-sm text-on-surface-variant font-medium text-xs">
              Capture &amp; AI Process (Draft Mode)
            </span>
          </div>
          <div className="w-full bg-surface-container-high h-1.5 rounded-full overflow-hidden">
            <div className="bg-primary h-full w-1/2 rounded-full transition-all duration-500"></div>
          </div>
        </div>

        {/* Class & Subject Info Card */}
        <div className="flex flex-col p-space-md rounded-2xl bg-surface-container-lowest shadow-sm border border-outline-variant/30 space-y-space-xs">
          <div className="flex items-center justify-between text-on-surface-variant text-xs">
            <span className="font-label-sm text-label-sm uppercase tracking-wider font-semibold">Active Roll Call</span>
            <span className="flex items-center gap-1 font-label-sm text-label-sm text-primary font-semibold">
              <span className="material-symbols-outlined text-[16px]">verified</span>
              Auto-Sync
            </span>
          </div>

          <div className="flex flex-wrap gap-space-xs pt-1">
            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-surface-container text-on-surface font-label-md text-label-md text-xs font-semibold">
              <span className="material-symbols-outlined text-[18px] text-primary">school</span>
              <span>B.Tech IT • 4th Year • Sec A</span>
            </div>
            <div className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-secondary-container text-on-secondary-container font-label-md text-label-md text-xs font-semibold">
              <span className="material-symbols-outlined text-[18px]">dns</span>
              <span>IT801 • Distributed OS</span>
            </div>
          </div>
        </div>

        {/* Capture Mode Switcher */}
        <div className="p-1 rounded-xl bg-surface-container flex items-center gap-1" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={activeMode === 'photos'}
            onClick={() => setActiveMode('photos')}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg font-label-md text-label-md text-xs font-semibold transition-all ${
              activeMode === 'photos'
                ? 'bg-surface-container-lowest text-on-surface shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            <span className="material-symbols-outlined text-[18px] text-primary">add_photo_alternate</span>
            <span>Classroom Photos</span>
          </button>

          <button
            type="button"
            role="tab"
            aria-selected={activeMode === 'live'}
            onClick={() => setActiveMode('live')}
            className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 rounded-lg font-label-md text-label-md text-xs font-semibold transition-all ${
              activeMode === 'live'
                ? 'bg-surface-container-lowest text-on-surface shadow-sm'
                : 'text-on-surface-variant hover:text-on-surface'
            }`}
          >
            <span className="material-symbols-outlined text-[18px]">videocam</span>
            <span>Live Stream</span>
          </button>
        </div>

        {/* Mode 1: Multi-Photo Upload Area */}
        {activeMode === 'photos' ? (
          <div className="flex flex-col space-y-space-md">
            {/* Dropzone Box */}
            <div
              onClick={() => fileInputRef.current?.click()}
              className="relative flex flex-col items-center justify-center p-space-lg rounded-2xl bg-surface-container-lowest shadow-sm border-2 border-dashed border-primary/20 text-center cursor-pointer group active:scale-[0.99] transition-transform overflow-hidden"
            >
              <div className="w-14 h-14 rounded-full bg-primary-fixed flex items-center justify-center text-primary mb-space-sm group-hover:scale-110 transition-transform shadow-inner">
                <span className="material-symbols-outlined text-[28px]">cloud_upload</span>
              </div>
              <h3 className="font-headline-sm text-headline-sm text-on-surface font-semibold text-base">
                Tap or Drop Classroom Shots
              </h3>
              <p className="font-body-sm text-body-sm text-on-surface-variant max-w-[280px] mt-1 text-xs">
                Supports JPG, PNG, HEIC up to 25MB each. Multi-angle classroom captures yield highest verification accuracy.
              </p>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
                aria-label="Upload Classroom Photos"
              />
            </div>

            {/* Pro-Tip Callout */}
            <div className="flex items-start gap-space-sm p-space-md rounded-2xl bg-surface-container-low shadow-sm border border-outline-variant/20">
              <div className="w-8 h-8 rounded-full bg-primary/10 flex items-center justify-center shrink-0 text-primary">
                <span className="material-symbols-outlined text-[20px]">lightbulb</span>
              </div>
              <div className="flex flex-col min-w-0">
                <span className="font-label-md text-label-md text-on-surface font-semibold text-xs">
                  Pro-Tip for High Recall
                </span>
                <p className="font-body-sm text-body-sm text-on-surface-variant mt-0.5 text-xs">
                  Upload 1+ classroom photos from different angles (left, center, right) to capture occluded faces across tiered desks.
                </p>
              </div>
            </div>

            {/* Uploaded Photos Gallery Preview */}
            <div className="flex flex-col space-y-space-xs">
              <div className="flex items-center justify-between px-1">
                <div className="flex items-center gap-1.5">
                  <span className="font-label-md text-label-md text-on-surface font-semibold text-xs">
                    Staged Angle Captures
                  </span>
                  <span className="px-2 py-0.5 rounded-full bg-surface-container-high text-on-surface-variant font-label-sm text-label-sm font-semibold text-xs">
                    {photos.length} files
                  </span>
                </div>
                {photos.length > 0 && (
                  <button
                    type="button"
                    onClick={clearAll}
                    className="font-label-sm text-label-sm text-primary font-semibold hover:underline text-xs"
                  >
                    Clear all
                  </button>
                )}
              </div>

              <div className="space-y-space-xs">
                {photos.map((photo) => (
                  <div
                    key={photo.id}
                    className="flex items-center justify-between p-space-sm rounded-2xl bg-surface-container-lowest shadow-sm border border-outline-variant/20 gap-space-sm hover:shadow-md transition-shadow"
                  >
                    <div className="flex items-center gap-space-sm min-w-0">
                      <div className="relative w-14 h-14 rounded-xl overflow-hidden bg-surface-container shrink-0">
                        <img src={photo.previewUrl} alt={photo.name} className="w-full h-full object-cover" />
                        <span className="absolute bottom-1 left-1 px-1 rounded bg-inverse-surface/80 text-inverse-on-surface text-[10px] leading-tight font-medium">
                          {photo.angleTag.split(' ')[0]}
                        </span>
                      </div>
                      <div className="flex flex-col min-w-0">
                        <span className="font-label-md text-label-md text-on-surface font-semibold truncate text-xs">
                          {photo.name}
                        </span>
                        <div className="flex items-center gap-1.5 mt-0.5">
                          <span className="px-1.5 py-0.5 rounded bg-surface-container-high text-on-surface-variant text-[10px] font-medium">
                            {photo.size}
                          </span>
                          <span className="font-body-sm text-body-sm text-on-surface-variant text-[10px]">
                            • {photo.angleTag}
                          </span>
                        </div>
                      </div>
                    </div>

                    <button
                      type="button"
                      onClick={() => removePhoto(photo.id)}
                      aria-label={`Remove image ${photo.name}`}
                      className="w-9 h-9 rounded-full flex items-center justify-center text-on-surface-variant hover:bg-surface-container transition-colors shrink-0"
                    >
                      <span className="material-symbols-outlined text-[18px]">close</span>
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ) : (
          /* Mode 2: Live Camera Viewfinder Preview */
          <div className="flex flex-col space-y-space-md">
            <div className="relative w-full aspect-video rounded-2xl overflow-hidden bg-inverse-surface shadow-md flex items-center justify-center">
              <img
                src="https://images.unsplash.com/photo-1524178232363-1fb2b075b655?auto=format&fit=crop&w=600&q=80"
                alt="Live Classroom Feed"
                className="w-full h-full object-cover opacity-80"
              />
              <div className="absolute inset-4 rounded-lg pointer-events-none flex flex-col justify-between">
                <div className="flex justify-between items-start">
                  <div className="w-6 h-6 border-l-2 border-t-2 border-primary-fixed"></div>
                  <div className="px-2 py-0.5 rounded bg-inverse-surface/80 text-inverse-on-surface text-xs font-semibold flex items-center gap-1">
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-ping"></span>
                    FEED ACTIVE • 1080p
                  </div>
                  <div className="w-6 h-6 border-r-2 border-t-2 border-primary-fixed"></div>
                </div>

                <div className="absolute top-[32%] left-[44%] w-16 h-20 rounded bg-primary/10 border border-primary-fixed flex flex-col justify-between p-1 shadow-sm">
                  <span className="px-1 rounded bg-primary text-on-primary text-[10px] self-start leading-none py-0.5 font-bold">
                    98.4%
                  </span>
                  <span className="text-on-primary text-[9px] truncate bg-inverse-surface/70 px-0.5 rounded">
                    ID: #4012
                  </span>
                </div>

                <div className="flex justify-between items-end">
                  <div className="w-6 h-6 border-l-2 border-b-2 border-primary-fixed"></div>
                  <button
                    type="button"
                    onClick={() => {
                      alert('Live camera frame snapped!');
                    }}
                    className="pointer-events-auto px-4 py-1.5 rounded-full bg-surface-container-lowest/90 backdrop-blur-md text-on-surface text-xs font-semibold flex items-center gap-1.5 shadow-md active:scale-95 transition-transform"
                  >
                    <span className="material-symbols-outlined text-[18px] text-primary">camera</span>
                    Snap Angle
                  </button>
                  <div className="w-6 h-6 border-r-2 border-b-2 border-primary-fixed"></div>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Technical Info Card */}
        <div className="p-space-md rounded-2xl bg-surface-container-low shadow-sm border border-outline-variant/20 flex items-start gap-space-sm">
          <div className="w-9 h-9 rounded-xl bg-surface-container-highest flex items-center justify-center shrink-0 text-primary">
            <span className="material-symbols-outlined text-[20px]">psychology</span>
          </div>
          <div className="flex flex-col min-w-0 space-y-1">
            <div className="flex items-center gap-2">
              <span className="font-label-md text-label-md text-on-surface font-semibold text-xs">
                AI Engine: Multi-scale dlib ResNet
              </span>
              <span className="px-1.5 py-0.2 rounded bg-tertiary-fixed text-on-tertiary-fixed text-[10px] font-bold">
                v3.4
              </span>
            </div>
            <p className="font-body-sm text-body-sm text-on-surface-variant leading-relaxed text-xs">
              Multi-face bounding box alignment + 128-D vector distance calculation against enrolled student centroids (threshold ≤ 0.60).
            </p>
          </div>
        </div>

        {/* Big Action Button */}
        <div className="flex flex-col space-y-space-xs pt-space-xs">
          <button
            type="button"
            disabled={isProcessing || photos.length === 0}
            onClick={handleProcess}
            className="w-full py-3.5 px-space-md rounded-2xl bg-primary text-on-primary font-headline-sm text-headline-sm flex items-center justify-center gap-2 shadow-lg shadow-primary/25 hover:bg-primary-container active:scale-[0.98] transition-all disabled:opacity-60 text-sm font-semibold"
          >
            {isProcessing ? (
              <>
                <span className="material-symbols-outlined text-[24px] animate-spin">autorenew</span>
                <span>Analyzing 128-D Biometrics...</span>
              </>
            ) : (
              <>
                <span className="material-symbols-outlined text-[24px]">auto_awesome</span>
                <span>Process Attendance with AI</span>
              </>
            )}
          </button>

          {isProcessing && (
            <div className="flex items-center justify-center gap-2 p-space-sm rounded-xl bg-surface-container text-on-surface-variant text-xs animate-pulse">
              <span className="material-symbols-outlined text-[18px] text-primary animate-spin">progress_activity</span>
              <span>Matching faces against enrolled class roster. Results will open in Review screen.</span>
            </div>
          )}

          <div className="flex items-center justify-center gap-1.5 text-on-surface-variant py-1 text-xs">
            <span className="material-symbols-outlined text-[16px] text-emerald-600">security</span>
            <span className="font-label-sm text-label-sm">Privacy safe: Biometrics matched locally in memory</span>
          </div>
        </div>
      </div>
    </main>
  );
};
