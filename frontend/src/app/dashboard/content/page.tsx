'use client';

import { useState } from 'react';
import { api } from '@/lib/api';
import type { ContentGenerateResponse } from '@/types';
import {
  Sparkles,
  Linkedin,
  Mail,
  Twitter,
  FileText,
  Copy,
  Check,
} from 'lucide-react';
import { cn } from '@/lib/utils';

const platforms = [
  { id: 'linkedin', name: 'LinkedIn', icon: Linkedin },
  { id: 'email', name: 'Email', icon: Mail },
  { id: 'twitter', name: 'Twitter', icon: Twitter },
  { id: 'blog', name: 'Blog', icon: FileText },
];

const tones = [
  'Professional',
  'Casual',
  'Persuasive',
  'Informative',
  'Friendly',
  'Urgent',
];

export default function ContentGeneratorPage() {
  const [platform, setPlatform] = useState('linkedin');
  const [targetAudience, setTargetAudience] = useState('');
  const [industry, setIndustry] = useState('');
  const [tone, setTone] = useState('Professional');
  const [topic, setTopic] = useState('');
  const [result, setResult] = useState<ContentGenerateResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [copiedIndex, setCopiedIndex] = useState<number | null>(null);

  const handleGenerate = async () => {
    if (!targetAudience || !industry) return;

    setLoading(true);
    try {
      const response = await api.generateContent({
        target_audience: targetAudience,
        industry,
        tone: tone.toLowerCase(),
        platform,
        topic: topic || undefined,
      });
      setResult(response);
    } catch (error) {
      console.error('Failed to generate content:', error);
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = (text: string, index: number) => {
    navigator.clipboard.writeText(text);
    setCopiedIndex(index);
    setTimeout(() => setCopiedIndex(null), 2000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Content Generator</h1>
        <p className="text-gray-500">Generate marketing content using AI</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Input Form */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Content Parameters
          </h2>

          {/* Platform Selection */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Platform
            </label>
            <div className="grid grid-cols-4 gap-2">
              {platforms.map((p) => (
                <button
                  key={p.id}
                  onClick={() => setPlatform(p.id)}
                  className={cn(
                    'flex flex-col items-center gap-2 p-3 rounded-lg border transition-colors',
                    platform === p.id
                      ? 'border-primary-500 bg-primary-50 text-primary-600'
                      : 'border-gray-200 hover:border-gray-300'
                  )}
                >
                  <p.icon className="w-5 h-5" />
                  <span className="text-xs">{p.name}</span>
                </button>
              ))}
            </div>
          </div>

          {/* Target Audience */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Target Audience *
            </label>
            <input
              type="text"
              value={targetAudience}
              onChange={(e) => setTargetAudience(e.target.value)}
              placeholder="e.g., Marketing Directors at mid-size companies"
              className="input"
            />
          </div>

          {/* Industry */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Industry *
            </label>
            <input
              type="text"
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              placeholder="e.g., SaaS, Healthcare, Finance"
              className="input"
            />
          </div>

          {/* Tone */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Tone
            </label>
            <div className="flex flex-wrap gap-2">
              {tones.map((t) => (
                <button
                  key={t}
                  onClick={() => setTone(t)}
                  className={cn(
                    'px-3 py-1 rounded-full text-sm transition-colors',
                    tone === t
                      ? 'bg-primary-600 text-white'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                  )}
                >
                  {t}
                </button>
              ))}
            </div>
          </div>

          {/* Topic */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Topic / Focus (Optional)
            </label>
            <textarea
              value={topic}
              onChange={(e) => setTopic(e.target.value)}
              placeholder="e.g., Introducing our new AI-powered analytics feature"
              className="input"
              rows={3}
            />
          </div>

          <button
            onClick={handleGenerate}
            disabled={loading || !targetAudience || !industry}
            className="btn-primary w-full flex items-center justify-center gap-2 disabled:opacity-50"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Sparkles className="w-5 h-5" />
                Generate Content
              </>
            )}
          </button>
        </div>

        {/* Results */}
        <div className="card">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">
            Generated Variations
          </h2>

          {!result ? (
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
                <FileText className="w-8 h-8 text-gray-400" />
              </div>
              <p className="text-gray-500">
                Fill in the parameters and click generate to create content
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {result.variations.map((variation, index) => (
                <div
                  key={index}
                  className="p-4 bg-gray-50 rounded-lg border border-gray-200"
                >
                  <div className="flex items-start justify-between mb-2">
                    <span className="inline-flex items-center gap-1 text-xs font-medium text-gray-500 bg-white px-2 py-1 rounded-full border">
                      Variation {index + 1}
                    </span>
                    <button
                      onClick={() => copyToClipboard(variation, index)}
                      className="flex items-center gap-1 text-sm text-gray-500 hover:text-primary-600"
                    >
                      {copiedIndex === index ? (
                        <>
                          <Check className="w-4 h-4 text-green-600" />
                          <span className="text-green-600">Copied!</span>
                        </>
                      ) : (
                        <>
                          <Copy className="w-4 h-4" />
                          Copy
                        </>
                      )}
                    </button>
                  </div>
                  <p className="text-gray-700 whitespace-pre-wrap">{variation}</p>
                </div>
              ))}

              {result.metadata?.tips && Array.isArray(result.metadata.tips) && (
                <div className="mt-6 p-4 bg-primary-50 rounded-lg">
                  <h3 className="font-medium text-primary-900 mb-2">Tips</h3>
                  <ul className="space-y-1">
                    {(result.metadata.tips as string[]).map((tip, i) => (
                      <li key={i} className="text-sm text-primary-700 flex items-start gap-2">
                        <span>•</span>
                        {tip}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
