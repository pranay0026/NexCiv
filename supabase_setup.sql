-- ==============================================================================
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
    DROP POLICY IF EXISTS "Public full access complaints" ON complaints;
    CREATE POLICY "Public full access complaints" ON complaints FOR ALL USING (true) WITH CHECK (true);
    
    DROP POLICY IF EXISTS "Public full access employees" ON employees;
    CREATE POLICY "Public full access employees" ON employees FOR ALL USING (true) WITH CHECK (true);
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
('fb573031-5605-5928-bf2a-32deffe39480', 'EMP-101', 'A. Ramesh Kumar', 'AR', 'a.ramesh.kumar@nexciv.gov', '+91 94401 00101', 'road', 'Roads & Buildings Department (R&B / Municipal)', 'Superintending Engineer (R&B)', 'Zone 1 - Vijayawada Central', 'active', 44, 35, 9, 2, 2.3, 79.5, 4.8, 'Needs review', 'Highway Engineering, Rapid Asphalt Paving'),
('bcd07165-da7e-548c-9e3b-3cdaac59042d', 'EMP-102', 'K. Srinivasa Rao', 'KS', 'k.srinivasa.rao@nexciv.gov', '+91 94401 00102', 'road', 'Roads & Buildings Department (R&B / Municipal)', 'Executive Engineer - Roads', 'Zone 2 - Benz Circle NH-16', 'active', 38, 30, 8, 1, 2.1, 78.9, 4.7, 'On track', 'Pothole Restoration, Bridge Maintenance'),
('34c536b4-3e79-5616-b2a1-4f4f36d3c044', 'EMP-103', 'P. Venkata Narayana', 'PV', 'p.venkata.narayana@nexciv.gov', '+91 94401 00103', 'road', 'Roads & Buildings Department (R&B / Municipal)', 'Assistant Executive Engineer', 'Zone 3 - Guntur West Corridor', 'active', 35, 29, 6, 0, 1.9, 82.9, 4.9, 'On track', 'Urban Roads, Quality Inspection'),
('c7b21a3f-85d4-5f57-8d2e-80591987347c', 'EMP-104', 'V. Anusha Reddy', 'VA', 'v.anusha.reddy@nexciv.gov', '+91 94401 00104', 'road', 'Roads & Buildings Department (R&B / Municipal)', 'Junior Engineer - Highway Safety', 'Zone 4 - Visakhapatnam Port Road', 'active', 32, 26, 6, 1, 2.4, 81.2, 4.6, 'On track', 'Safety Audits, Drainage Integration'),
('e14e2da1-1bf3-5b2d-9599-54c6c6f0eef0', 'EMP-105', 'M. Satyanarayana', 'MS', 'm.satyanarayana@nexciv.gov', '+91 94401 00105', 'road', 'Roads & Buildings Department (R&B / Municipal)', 'Field Work Inspector', 'Zone 5 - Tirupati Urban Link', 'active', 29, 25, 4, 0, 1.8, 86.2, 4.8, 'On track', 'Field Surveys, Rapid Repair Squad'),
('3b425656-f66d-5146-b47c-3ca7ea55e80f', 'EMP-106', 'T. Sai Krishna', 'TS', 't.sai.krishna@nexciv.gov', '+91 94401 00106', 'road', 'Roads & Buildings Department (R&B / Municipal)', 'Asphalt & Paving Supervisor', 'Zone 1 - Vijayawada East', 'active', 27, 22, 5, 1, 2.6, 81.5, 4.5, 'On track', 'Hot-mix Asphalt, Trench Filling'),
('dd6b9179-dc23-5e5c-8877-67a5df5df8da', 'EMP-107', 'D. Lakshmi Prasanna', 'DL', 'd.lakshmi.prasanna@nexciv.gov', '+91 94401 00107', 'road', 'Roads & Buildings Department (R&B / Municipal)', 'Quality Control Specialist', 'Zone 3 - Guntur Brodipet', 'active', 31, 27, 4, 0, 1.7, 87.1, 4.9, 'On track', 'Bitumen Testing, Structural Compliance'),
('edc70f96-6fc6-53f3-91d7-183f433f7f3a', 'EMP-108', 'Ch. Mohan Rao', 'CM', 'ch.mohan.rao@nexciv.gov', '+91 94401 00108', 'road', 'Roads & Buildings Department (R&B / Municipal)', 'Rapid Pothole Squad Lead', 'Zone 2 - Vijayawada Auto Nagar', 'on_leave', 40, 33, 7, 2, 2.2, 82.5, 4.7, 'Needs review', 'Jetpatcher Operations, Emergency Dispatch'),
('e42e1cbb-243b-5237-ac6e-c44c75586c4b', 'EMP-109', 'S. Devi Kumari', 'SD', 's.devi.kumari@nexciv.gov', '+91 94401 00109', 'drainage', 'Public Health & Drainage Department', 'Executive Engineer (Public Health)', 'Zone 1 - Vijayawada One-Town', 'active', 42, 34, 8, 1, 2.4, 81.0, 4.8, 'On track', 'Stormwater Masterplan, Outfall Channels'),
('c8e429f0-70e8-54df-8ed6-ba297401b44d', 'EMP-110', 'N. Suresh Babu', 'NS', 'n.suresh.babu@nexciv.gov', '+91 94401 00110', 'drainage', 'Public Health & Drainage Department', 'Assistant Executive Engineer - Sewerage', 'Zone 2 - Guntur Collectorate', 'active', 36, 28, 8, 2, 2.5, 77.8, 4.6, 'Needs review', 'Sewer Lines, High-pressure Jetting'),
('15f14a4a-eaf0-52e7-9cbb-981393c99086', 'EMP-111', 'B. Haritha', 'BH', 'b.haritha@nexciv.gov', '+91 94401 00111', 'drainage', 'Public Health & Drainage Department', 'Junior Engineer - Underground Drainage', 'Zone 4 - Vizag Beach Road', 'active', 30, 26, 4, 0, 2.0, 86.7, 4.9, 'On track', 'UDD Networks, Manhole Safety'),
('739ef79c-03bc-542c-872c-4423181a20f0', 'EMP-112', 'K. Venkatesh', 'KV', 'k.venkatesh@nexciv.gov', '+91 94401 00112', 'drainage', 'Public Health & Drainage Department', 'Sewer Jetting Crew Supervisor', 'Zone 1 - Vijayawada Gandhi Nagar', 'active', 39, 31, 8, 2, 2.7, 79.5, 4.5, 'Needs review', 'Suction Machines, Heavy Desilting'),
('f1644606-0671-5501-b845-2804159b9336', 'EMP-113', 'G. Nagaraju', 'GN', 'g.nagaraju@nexciv.gov', '+91 94401 00113', 'drainage', 'Public Health & Drainage Department', 'Nala Desilting In-Charge', 'Zone 3 - Guntur Arundelpet', 'active', 33, 27, 6, 1, 2.3, 81.8, 4.7, 'On track', 'Canal Desilting, Monsoonal Preparedness'),
('161b17ea-a160-5896-9550-5909e92c667e', 'EMP-114', 'M. Pavani', 'MP', 'm.pavani@nexciv.gov', '+91 94401 00114', 'drainage', 'Public Health & Drainage Department', 'Environmental Health Inspector', 'Zone 5 - Tirupati Ruia Corridor', 'active', 28, 25, 3, 0, 1.8, 89.3, 4.8, 'On track', 'Sewage Outflow, Vector Control'),
('f240cc4c-b322-529d-a0ae-cd30f60aa144', 'EMP-115', 'Y. Subba Rao', 'YS', 'y.subba.rao@nexciv.gov', '+91 94401 00115', 'drainage', 'Public Health & Drainage Department', 'Pumping Station Lead Operator', 'Zone 4 - Vizag MVP Colony', 'active', 34, 29, 5, 0, 2.1, 85.3, 4.7, 'On track', 'Lift Irrigation, Stormwater Pumps'),
('3ff492d0-0b2e-554e-9e53-4c705295b883', 'EMP-116', 'R. Kalyan Varma', 'RK', 'r.kalyan.varma@nexciv.gov', '+91 94401 00116', 'drainage', 'Public Health & Drainage Department', 'Emergency Inundation Dispatcher', 'Zone 2 - Vijayawada Benz Circle', 'active', 37, 30, 7, 1, 2.2, 81.1, 4.6, 'On track', 'Flash Flood Dewatering, Quick Response'),
('a809c700-3857-5dbc-a94f-07cb632b76a0', 'EMP-117', 'M. Farah Naz', 'MF', 'm.farah.naz@nexciv.gov', '+91 94401 00117', 'water_supply', 'Water Supply & Quality Department', 'Chief Water Works Engineer', 'Zone 1 - Vijayawada Head Water Works', 'active', 46, 36, 10, 2, 2.6, 78.3, 4.8, 'Needs review', 'Bulk Transmission, Municipal Distribution'),
('d75f2431-e64b-52d9-b7ca-cf0edd7a40f0', 'EMP-118', 'J. Chandra Sekhar', 'JC', 'j.chandra.sekhar@nexciv.gov', '+91 94401 00118', 'water_supply', 'Water Supply & Quality Department', 'Divisional Engineer - Pipeline Networks', 'Zone 4 - Vizag Siripuram', 'active', 40, 32, 8, 1, 2.3, 80.0, 4.7, 'On track', 'HDPE/DI Pipelines, Leak Mitigation'),
('45d1eb0c-567e-5c26-a78e-76e9e9190a17', 'EMP-119', 'P. Sandhya Rani', 'PS', 'p.sandhya.rani@nexciv.gov', '+91 94401 00119', 'water_supply', 'Water Supply & Quality Department', 'Water Quality Testing Analyst', 'Zone 2 - Guntur Gujjanagundla', 'active', 34, 30, 4, 0, 1.6, 88.2, 4.9, 'On track', 'Chlorination, Potability Certification'),
('87a149f1-5cc4-59ab-811a-f3f170c35943', 'EMP-120', 'K. Ramakrishna', 'KR', 'k.ramakrishna@nexciv.gov', '+91 94401 00120', 'water_supply', 'Water Supply & Quality Department', 'Transmission Mains Repair Squad Lead', 'Zone 3 - Guntur Brodipet', 'on_leave', 38, 30, 8, 2, 2.5, 78.9, 4.6, 'Needs review', 'Underground Pipeline Bursts, Welding'),
('ee087244-4e49-547c-a3c3-bb8570646164', 'EMP-121', 'S. Srinivasulu', 'SS', 's.srinivasulu@nexciv.gov', '+91 94401 00121', 'water_supply', 'Water Supply & Quality Department', 'Valve Operations & Pressure Inspector', 'Zone 1 - Vijayawada Governorpet', 'active', 31, 27, 4, 0, 1.9, 87.1, 4.8, 'On track', 'Pressure Regulation, SCADA Telemetry'),
('4c559b38-aa46-5602-a9ac-efa1130c2db0', 'EMP-122', 'V. Madhavi Latha', 'VM', 'v.madhavi.latha@nexciv.gov', '+91 94401 00122', 'water_supply', 'Water Supply & Quality Department', 'Filtration Plant Superintendent', 'Zone 5 - Tirupati Alipiri Plant', 'active', 35, 30, 5, 0, 2.0, 85.7, 4.9, 'On track', 'Rapid Sand Filters, Chemical Dosing'),
('ce7cf979-2a24-5da3-8c41-2d681db9557e', 'EMP-123', 'B. Prasad', 'BP', 'b.prasad@nexciv.gov', '+91 94401 00123', 'water_supply', 'Water Supply & Quality Department', 'Overhead Reservoir Lead', 'Zone 4 - Vizag Maddilapalem', 'active', 29, 25, 4, 1, 2.2, 86.2, 4.6, 'On track', 'ELSR Tank Cleaning, Float Sensors'),
('33e2757e-bb20-5a44-8f7c-14c55bac76a3', 'EMP-124', 'T. Shiva Kumar', 'TS', 't.shiva.kumar@nexciv.gov', '+91 94401 00124', 'water_supply', 'Water Supply & Quality Department', 'Acoustic Leak Detection Specialist', 'Zone 2 - Vijayawada Labbipet', 'active', 33, 28, 5, 0, 1.8, 84.8, 4.7, 'On track', 'Ultrasonic Sensors, Non-Revenue Water'),
('f0b6516d-29fa-51ea-9918-5982ffe8eb96', 'EMP-125', 'R. Prasad Naidu', 'RP', 'r.prasad.naidu@nexciv.gov', '+91 94401 00125', 'street_lights', 'Electrical & Street Lighting Wing', 'Executive Engineer - Electrical Wing', 'Zone 1 - Vijayawada PNBS Hub', 'active', 45, 38, 7, 0, 1.9, 84.4, 4.9, 'On track', 'Power Distribution, High-Mast Towers'),
('b653f55a-0a10-5481-81c8-d2f6bef5e39d', 'EMP-126', 'E. Divya', 'ED', 'e.divya@nexciv.gov', '+91 94401 00126', 'street_lights', 'Electrical & Street Lighting Wing', 'Assistant Engineer - Smart Street Lighting', 'Zone 4 - Vizag Beach Road', 'active', 37, 32, 5, 0, 1.8, 86.5, 4.8, 'On track', 'CCMS Timers, Energy Efficient LEDs'),
('baaa7adf-f473-582f-bf0d-5814bc2bf01f', 'EMP-127', 'K. Murali Krishna', 'KM', 'k.murali.krishna@nexciv.gov', '+91 94401 00127', 'street_lights', 'Electrical & Street Lighting Wing', 'High Tension Line Supervisor', 'Zone 2 - Benz Circle Flyover', 'active', 39, 31, 8, 1, 2.2, 79.5, 4.7, 'On track', 'Snapped Conductor Safety, 11kV Lines'),
('a2bfdf13-f9e8-5a7e-abd5-943dbeaf4149', 'EMP-128', 'G. Ravi Teja', 'GR', 'g.ravi.teja@nexciv.gov', '+91 94401 00128', 'street_lights', 'Electrical & Street Lighting Wing', 'Substation Maintenance Lead', 'Zone 3 - Guntur Ring Road Substation', 'active', 34, 29, 5, 0, 2.0, 85.3, 4.8, 'On track', 'Transformer Maintenance, Earth Faults'),
('6bb7c929-97da-5827-b93d-883e71888a87', 'EMP-129', 'L. Venkateswara Rao', 'LV', 'l.venkateswara.rao@nexciv.gov', '+91 94401 00129', 'street_lights', 'Electrical & Street Lighting Wing', 'Senior Lineman Lead', 'Zone 1 - Vijayawada Satyanarayanapuram', 'active', 41, 35, 6, 1, 2.1, 85.4, 4.6, 'On track', 'Aerial Hydraulic Platform, Cable Jointing'),
('492209eb-ae02-5f95-9f93-866887b576ae', 'EMP-130', 'P. Hemalatha', 'PH', 'p.hemalatha@nexciv.gov', '+91 94401 00130', 'street_lights', 'Electrical & Street Lighting Wing', 'SCADA & Automation Engineer', 'Zone 4 - Vizag IT Corridor', 'active', 30, 27, 3, 0, 1.7, 90.0, 4.9, 'On track', 'Feeder Automation, Remote Switching'),
('145e1f80-5a01-591f-bc4f-225920330914', 'EMP-131', 'S. Appala Raju', 'SA', 's.appala.raju@nexciv.gov', '+91 94401 00131', 'street_lights', 'Electrical & Street Lighting Wing', 'LED Fixture Replacement Squad Lead', 'Zone 5 - Tirupati Railway Approach', 'active', 36, 30, 6, 1, 2.3, 83.3, 4.7, 'On track', 'Pole Replacement, Street Luminaire'),
('194459b8-d5a7-5bb1-aefd-5b02aa944a12', 'EMP-132', 'V. Naresh Babu', 'VN', 'v.naresh.babu@nexciv.gov', '+91 94401 00132', 'street_lights', 'Electrical & Street Lighting Wing', 'Emergency Blackout Dispatch Officer', 'Zone 2 - Vijayawada Bhavanipuram', 'on_leave', 38, 33, 5, 0, 1.8, 86.8, 4.8, 'On track', 'Storm Outage Restoration, Night Patrol'),
('1149b3b3-87ca-534c-81bf-ff9b92f239e1', 'EMP-133', 'Dr. K. Radhakrishna', 'DK', 'k.radhakrishna@nexciv.gov', '+91 94401 00133', 'others', 'Sanitation & Solid Waste Management Wing', 'Chief Municipal Health Officer (CMHO)', 'Zone 1 - Vijayawada Central Ward', 'active', 48, 40, 8, 1, 2.2, 83.3, 4.9, 'On track', 'Solid Waste Masterplan, Public Hygiene'),
('a3c08eda-122c-50fd-9e7e-cb7c02bbde52', 'EMP-134', 'M. Swathi', 'MS', 'm.swathi@nexciv.gov', '+91 94401 00134', 'others', 'Sanitation & Solid Waste Management Wing', 'Sanitary Supervisor - Zone 1', 'Zone 1 - Vijayawada One-Town', 'active', 39, 32, 7, 1, 2.1, 82.1, 4.7, 'On track', 'Door-to-door Segregation, Dumper Bins'),
('971a15dc-0297-5d90-9d70-249dffcb55c3', 'EMP-135', 'P. Govindarajulu', 'PG', 'p.govindarajulu@nexciv.gov', '+91 94401 00135', 'others', 'Sanitation & Solid Waste Management Wing', 'Solid Waste Fleet Dispatcher', 'Zone 2 - Guntur Market Yard', 'active', 42, 34, 8, 2, 2.4, 81.0, 4.6, 'Needs review', 'Compactor Trucks, GPS Fleet Tracking'),
('6d6c66bc-b5fb-5a77-9210-0ad81e2c16aa', 'EMP-136', 'Ch. Sailaja', 'CS', 'ch.sailaja@nexciv.gov', '+91 94401 00136', 'others', 'Sanitation & Solid Waste Management Wing', 'Commercial Waste Enforcement Officer', 'Zone 4 - Vizag Jagadamba Center', 'active', 35, 30, 5, 0, 1.9, 85.7, 4.8, 'On track', 'Bulk Waste Generators, Plastic Ban'),
('b3fa8307-1af6-5d71-a761-fa586b126921', 'EMP-137', 'K. Appa Rao', 'KA', 'k.appa.rao@nexciv.gov', '+91 94401 00137', 'others', 'Sanitation & Solid Waste Management Wing', 'Dumping Yard Operations Lead', 'Zone 3 - Guntur Naidupet Yard', 'active', 33, 28, 5, 1, 2.5, 84.8, 4.5, 'On track', 'Landfill Management, Leachate Control'),
('e224c0e9-a70f-56f9-b506-04c02a28ac3d', 'EMP-138', 'B. Mahesh', 'BM', 'b.mahesh@nexciv.gov', '+91 94401 00138', 'others', 'Sanitation & Solid Waste Management Wing', 'Bio-Mining & Processing Supervisor', 'Zone 4 - Vizag Kapuluppada Yard', 'active', 36, 31, 5, 0, 2.0, 86.1, 4.8, 'On track', 'Legacy Waste Remediation, RDF Units'),
('7ddfb8a4-efdc-5b3d-8def-2ef7f7b12840', 'EMP-139', 'V. Padmavathi', 'VP', 'v.padmavathi@nexciv.gov', '+91 94401 00139', 'others', 'Sanitation & Solid Waste Management Wing', 'Public Sanitation Inspector', 'Zone 5 - Tirupati Temple Perimeter', 'active', 37, 33, 4, 0, 1.7, 89.2, 4.9, 'On track', 'Community Toilets, Swachh Survekshan'),
('96ff171e-aece-55ed-a0e9-9f0d5ef51a00', 'EMP-140', 'N. Durga Prasad', 'ND', 'n.durga.prasad@nexciv.gov', '+91 94401 00140', 'others', 'Sanitation & Solid Waste Management Wing', 'Rapid Cleanup Taskforce Head', 'Zone 2 - Vijayawada Benz Circle', 'active', 40, 35, 5, 1, 2.0, 87.5, 4.7, 'On track', 'C&D Debris Removal, Road Sweeping')
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
