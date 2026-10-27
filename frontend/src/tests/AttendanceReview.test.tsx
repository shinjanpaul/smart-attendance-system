import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import React from 'react';
import { AttendanceReviewScreen } from '../pages/AttendanceReviewScreen';
import { DraftResult } from '../types/attendance';

const mockDraft: DraftResult = {
  total_photos_processed: 2,
  total_faces_detected: 4,
  unmatched_faces_count: 0,
  present_count: 2,
  absent_count: 1,
  class_id: 1,
  subject_id: 1,
  date: '2026-10-17',
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
  ],
  absent_students: [
    {
      id: 6,
      username: 'ayush_nyas',
      name: 'Ayush Nyas',
      roll_number: 'IT202604',
      has_registered_face: true,
    },
  ],
  match_details: [
    {
      photo_index: 1,
      student_id: 3,
      student_name: 'Shinjan Paul',
      roll_number: 'IT202601',
      distance: 0.38,
      confidence: 0.865,
    },
    {
      photo_index: 1,
      student_id: 4,
      student_name: 'Biswajit Sinha',
      roll_number: 'IT202602',
      distance: 0.32,
      confidence: 0.912,
    },
  ],
};

describe('AttendanceReviewScreen Component', () => {
  it('renders student list and displays correct Present / Absent counts in bento cards', () => {
    render(
      <AttendanceReviewScreen
        draftData={mockDraft}
        onRetake={vi.fn()}
        onConfirmedSuccess={vi.fn()}
      />
    );

    // Verify student names are rendered
    expect(screen.getByText('Shinjan Paul')).toBeInTheDocument();
    expect(screen.getByText('Biswajit Sinha')).toBeInTheDocument();
    expect(screen.getByText('Ayush Nyas')).toBeInTheDocument();

    // Verify Bento stats
    expect(screen.getByText('2')).toBeInTheDocument(); // Present count
    expect(screen.getByText('1')).toBeInTheDocument(); // Absent count
  });

  it('allows teacher to toggle an absent student to Present', () => {
    render(
      <AttendanceReviewScreen
        draftData={mockDraft}
        onRetake={vi.fn()}
        onConfirmedSuccess={vi.fn()}
      />
    );

    const ayushToggle = screen.getByLabelText('Toggle attendance for Ayush Nyas');
    expect(ayushToggle).not.toBeChecked();

    // Click toggle to override status
    fireEvent.click(ayushToggle);
    expect(ayushToggle).toBeChecked();

    // Verify present label updates
    expect(screen.getByText(/Present \(Manual 1.0\)/i)).toBeInTheDocument();
  });

  it('allows quick mark present button for absent student', () => {
    render(
      <AttendanceReviewScreen
        draftData={mockDraft}
        onRetake={vi.fn()}
        onConfirmedSuccess={vi.fn()}
      />
    );

    const quickBtn = screen.getByText('Quick Mark Present');
    expect(quickBtn).toBeInTheDocument();

    fireEvent.click(quickBtn);

    const ayushToggle = screen.getByLabelText('Toggle attendance for Ayush Nyas');
    expect(ayushToggle).toBeChecked();
  });

  it('filters student list by segmented filter tabs', () => {
    render(
      <AttendanceReviewScreen
        draftData={mockDraft}
        onRetake={vi.fn()}
        onConfirmedSuccess={vi.fn()}
      />
    );

    const absentTab = screen.getByRole('tab', { name: /Absent/i });
    fireEvent.click(absentTab);

    // Ayush should be visible, others hidden
    expect(screen.getByText('Ayush Nyas')).toBeInTheDocument();
    expect(screen.queryByText('Shinjan Paul')).not.toBeInTheDocument();
  });
});
