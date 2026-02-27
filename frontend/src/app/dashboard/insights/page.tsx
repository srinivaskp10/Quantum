'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import type { InsightResponse } from '@/types';
import {
  Sparkles,
  TrendingUp,
  Megaphone,
  BarChart3,
  Users,
  RefreshCw,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const insightTypes = [
  {
    id: 'weekly_sales',
    name: 'Weekly Sales Summary',
    description: 'AI-generated summary of your weekly sales performance',
    icon: TrendingUp,
    color: 'bg-green-100 text-green-600',
  },
  {
    id: 'campaign_performance',
    name: 'Campaign Performance',
    description: 'Analysis of your marketing campaign effectiveness',
    icon: Megaphone,
    color: 'bg-blue-100 text-blue-600',
  },
  {
    id: 'revenue_forecast',
    name: 'Revenue Forecast',
    description: 'Predictive forecast for next quarter revenue',
    icon: BarChart3,
    color: 'bg-purple-100 text-purple-600',
  },
  {
    id: 'lead_analysis',
    name: 'Lead Funnel Analysis',
    description: 'Analysis of your lead sources and conversion funnel',
    icon: Users,
    color: 'bg-orange-100 text-orange-600',
  },
];

export default function InsightsPage() {
  const [selectedType, setSelectedType] = useState<string | null>(null);
  const [insight, setInsight] = useState<InsightResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const handleGenerateInsight = async (insightType: string) => {
    setSelectedType(insightType);
    setLoading(true);
    setInsight(null);

    try {
      const result = await api.generateInsights(insightType);
      setInsight(result);
    } catch (error) {
      console.error('Failed to generate insight:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">AI Insights</h1>
        <p className="text-gray-500">Generate intelligent insights from your business data</p>
      </div>

      {/* Insight Type Selection */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {insightTypes.map((type) => (
          <button
            key={type.id}
            onClick={() => handleGenerateInsight(type.id)}
            className={cn(
              'card text-left transition-all hover:shadow-md',
              selectedType === type.id && 'ring-2 ring-primary-500'
            )}
          >
            <div className={cn('w-12 h-12 rounded-lg flex items-center justify-center mb-3', type.color)}>
              <type.icon className="w-6 h-6" />
            </div>
            <h3 className="font-semibold text-gray-900">{type.name}</h3>
            <p className="text-sm text-gray-500 mt-1">{type.description}</p>
          </button>
        ))}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="card">
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-primary-100 mb-4">
                <Sparkles className="w-8 h-8 text-primary-600 animate-pulse" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Generating Insights...
              </h3>
              <p className="text-gray-500">AI is analyzing your data</p>
            </div>
          </div>
        </div>
      )}

      {/* Insight Result */}
      {insight && !loading && (
        <div className="card">
          <div className="flex items-start justify-between mb-6">
            <div>
              <h2 className="text-xl font-bold text-gray-900">{insight.title}</h2>
              <p className="text-sm text-gray-500 mt-1">
                Generated: {new Date(insight.generated_at).toLocaleString()}
              </p>
            </div>
            <button
              onClick={() => selectedType && handleGenerateInsight(selectedType)}
              className="btn-secondary flex items-center gap-2"
            >
              <RefreshCw className="w-4 h-4" />
              Regenerate
            </button>
          </div>

          {/* Summary */}
          <div className="prose max-w-none mb-6">
            <p className="text-gray-700 leading-relaxed">{insight.summary}</p>
          </div>

          {/* Key Metrics */}
          {insight.key_metrics && (
            <div className="mb-6">
              <h3 className="font-semibold text-gray-900 mb-3">Key Metrics</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(insight.key_metrics)
                  .filter(([key, value]) => typeof value === 'number' || typeof value === 'string')
                  .slice(0, 8)
                  .map(([key, value]) => (
                    <div key={key} className="bg-gray-50 rounded-lg p-4">
                      <p className="text-sm text-gray-500 capitalize">
                        {key.replace(/_/g, ' ')}
                      </p>
                      <p className="text-lg font-semibold text-gray-900 mt-1">
                        {typeof value === 'number'
                          ? value.toLocaleString()
                          : String(value)}
                      </p>
                    </div>
                  ))}
              </div>
            </div>
          )}

          {/* Recommendations */}
          {insight.recommendations && insight.recommendations.length > 0 && (
            <div>
              <h3 className="font-semibold text-gray-900 mb-3">Recommendations</h3>
              <div className="space-y-3">
                {insight.recommendations.map((rec, index) => (
                  <div
                    key={index}
                    className="flex items-start gap-3 p-4 bg-primary-50 rounded-lg"
                  >
                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-primary-600 text-white flex items-center justify-center text-sm font-medium">
                      {index + 1}
                    </div>
                    <p className="text-gray-700">{rec}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
