import React, { useState, useMemo } from 'react';
import { Layers, Target, Flame, Sparkles, Compass, Activity, Zap } from 'lucide-react';

const DOMAIN_COLORS = [
  { bg: 'rgba(14, 165, 233, 0.28)', border: '#38bdf8', hex: '#0ea5e9', text: '#7dd3fc' },
  { bg: 'rgba(168, 85, 247, 0.28)', border: '#c084fc', hex: '#a855f7', text: '#d8b4fe' },
  { bg: 'rgba(16, 185, 129, 0.28)', border: '#34d399', hex: '#10b981', text: '#6ee7b7' },
  { bg: 'rgba(245, 158, 11, 0.28)', border: '#fbbf24', hex: '#f59e0b', text: '#fde68a' },
  { bg: 'rgba(236, 72, 153, 0.28)', border: '#f472b6', hex: '#ec4899', text: '#fbcfe8' },
  { bg: 'rgba(99, 102, 241, 0.28)', border: '#818cf8', hex: '#6366f1', text: '#c7d2fe' }
];

// Kyte-Doolittle hydropathy values
const KD_HYDROPATHY = {
  A: 1.8, R: -4.5, N: -3.5, D: -3.5, C: 2.5,
  Q: -3.5, E: -3.5, G: -0.4, H: -3.2, I: 4.5,
  L: 3.8, K: -3.9, M: 1.9, F: 2.8, P: -1.6,
  S: -0.8, T: -0.7, W: -0.9, Y: -1.3, V: 4.2
};

function computeBiochemicalMetrics(sequence) {
  if (!sequence || sequence.length === 0) return null;
  const seq = sequence.toUpperCase();
  const len = seq.length;

  const counts = {};
  for (let i = 0; i < len; i++) {
    const aa = seq[i];
    counts[aa] = (counts[aa] || 0) + 1;
  }

  const getCount = (chars) => chars.reduce((acc, c) => acc + (counts[c] || 0), 0);

  const hydrophobic = getCount(['A', 'V', 'I', 'L', 'M', 'F', 'W', 'P', 'G']);
  const polar = getCount(['S', 'T', 'C', 'Y', 'N', 'Q']);
  const positive = getCount(['K', 'R', 'H']);
  const negative = getCount(['D', 'E']);
  const aromatic = getCount(['F', 'W', 'Y']);

  // GRAVY (Grand Average of Hydropathicity)
  let hydroSum = 0;
  for (let i = 0; i < len; i++) {
    hydroSum += KD_HYDROPATHY[seq[i]] || 0;
  }
  const gravy = (hydroSum / len).toFixed(2);

  // Aliphatic index = X(Ala) + 2.9 * X(Val) + 3.9 * (X(Ile) + X(Leu))
  const xA = ((counts['A'] || 0) / len) * 100;
  const xV = ((counts['V'] || 0) / len) * 100;
  const xI = ((counts['I'] || 0) / len) * 100;
  const xL = ((counts['L'] || 0) / len) * 100;
  const aliphaticIndex = (xA + 2.9 * xV + 3.9 * (xI + xL)).toFixed(1);

  // Theoretical Isoelectric Point (pI) via bisection using standard pKa values
  const nD = counts['D'] || 0;
  const nE = counts['E'] || 0;
  const nC = counts['C'] || 0;
  const nY = counts['Y'] || 0;
  const nH = counts['H'] || 0;
  const nK = counts['K'] || 0;
  const nR = counts['R'] || 0;

  const netChargeAtPH = (ph) => {
    const qN = 1 / (1 + Math.pow(10, ph - 8.6));
    const qK = nK / (1 + Math.pow(10, ph - 10.8));
    const qR = nR / (1 + Math.pow(10, ph - 12.5));
    const qH = nH / (1 + Math.pow(10, ph - 6.5));
    const qCterm = -1 / (1 + Math.pow(10, 3.6 - ph));
    const qD = -nD / (1 + Math.pow(10, 3.9 - ph));
    const qE = -nE / (1 + Math.pow(10, 4.1 - ph));
    const qC = -nC / (1 + Math.pow(10, 8.5 - ph));
    const qY = -nY / (1 + Math.pow(10, 10.1 - ph));
    return qN + qK + qR + qH + qCterm + qD + qE + qC + qY;
  };

  let low = 0.0;
  let high = 14.0;
  for (let iter = 0; iter < 30; iter++) {
    const mid = (low + high) / 2;
    if (netChargeAtPH(mid) > 0) {
      low = mid;
    } else {
      high = mid;
    }
  }
  const pI = ((low + high) / 2).toFixed(2);

  return {
    hydrophobicPct: ((hydrophobic / len) * 100).toFixed(1),
    polarPct: ((polar / len) * 100).toFixed(1),
    positivePct: ((positive / len) * 100).toFixed(1),
    negativePct: ((negative / len) * 100).toFixed(1),
    aromaticPct: ((aromatic / len) * 100).toFixed(1),
    gravy: parseFloat(gravy),
    aliphaticIndex: parseFloat(aliphaticIndex),
    pI: parseFloat(pI)
  };
}

