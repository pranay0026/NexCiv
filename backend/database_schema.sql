-- ==============================================================================
-- NEXCIV ANDHRA PRADESH MUNICIPAL GRIEVANCE & CADRE WORKFORCE DATABASE SCHEMA
-- Compatible with PostgreSQL 14+ and Supabase
-- ==============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. MUNICIPALITIES TABLE (All AP Urban Local Bodies: Corporations & Municipalities)
CREATE TABLE IF NOT EXISTS public.municipalities (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    short_name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL DEFAULT 'Municipality', -- 'Corporation' or 'Municipality'
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
    municipality_code VARCHAR(20) REFERENCES public.municipalities(code) ON DELETE SET NULL,
    ward VARCHAR(100),
    address TEXT,
    landmark VARCHAR(255),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. EMPLOYEES TABLE (Municipal Engineers, Inspectors & Cadre Personnel)
CREATE TABLE IF NOT EXISTS public.employees (
    id VARCHAR(100) PRIMARY KEY,
    employee_code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    initials VARCHAR(10),
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(50),
    password_hash VARCHAR(255) NOT NULL,
    municipality_code VARCHAR(20) REFERENCES public.municipalities(code) ON DELETE CASCADE,
    department VARCHAR(100) NOT NULL, -- 'road', 'drainage', 'water_supply', 'street_lights', 'others'
    department_name VARCHAR(255),
    designation VARCHAR(150) NOT NULL,
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

-- 4. COMPLAINTS MASTER TABLE
CREATE TABLE IF NOT EXISTS public.complaints (
    id VARCHAR(100) PRIMARY KEY,
    user_id UUID REFERENCES public.citizens(id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(100) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- 'pending', 'in_progress', 'resolved'
    department VARCHAR(255),
    department_code VARCHAR(100),
    municipal_corporation VARCHAR(20) REFERENCES public.municipalities(code) ON DELETE SET NULL,
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

-- 5. SEPARATE MUNICIPALITY COMPLAINTS TABLES (Partitioned for Absolute Data Isolation)

-- 5a. Eluru Municipal Corporation Complaints Table
CREATE TABLE IF NOT EXISTS public.complaints_elr (
    LIKE public.complaints INCLUDING ALL
);

-- 5b. Greater Visakhapatnam Municipal Corporation Complaints Table
CREATE TABLE IF NOT EXISTS public.complaints_gvmc (
    LIKE public.complaints INCLUDING ALL
);

-- 5c. Vijayawada Municipal Corporation Complaints Table
CREATE TABLE IF NOT EXISTS public.complaints_vmc (
    LIKE public.complaints INCLUDING ALL
);

-- 5d. Guntur Municipal Corporation Complaints Table
CREATE TABLE IF NOT EXISTS public.complaints_gmc (
    LIKE public.complaints INCLUDING ALL
);

-- 5e. Tirupati Municipal Corporation Complaints Table
CREATE TABLE IF NOT EXISTS public.complaints_tmc (
    LIKE public.complaints INCLUDING ALL
);

-- 5f. Kurnool Municipal Corporation Complaints Table
CREATE TABLE IF NOT EXISTS public.complaints_kmc (
    LIKE public.complaints INCLUDING ALL
);

-- Indexes for lightning fast municipal queries
CREATE INDEX IF NOT EXISTS idx_complaints_municipality ON public.complaints(municipal_corporation);
CREATE INDEX IF NOT EXISTS idx_complaints_status ON public.complaints(status);
CREATE INDEX IF NOT EXISTS idx_complaints_assigned_emp ON public.complaints(assigned_employee_id);
CREATE INDEX IF NOT EXISTS idx_employees_municipality ON public.employees(municipality_code);
CREATE INDEX IF NOT EXISTS idx_citizens_email ON public.citizens(email);
