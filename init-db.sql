-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create enum types
CREATE TYPE user_role AS ENUM ('admin', 'sales', 'marketing');
CREATE TYPE lead_status AS ENUM ('new', 'contacted', 'qualified', 'proposal', 'negotiation', 'closed_won', 'closed_lost');
CREATE TYPE lead_source AS ENUM ('website', 'referral', 'linkedin', 'cold_call', 'email_campaign', 'trade_show', 'other');
CREATE TYPE customer_status AS ENUM ('active', 'inactive', 'churned');
CREATE TYPE campaign_status AS ENUM ('draft', 'active', 'paused', 'completed', 'cancelled');
CREATE TYPE campaign_type AS ENUM ('email', 'social_media', 'ppc', 'content', 'event', 'webinar', 'other');
CREATE TYPE deal_stage AS ENUM ('prospecting', 'qualification', 'proposal', 'negotiation', 'closed_won', 'closed_lost');
CREATE TYPE document_type AS ENUM ('lead_note', 'customer_note', 'campaign_content', 'sales_note', 'insight');
