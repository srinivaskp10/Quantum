'use client';

import { useEffect, useState } from 'react';
import { api } from '@/lib/api';
import { formatCurrency, formatDate, formatPercent, getStatusColor, cn } from '@/lib/utils';
import type { SalesRecord } from '@/types';
import { Plus, Search, Filter, MoreVertical, DollarSign } from 'lucide-react';

export default function SalesPage() {
  const [records, setRecords] = useState<SalesRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [stageFilter, setStageFilter] = useState('');

  useEffect(() => {
    const fetchRecords = async () => {
      try {
        const params: { stage?: string } = {};
        if (stageFilter) params.stage = stageFilter;
        const data = await api.getSalesRecords(params);
        setRecords(data);
      } catch (error) {
        console.error('Failed to fetch sales records:', error);
      } finally {
        setLoading(false);
      }
    };
    fetchRecords();
  }, [stageFilter]);

  const filteredRecords = records.filter((record) =>
    record.deal_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const closedWon = records.filter((r) => r.stage === 'closed_won');
  const pipeline = records.filter(
    (r) => !['closed_won', 'closed_lost'].includes(r.stage)
  );
  const totalRevenue = closedWon.reduce((sum, r) => sum + r.amount, 0);
  const pipelineValue = pipeline.reduce((sum, r) => sum + r.amount, 0);
  const weightedPipeline = pipeline.reduce(
    (sum, r) => sum + r.amount * (r.probability / 100),
    0
  );

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
          <h1 className="text-2xl font-bold text-gray-900">Sales Pipeline</h1>
          <p className="text-gray-500">Track and manage your deals</p>
        </div>
        <button className="btn-primary flex items-center gap-2">
          <Plus className="w-4 h-4" />
          New Deal
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <p className="text-sm text-gray-500">Total Revenue</p>
          <p className="text-2xl font-bold text-green-600">
            {formatCurrency(totalRevenue)}
          </p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Pipeline Value</p>
          <p className="text-2xl font-bold text-gray-900">
            {formatCurrency(pipelineValue)}
          </p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Weighted Pipeline</p>
          <p className="text-2xl font-bold text-blue-600">
            {formatCurrency(weightedPipeline)}
          </p>
        </div>
        <div className="card">
          <p className="text-sm text-gray-500">Win Rate</p>
          <p className="text-2xl font-bold text-purple-600">
            {records.length > 0
              ? formatPercent(
                  (closedWon.length /
                    records.filter((r) =>
                      ['closed_won', 'closed_lost'].includes(r.stage)
                    ).length) *
                    100 || 0
                )
              : '0%'}
          </p>
        </div>
      </div>

      {/* Filters */}
      <div className="card">
        <div className="flex flex-col md:flex-row gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search deals..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="input pl-10"
            />
          </div>
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-400" />
            <select
              value={stageFilter}
              onChange={(e) => setStageFilter(e.target.value)}
              className="input w-auto"
            >
              <option value="">All Stages</option>
              <option value="prospecting">Prospecting</option>
              <option value="qualification">Qualification</option>
              <option value="proposal">Proposal</option>
              <option value="negotiation">Negotiation</option>
              <option value="closed_won">Closed Won</option>
              <option value="closed_lost">Closed Lost</option>
            </select>
          </div>
        </div>
      </div>

      {/* Sales Table */}
      <div className="card overflow-hidden p-0">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Deal
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Stage
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Amount
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Probability
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Close Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Created
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredRecords.map((record) => (
                <tr key={record.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 rounded-lg bg-green-100 flex items-center justify-center">
                        <DollarSign className="w-5 h-5 text-green-600" />
                      </div>
                      <div>
                        <p className="font-medium text-gray-900">{record.deal_name}</p>
                        <p className="text-sm text-gray-500">
                          {record.product_name || 'N/A'}
                        </p>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={cn(
                        'inline-flex px-2 py-1 text-xs font-medium rounded-full',
                        getStatusColor(record.stage)
                      )}
                    >
                      {record.stage.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4 font-medium text-gray-900">
                    {formatCurrency(record.amount)}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex items-center gap-2">
                      <div className="w-16 bg-gray-200 rounded-full h-2">
                        <div
                          className={cn(
                            'h-2 rounded-full',
                            record.probability >= 70
                              ? 'bg-green-500'
                              : record.probability >= 40
                              ? 'bg-yellow-500'
                              : 'bg-red-500'
                          )}
                          style={{ width: `${record.probability}%` }}
                        />
                      </div>
                      <span className="text-sm text-gray-600">
                        {formatPercent(record.probability)}
                      </span>
                    </div>
                  </td>
                  <td className="px-6 py-4 text-gray-500">
                    {record.close_date ? formatDate(record.close_date) : '-'}
                  </td>
                  <td className="px-6 py-4 text-gray-500">
                    {formatDate(record.created_at)}
                  </td>
                  <td className="px-6 py-4">
                    <button className="p-2 text-gray-400 hover:bg-gray-100 rounded-lg">
                      <MoreVertical className="w-4 h-4" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
