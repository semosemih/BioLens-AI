import React, { useState } from 'react';
import { AlertTriangle, ExternalLink, Target, Filter, Search, Dna } from 'lucide-react';

export default function MutationTable({ clinvarVariants, uniprotVariants, onSelectResidue, activeResidue }) {
  const [filterType, setFilterType] = useState('all'); // all, clinvar, uniprot
  const [searchFilter, setSearchFilter] = useState('');

  // Combine and normalize variants
  const combinedList = [];

  if (clinvarVariants && clinvarVariants.length > 0) {
    clinvarVariants.forEach(v => {
      combinedList.push({
        source: 'ClinVar',
        id: v.clinvarId,
        change: v.proteinChange || v.title,
        position: v.position,
        significance: v.clinicalSignificance || 'Pathogenic',
        disease: (v.conditions && v.conditions.length > 0) ? v.conditions.join(', ') : 'Belirtilmemiş',
        url: v.clinvarUrl
      });
    });
  }

  if (uniprotVariants && uniprotVariants.length > 0) {
    uniprotVariants.forEach((v, idx) => {
      combinedList.push({
        source: 'UniProt',
        id: v.featureId || `uni-${idx}`,
        change: v.change || `Pos ${v.position}`,
        position: v.position ? parseInt(v.position) : null,
        significance: v.type === 'Natural variant' ? 'Doğal Varyant' : 'Mutagenez',
        disease: v.description || 'Klinik veri',
        url: `https://www.uniprot.org/uniprotkb?query=${v.featureId || ''}`
      });
    });
  }

  // Filter list
  const filtered = combinedList.filter(item => {
    if (filterType === 'clinvar' && item.source !== 'ClinVar') return false;
    if (filterType === 'uniprot' && item.source !== 'UniProt') return false;
    if (searchFilter) {
      const q = searchFilter.toLowerCase();
      const matchChange = item.change && item.change.toLowerCase().includes(q);
      const matchDisease = item.disease && item.disease.toLowerCase().includes(q);
      const matchPos = item.position && item.position.toString().includes(q);
      if (!matchChange && !matchDisease && !matchPos) return false;
    }
    return true;
  });

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      {/* Title & Filter Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
        marginBottom: '16px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            background: 'rgba(244, 63, 94, 0.15)',
            border: '1px solid rgba(244, 63, 94, 0.3)',
            borderRadius: '10px',
            padding: '8px',
            color: '#fb7185'
          }}>
            <AlertTriangle size={20} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Bilinen Mutasyonlar ve Varyantlar</h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
              ClinVar & UniProt patojenik klinik kayıtları ({combinedList.length} varyant)
            </p>
          </div>
        </div>

        {/* Filters */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{ position: 'relative' }}>
            <Search size={14} style={{ position: 'absolute', left: '10px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input
              type="text"
              placeholder="Mutasyon / Hastalık ara..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              style={{
                background: 'rgba(255, 255, 255, 0.05)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '8px',
                padding: '6px 10px 6px 30px',
                color: '#fff',
                fontSize: '0.8rem',
                outline: 'none',
                width: '180px'
              }}
            />
          </div>

          <div style={{ display: 'flex', gap: '4px', background: 'rgba(255, 255, 255, 0.04)', padding: '2px', borderRadius: '8px' }}>
            {['all', 'clinvar', 'uniprot'].map(t => (
              <button
                key={t}
                onClick={() => setFilterType(t)}
                style={{
                  padding: '4px 8px',
                  borderRadius: '6px',
                  background: filterType === t ? 'rgba(56, 189, 248, 0.2)' : 'transparent',
                  color: filterType === t ? '#38bdf8' : 'var(--text-secondary)',
                  border: 'none',
                  fontSize: '0.75rem',
                  fontWeight: filterType === t ? 600 : 400,
                  cursor: 'pointer'
                }}
              >
                {t === 'all' ? 'Tümü' : t === 'clinvar' ? 'ClinVar' : 'UniProt'}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Table Container */}
      <div style={{ overflowX: 'auto', maxHeight: '380px', overflowY: 'auto' }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.82rem', textAlign: 'left' }}>
          <thead>
            <tr style={{
              background: 'rgba(15, 23, 42, 0.8)',
              borderBottom: '1px solid var(--border-subtle)',
              position: 'sticky',
              top: 0,
              zIndex: 2
            }}>
              <th style={{ padding: '10px 12px', color: 'var(--text-muted)', fontWeight: 600 }}>Mutasyon</th>
              <th style={{ padding: '10px 12px', color: 'var(--text-muted)', fontWeight: 600 }}>Pozisyon</th>
              <th style={{ padding: '10px 12px', color: 'var(--text-muted)', fontWeight: 600 }}>Klinik Anlam</th>
              <th style={{ padding: '10px 12px', color: 'var(--text-muted)', fontWeight: 600 }}>İlişkili Hastalık</th>
              <th style={{ padding: '10px 12px', color: 'var(--text-muted)', fontWeight: 600, textAlign: 'right' }}>3D Etkileşim</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan="5" style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)' }}>
                  Arama kriterlerine uygun mutasyon bulunamadı.
                </td>
              </tr>
            ) : (
              filtered.map((item, idx) => {
                const isSelected = activeResidue && activeResidue.position === item.position;
                const isPathogenic = item.significance.toLowerCase().includes('pathogenic') || item.significance.toLowerCase().includes('patojenik');

                return (
                  <tr
                    key={idx}
                    style={{
                      borderBottom: '1px solid rgba(255, 255, 255, 0.04)',
                      background: isSelected ? 'rgba(225, 29, 72, 0.15)' : 'transparent',
                      transition: 'background 0.15s'
                    }}
                  >
                    <td style={{ padding: '10px 12px', fontWeight: 600, color: '#f8fafc' }}>
                      <span className="font-mono">{item.change}</span>
                      <span className="badge" style={{
                        marginLeft: '8px',
                        fontSize: '0.65rem',
                        padding: '2px 6px',
                        background: item.source === 'ClinVar' ? 'rgba(14, 165, 233, 0.15)' : 'rgba(168, 85, 247, 0.15)',
                        color: item.source === 'ClinVar' ? '#38bdf8' : '#c084fc',
                        borderColor: 'transparent'
                      }}>
                        {item.source}
                      </span>
                    </td>

                    <td style={{ padding: '10px 12px', color: 'var(--text-secondary)' }}>
                      {item.position ? (
                        <span className="font-mono" style={{ color: '#38bdf8' }}>{item.position}</span>
                      ) : (
                        <span style={{ color: 'var(--text-muted)' }}>--</span>
                      )}
                    </td>

                    <td style={{ padding: '10px 12px' }}>
                      <span className="badge" style={{
                        fontSize: '0.7rem',
                        padding: '3px 8px',
                        background: isPathogenic ? 'rgba(244, 63, 94, 0.15)' : 'rgba(245, 158, 11, 0.15)',
                        color: isPathogenic ? '#fb7185' : '#fbbf24',
                        borderColor: isPathogenic ? 'rgba(244, 63, 94, 0.3)' : 'rgba(245, 158, 11, 0.3)'
                      }}>
                        {item.significance}
                      </span>
                    </td>

                    <td style={{ padding: '10px 12px', color: 'var(--text-secondary)', maxWidth: '240px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }} title={item.disease}>
                      {item.disease}
                    </td>

                    <td style={{ padding: '10px 12px', textAlign: 'right' }}>
                      <div style={{ display: 'inline-flex', alignItems: 'center', gap: '6px' }}>
                        {item.position && (
                          <button
                            onClick={() => onSelectResidue && onSelectResidue(item)}
                            title="3D AlphaFold modelinde kalıntıyı vurgula ve yakınlaştır"
                            style={{
                              display: 'inline-flex',
                              alignItems: 'center',
                              gap: '4px',
                              background: isSelected ? '#e11d48' : 'rgba(56, 189, 248, 0.12)',
                              color: isSelected ? '#fff' : '#38bdf8',
                              border: isSelected ? '1px solid #e11d48' : '1px solid rgba(56, 189, 248, 0.3)',
                              borderRadius: '6px',
                              padding: '4px 8px',
                              fontSize: '0.72rem',
                              fontWeight: 500,
                              cursor: 'pointer',
                              transition: 'all 0.2s'
                            }}
                          >
                            <Target size={12} />
                            3D Odaklan
                          </button>
                        )}

                        {item.url && (
                          <a
                            href={item.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            style={{
                              color: 'var(--text-muted)',
                              display: 'inline-flex',
                              alignItems: 'center',
                              padding: '4px'
                            }}
                            title="Veritabanı Kaydını İncele"
                          >
                            <ExternalLink size={13} />
                          </a>
                        )}
                      </div>
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
