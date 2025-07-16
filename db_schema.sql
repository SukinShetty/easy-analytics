-- Run in ToolJet DB query editor

-- Sales Team table
CREATE TABLE IF NOT EXISTS sales_team (
  id BIGINT PRIMARY KEY,
  display_name VARCHAR(255),
  email VARCHAR(255),
  is_active BOOLEAN DEFAULT false,
  work_number VARCHAR(50),
  mobile_number VARCHAR(50)
);

-- Contact Statuses/Pipeline Stages table
CREATE TABLE IF NOT EXISTS contact_statuses (
  id BIGINT PRIMARY KEY,
  name VARCHAR(255),
  position INTEGER,
  partial BOOLEAN DEFAULT false,
  forecast_type VARCHAR(100),
  lifecycle_stage_id BIGINT
);

-- Appointments table
CREATE TABLE IF NOT EXISTS appointments (
  id BIGINT PRIMARY KEY,
  title VARCHAR(500),
  description TEXT,
  location VARCHAR(500),
  from_date TIMESTAMP WITH TIME ZONE,
  end_date TIMESTAMP WITH TIME ZONE,
  is_allday BOOLEAN DEFAULT false,
  time_zone VARCHAR(100),
  provider VARCHAR(100),
  creater_id BIGINT,
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE,
  outcome_id BIGINT,
  conference_id VARCHAR(255)
);

-- Tasks table
CREATE TABLE IF NOT EXISTS tasks (
  id BIGINT PRIMARY KEY,
  title VARCHAR(500),
  description TEXT,
  due_date TIMESTAMP WITH TIME ZONE,
  is_completed BOOLEAN DEFAULT false,
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE,
  creater_id BIGINT,
  task_type_id BIGINT,
  priority VARCHAR(50)
);

CREATE TABLE IF NOT EXISTS deals (
  id BIGINT PRIMARY KEY,
  name VARCHAR(255),
  amount DECIMAL(10,2),
  close_date DATE,
  product_id BIGINT,
  account_id BIGINT,
  contact_id BIGINT
);

CREATE TABLE IF NOT EXISTS contacts (
  id BIGINT PRIMARY KEY,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  email VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS accounts (
  id BIGINT PRIMARY KEY,
  name VARCHAR(255),
  industry VARCHAR(255)
);

CREATE TABLE IF NOT EXISTS products (
  id BIGINT PRIMARY KEY,
  name VARCHAR(255),
  price DECIMAL(10,2)
);

-- Updated Sales Activities table with comprehensive fields
CREATE TABLE IF NOT EXISTS sales_activities (
  id BIGINT PRIMARY KEY,
  title VARCHAR(500),
  activity_type VARCHAR(255),
  targetable_type VARCHAR(100),
  targetable_id BIGINT,
  start_date TIMESTAMP WITH TIME ZONE,
  end_date TIMESTAMP WITH TIME ZONE,
  created_at TIMESTAMP WITH TIME ZONE,
  updated_at TIMESTAMP WITH TIME ZONE,
  creater_id BIGINT,
  outcome VARCHAR(255)
); 