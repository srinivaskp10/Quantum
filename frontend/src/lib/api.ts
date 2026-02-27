import axios, { AxiosInstance } from 'axios';
import type {
  User,
  AuthResponse,
  Lead,
  Customer,
  Campaign,
  SalesRecord,
  KPIs,
  LeadScoreResponse,
  ChatResponse,
  ContentGenerateResponse,
  InsightResponse,
} from '@/types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

class ApiClient {
  private client: AxiosInstance;
  private token: string | null = null;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.client.interceptors.request.use((config) => {
      if (this.token) {
        config.headers.Authorization = `Bearer ${this.token}`;
      }
      return config;
    });
  }

  setToken(token: string | null) {
    this.token = token;
    if (typeof window !== 'undefined') {
      if (token) {
        localStorage.setItem('token', token);
      } else {
        localStorage.removeItem('token');
      }
    }
  }

  loadToken() {
    if (typeof window !== 'undefined') {
      this.token = localStorage.getItem('token');
    }
  }

  // Auth
  async login(email: string, password: string): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/login', { email, password });
    this.setToken(response.data.access_token);
    return response.data;
  }

  async register(email: string, password: string, full_name: string, role: string): Promise<AuthResponse> {
    const response = await this.client.post<AuthResponse>('/auth/register', {
      email,
      password,
      full_name,
      role,
    });
    this.setToken(response.data.access_token);
    return response.data;
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.client.get<User>('/auth/me');
    return response.data;
  }

  logout() {
    this.setToken(null);
  }

  // Leads
  async getLeads(params?: { status?: string; source?: string; industry?: string }): Promise<Lead[]> {
    const response = await this.client.get<Lead[]>('/leads', { params });
    return response.data;
  }

  async getLead(id: number): Promise<Lead> {
    const response = await this.client.get<Lead>(`/leads/${id}`);
    return response.data;
  }

  async createLead(data: Partial<Lead>): Promise<Lead> {
    const response = await this.client.post<Lead>('/leads', data);
    return response.data;
  }

  async updateLead(id: number, data: Partial<Lead>): Promise<Lead> {
    const response = await this.client.put<Lead>(`/leads/${id}`, data);
    return response.data;
  }

  async deleteLead(id: number): Promise<void> {
    await this.client.delete(`/leads/${id}`);
  }

  async uploadLeadsCSV(file: File): Promise<{ created_count: number; errors: unknown[] }> {
    const formData = new FormData();
    formData.append('file', file);
    const response = await this.client.post('/leads/upload-csv', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return response.data;
  }

  // Customers
  async getCustomers(params?: { status?: string; industry?: string }): Promise<Customer[]> {
    const response = await this.client.get<Customer[]>('/customers', { params });
    return response.data;
  }

  async getCustomer(id: number): Promise<Customer> {
    const response = await this.client.get<Customer>(`/customers/${id}`);
    return response.data;
  }

  async createCustomer(data: Partial<Customer>): Promise<Customer> {
    const response = await this.client.post<Customer>('/customers', data);
    return response.data;
  }

  async convertLeadToCustomer(leadId: number): Promise<Customer> {
    const response = await this.client.post<Customer>(`/customers/convert-lead/${leadId}`);
    return response.data;
  }

  // Campaigns
  async getCampaigns(params?: { status?: string; campaign_type?: string }): Promise<Campaign[]> {
    const response = await this.client.get<Campaign[]>('/campaigns', { params });
    return response.data;
  }

  async getCampaign(id: number): Promise<Campaign> {
    const response = await this.client.get<Campaign>(`/campaigns/${id}`);
    return response.data;
  }

  async createCampaign(data: Partial<Campaign>): Promise<Campaign> {
    const response = await this.client.post<Campaign>('/campaigns', data);
    return response.data;
  }

  async updateCampaign(id: number, data: Partial<Campaign>): Promise<Campaign> {
    const response = await this.client.put<Campaign>(`/campaigns/${id}`, data);
    return response.data;
  }

  // Sales Records
  async getSalesRecords(params?: { stage?: string; customer_id?: number }): Promise<SalesRecord[]> {
    const response = await this.client.get<SalesRecord[]>('/sales', { params });
    return response.data;
  }

  async createSalesRecord(data: Partial<SalesRecord>): Promise<SalesRecord> {
    const response = await this.client.post<SalesRecord>('/sales', data);
    return response.data;
  }

  async updateSalesRecord(id: number, data: Partial<SalesRecord>): Promise<SalesRecord> {
    const response = await this.client.put<SalesRecord>(`/sales/${id}`, data);
    return response.data;
  }

  // Dashboard
  async getKPIs(): Promise<KPIs> {
    const response = await this.client.get<KPIs>('/dashboard/kpis');
    return response.data;
  }

  async getRevenueOverTime(months?: number): Promise<{ year: number; month: number; revenue: number }[]> {
    const response = await this.client.get('/dashboard/revenue-over-time', { params: { months } });
    return response.data;
  }

  async getLeadFunnel(): Promise<{ stage: string; count: number }[]> {
    const response = await this.client.get('/dashboard/lead-funnel');
    return response.data;
  }

  async getCampaignPerformance(): Promise<Campaign[]> {
    const response = await this.client.get('/dashboard/campaign-performance');
    return response.data;
  }

  async getLeadSources(): Promise<{ source: string; count: number }[]> {
    const response = await this.client.get('/dashboard/lead-sources');
    return response.data;
  }

  // AI Features
  async scoreLead(leadId: number): Promise<LeadScoreResponse> {
    const response = await this.client.post<LeadScoreResponse>('/ai/score-lead', { lead_id: leadId });
    return response.data;
  }

  async chat(message: string, conversationId?: string): Promise<ChatResponse> {
    const response = await this.client.post<ChatResponse>('/ai/chat', {
      message,
      conversation_id: conversationId,
    });
    return response.data;
  }

  async generateContent(data: {
    target_audience: string;
    industry: string;
    tone: string;
    platform: string;
    topic?: string;
    key_points?: string[];
  }): Promise<ContentGenerateResponse> {
    const response = await this.client.post<ContentGenerateResponse>('/ai/generate-content', data);
    return response.data;
  }

  async generateInsights(insightType: string): Promise<InsightResponse> {
    const response = await this.client.post<InsightResponse>('/ai/insights', {
      insight_type: insightType,
    });
    return response.data;
  }
}

export const api = new ApiClient();
