-- ==============================================================================
-- NEX-CIV LEGAL COMPLIANCE & GRIEVANCE MANAGEMENT EXTENSION SCHEMA
-- Andhra Pradesh Public Services Delivery Guarantee Act, 2017 (Act No. 6 of 2018)
-- Digital Personal Data Protection Act, 2023 & AP Departmental Citizen Charters
-- ==============================================================================

-- 1. Extend complaints table with statutory tracking & reasoned resolution columns
ALTER TABLE IF EXISTS public.complaints ADD COLUMN IF NOT EXISTS grievance_ref_number VARCHAR(100);
ALTER TABLE IF EXISTS public.complaints ADD COLUMN IF NOT EXISTS workflow_type VARCHAR(50) DEFAULT 'ordinary_grievance'; -- 'notified_service', 'ordinary_grievance', 'specialized'
ALTER TABLE IF EXISTS public.complaints ADD COLUMN IF NOT EXISTS legal_rule_id VARCHAR(100);
ALTER TABLE IF EXISTS public.complaints ADD COLUMN IF NOT EXISTS legal_source TEXT;
ALTER TABLE IF EXISTS public.complaints ADD COLUMN IF NOT EXISTS designated_officer VARCHAR(255);
ALTER TABLE IF EXISTS public.complaints ADD COLUMN IF NOT EXISTS appellate_authority VARCHAR(255);
ALTER TABLE IF EXISTS public.complaints ADD COLUMN IF NOT EXISTS expected_resolution_date TIMESTAMPTZ;
ALTER TABLE IF EXISTS public.complaints ADD COLUMN IF NOT EXISTS deadline_formatted VARCHAR(150);
ALTER TABLE IF EXISTS public.complaints ADD COLUMN IF NOT EXISTS action_taken TEXT;
ALTER TABLE IF EXISTS public.complaints ADD COLUMN IF NOT EXISTS resolution_summary TEXT;
ALTER TABLE IF EXISTS public.complaints ADD COLUMN IF NOT EXISTS rejection_reason TEXT;
ALTER TABLE IF EXISTS public.complaints ADD COLUMN IF NOT EXISTS escalation_level INT DEFAULT 1;
ALTER TABLE IF EXISTS public.complaints ADD COLUMN IF NOT EXISTS reopened_count INT DEFAULT 0;
ALTER TABLE IF EXISTS public.complaints ADD COLUMN IF NOT EXISTS reopened_at TIMESTAMPTZ;
ALTER TABLE IF EXISTS public.complaints ADD COLUMN IF NOT EXISTS reopen_reason TEXT;
ALTER TABLE IF EXISTS public.complaints ADD COLUMN IF NOT EXISTS appealed BOOLEAN DEFAULT FALSE;

