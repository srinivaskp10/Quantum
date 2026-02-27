export type UserRole = 'admin' | 'sales' | 'marketing';

export interface User {
  id: number;
  email: string;
  full_name: string;
  role: UserRole;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export type LeadStatus = 
  | 'new' 
  | 'contacted' 
  | 'qualified' 
  | 'proposal' 
  | 'negotiation' 
  | 'closed_won' 
  | 'closed_lost';

export type LeadSource = 
  | 'website' 
  | 'referral' 
  | 'linkedin' 
  | 'cold_call' 
  | 'email_campaign' 
  | 'trade_show' 
  | 'other';

export interface Lead {
  id: number;
  company_name: string;
  contact_name: string;
  email: string;
  phone?: string;
  job_title?: string;
  industry?: string;
  company_size?: string;
  annual_revenue?: number;
  location?: string;
  status: LeadStatus;
  source: LeadSource;
  ai_score?: number;
  ai_score_reasoning?: string;
  estimated_value?: number;
  notes?: string;
  assigned_to?: number;
  created_at: string;
  updated_at: string;
}

export type CustomerStatus = 'active' | 'inactive' | 'churned';

export interface Customer {
  id: number;
  lead_id?: number;
  company_name: string;
  contact_name: string;
  email: string;
  phone?: string;
  industry?: string;
  company_size?: string;
  location?: string;
  status: CustomerStatus;
  lifetime_value: number;
  total_purchases: number;
  created_at: string;
  updated_at: string;
}

export type CampaignStatus = 'draft' | 'active' | 'paused' | 'completed' | 'cancelled';
export type CampaignType = 'email' | 'social_media' | 'ppc' | 'content' | 'event' | 'webinar' | 'other';

export interface Campaign {
  id: number;
  name: string;
  description?: string;
  campaign_type: CampaignType;
  status: CampaignStatus;
  target_audience?: string;
  target_industry?: string;
  budget: number;
  spent: number;
  impressions: number;
  clicks: number;
  conversions: number;
  leads_generated: number;
  revenue_attributed: number;
  click_through_rate: number;
  conversion_rate: number;
  cost_per_lead: number;
  roi: number;
  start_date?: string;
  end_date?: string;
  created_at: string;
  updated_at: string;
}

export type DealStage = 
  | 'prospecting' 
  | 'qualification' 
  | 'proposal' 
  | 'negotiation' 
  | 'closed_won' 
  | 'closed_lost';

export interface SalesRecord {
  id: number;
  customer_id: number;
  sales_rep_id?: number;
  deal_name: string;
  description?: string;
  amount: number;
  currency: string;
  stage: DealStage;
  probability: number;
  product_name?: string;
  quantity: number;
  close_date?: string;
  actual_close_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export interface KPIs {
  total_revenue: number;
  total_leads: number;
  converted_leads: number;
  conversion_rate: number;
  active_campaigns: number;
  total_customers: number;
  pipeline_value: number;
  average_deal_size: number;
}

export interface LeadScoreResponse {
  lead_id: number;
  score: number;
  probability: number;
  reasoning: string;
  factors: string[];
  recommendations: string[];
}

export interface ChatResponse {
  answer: string;
  sql_query?: string;
  data?: Record<string, unknown>[];
  conversation_id: string;
}

export interface ContentGenerateResponse {
  variations: string[];
  platform: string;
  tone: string;
  metadata: Record<string, unknown>;
}

export interface InsightResponse {
  insight_type: string;
  title: string;
  summary: string;
  key_metrics: Record<string, unknown>;
  recommendations: string[];
  generated_at: string;
}
