import React, { useState } from 'react';
import { Sparkles, Copy, Check, BookOpen, Brain, Activity } from 'lucide-react';

export default function AISummaryCard({ aiSummary, geneSymbol }) {
  const [copied, setCopied] = useState(false);

  if (!aiSummary || !aiSummary.sections) return null;

  const handleCopy = () => {
    const textToCopy = aiSummary.sections.map(s => {
      return `### ${s.title}\n` + s.items.map(item => `• ${item}`).join('\n');
    }).join('\n\n');

    navigator.clipboard.writeText(`BioLens AI - ${geneSymbol} Biyomedikal Özet:\n\n` + textToCopy);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  return (
    <div className="glass-panel" style={{
      padding: '26px',
      position: 'relative',
      background: 'linear-gradient(135deg, rgba(15, 23, 42, 0.85) 0%, rgba(13, 27, 42, 0.75) 100%)',
      border: '1px solid rgba(56, 189, 248, 0.25)',
      boxShadow: '0 12px 32px rgba(0, 0, 0, 0.45), 0 0 35px rgba(56, 189, 248, 0.1)'
    }}>
      {/* Card Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
        marginBottom: '20px',
        paddingBottom: '16px',
        borderBottom: '1px solid var(--border-subtle)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            background: 'linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)',
            borderRadius: '12px',
            padding: '10px',
            color: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 15px rgba(14, 165, 233, 0.35)'
          }}>
            <Sparkles size={22} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc' }}>
                Biyomedikal Yapay Zekâ Analizi
              </h3>
              <span className="badge badge-cyan" style={{ fontSize: '0.7rem' }}>
                {geneSymbol}
              </span>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
              {aiSummary.source || 'BioLens Biyomedikal NLP & LLM Sentezi'}
            </p>
          </div>
        </div>

        <button
          onClick={handleCopy}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: copied ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.06)',
            color: copied ? '#34d399' : 'var(--text-secondary)',
            border: copied ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid var(--border-subtle)',
            borderRadius: '8px',
            padding: '7px 12px',
            fontSize: '0.8rem',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
        >
          {copied ? <Check size={14} /> : <Copy size={14} />}
          {copied ? 'Kopyalandı' : 'Özeti Kopyala'}
        </button>
      </div>

      {/* Sections Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '18px' }}>
        {aiSummary.sections.map((section, idx) => (
          <div
            key={idx}
            style={{
              background: 'rgba(9, 14, 26, 0.6)',
              borderRadius: 'var(--radius-md)',
              border: '1px solid var(--border-subtle)',
              padding: '16px 18px',
              transition: 'transform 0.2s, border-color 0.2s',
            }}
          >
            <h4 style={{
              fontSize: '0.95rem',
              fontWeight: 600,
              color: '#38bdf8',
              marginBottom: '10px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}>
              {section.title}
            </h4>

            <ul style={{ listStyle: 'none', padding: 0, margin: 0, display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {section.items.map((item, itemIdx) => (
                <li
                  key={itemIdx}
                  style={{
                    fontSize: '0.85rem',
                    color: 'var(--text-primary)',
                    lineHeight: 1.55,
                    display: 'flex',
                    alignItems: 'flex-start',
                    gap: '8px'
                  }}
                >
                  <span style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    background: '#0ea5e9',
                    marginTop: '8px',
                    flexShrink: 0
                  }}></span>
                  <span dangerouslySetInnerHTML={{
                    __html: item.replace(/\*\*(.*?)\*\*/g, '<strong style="color: #f1f5f9; font-weight:600;">$1</strong>')
                  }}></span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