-- 2. Legal Service Rules Table (Configurable statutory timelines & appellate cadre)
CREATE TABLE IF NOT EXISTS public.legal_service_rules (
    id VARCHAR(100) PRIMARY KEY,
    department_code VARCHAR(100) NOT NULL,
    department_name VARCHAR(255) NOT NULL,
    service_key VARCHAR(150) NOT NULL,
    service_name VARCHAR(255) NOT NULL,
    workflow_type VARCHAR(50) NOT NULL DEFAULT 'ordinary_grievance', -- 'notified_service', 'ordinary_grievance'
    legal_source TEXT NOT NULL,
    go_reference VARCHAR(255),
    prescribed_timeline_days INT NOT NULL,
    calculation_method VARCHAR(50) NOT NULL DEFAULT 'working_days', -- 'working_days', 'calendar_days'
    designated_officer_title VARCHAR(255) NOT NULL,
    first_appellate_authority VARCHAR(255) NOT NULL,
    second_appellate_authority VARCHAR(255) NOT NULL,
    appeal_deadline_days INT DEFAULT 30,
    compensation_applicable BOOLEAN DEFAULT FALSE,
    compensation_rate_per_day INT DEFAULT 0,
    max_compensation INT DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    version INT DEFAULT 1,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. Legal Rule Version History (Audit trail of administrative timeline modifications)
CREATE TABLE IF NOT EXISTS public.legal_rule_versions (
    id VARCHAR(100) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    rule_id VARCHAR(100) NOT NULL REFERENCES public.legal_service_rules(id) ON DELETE CASCADE,
    version INT NOT NULL,
    changes_summary TEXT NOT NULL,
    updated_by VARCHAR(255) NOT NULL,
    previous_config JSONB NOT NULL,
    new_config JSONB NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. Grievance Investigations (Employee field investigations and action taken reports)
CREATE TABLE IF NOT EXISTS public.grievance_investigations (
    id VARCHAR(100) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    complaint_id VARCHAR(100) NOT NULL REFERENCES public.complaints(id) ON DELETE CASCADE,
    employee_id VARCHAR(100) NOT NULL,
    employee_name VARCHAR(255) NOT NULL,
    investigation_performed TEXT NOT NULL,
    location_inspected VARCHAR(500),
    findings TEXT NOT NULL,
    action_taken TEXT NOT NULL,
    supporting_evidence_urls JSONB DEFAULT '[]'::jsonb,
    is_resolved BOOLEAN NOT NULL DEFAULT FALSE,
    inability_reason TEXT,
    further_action_required TEXT,
    supervisor_verified BOOLEAN DEFAULT FALSE,
    supervisor_id VARCHAR(100),
    supervisor_remarks TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. Grievance Activity Logs (Immutable Audit Trail - Rule 5.4)
CREATE TABLE IF NOT EXISTS public.grievance_activity_logs (
    id VARCHAR(100) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    complaint_id VARCHAR(100) NOT NULL,
    actor_role VARCHAR(50) NOT NULL, -- 'citizen', 'employee', 'department', 'system'
    actor_id VARCHAR(100),
    actor_name VARCHAR(255),
    action VARCHAR(255) NOT NULL,
    previous_status VARCHAR(50),
    new_status VARCHAR(50),
    comments TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. Grievance Escalations (Multi-Level Administrative Escalation Model - Rule 6.4)
CREATE TABLE IF NOT EXISTS public.grievance_escalations (
    id VARCHAR(100) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    complaint_id VARCHAR(100) NOT NULL REFERENCES public.complaints(id) ON DELETE CASCADE,
    escalation_level INT NOT NULL, -- 1: Assigned, 2: Supervising, 3: Dept Head, 4: Higher Authority
    escalated_from_id VARCHAR(100),
    escalated_to_title VARCHAR(255) NOT NULL,
    reason TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'open',
    action_taken TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Grievance Statutory Appeals (Sections 10 & 11 of Act No. 6 of 2018)
CREATE TABLE IF NOT EXISTS public.grievance_appeals (
    id VARCHAR(100) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    complaint_id VARCHAR(100) NOT NULL REFERENCES public.complaints(id) ON DELETE CASCADE,
    appeal_level INT NOT NULL DEFAULT 1, -- 1: First Appellate Authority, 2: Second Appellate Authority
    appellant_name VARCHAR(255) NOT NULL,
    appellant_email VARCHAR(255),
    appeal_ground TEXT NOT NULL,
    supporting_doc_urls JSONB DEFAULT '[]'::jsonb,
    status VARCHAR(50) DEFAULT 'filed', -- 'filed', 'under_hearing', 'disposed', 'rejected'
    hearing_date TIMESTAMPTZ,
    order_summary TEXT,
    order_doc_url TEXT,
    penalty_recommended NUMERIC(10, 2) DEFAULT 0.00,
    disposal_date TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. Grievance Citizen Feedback & Reopening (Rule 4.5)
CREATE TABLE IF NOT EXISTS public.grievance_feedback (
    id VARCHAR(100) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    complaint_id VARCHAR(100) NOT NULL REFERENCES public.complaints(id) ON DELETE CASCADE,
    citizen_name VARCHAR(255),
    rating INT CHECK (rating >= 1 AND rating <= 5),
    is_resolved_confirmed BOOLEAN NOT NULL DEFAULT TRUE,
    comments TEXT,
    reopen_requested BOOLEAN DEFAULT FALSE,
    reopen_reason TEXT,
    reopen_evidence_urls JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. Notification Logs
CREATE TABLE IF NOT EXISTS public.notification_logs (
    id VARCHAR(100) PRIMARY KEY DEFAULT gen_random_uuid()::text,
    complaint_id VARCHAR(100) NOT NULL,
    recipient VARCHAR(255) NOT NULL,
    channel VARCHAR(50) NOT NULL, -- 'email', 'sms', 'in_app'
    notification_type VARCHAR(100) NOT NULL,
    title VARCHAR(255) NOT NULL,
    message TEXT NOT NULL,
    status VARCHAR(50) DEFAULT 'sent',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for lightning fast compliance monitoring queries
CREATE INDEX IF NOT EXISTS idx_activity_logs_complaint ON public.grievance_activity_logs(complaint_id);
CREATE INDEX IF NOT EXISTS idx_investigations_complaint ON public.grievance_investigations(complaint_id);
CREATE INDEX IF NOT EXISTS idx_escalations_complaint ON public.grievance_escalations(complaint_id);
CREATE INDEX IF NOT EXISTS idx_appeals_complaint ON public.grievance_appeals(complaint_id);
CREATE INDEX IF NOT EXISTS idx_feedback_complaint ON public.grievance_feedback(complaint_id);
CREATE INDEX IF NOT EXISTS idx_legal_rules_dept ON public.legal_service_rules(department_code);
CREATE INDEX IF NOT EXISTS idx_complaints_ref_num ON public.complaints(grievance_ref_number);
