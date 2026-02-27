'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { formatCurrency, formatPercent, formatDate, getStatusColor, cn } from '@/lib/utils';
import type { Campaign } from '@/types';
import { Plus, Search, Filter, MoreVertical, TrendingUp, TrendingDown } from 'lucide-react';

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  useEffect(() => {
    const fetchCampaigns = async () => {
      try {
        const params: { status?: string } = {};
        if (statusFilter) params.status = statusFilter;
        const data = await api.getCampaigns(params);
        setCampaigns(data);
      } catch (error) {
        console.error('Failed to fetch campaigns:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchCampaigns();
  }, [statusFilter]);

  const filteredCampaigns = campaigns.filter((campaign) =>
    campaign.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const totalBudget = campaigns.reduce((sum, c) => sum + c.budget, 0);
  const totalSpent = campaigns.reduce((sum, c) => sum + c.spent, 0);
  const totalLeads = campaigns.reduce((sum, c) => sum + c.leads_generated, 0);
  const totalRevenue = campaigns.reduce((sum, c) => sum + c.revenue_attributed, 0);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Campaigns</h1>
          <p className="text-gray-500">Manage your marketing campaigns</p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          Create Campaign
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <p className="text-sm text-gray-500">Total Budget</p>
          <p className="text-2xl font-bold text-gray-900">{formatCurrency(totalBudget)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Total Spent</p>
          <p className="text-2xl font-bold text-orange-600">{formatCurrency(totalSpent)}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Leads Generated</p>
          <p className="text-2xl font-bold text-blue-600">{totalLeads}</p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Revenue Attributed</p>
          <p className="text-2xl font-bold text-green-600">{formatCurrency(totalRevenue)}</p>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search campaigns..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="input w-auto"
            >
              <option value="">All Status</option>
              <option value="draft">Draft</option>
              <option value="active">Active</option>
              <option value="paused">Paused</option>
              <option value="completed">Completed</option>
            </select>
          </div>
        </div>
      </div>

      {/* Campaigns Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCampaigns.map((campaign) => (
          <div key={campaign.id} className="card">
            <div className="flex items-start justify-between mb-4">
              <div>
                <span
                  className={cn(
                    'inline-flex px-2 py-1 text-xs font-medium rounded-full mb-2',
                    getStatusColor(campaign.status)
                  )}
                >
                  {campaign.status}
                </span>
                <h3 className="font-semibold text-gray-900">{campaign.name}</h3>
                <p className="text-sm text-gray-500 capitalize">
                  {campaign.campaign_type.replace('_', ' ')}
                </p>
              </div>
              <button className="p-2 text-gray-400 hover:bg-gray-100 rounded-lg">
                <MoreVertical className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Budget</span>
                <span className="font-medium text-gray-900">
                  {formatCurrency(campaign.spent)} / {formatCurrency(campaign.budget)}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div
                  className="bg-primary-600 h-2 rounded-full"
                  style={{
                    width: `${Math.min((campaign.spent / campaign.budget) * 100, 100)}%`,
                  }}
                />
              </div>

              <div className="grid grid-cols-2 gap-4 pt-2">
                <div>
                  <p className="text-xs text-gray-500">Leads</p>
                  <p className="font-semibold text-gray-900">{campaign.leads_generated}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">Conversions</p>
                  <p className="font-semibold text-gray-900">{campaign.conversions}</p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">CTR</p>
                  <p className="font-semibold text-gray-900">
                    {formatPercent(campaign.click_through_rate)}
                  </p>
                </div>
                <div>
                  <p className="text-xs text-gray-500">ROI</p>
                  <div className="flex items-center gap-1">
                    {campaign.roi >= 0 ? (
                      <TrendingUp className="w-4 h-4 text-green-600" />
                    ) : (
                      <TrendingDown className="w-4 h-4 text-red-600" />
                    )}
                    <span
                      className={cn(
                        'font-semibold',
                        campaign.roi >= 0 ? 'text-green-600' : 'text-red-600'
                      )}
                    >
                      {formatPercent(campaign.roi)}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
