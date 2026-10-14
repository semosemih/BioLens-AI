import React, { useState } from 'react';
import { Dna, MapPin, Tag, Copy, Check, ChevronDown, ChevronUp, Layers } from 'lucide-react';

export default function ProteinOverview({ protein }) {
  const [showFasta, setShowFasta] = useState(false);
  const [copiedFasta, setCopiedFasta] = useState(false);

  if (!protein) return null;

  const {
    proteinName,
    geneSymbol,
    accession,
    organism,
    commonOrganism,
    length,
    mass,
    sequence,
    subcellularLocations,
    goTerms,
    functions
  } = protein;

  const handleCopyFasta = () => {
    const fasta = `>${accession}|${geneSymbol}|${proteinName} [${organism}]\n${sequence}`;
    navigator.clipboard.writeText(fasta);
    setCopiedFasta(true);
    setTimeout(() => setCopiedFasta(false), 2000);
  };

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      {/* Header Info */}
      <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px', marginBottom: '20px' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '6px' }}>
            <span className="badge badge-cyan">{geneSymbol}</span>
            <span className="badge badge-blue">UniProt: {accession}</span>
            <span className="badge badge-emerald">{commonOrganism || organism}</span>
          </div>
          <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: '#f8fafc', lineHeight: 1.3 }}>
            {proteinName}
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            {organism} • {length} Amino Asit • {(mass ? (mass / 1000).toFixed(1) + ' kDa' : '--')}
          </p>
        </div>

        {/* FASTA action */}
        <button
          onClick={() => setShowFasta(!showFasta)}
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '8px',
            padding: '8px 14px',
            color: 'var(--text-secondary)',
            fontSize: '0.8rem',
            cursor: 'pointer',
            transition: 'all 0.2s'
          }}
        >
          <Dna size={15} />
          <span>FASTA Dizisi</span>
          {showFasta ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </button>
      </div>

      {/* FASTA Sequence Viewer Drawer */}
      {showFasta && (
        <div style={{
          background: 'rgba(6, 9, 17, 0.95)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '16px',
          marginBottom: '20px'
        }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
            <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
              &gt;{accession}|{geneSymbol} ({length} aa)
            </span>
            <button
              onClick={handleCopyFasta}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                background: 'rgba(56, 189, 248, 0.15)',
                border: '1px solid rgba(56, 189, 248, 0.3)',
                color: '#38bdf8',
                borderRadius: '6px',
                padding: '4px 8px',
                fontSize: '0.75rem',
                cursor: 'pointer'
              }}
            >
              {copiedFasta ? <Check size={12} /> : <Copy size={12} />}
              {copiedFasta ? 'Kopyalandı' : 'Kopyala'}
            </button>
          </div>
          <div style={{
            fontFamily: 'var(--font-mono)',
            fontSize: '0.75rem',
            color: '#93c5fd',
            lineHeight: 1.6,
            wordBreak: 'break-all',
            maxHeight: '140px',
            overflowY: 'auto',
            paddingRight: '6px'
          }}>
            {sequence}
          </div>
        </div>
      )}

      {/* Primary Biological Function */}
      {functions && functions.length > 0 && (
        <div style={{ marginBottom: '20px' }}>
          <h4 style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '8px' }}>
            Biyolojik İşlev Açıklaması
          </h4>
          <p style={{ fontSize: '0.88rem', color: 'var(--text-primary)', lineHeight: 1.6, background: 'rgba(255, 255, 255, 0.02)', padding: '12px 16px', borderRadius: '8px', border: '1px solid var(--border-subtle)' }}>
            {functions[0]}
          </p>
        </div>
      )}

      {/* Subcellular Localization */}
      {subcellularLocations && subcellularLocations.length > 0 && (
        <div style={{ marginBottom: '18px' }}>
          <h4 style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <MapPin size={14} />
            Hücresel Yerleşim (Subcellular Location)
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {subcellularLocations.map((loc, idx) => (
              <span
                key={idx}
                style={{
                  background: 'rgba(99, 102, 241, 0.12)',
                  border: '1px solid rgba(99, 102, 241, 0.25)',
                  color: '#a5b4fc',
                  padding: '4px 10px',
                  borderRadius: '8px',
                  fontSize: '0.78rem',
                  fontWeight: 500
                }}
              >
                {loc}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Gene Ontology (GO) Processes */}
      {goTerms && (
        <div>
          <h4 style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Layers size={14} />
            Gen Ontolojisi (Gene Ontology - Biyolojik Süreçler)
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {goTerms.biologicalProcess && goTerms.biologicalProcess.slice(0, 6).map((term, idx) => (
              <span
                key={idx}
                style={{
                  background: 'rgba(16, 185, 129, 0.1)',
                  border: '1px solid rgba(16, 185, 129, 0.2)',
                  color: '#6ee7b7',
                  padding: '4px 10px',
                  borderRadius: '8px',
                  fontSize: '0.76rem'
                }}
                title={term.id}
              >
                {term.name}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
