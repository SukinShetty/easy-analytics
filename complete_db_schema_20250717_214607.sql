-- Complete Freshworks CRM Database Schema
-- Auto-generated from API discovery

-- Table for appointments
CREATE TABLE IF NOT EXISTS appointments (
  can_checkin BOOLEAN,
  can_checkin_checkout BOOLEAN,
  checkedin_at TEXT,
  checkedin_duration TEXT,
  checkedout_at TEXT,
  checkedout_latitude TEXT,
  checkedout_location TEXT,
  checkedout_longitude TEXT,
  conference_id TEXT,
  created_at TIMESTAMP WITH TIME ZONE,
  creater_id BIGINT,
  description TEXT,
  end_date TIMESTAMP WITH TIME ZONE,
  from_date TIMESTAMP WITH TIME ZONE,
  has_multiple_emails BOOLEAN,
  id BIGINT PRIMARY KEY,
  is_allday BOOLEAN,
  latitude TEXT,
  location TEXT,
  longitude TEXT,
  outcome_id TEXT,
  provider TEXT,
  targetables JSONB,
  targetables_with_email JSONB,
  time_zone TEXT,
  title TEXT,
  updated_at TIMESTAMP WITH TIME ZONE
);
