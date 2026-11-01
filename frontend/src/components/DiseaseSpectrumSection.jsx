import React, { useState } from 'react';
import {
  Stethoscope,
  Search,
  ExternalLink,
  Pill,
  Dna,
  ShieldAlert,
  ChevronDown,
  ChevronUp,
  Target,
  Activity,
  Layers
} from 'lucide-react';

function normalizeTr(str) {
  if (!str) return '';
  return str
    .replace(/İ/g, 'i')
    .replace(/I/g, 'i')
    .replace(/ı/g, 'i')
    .replace(/Ş/g, 's')
    .replace(/ş/g, 's')
    .replace(/Ğ/g, 'g')
    .replace(/ğ/g, 'g')
    .replace(/Ü/g, 'u')
    .replace(/ü/g, 'u')
    .replace(/Ö/g, 'o')
    .replace(/ö/g, 'o')
    .replace(/Ç/g, 'c')
    .replace(/ç/g, 'c')
    .toLowerCase()
    .trim();
}

function getSpecialtyStyle(specialty) {
  const s = (specialty || '').toLowerCase();
  if (s.includes('onkoloji')) {
    return {
      bg: 'rgba(244, 63, 94, 0.14)',
      border: 'rgba(244, 63, 94, 0.35)',
      color: '#fb7185'
    };
  }
  if (s.includes('nöroloji') || s.includes('nöro')) {
    return {
      bg: 'rgba(168, 85, 247, 0.14)',
      border: 'rgba(168, 85, 247, 0.35)',
      color: '#c084fc'
    };
  }
  if (s.includes('endokrinoloji') || s.includes('metabolizma')) {
    return {
      bg: 'rgba(16, 185, 129, 0.14)',
      border: 'rgba(16, 185, 129, 0.35)',
      color: '#34d399'
    };
  }
  if (s.includes('kardiyoloji') || s.includes('hematoloji')) {
    return {
      bg: 'rgba(245, 158, 11, 0.14)',
      border: 'rgba(245, 158, 11, 0.35)',
      color: '#fbbf24'
    };
  }
  if (s.includes('genetik')) {
    return {
      bg: 'rgba(56, 189, 248, 0.14)',
      border: 'rgba(56, 189, 248, 0.35)',
      color: '#38bdf8'
    };
  }
  return {
    bg: 'rgba(99, 102, 241, 0.14)',
    border: 'rgba(99, 102, 241, 0.35)',
    color: '#818cf8'
  };
}

