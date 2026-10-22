import json
from pathlib import Path

def main():
    json_path = Path("backend/data/local_employees.json")
    with open(json_path, "r", encoding="utf-8") as f:
        employees = json.load(f)

    sql_parts = []
    for emp in employees:
        skills = emp.get("skills", "").replace("'", "''")
        desig = emp.get("designation", "").replace("'", "''")
        name = emp.get("name", "").replace("'", "''")
        dept_name = emp.get("department_name", "").replace("'", "''")
        zone = emp.get("zone", "").replace("'", "''")

        sql_parts.append(
            f"('{emp['id']}', '{emp['employee_code']}', '{name}', '{emp.get('initials', '')}', '{emp['email']}', '{emp.get('phone', '')}', '{emp['department']}', '{dept_name}', '{desig}', '{zone}', '{emp['status']}', {emp['assigned_count']}, {emp['completed_count']}, {emp['pending_count']}, {emp['overdue_count']}, {emp['avg_resolution_days']}, {emp['completion_rate']}, {emp['rating']}, '{emp['performance']}', '{skills}')"
        )

    insert_rows = ",\n".join(sql_parts)

    full_sql = f"""-- ==============================================================================
-- NEXCIV SUPABASE COMPLETE DATABASE SETUP & MIGRATION SCRIPT (PHASE 1 & PHASE 2)
-- Run this script in your Supabase Dashboard -> SQL Editor -> Run
-- This script creates the complaints and employees tables, disables RLS for
-- smooth backend control, and seeds 40 real-world municipal employees & test complaints.
-- ==============================================================================

-- 1. Complaints Table
CREATE TABLE IF NOT EXISTS complaints (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID,                             -- Nullable to allow system, demo, and anonymous reports
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    category TEXT NOT NULL DEFAULT 'road',     -- road, drainage, water_supply, street_lights, others
    department TEXT,                          -- Roads & Buildings, Drainage, Water Supply, Electrical, Sanitation
    department_code TEXT,                     -- road, drainage, water_supply, street_lights, others
    priority TEXT DEFAULT 'Medium',           -- Critical, High, Medium, Low
    priority_score DOUBLE PRECISION DEFAULT 50.0, -- Multimodal composite urgency score (0.0 - 100.0)
    confidence DOUBLE PRECISION DEFAULT 0.90, -- AI Classification confidence (0.0 - 1.0)
    status TEXT NOT NULL DEFAULT 'pending',   -- pending, in_progress, resolved
    location_lat DOUBLE PRECISION,
    location_lng DOUBLE PRECISION,
    location_address TEXT,
    zone_type TEXT DEFAULT 'residential',     -- hospital, school, highway, transit_hub, residential
    vulnerability_multiplier DOUBLE PRECISION DEFAULT 1.00, -- 1.50x hospital, 1.35x school, 1.30x highway
    municipal_sla TEXT,                       -- e.g. "0 - 4 Hours (Emergency Dispatch)"
    assigned_team TEXT,                       -- e.g. "Roads & Buildings Rapid Response Team"
    assigned_employee_id TEXT,                -- e.g. "EMP-101"
    citizen_name TEXT,                        -- Citizen contact name
    citizen_email TEXT,                       -- Citizen email address
    citizen_phone TEXT,                       -- Citizen phone number
    image_url TEXT,                           -- Base64 or public storage URL
    is_duplicate BOOLEAN DEFAULT FALSE,
    master_complaint_id UUID,
    duplicate_count INTEGER DEFAULT 0,
    upvote_count INTEGER DEFAULT 1,
    image_hash TEXT,
    defect_type TEXT,
    visual_score DOUBLE PRECISION,
    cluster_id TEXT,
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Safe Column Additions & Constraint Adjustments (for existing Supabase instances)
ALTER TABLE complaints ALTER COLUMN user_id DROP NOT NULL;
ALTER TABLE complaints DROP CONSTRAINT IF EXISTS complaints_user_id_fkey;

ALTER TABLE complaints ADD COLUMN IF NOT EXISTS department TEXT;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS department_code TEXT;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS priority_score DOUBLE PRECISION DEFAULT 50.0;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS confidence DOUBLE PRECISION DEFAULT 0.90;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS zone_type TEXT DEFAULT 'residential';
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS vulnerability_multiplier DOUBLE PRECISION DEFAULT 1.00;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS municipal_sla TEXT;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS assigned_team TEXT;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS assigned_employee_id TEXT;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS citizen_name TEXT;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS citizen_email TEXT;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS citizen_phone TEXT;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS is_duplicate BOOLEAN DEFAULT FALSE;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS master_complaint_id UUID;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS duplicate_count INTEGER DEFAULT 0;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS upvote_count INTEGER DEFAULT 1;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS image_hash TEXT;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS defect_type TEXT;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS visual_score DOUBLE PRECISION;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS cluster_id TEXT;
ALTER TABLE complaints ADD COLUMN IF NOT EXISTS resolved_at TIMESTAMPTZ;

-- 2. Employees Table (40 Municipal Field Officers & Engineers)
CREATE TABLE IF NOT EXISTS employees (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    employee_code VARCHAR(20) UNIQUE NOT NULL, -- EMP-101 through EMP-140
    name VARCHAR(120) NOT NULL,
    initials VARCHAR(10),
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(30),
    department VARCHAR(50) NOT NULL,          -- road, drainage, water_supply, street_lights, others
    department_name VARCHAR(120) NOT NULL,
    designation VARCHAR(120) NOT NULL,
    zone VARCHAR(120) NOT NULL,
    status VARCHAR(20) DEFAULT 'active',      -- active, on_duty, on_leave
    assigned_count INTEGER DEFAULT 0,
    completed_count INTEGER DEFAULT 0,
    pending_count INTEGER DEFAULT 0,
    overdue_count INTEGER DEFAULT 0,
    avg_resolution_days DOUBLE PRECISION DEFAULT 2.4,
    completion_rate DOUBLE PRECISION DEFAULT 80.0,
    rating DOUBLE PRECISION DEFAULT 4.5,
    performance VARCHAR(50) DEFAULT 'On track', -- 'On track', 'Needs review', 'Attention needed'
    skills TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- 3. Row-Level Security (RLS) Configuration
-- We disable RLS or add open policies so frontend/backend can query and insert seamlessly.
ALTER TABLE complaints DISABLE ROW LEVEL SECURITY;
ALTER TABLE employees DISABLE ROW LEVEL SECURITY;

DO $$
BEGIN
    -- Fallback policies in case RLS is later enabled
    DROP POLICY IF EXISTS \"Public full access complaints\" ON complaints;
    CREATE POLICY \"Public full access complaints\" ON complaints FOR ALL USING (true) WITH CHECK (true);
    
    DROP POLICY IF EXISTS \"Public full access employees\" ON employees;
    CREATE POLICY \"Public full access employees\" ON employees FOR ALL USING (true) WITH CHECK (true);
EXCEPTION WHEN OTHERS THEN
    NULL;
END $$;

-- 4. High-Performance Query Indexes
CREATE INDEX IF NOT EXISTS idx_complaints_category ON complaints(category);
CREATE INDEX IF NOT EXISTS idx_complaints_dept_code ON complaints(department_code);
CREATE INDEX IF NOT EXISTS idx_complaints_priority ON complaints(priority);
CREATE INDEX IF NOT EXISTS idx_complaints_prio_score ON complaints(priority_score DESC);
CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);
CREATE INDEX IF NOT EXISTS idx_complaints_created_at ON complaints(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_complaints_assigned_emp ON complaints(assigned_employee_id);

CREATE INDEX IF NOT EXISTS idx_employees_code ON employees(employee_code);
CREATE INDEX IF NOT EXISTS idx_employees_dept ON employees(department);
CREATE INDEX IF NOT EXISTS idx_employees_status ON employees(status);
CREATE INDEX IF NOT EXISTS idx_employees_zone ON employees(zone);

-- Atomic Upvote Function for Duplicate Reports
CREATE OR REPLACE FUNCTION increment_upvote(row_id UUID)
RETURNS VOID AS $$
BEGIN
    UPDATE complaints
    SET upvote_count = COALESCE(upvote_count, 1) + 1,
        priority_score = LEAST(100.0, COALESCE(priority_score, 50.0) + 5.0)
    WHERE id = row_id;
END;
$$ LANGUAGE plpgsql;

-- 5. Seed 40 Municipal Employees Across All 5 Wings (8 per Department)
INSERT INTO employees (
    id, employee_code, name, initials, email, phone, department, department_name,
    designation, zone, status, assigned_count, completed_count, pending_count,
    overdue_count, avg_resolution_days, completion_rate, rating, performance, skills
) VALUES
{insert_rows}
ON CONFLICT (employee_code) DO UPDATE SET
    name = EXCLUDED.name,
    email = EXCLUDED.email,
    phone = EXCLUDED.phone,
    department = EXCLUDED.department,
    department_name = EXCLUDED.department_name,
    designation = EXCLUDED.designation,
    zone = EXCLUDED.zone,
    assigned_count = EXCLUDED.assigned_count,
    completed_count = EXCLUDED.completed_count,
    pending_count = EXCLUDED.pending_count,
    rating = EXCLUDED.rating;

-- 6. Seed Baseline Realistic Complaints
INSERT INTO complaints (
    id, user_id, title, description, category, department, department_code, 
    priority, priority_score, confidence, status, location_lat, location_lng, 
    location_address, zone_type, vulnerability_multiplier, municipal_sla, assigned_team, assigned_employee_id
) VALUES 
(
    'a1111111-1111-1111-1111-111111111111', 
    NULL,
    'Massive road cave-in and sinkhole near Benz Circle Flyover',
    'Deep dangerous trench and sinkhole formed on the main NH-16 highway approach slab after heavy downpour. Two-wheelers skidding and fatal accident hazard.',
    'road',
    'Roads & Buildings Department (R&B / Municipal)',
    'road',
    'Critical',
    98.5,
    0.994,
    'pending',
    16.4990,
    80.6540,
    'NH-16 Benz Circle Flyover, Vijayawada',
    'highway',
    1.30,
    '0 - 4 Hours (Emergency Dispatch)',
    'Roads & Buildings Rapid Response Team',
    'EMP-101'
),
(
    'b2222222-2222-2222-2222-222222222222', 
    NULL,
    'Drinking water pipeline burst and yellow contaminated supply near KGH Casualty',
    'Main drinking water pipeline burst open and contaminated sewage is seeping in outside KGH Casualty Gate. Zero potable water for hospital wards.',
    'water_supply',
    'Water Supply & Quality Department',
    'water_supply',
    'Critical',
    99.2,
    0.998,
    'in_progress',
    17.7102,
    83.3050,
    'King George Hospital (KGH) Casualty Gate, Maharanipeta, Visakhapatnam',
    'hospital',
    1.50,
    '0 - 4 Hours (Emergency Dispatch)',
    'Water Works Emergency Repair Squad',
    'EMP-117'
),
(
    'c3333333-3333-3333-3333-333333333333', 
    NULL,
    'Live APEPDCL electric wire snapped and sparking on wet road',
    'High voltage electrical transmission line snapped from concrete pole and sparking in water puddle outside RTC Bus Terminal.',
    'street_lights',
    'Electrical & Street Lighting Wing',
    'street_lights',
    'Critical',
    99.8,
    0.997,
    'pending',
    16.5080,
    80.6210,
    'Pandit Nehru Bus Station (PNBS), Vijayawada',
    'transit_hub',
    1.25,
    '0 - 4 Hours (Emergency Dispatch)',
    'APEPDCL Lineman Quick Response Team',
    'EMP-125'
),
(
    'd4444444-4444-4444-4444-444444444444', 
    NULL,
    'Toxic black sewage overflow from blocked storm water nala',
    'Main municipal canal choked with plastic waste, sewage backflow submerging residential street and spreading foul stench.',
    'drainage',
    'Public Health & Drainage Department',
    'drainage',
    'High',
    82.0,
    0.985,
    'in_progress',
    16.3010,
    80.4410,
    'Brodipet 4th Line, Guntur',
    'residential',
    1.00,
    '24 Hours (Next Shift Field Team)',
    'Drainage & Sewerage Jetting Crew',
    'EMP-109'
),
(
    'e5555555-5555-5555-5555-555555555555', 
    NULL,
    'Overflowing community garbage dumper bin and illegal roadside dumping',
    'Commercial garbage bin overflowing for three days with stray cattle littering plastic on the road.',
    'others',
    'Sanitation & Solid Waste Management Wing',
    'others',
    'Medium',
    55.0,
    0.996,
    'resolved',
    17.7420,
    83.3370,
    'MVP Colony Sector 4, Visakhapatnam',
    'residential',
    1.00,
    '48 - 72 Hours (Standard Municipal Maintenance)',
    'GVMC Sanitation Wing Zone 2',
    'EMP-133'
)
ON CONFLICT (id) DO NOTHING;
"""

    out_file = Path("supabase_setup.sql")
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(full_sql)

    print(f"Updated {out_file} successfully with 40 employees and full schema.")

if __name__ == "__main__":
    main()
