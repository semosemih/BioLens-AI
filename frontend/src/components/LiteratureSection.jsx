import React, { useState } from 'react';
import { BookOpen, ExternalLink, ChevronDown, ChevronUp, Award } from 'lucide-react';

export default function LiteratureSection({ literature, geneSymbol }) {
  const [expandedIndex, setExpandedIndex] = useState(0);

  if (!literature || literature.length === 0) return null;

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            background: 'rgba(99, 102, 241, 0.15)',
            border: '1px solid rgba(99, 102, 241, 0.3)',
            borderRadius: '10px',
            padding: '8px',
            color: '#818cf8'
          }}>
            <BookOpen size={20} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Bilimsel Literatür & Yayınlar</h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              Europe PMC / PubMed hakemli makale kaynakları ({literature.length} yayın)
            </p>
          </div>
        </div>

        <span className="badge badge-purple" style={{ fontSize: '0.7rem' }}>
          Yüksek Atıflı
        </span>
      </div>

      {/* Articles List */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {literature.map((paper, idx) => {
          const isExpanded = expandedIndex === idx;

          return (
            <div
              key={idx}
              style={{
                background: 'rgba(10, 16, 28, 0.5)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '16px',
                transition: 'all 0.2s'
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: '12px' }}>
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px', flexWrap: 'wrap' }}>
                    {paper.journal && (
                      <span className="badge badge-blue" style={{ fontSize: '0.68rem', padding: '2px 8px' }}>
                        {paper.journal}
                      </span>
                    )}
                    {paper.year && (
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        {paper.year}
                      </span>
                    )}
                    {paper.citations > 0 && (
                      <span style={{
                        fontSize: '0.72rem',
                        color: '#fbbf24',
                        background: 'rgba(245, 158, 11, 0.12)',
                        padding: '2px 6px',
                        borderRadius: '4px',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '4px'
                      }}>
                        <Award size={11} />
                        {paper.citations} Atıf
                      </span>
                    )}
                  </div>

                  <h4 style={{
                    fontSize: '0.92rem',
                    fontWeight: 600,
                    color: '#f8fafc',
                    lineHeight: 1.4,
                    marginBottom: '6px'
                  }}>
                    {paper.title}
                  </h4>

                  <p style={{ fontSize: '0.76rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
                    {paper.authors}
                  </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                  {paper.url && (
                    <a
                      href={paper.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      style={{
                        background: 'rgba(255, 255, 255, 0.05)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: '6px',
                        padding: '6px',
                        color: 'var(--text-secondary)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        textDecoration: 'none'
                      }}
                      title="PubMed veya DOI Kaynağına Git"
                    >
                      <ExternalLink size={14} />
                    </a>
                  )}

                  {paper.abstract && (
                    <button
                      onClick={() => setExpandedIndex(isExpanded ? -1 : idx)}
                      style={{
                        background: 'rgba(255, 255, 255, 0.05)',
                        border: '1px solid var(--border-subtle)',
                        borderRadius: '6px',
                        padding: '6px',
                        color: 'var(--text-secondary)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}
                      title={isExpanded ? "Özeti Kapat" : "Özeti Göster"}
                    >
                      {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                    </button>
                  )}
                </div>
              </div>

              {/* Expandable Abstract */}
              {isExpanded && paper.abstract && (
                <div style={{
                  marginTop: '12px',
                  paddingTop: '12px',
                  borderTop: '1px solid rgba(255, 255, 255, 0.06)',
                  fontSize: '0.82rem',
                  color: 'var(--text-secondary)',
                  lineHeight: 1.55,
                  background: 'rgba(6, 9, 17, 0.4)',
                  padding: '12px',
                  borderRadius: '8px'
                }}>
                  <strong style={{ color: '#e2e8f0', display: 'block', marginBottom: '4px' }}>
                    Makale Özeti (Abstract):
                  </strong>
                  {paper.abstract}
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