export default function DiseaseSpectrumSection({
  diseaseProfile,
  geneSymbol,
  onSelectResidue,
  lang = 'en'
}) {
  const [selectedSpecialty, setSelectedSpecialty] = useState('ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [showAll, setShowAll] = useState(false);

  if (!diseaseProfile || !diseaseProfile.diseases || diseaseProfile.diseases.length === 0) {
    return null;
  }

  const {
    diseases = [],
    specialtyBreakdown = [],
    generalClinicalNotes = [],
    targetedDrugs = [],
    pharmaceuticalNotes = []
  } = diseaseProfile;

  const filteredDiseases = diseases.filter((d) => {
    if (selectedSpecialty !== 'ALL') {
      const matchPrim = d.primarySpecialty === selectedSpecialty;
      const matchCat = (d.category || '').toLowerCase().includes(selectedSpecialty.toLowerCase());
      if (!matchPrim && !matchCat) return false;
    }
    if (searchQuery.trim()) {
      const q = normalizeTr(searchQuery);
      const hay = normalizeTr(
        `${d.name || ''} ${d.englishName || ''} ${d.acronym || ''} ${d.category || ''} ${d.inheritance || ''} ${d.pathophysiology || ''} ${d.clinicalManagement || ''} ${(d.relatedMutations || []).join(' ')}`
      );
      return hay.includes(q);
    }
    return true;
  });

  const visibleDiseases = showAll || searchQuery.trim() || selectedSpecialty !== 'ALL'
    ? filteredDiseases
    : filteredDiseases.slice(0, 6);

  const handleMutationClick = (mutStr) => {
    if (!onSelectResidue || !mutStr) return;
    const digits = mutStr.replace(/[^0-9]/g, '');
    if (digits) {
      const pos = parseInt(digits, 10);
      if (!isNaN(pos) && pos > 0) {
        onSelectResidue({
          change: mutStr,
          position: pos
        });
      }
    }
  };

  return (
    <div className="glass-panel" style={{
      padding: '26px',
      border: '1px solid rgba(244, 63, 94, 0.25)',
      background: 'linear-gradient(145deg, rgba(15, 23, 42, 0.9) 0%, rgba(18, 16, 32, 0.85) 100%)'
    }}>
      {/* Section Header */}
      <div style={{
        display: 'flex',
        alignItems: 'flex-start',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px',
        marginBottom: '20px',
        paddingBottom: '16px',
        borderBottom: '1px solid var(--border-subtle)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            background: 'linear-gradient(135deg, #e11d48 0%, #9333ea 100%)',
            borderRadius: '12px',
            padding: '10px',
            color: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 18px rgba(225, 29, 72, 0.35)'
          }}>
            <Stethoscope size={22} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <h3 style={{ fontSize: '1.15rem', fontWeight: 700, color: '#f8fafc' }}>
                {lang === 'en'
                  ? 'Comprehensive Clinical Disease Spectrum, Syndromes & Pathophysiology'
                  : 'Kapsamlı Klinik Hastalık Spektrumu, Sendromlar & Patofizyoloji'}
              </h3>
              <span className="badge badge-rose" style={{ fontSize: '0.72rem', padding: '3px 10px' }}>
                {diseases.length} {lang === 'en' ? 'Clinical Conditions / Syndromes' : 'Klinik Hastalık / Sendrom'}
              </span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '3px' }}>
              {lang === 'en'
                ? `Multi-source clinical synthesis of oncological, hereditary (OMIM / Orphanet), metabolic, neurological, and systemic pathologies associated with ${geneSymbol}`
                : `${geneSymbol} ile ilişkili onkolojik, kalıtsal (OMIM / Orphanet), metabolik, nörolojik ve sistemik patolojilerin çok kaynaklı klinik sentezi`}
            </p>
          </div>
        </div>

        {/* Search Input inside Disease Spectrum */}
        <div style={{ position: 'relative', minWidth: '250px' }}>
          <Search
            size={15}
            style={{
              position: 'absolute',
              left: '12px',
              top: '50%',
              transform: 'translateY(-50%)',
              color: 'var(--text-muted)'
            }}
          />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder={lang === 'en' ? 'Search disease, syndrome, drug or OMIM...' : 'Hastalık, sendrom, ilaç veya OMIM ara...'}
            style={{
              width: '100%',
              background: 'rgba(6, 9, 17, 0.75)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '10px',
              padding: '8px 12px 8px 34px',
              color: '#fff',
              fontSize: '0.82rem',
              outline: 'none'
            }}
          />
        </div>
      </div>

      {/* Specialty Breakdown Filter Pills */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        gap: '8px',
        flexWrap: 'wrap',
        marginBottom: '18px'
      }}>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '4px', marginRight: '4px' }}>
          <Layers size={13} />
          {lang === 'en' ? 'Medical Specialty Filter:' : 'Tıbbi Branş Filtresi:'}
        </span>
        <button
          onClick={() => setSelectedSpecialty('ALL')}
          style={{
            background: selectedSpecialty === 'ALL' ? 'rgba(244, 63, 94, 0.22)' : 'rgba(255, 255, 255, 0.04)',
            border: selectedSpecialty === 'ALL' ? '1px solid #fb7185' : '1px solid var(--border-subtle)',
            color: selectedSpecialty === 'ALL' ? '#fb7185' : 'var(--text-secondary)',
            borderRadius: '9999px',
            padding: '5px 12px',
            fontSize: '0.76rem',
            fontWeight: selectedSpecialty === 'ALL' ? 600 : 400,
            cursor: 'pointer',
            transition: 'all 0.15s'
          }}
        >
          {lang === 'en' ? `All (${diseases.length})` : `Tümü (${diseases.length})`}
        </button>

        {specialtyBreakdown.map((item, idx) => {
          const isSelected = selectedSpecialty === item.specialty;
          const style = getSpecialtyStyle(item.specialty);
          const displaySpec = lang === 'en' ? (item.specialtyEn || item.specialty) : item.specialty;
          return (
            <button
              key={idx}
              onClick={() => setSelectedSpecialty(isSelected ? 'ALL' : item.specialty)}
              style={{
                background: isSelected ? style.bg : 'rgba(255, 255, 255, 0.04)',
                border: isSelected ? `1px solid ${style.color}` : '1px solid var(--border-subtle)',
                color: isSelected ? style.color : 'var(--text-secondary)',
                borderRadius: '9999px',
                padding: '5px 12px',
                fontSize: '0.76rem',
                fontWeight: isSelected ? 600 : 400,
                cursor: 'pointer',
                transition: 'all 0.15s'
              }}
            >
              {displaySpec} ({item.count})
            </button>
          );
        })}
      </div>

      {/* Targeted Drugs & Pharmaceutical Note Banner (if available) */}
      {(targetedDrugs.length > 0 || pharmaceuticalNotes.length > 0) && (
        <div style={{
          background: 'rgba(16, 185, 129, 0.08)',
          border: '1px solid rgba(16, 185, 129, 0.25)',
          borderRadius: '12px',
          padding: '12px 16px',
          marginBottom: '20px',
          display: 'flex',
          flexDirection: 'column',
          gap: '8px'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', fontSize: '0.8rem', fontWeight: 600, color: '#34d399' }}>
              <Pill size={15} />
              {lang === 'en'
                ? 'Targeted Drugs & Pharmacological Agents (DrugBank / UniProt):'
                : 'Hedefe Yönelik İlaç & Farmakolojik Ajanlar (DrugBank / UniProt):'}
            </span>
            {targetedDrugs.slice(0, 12).map((drug, idx) => (
              <a
                key={idx}
                href={`https://go.drugbank.com/drugs/${drug.id}`}
                target="_blank"
                rel="noopener noreferrer"
                style={{
                  background: 'rgba(16, 185, 129, 0.15)',
                  border: '1px solid rgba(16, 185, 129, 0.3)',
                  color: '#6ee7b7',
                  borderRadius: '6px',
                  padding: '2px 8px',
                  fontSize: '0.74rem',
                  fontWeight: 500,
                  textDecoration: 'none',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px'
                }}
                title={`DrugBank: ${drug.id}`}
              >
                {drug.name}
                <ExternalLink size={10} />
              </a>
            ))}
          </div>
          {pharmaceuticalNotes.length > 0 && (
            <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              {pharmaceuticalNotes[0]}
            </div>
          )}
        </div>
      )}

      {/* Disease Cards Grid */}
      {visibleDiseases.length === 0 ? (
        <div style={{ padding: '32px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.88rem' }}>
          {lang === 'en'
            ? 'No matching clinical disease records found.'
            : 'Arama kriterlerine uygun klinik hastalık kaydı bulunamadı.'}
        </div>
      ) : (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(380px, 1fr))',
          gap: '16px'
        }}>
          {visibleDiseases.map((disease, idx) => {
            const specStyle = getSpecialtyStyle(disease.category);
            const displayCategory = lang === 'en' ? (disease.categoryEn || disease.primarySpecialtyEn || disease.category) : disease.category;
            const displayInheritance = lang === 'en' ? (disease.inheritanceEn || disease.inheritance) : disease.inheritance;
            const displayPrimaryTitle = lang === 'en' ? (disease.englishName || disease.name) : disease.name;
            const displaySecondaryTitle = lang === 'en' ? disease.name : disease.englishName;
            const displayPatho = lang === 'en' ? (disease.pathophysiologyEn || disease.pathophysiology) : disease.pathophysiology;
            const displayManagement = lang === 'en' ? (disease.clinicalManagementEn || disease.clinicalManagement) : disease.clinicalManagement;

            return (
              <div
                key={idx}
                style={{
                  background: 'rgba(8, 12, 24, 0.78)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '12px',
                  padding: '18px',
                  display: 'flex',
                  flexDirection: 'column',
                  justifyContent: 'space-between',
                  gap: '12px',
                  transition: 'border-color 0.2s'
                }}
              >
                <div>
                  {/* Top Badges Row */}
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '6px', marginBottom: '8px' }}>
                    <span style={{
                      background: specStyle.bg,
                      border: `1px solid ${specStyle.border}`,
                      color: specStyle.color,
                      padding: '2px 9px',
                      borderRadius: '6px',
                      fontSize: '0.7rem',
                      fontWeight: 600
                    }}>
                      {displayCategory}
                    </span>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
                      {displayInheritance && (
                        <span style={{
                          background: 'rgba(255, 255, 255, 0.05)',
                          border: '1px solid var(--border-subtle)',
                          color: 'var(--text-secondary)',
                          padding: '2px 8px',
                          borderRadius: '6px',
                          fontSize: '0.68rem'
                        }}>
                          {displayInheritance}
                        </span>
                      )}
                      {disease.acronym && (
                        <span className="font-mono" style={{
                          background: 'rgba(56, 189, 248, 0.12)',
                          color: '#38bdf8',
                          padding: '2px 6px',
                          borderRadius: '4px',
                          fontSize: '0.68rem',
                          fontWeight: 600
                        }}>
                          {disease.acronym}
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Disease Name */}
                  <h4 style={{ fontSize: '0.98rem', fontWeight: 700, color: '#f8fafc', lineHeight: 1.35, marginBottom: '4px' }}>
                    {displayPrimaryTitle}
                  </h4>
                  {displaySecondaryTitle && displaySecondaryTitle.toLowerCase() !== displayPrimaryTitle.toLowerCase() && (
                    <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginBottom: '8px', fontStyle: 'italic' }}>
                      {displaySecondaryTitle}
                    </div>
                  )}

                  {/* Pathophysiology Description */}
                  <p style={{ fontSize: '0.83rem', color: 'var(--text-primary)', lineHeight: 1.55, marginTop: '6px' }}>
                    {displayPatho}
                  </p>

                  {/* Clinical Management / Targeted Therapy Box */}
                  {displayManagement && (
                    <div style={{
                      marginTop: '10px',
                      background: 'rgba(14, 165, 233, 0.08)',
                      borderLeft: '3px solid #38bdf8',
                      borderRadius: '0 8px 8px 0',
                      padding: '8px 12px',
                      fontSize: '0.79rem',
                      color: '#e2e8f0',
                      lineHeight: 1.5
                    }}>
                      <strong style={{ color: '#38bdf8', display: 'inline-flex', alignItems: 'center', gap: '4px', marginRight: '6px' }}>
                        <Activity size={12} />
                        {lang === 'en' ? 'Clinical Management & Targeted Therapy:' : 'Klinik Yaklaşım & Hedefli Tedavi:'}
                      </strong>
                      {displayManagement}
                    </div>
                  )}
                </div>

                {/* Bottom Row: Related Mutations & External Database Links */}
                <div style={{
                  paddingTop: '10px',
                  borderTop: '1px solid rgba(255, 255, 255, 0.05)',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '8px'
                }}>
                  {disease.relatedMutations && disease.relatedMutations.length > 0 && (
                    <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '5px' }}>
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginRight: '2px' }}>
                        {lang === 'en' ? 'Associated Variants:' : 'İlişkili Varyantlar:'}
                      </span>
                      {disease.relatedMutations.slice(0, 5).map((mut, mIdx) => (
                        <button
                          key={mIdx}
                          type="button"
                          onClick={() => handleMutationClick(mut)}
                          title={lang === 'en' ? 'Focus on this variant residue in 3D structure' : '3B yapıda bu mutasyon kalıntısına odaklan'}
                          className="font-mono"
                          style={{
                            background: 'rgba(244, 63, 94, 0.12)',
                            border: '1px solid rgba(244, 63, 94, 0.28)',
                            color: '#fda4af',
                            borderRadius: '5px',
                            padding: '1px 6px',
                            fontSize: '0.69rem',
                            cursor: 'pointer',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '3px'
                          }}
                        >
                          <Target size={10} />
                          {mut}
                        </button>
                      ))}
                    </div>
                  )}

                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '6px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '5px', flexWrap: 'wrap' }}>
                      {(disease.sources || []).map((src, sIdx) => (
                        <span
                          key={sIdx}
                          style={{
                            fontSize: '0.66rem',
                            color: 'var(--text-muted)',
                            background: 'rgba(255, 255, 255, 0.04)',
                            padding: '1px 6px',
                            borderRadius: '4px'
                          }}
                        >
                          {lang === 'en' && src === 'Klinik Rehber'
                            ? 'Clinical Guideline'
                            : lang === 'en' && src === 'UniProt Varyant'
                            ? 'UniProt Variant'
                            : src}
                        </span>
                      ))}
                    </div>

                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      {disease.omimId && (
                        <a
                          href={`https://www.omim.org/entry/${disease.omimId}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            fontSize: '0.72rem',
                            color: '#38bdf8',
                            textDecoration: 'none',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '3px',
                            fontWeight: 500
                          }}
                        >
                          OMIM #{disease.omimId}
                          <ExternalLink size={11} />
                        </a>
                      )}
                      {disease.orphaId && (
                        <a
                          href={`https://www.orpha.net/en/disease/detail/${disease.orphaId}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          style={{
                            fontSize: '0.72rem',
                            color: '#c084fc',
                            textDecoration: 'none',
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '3px',
                            fontWeight: 500
                          }}
                        >
                          ORPHA:{disease.orphaId}
                          <ExternalLink size={11} />
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* Expand / Collapse All Diseases Button */}
      {filteredDiseases.length > 6 && !searchQuery.trim() && selectedSpecialty === 'ALL' && (
        <div style={{ marginTop: '18px', textAlign: 'center' }}>
          <button
            type="button"
            onClick={() => setShowAll(!showAll)}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              background: 'rgba(56, 189, 248, 0.12)',
              border: '1px solid rgba(56, 189, 248, 0.3)',
              color: '#38bdf8',
              borderRadius: '10px',
              padding: '8px 18px',
              fontSize: '0.82rem',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            {showAll ? (
              <>
                <ChevronUp size={16} />
                <span>{lang === 'en' ? 'Collapse View' : 'Görünümü Daralt'}</span>
              </>
            ) : (
              <>
                <ChevronDown size={16} />
                <span>
                  {lang === 'en'
                    ? `Show All Associated Diseases & Syndromes (${filteredDiseases.length} Conditions)`
                    : `Tüm İlişkili Hastalıkları ve Sendromları Göster (${filteredDiseases.length} Hastalık)`}
                </span>
              </>
            )}
          </button>
        </div>
      )}

      {/* General Somatic / Clinical Notes from UniProt if present */}
      {generalClinicalNotes.length > 0 && (
        <div style={{
          marginTop: '18px',
          background: 'rgba(255, 255, 255, 0.02)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '10px',
          padding: '12px 16px',
          fontSize: '0.79rem',
          color: 'var(--text-secondary)',
          lineHeight: 1.55
        }}>
          <strong style={{ color: '#f8fafc', display: 'block', marginBottom: '4px' }}>
            {lang === 'en'
              ? '📋 Additional Clinical & Somatic Tumor Spectrum Note (UniProtKB):'
              : '📋 Ek Klinik ve Somatik Tümör Spektrumu Notu (UniProtKB):'}
          </strong>
          {generalClinicalNotes.join(' ')}
        </div>
      )}
    </div>
  );
}

