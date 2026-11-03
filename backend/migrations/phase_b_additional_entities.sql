-- Phase B – Additional Entities Migration for NEXCIV
-- Run this script against the Supabase/Postgres database.

-- 1. SLA Rules Table
CREATE TABLE IF NOT EXISTS public.sla_rules (
    sla_rule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    municipality_code VARCHAR(20) NOT NULL REFERENCES public.municipalities(code) ON DELETE CASCADE,
    department VARCHAR(100) NOT NULL,
    complaint_category VARCHAR(100) NOT NULL,
    severity_level VARCHAR(20) NOT NULL,
    resolution_duration INT NOT NULL, -- numeric value
    duration_unit VARCHAR(10) NOT NULL, -- e.g., 'hours', 'days'
    calendar_type VARCHAR(20) NOT NULL, -- e.g., 'working_days', 'calendar_days'
    source_document VARCHAR(255),
    source_url TEXT,
    government_order_number VARCHAR(50),
    effective_from DATE,
    effective_to DATE,
    verification_status VARCHAR(20) DEFAULT 'unverified',
    last_verified_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sla_rules_municipality ON public.sla_rules(municipality_code);
CREATE INDEX IF NOT EXISTS idx_sla_rules_department ON public.sla_rules(department);

-- 2. Employee Skills Table (many‑to‑many)
CREATE TABLE IF NOT EXISTS public.employee_skills (
    employee_id VARCHAR(100) NOT NULL REFERENCES public.employees(id) ON DELETE CASCADE,
    skill_name VARCHAR(100) NOT NULL,
    proficiency INT CHECK (proficiency BETWEEN 1 AND 5),
    PRIMARY KEY (employee_id, skill_name)
);

-- 3. Employee Availability Table
CREATE TABLE IF NOT EXISTS public.employee_availability (
    employee_id VARCHAR(100) PRIMARY KEY REFERENCES public.employees(id) ON DELETE CASCADE,
    availability_status VARCHAR(20) NOT NULL DEFAULT 'available', -- available, on_leave, out_of_office
    available_from TIMESTAMPTZ,
    available_to TIMESTAMPTZ,
    notes TEXT,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Priority Predictions Table (stores each prediction instance)
CREATE TABLE IF NOT EXISTS public.priority_predictions (
    prediction_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    complaint_id VARCHAR(100) NOT NULL REFERENCES public.complaints(id) ON DELETE CASCADE,
    model_version VARCHAR(50) NOT NULL,
    priority_label VARCHAR(20) NOT NULL,
    priority_score NUMERIC(5,2) NOT NULL,
    confidence NUMERIC(5,4),
    predicted_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_priority_predictions_complaint ON public.priority_predictions(complaint_id);

-- 5. Priority Feature Values (store raw feature values used for scoring)
CREATE TABLE IF NOT EXISTS public.priority_feature_values (
    feature_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prediction_id UUID NOT NULL REFERENCES public.priority_predictions(prediction_id) ON DELETE CASCADE,
    feature_name VARCHAR(100) NOT NULL,
    feature_value NUMERIC,
    CONSTRAINT uq_feature_per_prediction UNIQUE (prediction_id, feature_name)
);

-- 6. Employee Assignments Table (work orders)
CREATE TABLE IF NOT EXISTS public.employee_assignments (
    assignment_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    complaint_id VARCHAR(100) NOT NULL REFERENCES public.complaints(id) ON DELETE CASCADE,
    employee_id VARCHAR(100) NOT NULL REFERENCES public.employees(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ DEFAULT NOW(),
    status VARCHAR(20) NOT NULL DEFAULT 'assigned', -- assigned, in_progress, completed, cancelled
    resolved_at TIMESTAMPTZ,
    notes TEXT
);
CREATE INDEX IF NOT EXISTS idx_employee_assignments_employee ON public.employee_assignments(employee_id);
CREATE INDEX IF NOT EXISTS idx_employee_assignments_complaint ON public.employee_assignments(complaint_id);

-- 7. Workload Snapshots (periodic aggregation for reporting)
CREATE TABLE IF NOT EXISTS public.workload_snapshots (
    snapshot_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id VARCHAR(100) NOT NULL REFERENCES public.employees(id) ON DELETE CASCADE,
    municipality_code VARCHAR(20) NOT NULL REFERENCES public.municipalities(code) ON DELETE CASCADE,
    workload_score NUMERIC(5,2) NOT NULL,
    snapshot_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Escalation Rules Table
CREATE TABLE IF NOT EXISTS public.escalation_rules (
    escalation_rule_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    municipality_code VARCHAR(20) NOT NULL REFERENCES public.municipalities(code) ON DELETE CASCADE,
    department VARCHAR(100) NOT NULL,
    priority_threshold INT NOT NULL, -- e.g., priority score > 80 triggers escalation
    escalation_level VARCHAR(20) NOT NULL, -- e.g., 'supervisor', 'head', 'commissioner'
    response_time_hours INT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. Escalation History Table
CREATE TABLE IF NOT EXISTS public.escalation_history (
    escalation_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    complaint_id VARCHAR(100) NOT NULL REFERENCES public.complaints(id) ON DELETE CASCADE,
    escalated_by VARCHAR(100) NOT NULL REFERENCES public.employees(id),
    escalation_level VARCHAR(20) NOT NULL,
    reason TEXT,
    escalated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 10. Resolution Records Table
CREATE TABLE IF NOT EXISTS public.resolution_records (
    resolution_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    complaint_id VARCHAR(100) NOT NULL REFERENCES public.complaints(id) ON DELETE CASCADE,
    employee_id VARCHAR(100) NOT NULL REFERENCES public.employees(id) ON DELETE CASCADE,
    resolution_notes TEXT,
    proof_url TEXT,
    resolved_at TIMESTAMPTZ DEFAULT NOW()
);

-- 11. Employee Audit Logs (track admin actions)
CREATE TABLE IF NOT EXISTS public.employee_audit_logs (
    log_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id VARCHAR(100) NOT NULL REFERENCES public.employees(id) ON DELETE CASCADE,
    action VARCHAR(100) NOT NULL,
    performed_by VARCHAR(100) NOT NULL REFERENCES public.employees(id),
    details JSONB,
    performed_at TIMESTAMPTZ DEFAULT NOW()
);

-- 12. Priority Model Versions Table (track model updates)
CREATE TABLE IF NOT EXISTS public.priority_model_versions (
    model_version_id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL,
    version VARCHAR(20) NOT NULL,
    description TEXT,
    deployed_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for fast lookup
CREATE INDEX IF NOT EXISTS idx_complaints_municipality ON public.complaints(municipal_corporation);
CREATE INDEX IF NOT EXISTS idx_complaints_department ON public.complaints(department);
CREATE INDEX IF NOT EXISTS idx_employee_assignments_status ON public.employee_assignments(status);

-- End of Phase B migration
