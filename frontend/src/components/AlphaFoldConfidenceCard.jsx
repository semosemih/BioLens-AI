import React from 'react';
import { ShieldCheck, HelpCircle, Download, ExternalLink, Activity } from 'lucide-react';

export default function AlphaFoldConfidenceCard({ alphafold, accession }) {
  if (!alphafold) return null;

  const {
    globalMetricValue,
    confidenceTier,
    confidenceDesc,
    badgeColor,
    plddtScale,
    pdbUrl,
    cifUrl
  } = alphafold;

  // Calculate circular stroke dash for gauge
  const radius = 38;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = globalMetricValue 
    ? circumference - (globalMetricValue / 100) * circumference 
    : 0;

  return (
    <div className="glass-panel" style={{ padding: '24px' }}>
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '16px' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            background: 'rgba(56, 189, 248, 0.15)',
            border: '1px solid rgba(56, 189, 248, 0.3)',
            borderRadius: '10px',
            padding: '8px',
            color: '#38bdf8'
          }}>
            <ShieldCheck size={20} />
          </div>
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 600 }}>Yapısal Tahmin Güvenilirliği</h3>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>AlphaFold per-residue pLDDT metriği</p>
          </div>
        </div>

        <span 
          className="badge" 
          style={{ 
            backgroundColor: `${badgeColor}22`, 
            color: badgeColor, 
            borderColor: `${badgeColor}55`,
            fontSize: '0.75rem',
            padding: '4px 12px'
          }}
        >
          {confidenceTier}
        </span>
      </div>

      {/* Score gauge & overview */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'auto 1fr',
        gap: '20px',
        alignItems: 'center',
        padding: '16px',
        background: 'rgba(10, 16, 28, 0.5)',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)',
        marginBottom: '20px'
      }}>
        {/* Radial gauge */}
        <div style={{ position: 'relative', width: '96px', height: '96px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
          <svg width="96" height="96" style={{ transform: 'rotate(-90deg)' }}>
            <circle
              cx="48"
              cy="48"
              r={radius}
              stroke="rgba(255, 255, 255, 0.08)"
              strokeWidth="7"
              fill="transparent"
            />
            <circle
              cx="48"
              cy="48"
              r={radius}
              stroke={badgeColor || '#38bdf8'}
              strokeWidth="7"
              strokeDasharray={circumference}
              strokeDashoffset={strokeDashoffset}
              strokeLinecap="round"
              fill="transparent"
              style={{ transition: 'stroke-dashoffset 1s ease' }}
            />
          </svg>
          <div style={{
            position: 'absolute',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            textAlign: 'center'
          }}>
            <span style={{ fontSize: '1.25rem', fontWeight: 700, color: '#f8fafc', fontFamily: 'var(--font-display)' }}>
              {globalMetricValue || '--'}
            </span>
            <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
              / 100
            </span>
          </div>
        </div>

        {/* Scientific description */}
        <div>
          <h4 style={{ fontSize: '0.9rem', fontWeight: 600, color: '#f1f5f9', marginBottom: '4px' }}>
            Ortalama pLDDT Skoru: {globalMetricValue}
          </h4>
          <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.45 }}>
            {confidenceDesc}
          </p>
        </div>
      </div>

      {/* pLDDT Scale Legend */}
      <div style={{ marginBottom: '20px' }}>
        <h5 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '8px', textTransform: 'uppercase', letterSpacing: '0.04em' }}>
          AlphaFold Renk ve Güven Skalası
        </h5>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(130px, 1fr))', gap: '8px' }}>
          {plddtScale && plddtScale.map((tier, idx) => (
            <div
              key={idx}
              style={{
                background: 'rgba(255, 255, 255, 0.03)',
                border: '1px solid var(--border-subtle)',
                borderRadius: '8px',
                padding: '8px 10px',
                display: 'flex',
                alignItems: 'center',
                gap: '8px'
              }}
            >
              <div style={{
                width: '12px',
                height: '12px',
                borderRadius: '3px',
                backgroundColor: tier.color,
                flexShrink: 0
              }}></div>
              <div style={{ overflow: 'hidden' }}>
                <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#e2e8f0' }}>
                  {tier.range}
                </div>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', whiteSpace: 'nowrap', textOverflow: 'ellipsis', overflow: 'hidden' }}>
                  {tier.level}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Download & External Links */}
      <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
        {pdbUrl && (
          <a
            href={pdbUrl}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              background: 'rgba(56, 189, 248, 0.1)',
              border: '1px solid rgba(56, 189, 248, 0.25)',
              color: '#38bdf8',
              borderRadius: '8px',
              padding: '8px 12px',
              fontSize: '0.8rem',
              fontWeight: 500,
              textDecoration: 'none',
              transition: 'all 0.2s'
            }}
          >
            <Download size={14} />
            .PDB İndir
          </a>
        )}

        {cifUrl && (
          <a
            href={cifUrl}
            target="_blank"
            rel="noopener noreferrer"
            style={{
              flex: 1,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '6px',
              background: 'rgba(255, 255, 255, 0.05)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-secondary)',
              borderRadius: '8px',
              padding: '8px 12px',
              fontSize: '0.8rem',
              fontWeight: 500,
              textDecoration: 'none',
              transition: 'all 0.2s'
            }}
          >
            <Download size={14} />
            .mmCIF İndir
          </a>
        )}

        <a
          href={`https://alphafold.ebi.ac.uk/entry/${accession}`}
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '6px',
            background: 'rgba(255, 255, 255, 0.05)',
            border: '1px solid var(--border-subtle)',
            color: 'var(--text-secondary)',
            borderRadius: '8px',
            padding: '8px 12px',
            fontSize: '0.8rem',
            textDecoration: 'none'
          }}
          title="AlphaFold EBI Sayfasını Aç"
        >
          <ExternalLink size={14} />
          AlphaFold DB
        </a>
      </div>
    </div>
  );
}
