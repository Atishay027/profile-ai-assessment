export interface Profile {
  user_id: string;
  full_name: string;
  city: string;
  occupation: string | null;
  bio: string | null;
  created_at: string;
  updated_at: string;
}

export interface ProfileUpdateInput {
  full_name?: string;
  city?: string;
  occupation?: string;
  bio?: string;
}

export interface InsightResult {
  summary: string;
  communication_style: string;
  suggested_focus: string;
}

export type ResponseStatus = "pending" | "accepted" | "declined" | "expired";
export type AttendanceStatus = "attendance_pending" | "attended" | "not_attended";
export type Bucket =
  | "ACTIONABLE"
  | "ACCEPTED_UPCOMING"
  | "ATTENDANCE_PENDING"
  | "ATTENDED"
  | "NOT_ATTENDED"
  | "DECLINED"
  | "EXPIRED";

export interface Invitation {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  location: string | null;
  event_start: string;
  event_end: string;
  rsvp_deadline: string | null;
  response_status: ResponseStatus;
  attendance_status: AttendanceStatus;
  responded_at: string | null;
  attendance_recorded_at: string | null;
  created_at: string;
  updated_at: string;
  bucket: Bucket;
  can_respond: boolean;
  can_submit_feedback: boolean;
}

export interface FeedbackInput {
  rating?: number;
  comment: string;
}

export interface Feedback {
  id: string;
  invitation_id: string;
  user_id: string;
  rating: number | null;
  comment: string;
  created_at: string;
}

export interface ApiErrorBody {
  detail: string | Array<{ loc: (string | number)[]; msg: string; type: string }>;
  code?: string;
}