export default function ProteinDomainMap({
  protein,
  clinvarVariants = [],
  onSelectResidue,
  activeResidue,
  lang = 'en'
}) {
  const [hoveredItem, setHoveredItem] = useState(null);

  if (!protein || !protein.length) return null;

  const seqLength = protein.length;
  const rawFeatures = protein.structuralFeatures || [];
  const uniprotVariants = protein.variants || [];

  // Separate range domains/regions from single-residue active/binding sites
  const { domains, functionalSites } = useMemo(() => {
    const doms = [];
    const sites = [];

    rawFeatures.forEach((f) => {
      if (!f.start) return;
      const span = (f.end || f.start) - f.start;
      const descLow = (f.description || '').toLowerCase();
      if (descLow === 'disordered' || descLow.startsWith('interaction with')) {
        return;
      }

      if (
        ['Domain', 'DNA binding', 'Zinc finger', 'Transmembrane', 'Repeat', 'Motif', 'Coiled coil'].includes(f.type) ||
        (f.type === 'Region' && span >= 12)
      ) {
        doms.push({
          ...f,
          end: f.end || f.start
        });
      } else if (['Active site', 'Binding site', 'Site'].includes(f.type) || span <= 5) {
        sites.push({
          ...f,
          position: f.start
        });
      }
    });

    // Sort domains by start position and filter out exact duplicates
    doms.sort((a, b) => a.start - b.start || (b.end - b.start) - (a.end - a.start));
    const uniqueDoms = [];
    doms.forEach((d) => {
      const dup = uniqueDoms.some(
        (u) => Math.abs(u.start - d.start) <= 3 && Math.abs(u.end - d.end) <= 3
      );
      if (!dup && uniqueDoms.length < 10) {
        uniqueDoms.push(d);
      }
    });

    return { domains: uniqueDoms, functionalSites: sites.slice(0, 12) };
  }, [rawFeatures]);

  // Build mutation hotspot pins along the sequence
  const hotspotPins = useMemo(() => {
    const byPos = new Map();

    clinvarVariants.forEach((v) => {
      if (!v.position || v.position > seqLength || v.position < 1) return;
      const existing = byPos.get(v.position) || {
        position: v.position,
        count: 0,
        changes: [],
        diseases: [],
        source: 'ClinVar'
      };
      existing.count += 1;
      const ch = v.proteinChange || v.title;
      if (ch && !existing.changes.includes(ch)) existing.changes.push(ch);
      (v.conditions || []).forEach((c) => {
        if (c && !existing.diseases.includes(c)) existing.diseases.push(c);
      });
      byPos.set(v.position, existing);
    });

    uniprotVariants.forEach((v) => {
      const pos = v.position ? parseInt(v.position, 10) : null;
      if (!pos || pos > seqLength || pos < 1) return;
      const existing = byPos.get(pos) || {
        position: pos,
        count: 0,
        changes: [],
        diseases: [],
        source: 'UniProt'
      };
      existing.count += 1;
      if (v.change && !existing.changes.includes(v.change)) existing.changes.push(v.change);
      if (v.description && !existing.diseases.includes(v.description)) {
        existing.diseases.push(v.description);
      }
      byPos.set(pos, existing);
    });

    return Array.from(byPos.values())
      .sort((a, b) => b.count - a.count || a.position - b.position)
      .slice(0, 28)
      .sort((a, b) => a.position - b.position);
  }, [clinvarVariants, uniprotVariants, seqLength]);

  const bioMetrics = useMemo(() => computeBiochemicalMetrics(protein.sequence), [protein.sequence]);

  const handleDomainClick = (dom, colorObj) => {
    if (!onSelectResidue) return;
    onSelectResidue({
      isDomain: true,
      start: dom.start,
      end: dom.end,
      change: dom.description || dom.type,
      color: colorObj.hex
    });
  };

  const handlePinClick = (pin) => {
    if (!onSelectResidue) return;
    onSelectResidue({
      position: pin.position,
      change: pin.changes[0] || `Pos ${pin.position}`
    });
  };

  // Position ticks
  const ticks = [1];
  const step = Math.max(50, Math.round(seqLength / 6 / 50) * 50);
  for (let t = step; t < seqLength - step * 0.4; t += step) {
    ticks.push(t);
  }
  if (seqLength > 1) ticks.push(seqLength);

  return (
    <div className="glass-panel" style={{
      padding: '24px',
      border: '1px solid rgba(56, 189, 248, 0.22)',
      background: 'linear-gradient(145deg, rgba(12, 18, 34, 0.9) 0%, rgba(9, 13, 24, 0.88) 100%)'
    }}>
      {/* Header */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
        marginBottom: '18px'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <div style={{
            background: 'linear-gradient(135deg, #0ea5e9 0%, #8b5cf6 100%)',
            borderRadius: '10px',
            padding: '9px',
            color: '#fff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: '0 4px 14px rgba(14, 165, 233, 0.3)'
          }}>
            <Compass size={20} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
              <h3 style={{ fontSize: '1.08rem', fontWeight: 700, color: '#f8fafc' }}>
                {lang === 'en'
                  ? '1D Functional Domain Architecture, Mutation Hotspots & Biophysical Profile'
                  : '1B Fonksiyonel Domain Mimarisi, Mutasyon Odakları & Biyofiziksel Profil'}
              </h3>
              <span className="badge badge-cyan" style={{ fontSize: '0.7rem' }}>
                {seqLength} aa
              </span>
            </div>
            <p style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
              {lang === 'en'
                ? 'Click any structural domain or clinical mutation lollipop pin to highlight and focus directly in the 3D AlphaFold model'
                : '3B AlphaFold modelinde doğrudan vurgulamak ve yakınlaştırmak için herhangi bir domain bloğuna veya mutasyon pinine tıklayın'}
            </p>
          </div>
        </div>

        {/* Hovered Info Pill */}
        {hoveredItem && (
          <div style={{
            background: 'rgba(15, 23, 42, 0.95)',
            border: '1px solid rgba(56, 189, 248, 0.4)',
            borderRadius: '8px',
            padding: '6px 12px',
            fontSize: '0.78rem',
            color: '#f8fafc',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}>
            <Target size={13} color="#38bdf8" />
            <span>{hoveredItem}</span>
          </div>
        )}
      </div>

      {/* Interactive 1D Linear Track Container */}
      <div style={{
        background: 'rgba(6, 9, 17, 0.75)',
        border: '1px solid var(--border-subtle)',
        borderRadius: '12px',
        padding: '28px 20px 22px 20px',
        position: 'relative',
        marginBottom: '18px'
      }}>
        {/* Mutation Hotspot Lollipop Pins Track */}
        {hotspotPins.length > 0 && (
          <div style={{ position: 'relative', height: '38px', width: '100%', marginBottom: '4px' }}>
            <span style={{
              position: 'absolute',
              top: '-18px',
              left: 0,
              fontSize: '0.68rem',
              color: 'var(--text-muted)',
              textTransform: 'uppercase',
              letterSpacing: '0.04em',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}>
              <Flame size={11} color="#fb7185" />
              {lang === 'en'
                ? `Pathogenic & Clinical Variant Lollipops (${hotspotPins.length} positions)`
                : `Patojenik & Klinik Mutasyon Pinleri (${hotspotPins.length} pozisyon)`}
            </span>

            {hotspotPins.map((pin, idx) => {
              const leftPct = Math.min(99.2, Math.max(0.8, (pin.position / seqLength) * 100));
              const isSelected = activeResidue && !activeResidue.isDomain && activeResidue.position === pin.position;
              const isHotspot = pin.count >= 2;
              const stemHeight = isHotspot ? 24 : 16;
              const dotSize = isSelected ? 12 : isHotspot ? 9 : 7;
              const pinColor = isSelected ? '#38bdf8' : isHotspot ? '#f43f5e' : '#fb7185';
              const labelStr = `${pin.changes[0] || `Pos ${pin.position}`} (aa ${pin.position})${pin.diseases[0] ? ` • ${pin.diseases[0].slice(0, 60)}` : ''}`;

              return (
                <div
                  key={idx}
                  onClick={() => handlePinClick(pin)}
                  onMouseEnter={() => setHoveredItem(labelStr)}
                  onMouseLeave={() => setHoveredItem(null)}
                  title={labelStr}
                  style={{
                    position: 'absolute',
                    left: `${leftPct}%`,
                    bottom: 0,
                    transform: 'translateX(-50%)',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    cursor: 'pointer',
                    zIndex: isSelected ? 15 : isHotspot ? 10 : 5
                  }}
                >
                  <div style={{
                    width: `${dotSize}px`,
                    height: `${dotSize}px`,
                    borderRadius: '50%',
                    background: pinColor,
                    border: isSelected ? '2px solid #fff' : '1px solid rgba(255,255,255,0.4)',
                    boxShadow: isHotspot || isSelected ? `0 0 8px ${pinColor}` : 'none',
                    transition: 'transform 0.15s'
                  }} />
                  <div style={{
                    width: '1.5px',
                    height: `${stemHeight}px`,
                    background: `linear-gradient(to bottom, ${pinColor}, rgba(244, 63, 94, 0.25))`
                  }} />
                </div>
              );
            })}
          </div>
        )}

        {/* Main Backbone & Domains Bar */}
        <div style={{
          position: 'relative',
          height: '32px',
          width: '100%',
          background: 'rgba(30, 41, 59, 0.75)',
          borderRadius: '8px',
          border: '1px solid rgba(148, 163, 184, 0.2)',
          overflow: 'hidden',
          display: 'flex',
          alignItems: 'center'
        }}>
          {/* N-terminus and C-terminus subtle labels */}
          <span style={{
            position: 'absolute',
            left: '8px',
            fontSize: '0.65rem',
            fontWeight: 700,
            color: 'rgba(255,255,255,0.35)',
            zIndex: 1,
            pointerEvents: 'none'
          }}>
            N-term
          </span>
          <span style={{
            position: 'absolute',
            right: '8px',
            fontSize: '0.65rem',
            fontWeight: 700,
            color: 'rgba(255,255,255,0.35)',
            zIndex: 1,
            pointerEvents: 'none'
          }}>
            C-term
          </span>

          {/* Domain Blocks */}
          {domains.map((dom, idx) => {
            const colorObj = DOMAIN_COLORS[idx % DOMAIN_COLORS.length];
            const leftPct = Math.max(0, ((dom.start - 1) / seqLength) * 100);
            const widthPct = Math.min(100 - leftPct, Math.max(1.8, ((dom.end - dom.start + 1) / seqLength) * 100));
            const isSelected =
              activeResidue &&
              activeResidue.isDomain &&
              activeResidue.start === dom.start &&
              activeResidue.end === dom.end;
            const hoverText = `${dom.type}: ${dom.description} (${dom.start} - ${dom.end} aa)`;

            return (
              <div
                key={idx}
                onClick={() => handleDomainClick(dom, colorObj)}
                onMouseEnter={() => setHoveredItem(hoverText)}
                onMouseLeave={() => setHoveredItem(null)}
                title={hoverText}
                style={{
                  position: 'absolute',
                  left: `${leftPct}%`,
                  width: `${widthPct}%`,
                  top: '2px',
                  bottom: '2px',
                  background: colorObj.bg,
                  border: isSelected ? '2px solid #ffffff' : `1px solid ${colorObj.border}`,
                  borderRadius: '6px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  overflow: 'hidden',
                  padding: '0 6px',
                  zIndex: isSelected ? 8 : 3,
                  boxShadow: isSelected ? `0 0 12px ${colorObj.hex}` : 'none',
                  transition: 'all 0.15s'
                }}
              >
                {widthPct >= 7 && (
                  <span style={{
                    fontSize: '0.7rem',
                    fontWeight: 600,
                    color: '#f8fafc',
                    whiteSpace: 'nowrap',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis',
                    textShadow: '0 1px 3px rgba(0,0,0,0.8)'
                  }}>
                    {dom.description}
                  </span>
                )}
              </div>
            );
          })}
        </div>

        {/* Ruler Coordinate Ticks */}
        <div style={{
          position: 'relative',
          height: '18px',
          width: '100%',
          marginTop: '6px'
        }}>
          {ticks.map((t, i) => {
            const pct = t === 1 ? 0 : t === seqLength ? 100 : (t / seqLength) * 100;
            const transform = t === 1 ? 'none' : t === seqLength ? 'translateX(-100%)' : 'translateX(-50%)';
            return (
              <span
                key={i}
                className="font-mono"
                style={{
                  position: 'absolute',
                  left: `${pct}%`,
                  transform,
                  fontSize: '0.68rem',
                  color: 'var(--text-muted)'
                }}
              >
                {t} aa
              </span>
            );
          })}
        </div>

        {/* Clickable Domain Pills & Active Sites Legend */}
        {(domains.length > 0 || functionalSites.length > 0) && (
          <div style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '8px',
            marginTop: '14px',
            paddingTop: '12px',
            borderTop: '1px solid rgba(255, 255, 255, 0.06)'
          }}>
            {domains.map((dom, idx) => {
              const colorObj = DOMAIN_COLORS[idx % DOMAIN_COLORS.length];
              const isSelected =
                activeResidue &&
                activeResidue.isDomain &&
                activeResidue.start === dom.start &&
                activeResidue.end === dom.end;

              return (
                <button
                  key={`dom-pill-${idx}`}
                  type="button"
                  onClick={() => handleDomainClick(dom, colorObj)}
                  style={{
                    background: isSelected ? colorObj.hex : colorObj.bg,
                    border: `1px solid ${colorObj.border}`,
                    color: isSelected ? '#fff' : colorObj.text,
                    borderRadius: '8px',
                    padding: '4px 10px',
                    fontSize: '0.73rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '6px',
                    transition: 'all 0.15s'
                  }}
                >
                  <Layers size={12} />
                  <span>{dom.description}</span>
                  <span className="font-mono" style={{ opacity: 0.8, fontSize: '0.68rem' }}>
                    ({dom.start}-{dom.end})
                  </span>
                </button>
              );
            })}

            {functionalSites.slice(0, 6).map((site, idx) => (
              <button
                key={`site-pill-${idx}`}
                type="button"
                onClick={() =>
                  onSelectResidue &&
                  onSelectResidue({
                    position: site.position,
                    change: `${site.type}: ${site.description}`
                  })
                }
                style={{
                  background: 'rgba(245, 158, 11, 0.12)',
                  border: '1px solid rgba(245, 158, 11, 0.35)',
                  color: '#fbbf24',
                  borderRadius: '8px',
                  padding: '4px 10px',
                  fontSize: '0.72rem',
                  fontWeight: 500,
                  cursor: 'pointer',
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '5px'
                }}
              >
                <Zap size={11} />
                <span>{site.description || site.type}</span>
                <span className="font-mono" style={{ fontSize: '0.68rem' }}>
                  (Pos {site.position})
                </span>
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Biochemical & Physicochemical Sequence Properties */}
      {bioMetrics && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
          gap: '16px',
          alignItems: 'center'
        }}>
          {/* Left: Stacked Amino Acid Composition Bar */}
          <div style={{
            background: 'rgba(10, 15, 28, 0.6)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '10px',
            padding: '12px 16px'
          }}>
            <div style={{
              fontSize: '0.75rem',
              fontWeight: 600,
              color: 'var(--text-secondary)',
              marginBottom: '8px',
              display: 'flex',
              justifyContent: 'space-between'
            }}>
              <span>
                {lang === 'en' ? 'Amino Acid Residue Polarity & Charge Distribution' : 'Amino Asit Polarite & Yük Dağılımı'}
              </span>
              <span style={{ color: 'var(--text-muted)', fontSize: '0.7rem' }}>
                {lang === 'en' ? `Aromatic: ${bioMetrics.aromaticPct}%` : `Aromatik: %${bioMetrics.aromaticPct}`}
              </span>
            </div>

            {/* Stacked Progress Bar */}
            <div style={{
              height: '10px',
              width: '100%',
              borderRadius: '999px',
              overflow: 'hidden',
              display: 'flex',
              marginBottom: '8px',
              background: 'rgba(255,255,255,0.05)'
            }}>
              <div style={{ width: `${bioMetrics.hydrophobicPct}%`, background: '#f59e0b' }} title={`Hydrophobic: ${bioMetrics.hydrophobicPct}%`} />
              <div style={{ width: `${bioMetrics.polarPct}%`, background: '#10b981' }} title={`Polar Uncharged: ${bioMetrics.polarPct}%`} />
              <div style={{ width: `${bioMetrics.positivePct}%`, background: '#3b82f6' }} title={`Basic (+): ${bioMetrics.positivePct}%`} />
              <div style={{ width: `${bioMetrics.negativePct}%`, background: '#f43f5e' }} title={`Acidic (-): ${bioMetrics.negativePct}%`} />
            </div>

            {/* Legend */}
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '12px', fontSize: '0.71rem', color: 'var(--text-secondary)' }}>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f59e0b' }} />
                {lang === 'en' ? 'Hydrophobic:' : 'Hidrofobik:'} <strong>{bioMetrics.hydrophobicPct}%</strong>
              </span>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#10b981' }} />
                {lang === 'en' ? 'Polar:' : 'Polar:'} <strong>{bioMetrics.polarPct}%</strong>
              </span>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#3b82f6' }} />
                {lang === 'en' ? 'Basic (+):' : 'Bazik (+):'} <strong>{bioMetrics.positivePct}%</strong>
              </span>
              <span style={{ display: 'inline-flex', alignItems: 'center', gap: '4px' }}>
                <span style={{ width: '8px', height: '8px', borderRadius: '50%', background: '#f43f5e' }} />
                {lang === 'en' ? 'Acidic (-):' : 'Asidik (-):'} <strong>{bioMetrics.negativePct}%</strong>
              </span>
            </div>
          </div>

          {/* Right: Computed Biophysical Metrics (pI, GRAVY, Aliphatic Index) */}
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(3, 1fr)',
            gap: '10px'
          }}>
            <div style={{
              background: 'rgba(10, 15, 28, 0.6)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '10px',
              padding: '10px 12px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                {lang === 'en' ? 'Theoretical pI' : 'Teorik pI (İzoelektrik)'}
              </div>
              <div className="font-mono" style={{ fontSize: '1.08rem', fontWeight: 700, color: '#38bdf8', marginTop: '2px' }}>
                pH {bioMetrics.pI}
              </div>
              <div style={{ fontSize: '0.66rem', color: 'var(--text-secondary)' }}>
                {bioMetrics.pI < 6.5
                  ? (lang === 'en' ? 'Acidic Protein' : 'Asidik Protein')
                  : bioMetrics.pI > 7.5
                  ? (lang === 'en' ? 'Basic Protein' : 'Bazik Protein')
                  : (lang === 'en' ? 'Near-Neutral' : 'Nötr Civarı')}
              </div>
            </div>

            <div style={{
              background: 'rgba(10, 15, 28, 0.6)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '10px',
              padding: '10px 12px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                {lang === 'en' ? 'GRAVY Hydropathy' : 'GRAVY Hidropati'}
              </div>
              <div className="font-mono" style={{ fontSize: '1.08rem', fontWeight: 700, color: '#c084fc', marginTop: '2px' }}>
                {bioMetrics.gravy > 0 ? `+${bioMetrics.gravy}` : bioMetrics.gravy}
              </div>
              <div style={{ fontSize: '0.66rem', color: 'var(--text-secondary)' }}>
                {bioMetrics.gravy < 0
                  ? (lang === 'en' ? 'Hydrophilic / Soluble' : 'Hidrofilik / Çözünür')
                  : (lang === 'en' ? 'Hydrophobic / Membrane' : 'Hidrofobik / Membran')}
              </div>
            </div>

            <div style={{
              background: 'rgba(10, 15, 28, 0.6)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '10px',
              padding: '10px 12px',
              textAlign: 'center'
            }}>
              <div style={{ fontSize: '0.68rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>
                {lang === 'en' ? 'Aliphatic Index' : 'Alifatik İndeks'}
              </div>
              <div className="font-mono" style={{ fontSize: '1.08rem', fontWeight: 700, color: '#34d399', marginTop: '2px' }}>
                {bioMetrics.aliphaticIndex}
              </div>
              <div style={{ fontSize: '0.66rem', color: 'var(--text-secondary)' }}>
                {bioMetrics.aliphaticIndex >= 80
                  ? (lang === 'en' ? 'High Thermostability' : 'Yüksek Termostabilite')
                  : (lang === 'en' ? 'Moderate Flexibility' : 'Esnek Konformasyon')}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

