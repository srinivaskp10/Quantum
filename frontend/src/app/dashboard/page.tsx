'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { formatCurrency, formatNumber, formatPercent } from '@/lib/utils';
import type { KPIs } from '@/types';
import {
  DollarSign,
  Users,
  Target,
  TrendingUp,
  Megaphone,
  Building2,
  PieChart,
  ArrowUp,
} from 'lucide-react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  BarChart,
  Bar,
  PieChart as RechartsPie,
  Pie,
  Cell,
} from 'recharts';

const COLORS = ['#0ea5e9', '#22c55e', '#f59e0b', '#ef4444', '#8b5cf6', '#ec4899'];

export default function DashboardPage() {
  const [kpis, setKpis] = useState<KPIs | null>(null);
  const [revenueData, setRevenueData] = useState<{ year: number; month: number; revenue: number }[]>([]);
  const [funnelData, setFunnelData] = useState<{ stage: string; count: number }[]>([]);
  const [sourceData, setSourceData] = useState<{ source: string; count: number }[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [kpisRes, revenueRes, funnelRes, sourceRes] = await Promise.all([
          api.getKPIs(),
          api.getRevenueOverTime(12),
          api.getLeadFunnel(),
          api.getLeadSources(),
        ]);
        setKpis(kpisRes);
        setRevenueData(revenueRes);
        setFunnelData(funnelRes);
        setSourceData(sourceRes);
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const kpiCards = [
    {
      title: 'Total Revenue',
      value: formatCurrency(kpis?.total_revenue || 0),
      icon: DollarSign,
      color: 'bg-green-500',
      change: '+12.5%',
    },
    {
      title: 'Total Leads',
      value: formatNumber(kpis?.total_leads || 0),
      icon: Users,
      color: 'bg-blue-500',
      change: '+8.2%',
    },
    {
      title: 'Conversion Rate',
      value: formatPercent(kpis?.conversion_rate || 0),
      icon: Target,
      color: 'bg-purple-500',
      change: '+2.4%',
    },
    {
      title: 'Pipeline Value',
      value: formatCurrency(kpis?.pipeline_value || 0),
      icon: TrendingUp,
      color: 'bg-orange-500',
      change: '+15.3%',
    },
    {
      title: 'Active Campaigns',
      value: formatNumber(kpis?.active_campaigns || 0),
      icon: Megaphone,
      color: 'bg-pink-500',
      change: '+3',
    },
    {
      title: 'Total Customers',
      value: formatNumber(kpis?.total_customers || 0),
      icon: Building2,
      color: 'bg-cyan-500',
      change: '+5.1%',
    },
  ];

  const formattedRevenueData = revenueData.map((d) => ({
    name: `${d.month}/${d.year}`,
    revenue: d.revenue,
  }));

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-500">Welcome to your Sales Intelligence Platform</p>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {kpiCards.map((kpi) => (
          <div key={kpi.title} className="card">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-gray-500">{kpi.title}</p>
                <p className="text-2xl font-bold text-gray-900 mt-1">{kpi.value}</p>
                <div className="flex items-center gap-1 mt-2 text-sm text-green-600">
                  <ArrowUp className="w-4 h-4" />
                  {kpi.change}
                </div>
              </div>
              <div className={`p-3 rounded-lg ${kpi.color}`}>
                <kpi.icon className="w-6 h-6 text-white" />
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Revenue Over Time */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenue Over Time</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={formattedRevenueData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis dataKey="name" stroke="#6b7280" fontSize={12} />
                <YAxis stroke="#6b7280" fontSize={12} tickFormatter={(v) => `$${v / 1000}k`} />
                <Tooltip
                  formatter={(value: number) => [formatCurrency(value), 'Revenue']}
                  contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }}
                />
                <Line
                  type="monotone"
                  dataKey="revenue"
                  stroke="#0ea5e9"
                  strokeWidth={2}
                  dot={{ fill: '#0ea5e9' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Lead Funnel */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Lead Conversion Funnel</h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={funnelData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis type="number" stroke="#6b7280" fontSize={12} />
                <YAxis dataKey="stage" type="category" stroke="#6b7280" fontSize={12} width={100} />
                <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }} />
                <Bar dataKey="count" fill="#0ea5e9" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* Bottom Row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Lead Sources */}
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Lead Sources</h3>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <RechartsPie>
                <Pie
                  data={sourceData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="count"
                  nameKey="source"
                  label={({ source }) => source}
                >
                  {sourceData.map((_, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '8px', border: '1px solid #e5e7eb' }} />
              </RechartsPie>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Quick Stats */}
        <div className="card lg:col-span-2">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>
          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500">Avg. Deal Size</p>
              <p className="text-xl font-bold text-gray-900">
                {formatCurrency(kpis?.average_deal_size || 0)}
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500">Converted Leads</p>
              <p className="text-xl font-bold text-gray-900">
                {formatNumber(kpis?.converted_leads || 0)}
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500">Win Rate</p>
              <p className="text-xl font-bold text-gray-900">
                {kpis?.total_leads
                  ? formatPercent((kpis.converted_leads / kpis.total_leads) * 100)
                  : '0%'}
              </p>
            </div>
            <div className="p-4 bg-gray-50 rounded-lg">
              <p className="text-sm text-gray-500">Pipeline Coverage</p>
              <p className="text-xl font-bold text-gray-900">
                {kpis?.total_revenue
                  ? `${((kpis.pipeline_value / kpis.total_revenue) * 100).toFixed(0)}%`
                  : '0%'}
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
