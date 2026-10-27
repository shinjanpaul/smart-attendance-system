/**
 * VeriFace AI Attendance System - Strict TypeScript Type Definitions
 * Matches Section 4.1 of the API Handover Specification
 */

export type Role = 'STUDENT' | 'TEACHER' | 'ADMIN';
export type AttendanceStatus = 'PRESENT' | 'ABSENT';

export interface StudentClass {
  id: number;
  name: string;
  department: string;
}

export interface Subject {
  id: number;
  name: string;
  code: string;
  student_class: number;
  student_class_name?: string;
}

export interface Student {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: Role;
  department: string;
  roll_number: string;
  student_class: number;
  student_class_name?: string;
  has_registered_face: boolean;
  profile_picture: string | null;
}

export interface Teacher {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: Role;
  department: string;
}

export interface DraftStudent {
  id: number;
  username: string;
  name: string;
  roll_number: string;
  has_registered_face: boolean;
  avatarUrl?: string;
}

export interface MatchDetail {
  photo_index: number;
  student_id: number | null;
  student_name: string;
  roll_number: string | null;
  distance: number;
  confidence: number;
}

export interface DraftResult {
  total_photos_processed: number;
  total_faces_detected: number;
  unmatched_faces_count: number;
  present_count: number;
  absent_count: number;
  class_id: number;
  subject_id: number | null;
  date: string;
  present_students: DraftStudent[];
  absent_students: DraftStudent[];
  match_details: MatchDetail[];
}

export interface ConfirmRecord {
  student_id: number;
  status: AttendanceStatus;
  confidence: number;
}

export interface ConfirmPayload {
  class_id: number;
  subject_id?: number | null;
  date: string;
  records: ConfirmRecord[];
}

export interface ConfirmResponse {
  message: string;
  created_records_count: number;
  updated_records_count: number;
  date: string;
}

export interface AttendanceLog {
  id: number;
  student: number;
  student_name: string;
  student_roll: string;
  student_class: number;
  class_name: string;
  subject: number;
  subject_name: string;
  date: string;
  timestamp: string;
  status: AttendanceStatus;
  verification_method: string;
  confidence_score: number;
  snapshot: string | null;
}
