-- ==============================================================================
-- NEXCIV ANDHRA PRADESH MUNICIPAL GRIEVANCE & CADRE WORKFORCE DATABASE SCHEMA
-- Fully Idempotent Migration Script (Runs seamlessly on fresh or existing databases)
-- ==============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. MUNICIPALITIES TABLE (All AP Urban Local Bodies: Corporations & Municipalities)
CREATE TABLE IF NOT EXISTS public.municipalities (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'Municipality',
    district VARCHAR(100) NOT NULL,
    headquarters VARCHAR(255),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(50),
    wards_count INT DEFAULT 50,
    population VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 2. CITIZENS TABLE (Registered Citizens of AP)
CREATE TABLE IF NOT EXISTS public.citizens (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    password_hash VARCHAR(255) NOT NULL,
    municipality_code VARCHAR(20),
    ward VARCHAR(100),
    address TEXT,
    landmark VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. EMPLOYEES TABLE (Municipal Engineers, Inspectors & Cadre Personnel)
CREATE TABLE IF NOT EXISTS public.employees (
    id VARCHAR(100) PRIMARY KEY,
    employee_code VARCHAR(50) UNIQUE,
    name VARCHAR(255) NOT NULL,
    initials VARCHAR(10),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    password_hash VARCHAR(255) NOT NULL,
    municipality_code VARCHAR(20),
    department VARCHAR(100) NOT NULL,
    department_name VARCHAR(255),
    designation VARCHAR(150),
    zone VARCHAR(100) DEFAULT 'Central Zone',
    status VARCHAR(50) DEFAULT 'Active',
    assigned_count INT DEFAULT 0,
    completed_count INT DEFAULT 0,
    pending_count INT DEFAULT 0,
    overdue_count INT DEFAULT 0,
    avg_resolution_days NUMERIC(4, 2) DEFAULT 1.5,
    completion_rate INT DEFAULT 100,
    rating NUMERIC(3, 1) DEFAULT 4.8,
    performance VARCHAR(50) DEFAULT 'On track',
    skills TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Ensure all modern columns exist if employees table was already present
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS municipality_code VARCHAR(20);
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS employee_code VARCHAR(50);
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS initials VARCHAR(10);
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS department_name VARCHAR(255);
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS designation VARCHAR(150);
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS zone VARCHAR(100) DEFAULT 'Central Zone';
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS status VARCHAR(50) DEFAULT 'Active';
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS assigned_count INT DEFAULT 0;
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS completed_count INT DEFAULT 0;
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS pending_count INT DEFAULT 0;
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS overdue_count INT DEFAULT 0;
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS avg_resolution_days NUMERIC(4, 2) DEFAULT 1.5;
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS completion_rate INT DEFAULT 100;
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS rating NUMERIC(3, 1) DEFAULT 4.8;
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS performance VARCHAR(50) DEFAULT 'On track';
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS skills TEXT;
ALTER TABLE public.employees ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE;

-- 4. COMPLAINTS MASTER TABLE
CREATE TABLE IF NOT EXISTS public.complaints (
    id VARCHAR(100) PRIMARY KEY,
    user_id UUID,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    department VARCHAR(255),
    department_code VARCHAR(100),
    municipal_corporation VARCHAR(20),
    ward VARCHAR(100),
    landmark VARCHAR(255),
    confidence NUMERIC(5, 4) DEFAULT 0.95,
    priority VARCHAR(50) DEFAULT 'Medium',
    priority_score NUMERIC(5, 2) DEFAULT 60.0,
    location_lat NUMERIC(10, 7),
    location_lng NUMERIC(10, 7),
    location_address TEXT,
    image_url TEXT,
    image_data TEXT,
    images JSONB DEFAULT '[]'::jsonb,
    zone_type VARCHAR(100) DEFAULT 'residential',
    vulnerability_multiplier NUMERIC(4, 2) DEFAULT 1.0,
    municipal_sla VARCHAR(100) DEFAULT '24 - 48 Hours',
    assigned_team VARCHAR(255),
    assigned_employee_id VARCHAR(50),
    citizen_name VARCHAR(255),
    citizen_email VARCHAR(255),
    citizen_phone VARCHAR(50),
    is_duplicate BOOLEAN DEFAULT FALSE,
    master_complaint_id VARCHAR(100),
    duplicate_count INT DEFAULT 0,
    upvote_count INT DEFAULT 1,
    image_hash VARCHAR(100),
    defect_type VARCHAR(100),
    visual_score NUMERIC(5, 2),
    resolution_notes TEXT,
    resolution_proof_url TEXT,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Crucial: Ensure all columns exist in public.complaints even if the table already existed!
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS municipal_corporation VARCHAR(20);
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS user_id UUID;
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS ward VARCHAR(100);
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS landmark VARCHAR(255);
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS department VARCHAR(255);
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS department_code VARCHAR(100);
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS confidence NUMERIC(5, 4) DEFAULT 0.95;
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS priority VARCHAR(50) DEFAULT 'Medium';
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS priority_score NUMERIC(5, 2) DEFAULT 60.0;
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS location_lat NUMERIC(10, 7);
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS location_lng NUMERIC(10, 7);
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS location_address TEXT;
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS image_url TEXT;
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS image_data TEXT;
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS images JSONB DEFAULT '[]'::jsonb;
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS zone_type VARCHAR(100) DEFAULT 'residential';
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS vulnerability_multiplier NUMERIC(4, 2) DEFAULT 1.0;
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS municipal_sla VARCHAR(100) DEFAULT '24 - 48 Hours';
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS assigned_team VARCHAR(255);
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS assigned_employee_id VARCHAR(50);
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS citizen_name VARCHAR(255);
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS citizen_email VARCHAR(255);
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS citizen_phone VARCHAR(50);
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS is_duplicate BOOLEAN DEFAULT FALSE;
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS master_complaint_id VARCHAR(100);
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS duplicate_count INT DEFAULT 0;
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS upvote_count INT DEFAULT 1;
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS image_hash VARCHAR(100);
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS defect_type VARCHAR(100);
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS visual_score NUMERIC(5, 2);
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS resolution_notes TEXT;
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS resolution_proof_url TEXT;
ALTER TABLE public.complaints ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMPTZ;

-- 5. SEPARATE MUNICIPALITY COMPLAINTS TABLES (Partitioned for Absolute Data Isolation)
CREATE TABLE IF NOT EXISTS public.complaints_elr (LIKE public.complaints INCLUDING ALL);
CREATE TABLE IF NOT EXISTS public.complaints_gvmc (LIKE public.complaints INCLUDING ALL);
CREATE TABLE IF NOT EXISTS public.complaints_vmc (LIKE public.complaints INCLUDING ALL);
CREATE TABLE IF NOT EXISTS public.complaints_gmc (LIKE public.complaints INCLUDING ALL);
CREATE TABLE IF NOT EXISTS public.complaints_tmc (LIKE public.complaints INCLUDING ALL);
CREATE TABLE IF NOT EXISTS public.complaints_kmc (LIKE public.complaints INCLUDING ALL);

-- In case municipality tables already existed, ensure they have municipal_corporation as well
ALTER TABLE public.complaints_elr ADD COLUMN IF NOT EXISTS municipal_corporation VARCHAR(20);
ALTER TABLE public.complaints_gvmc ADD COLUMN IF NOT EXISTS municipal_corporation VARCHAR(20);
ALTER TABLE public.complaints_vmc ADD COLUMN IF NOT EXISTS municipal_corporation VARCHAR(20);
ALTER TABLE public.complaints_gmc ADD COLUMN IF NOT EXISTS municipal_corporation VARCHAR(20);
ALTER TABLE public.complaints_tmc ADD COLUMN IF NOT EXISTS municipal_corporation VARCHAR(20);
ALTER TABLE public.complaints_kmc ADD COLUMN IF NOT EXISTS municipal_corporation VARCHAR(20);

-- Indexes for lightning fast municipal queries
CREATE INDEX IF NOT EXISTS idx_complaints_municipality ON public.complaints(municipal_corporation);
CREATE INDEX IF NOT EXISTS idx_complaints_status ON public.complaints(status);
CREATE INDEX IF NOT EXISTS idx_complaints_assigned_emp ON public.complaints(assigned_employee_id);
CREATE INDEX IF NOT EXISTS idx_employees_municipality ON public.employees(municipality_code);
CREATE INDEX IF NOT EXISTS idx_citizens_email ON public.citizens(email);
