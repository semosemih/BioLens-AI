import React, { useState, useEffect, useRef } from 'react';
import { Search, Sparkles, Dna, Activity, Shield, Flame, Heart, Brain, Filter, Zap } from 'lucide-react';

const ICON_MAP = {
  shield: Shield,
  activity: Activity,
  dna: Dna,
  zap: Zap,
  filter: Filter,
  heart: Heart,
  brain: Brain,
  flame: Flame
};

export default function Header({ onSearch, currentQuery, loading, examples }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const searchTimeoutRef = useRef(null);

  useEffect(() => {
    if (currentQuery) {
      setSearchTerm(currentQuery);
    }
  }, [currentQuery]);

  const handleInputChange = (e) => {
    const val = e.target.value;
    setSearchTerm(val);

    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    if (val.trim().length >= 2) {
      searchTimeoutRef.current = setTimeout(async () => {
        try {
          const res = await fetch(`/api/search?q=${encodeURIComponent(val.trim())}`);
          if (res.ok) {
            const data = await res.json();
            setSuggestions(data.results || []);
            setShowSuggestions(true);
          }
        } catch (err) {
          console.error('Autocomplete error:', err);
        }
      }, 300);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (searchTerm.trim()) {
      setShowSuggestions(false);
      onSearch(searchTerm.trim());
    }
  };

  const handleSelectSuggestion = (gene) => {
    setSearchTerm(gene);
    setShowSuggestions(false);
    onSearch(gene);
  };

  return (
    <header style={{
      borderBottom: '1px solid var(--border-subtle)',
      background: 'rgba(6, 9, 17, 0.85)',
      backdropFilter: 'blur(20px)',
      position: 'sticky',
      top: 0,
      zIndex: 50,
      padding: '16px 24px'
    }}>
      <div style={{
        maxWidth: '1440px',
        margin: '0 auto',
        display: 'flex',
        flexDirection: 'column',
        gap: '16px'
      }}>
        {/* Top brand line & search input */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '16px'
        }}>
          {/* Logo */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }} onClick={() => onSearch('TP53')}>
            <div style={{
              width: '42px',
              height: '42px',
              borderRadius: '12px',
              background: 'linear-gradient(135deg, #06b6d4 0%, #3b82f6 50%, #6366f1 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#fff',
              boxShadow: '0 0 20px rgba(6, 182, 212, 0.4)'
            }}>
              <Dna size={24} className="pulse-glow" />
            </div>
            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <h1 style={{ fontSize: '1.4rem', fontWeight: 800, letterSpacing: '-0.03em', background: 'linear-gradient(90deg, #f8fafc, #38bdf8)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
                  BioLens AI
                </h1>
                <span className="badge badge-cyan" style={{ fontSize: '0.65rem', padding: '2px 6px' }}>v1.0 Prototip</span>
              </div>
              <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                Protein Keşfi & Hastalık İlişkileri Platformu
              </p>
            </div>
          </div>

          {/* Search bar */}
          <div style={{ position: 'relative', width: '100%', maxWidth: '520px' }}>
            <form onSubmit={handleSubmit} style={{ position: 'relative' }}>
              <Search
                size={18}
                style={{
                  position: 'absolute',
                  left: '14px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--text-muted)'
                }}
              />
              <input
                type="text"
                value={searchTerm}
                onChange={handleInputChange}
                onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                placeholder="Protein veya gen adı girin (örn. TP53, EGFR, BRCA1, INS)..."
                style={{
                  width: '100%',
                  background: 'rgba(15, 23, 42, 0.75)',
                  border: '1px solid rgba(56, 189, 248, 0.3)',
                  borderRadius: '12px',
                  padding: '12px 100px 12px 42px',
                  color: '#fff',
                  fontSize: '0.9rem',
                  outline: 'none',
                  boxShadow: '0 4px 15px rgba(0, 0, 0, 0.3)',
                  transition: 'all 0.2s'
                }}
              />
              <button
                type="submit"
                disabled={loading}
                style={{
                  position: 'absolute',
                  right: '6px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'linear-gradient(135deg, #0ea5e9, #2563eb)',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '7px 14px',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  cursor: loading ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                  transition: 'all 0.2s'
                }}
              >
                {loading ? 'Aranıyor...' : 'Keşfet'}
              </button>
            </form>

            {/* Suggestions dropdown */}
            {showSuggestions && suggestions.length > 0 && (
              <div style={{
                position: 'absolute',
                top: 'calc(100% + 6px)',
                left: 0,
                right: 0,
                background: 'rgba(10, 16, 28, 0.96)',
                backdropFilter: 'blur(16px)',
                border: '1px solid var(--border-hover)',
                borderRadius: '12px',
                boxShadow: 'var(--shadow-lg)',
                zIndex: 100,
                overflow: 'hidden'
              }}>
                {suggestions.map((hit, idx) => (
                  <div
                    key={idx}
                    onClick={() => handleSelectSuggestion(hit.geneSymbol || hit.accession)}
                    style={{
                      padding: '10px 16px',
                      borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      transition: 'background 0.15s'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.background = 'rgba(56, 189, 248, 0.1)'}
                    onMouseLeave={(e) => e.currentTarget.style.background = 'transparent'}
                  >
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{ fontWeight: 600, color: '#38bdf8' }}>{hit.geneSymbol}</span>
                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>({hit.accession})</span>
                      </div>
                      <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>
                        {hit.proteinName}
                      </div>
                    </div>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                      {hit.length} aa
                    </span>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Real Scientific Databases badge group */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>Kaynaklar:</span>
            <span className="badge badge-blue" style={{ fontSize: '0.65rem' }}>UniProt</span>
            <span className="badge badge-cyan" style={{ fontSize: '0.65rem' }}>AlphaFold DB</span>
            <span className="badge badge-rose" style={{ fontSize: '0.65rem' }}>ClinVar</span>
            <span className="badge badge-purple" style={{ fontSize: '0.65rem' }}>PubMed</span>
          </div>
        </div>

        {/* Quick select example protein pills */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          overflowX: 'auto',
          paddingBottom: '4px'
        }}>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', flexShrink: 0 }}>
            Hızlı İncele:
          </span>
          {examples && examples.map((ex, idx) => {
            const IconComponent = ICON_MAP[ex.icon] || Dna;
            const isSelected = currentQuery && currentQuery.toUpperCase() === ex.symbol;

            return (
              <button
                key={idx}
                onClick={() => onSearch(ex.symbol)}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  background: isSelected ? 'rgba(56, 189, 248, 0.25)' : 'rgba(255, 255, 255, 0.04)',
                  border: isSelected ? '1px solid #38bdf8' : '1px solid var(--border-subtle)',
                  borderRadius: '9999px',
                  padding: '5px 12px',
                  color: isSelected ? '#38bdf8' : 'var(--text-secondary)',
                  fontSize: '0.76rem',
                  fontWeight: 500,
                  cursor: 'pointer',
                  flexShrink: 0,
                  transition: 'all 0.15s'
                }}
                title={`${ex.name} • ${ex.category}`}
              >
                <IconComponent size={12} />
                <span><strong>{ex.symbol}</strong> - {ex.name.split(' ')[0]}</span>
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}
