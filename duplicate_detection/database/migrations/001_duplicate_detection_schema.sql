-- ==============================================================================
-- NEXCIV MULTILINGUAL & MULTIMODAL DUPLICATE COMPLAINT DETECTION SCHEMA
-- PostgreSQL + pgvector Migration (Fully Idempotent)
-- ==============================================================================

-- 1. Enable pgvector and UUID extensions
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2. MASTER INCIDENTS TABLE
-- Consolidates multiple duplicate citizen grievances into a single actionable incident
CREATE TABLE IF NOT EXISTS public.master_incidents (
    incident_id VARCHAR(100) PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    description TEXT NOT NULL,
    department VARCHAR(100) NOT NULL,
    department_code VARCHAR(50) NOT NULL,
    complaint_type VARCHAR(100) NOT NULL,
    municipality VARCHAR(50) NOT NULL,
    ward VARCHAR(100) NOT NULL,
    landmark VARCHAR(255),
    location_lat NUMERIC(10, 7),
    location_lng NUMERIC(10, 7),
    location_address TEXT,
    status VARCHAR(50) NOT NULL DEFAULT 'open', -- 'open', 'investigating', 'in_progress', 'resolved'
    priority VARCHAR(50) DEFAULT 'Medium',
    priority_score NUMERIC(5, 2) DEFAULT 60.0,
    linked_complaints_count INT DEFAULT 1,
    citizens_affected_count INT DEFAULT 1,
    primary_image_url TEXT,
    primary_image_hash VARCHAR(64),
    assigned_team VARCHAR(255),
    assigned_employee_id VARCHAR(50),
    first_reported_at TIMESTAMPTZ DEFAULT NOW(),
    last_reported_at TIMESTAMPTZ DEFAULT NOW(),
    resolved_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. COMPLAINT EMBEDDINGS TABLE (Layer 1 Dense Semantic Vectors)
-- Stores 1024-dimensional normalized dense vectors (bge-m3 / multilingual-e5) or 768-dim mpnet
CREATE TABLE IF NOT EXISTS public.complaint_embeddings (
    complaint_id VARCHAR(100) PRIMARY KEY REFERENCES public.complaints(id) ON DELETE CASCADE,
    incident_id VARCHAR(100),
    embedding vector(768), -- compatible with multilingual mpnet / adaptable to 1024
    embedding_model VARCHAR(100) NOT NULL DEFAULT 'paraphrase-multilingual-mpnet-base-v2',
    language_code VARCHAR(10) DEFAULT 'en',
    department_code VARCHAR(50),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. COMPLAINT INCIDENT LINKS TABLE
-- Maps every citizen complaint to its corresponding master incident with audit trail
CREATE TABLE IF NOT EXISTS public.complaint_links (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    complaint_id VARCHAR(100) NOT NULL REFERENCES public.complaints(id) ON DELETE CASCADE,
    master_incident_id VARCHAR(100) NOT NULL REFERENCES public.master_incidents(incident_id) ON DELETE CASCADE,
    link_type VARCHAR(50) NOT NULL DEFAULT 'ai_auto', -- 'ai_auto', 'officer_verified', 'citizen_confirmed'
    similarity_score NUMERIC(5, 4) NOT NULL DEFAULT 1.0,
    linked_by_user_id VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(complaint_id, master_incident_id)
);

-- 5. DUPLICATE PREDICTIONS AUDIT TABLE
-- Tracks every AI duplicate evaluation between newly submitted complaints and candidates
CREATE TABLE IF NOT EXISTS public.duplicate_predictions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    new_complaint_id VARCHAR(100) NOT NULL,
    candidate_incident_id VARCHAR(100) NOT NULL,
    composite_duplicate_score NUMERIC(5, 4) NOT NULL,
    semantic_similarity NUMERIC(5, 4) NOT NULL,
    location_similarity NUMERIC(5, 4) NOT NULL,
    cross_encoder_score NUMERIC(5, 4) NOT NULL,
    temporal_compatibility NUMERIC(5, 4) NOT NULL,
    image_similarity NUMERIC(5, 4) NOT NULL,
    distance_meters NUMERIC(10, 2),
    decision VARCHAR(50) NOT NULL, -- 'duplicate', 'review_required', 'new_incident'
    reasons JSONB DEFAULT '[]'::jsonb,
    evaluated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. DUPLICATE REVIEWS TABLE (Cadre & Officer Human-in-the-Loop Actions)
CREATE TABLE IF NOT EXISTS public.duplicate_reviews (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    prediction_id UUID REFERENCES public.duplicate_predictions(id) ON DELETE SET NULL,
    complaint_id VARCHAR(100) NOT NULL,
    target_incident_id VARCHAR(100) NOT NULL,
    reviewer_employee_id VARCHAR(100) NOT NULL,
    review_action VARCHAR(50) NOT NULL, -- 'confirm_duplicate', 'reject_duplicate', 'split_incident'
    reviewer_notes TEXT,
    reviewed_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. PERFORMANCE & RETRIEVAL INDEXES
CREATE INDEX IF NOT EXISTS idx_master_incidents_dept ON public.master_incidents(department_code);
CREATE INDEX IF NOT EXISTS idx_master_incidents_muni ON public.master_incidents(municipality);
CREATE INDEX IF NOT EXISTS idx_master_incidents_status ON public.master_incidents(status);
CREATE INDEX IF NOT EXISTS idx_complaint_links_incident ON public.complaint_links(master_incident_id);
CREATE INDEX IF NOT EXISTS idx_complaint_links_complaint ON public.complaint_links(complaint_id);

-- Optional HNSW Index for ultra-fast Cosine similarity search on vector embeddings
-- CREATE INDEX IF NOT EXISTS idx_complaint_embeddings_cosine 
-- ON public.complaint_embeddings USING hnsw (embedding vector_cosine_ops);
