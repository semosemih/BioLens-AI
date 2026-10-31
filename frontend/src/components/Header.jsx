import React, { useState, useEffect, useRef } from 'react';
import { Search, Dna, Activity, Shield, Flame, Heart, Brain, Filter, Zap, History, X, CheckCircle2 } from 'lucide-react';

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

export default function Header({ onSearch, currentQuery, loading, examples }) {
  const [searchTerm, setSearchTerm] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [searchingSuggestions, setSearchingSuggestions] = useState(false);
  const [activeIndex, setActiveIndex] = useState(-1);
  const [recentSearches, setRecentSearches] = useState([]);

  const searchTimeoutRef = useRef(null);
  const abortControllerRef = useRef(null);
  const searchContainerRef = useRef(null);
  const inputRef = useRef(null);

  // Load recent searches from localStorage
  useEffect(() => {
    try {
      const saved = localStorage.getItem('biolens_recent_searches');
      if (saved) {
        setRecentSearches(JSON.parse(saved));
      }
    } catch (e) {
      console.error('Failed to load recent searches:', e);
    }
  }, []);

  // Close suggestions dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (searchContainerRef.current && !searchContainerRef.current.contains(event.target)) {
        setShowSuggestions(false);
        setActiveIndex(-1);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const saveRecent = (query) => {
    if (!query) return;
    const clean = query.trim().toUpperCase();
    if (!clean || clean.length > 20) return;

    setRecentSearches((prev) => {
      const filtered = prev.filter((item) => item !== clean);
      const updated = [clean, ...filtered].slice(0, 6);
      try {
        localStorage.setItem('biolens_recent_searches', JSON.stringify(updated));
      } catch (e) {}
      return updated;
    });
  };

  useEffect(() => {
    if (currentQuery) {
      setSearchTerm(currentQuery);
      saveRecent(currentQuery);
    }
  }, [currentQuery]);

  // Filter curated examples locally for instant zero-latency feedback
  const getInstantLocalMatches = (rawVal) => {
    const q = normalizeTr(rawVal);
    if (!q || !examples || examples.length === 0) return [];
    return examples
      .filter((ex) => {
        const sym = normalizeTr(ex.symbol);
        const name = normalizeTr(ex.name);
        const cat = normalizeTr(ex.category);
        const desc = normalizeTr(ex.description);
        return sym.includes(q) || name.includes(q) || cat.includes(q) || desc.includes(q);
      })
      .map((ex) => ({
        accession: '',
        geneSymbol: ex.symbol,
        proteinName: ex.name,
        turkishName: ex.name,
        organism: 'Homo sapiens',
        reviewed: true,
        isCuratedLocal: true
      }));
  };

  const triggerAutocomplete = (val) => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const trimmed = val.trim();
    if (trimmed.length === 0) {
      setSuggestions([]);
      setSearchingSuggestions(false);
      setShowSuggestions(false);
      setActiveIndex(-1);
      return;
    }

    // Immediate local matches so dropdown responds instantaneously
    const localInstant = getInstantLocalMatches(trimmed);
    if (localInstant.length > 0) {
      setSuggestions((prev) => (prev.length > 0 ? prev : localInstant));
      setShowSuggestions(true);
    }

    setSearchingSuggestions(true);
    searchTimeoutRef.current = setTimeout(async () => {
      const controller = new AbortController();
      abortControllerRef.current = controller;

      try {
        const res = await fetch(`/api/search?q=${encodeURIComponent(trimmed)}`, {
          signal: controller.signal
        });
        if (res.ok) {
          const data = await res.json();
          const apiHits = data.results || [];
          setSuggestions(apiHits);
          setShowSuggestions(true);
          setActiveIndex(-1);
        }
      } catch (err) {
        if (err.name !== 'AbortError') {
          console.error('Autocomplete error:', err);
        }
      } finally {
        if (abortControllerRef.current === controller) {
          setSearchingSuggestions(false);
        }
      }
    }, 160);
  };

  const handleInputChange = (e) => {
    const val = e.target.value;
    setSearchTerm(val);
    triggerAutocomplete(val);
  };

  const handleClearSearch = () => {
    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    if (abortControllerRef.current) abortControllerRef.current.abort();
    setSearchTerm('');
    setSuggestions([]);
    setShowSuggestions(false);
    setSearchingSuggestions(false);
    setActiveIndex(-1);
    if (inputRef.current) {
      inputRef.current.focus();
    }
  };

  const handleSelectSuggestion = (hit) => {
    const displayGene = hit.geneSymbol || hit.accession;
    const targetIdentifier = hit.accession || hit.geneSymbol;
    setSearchTerm(displayGene);
    setShowSuggestions(false);
    setActiveIndex(-1);
    onSearch(targetIdentifier, displayGene);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (searchTimeoutRef.current) clearTimeout(searchTimeoutRef.current);
    if (abortControllerRef.current) abortControllerRef.current.abort();
    setSearchingSuggestions(false);

    // If user navigated to a suggestion with keyboard arrows, select it
    if (showSuggestions && activeIndex >= 0 && suggestions[activeIndex]) {
      handleSelectSuggestion(suggestions[activeIndex]);
      return;
    }

    const trimmed = searchTerm.trim();
    if (!trimmed) return;

    setShowSuggestions(false);
    setActiveIndex(-1);

    // If suggestions are already loaded for this query and top hit matches closely, use its accession directly
    if (suggestions.length > 0) {
      const qNorm = normalizeTr(trimmed);
      const top = suggestions[0];
      const topGene = normalizeTr(top.geneSymbol);
      const topAcc = normalizeTr(top.accession);
      const topTr = normalizeTr(top.turkishName);
      const topName = normalizeTr(top.proteinName);
      const topAliases = (top.allGenes || []).map(normalizeTr);

      if (
        qNorm === topGene ||
        qNorm === topAcc ||
        qNorm === topTr ||
        qNorm === topName ||
        topAliases.includes(qNorm)
      ) {
        handleSelectSuggestion(top);
        return;
      }
    }

    onSearch(trimmed);
  };

  const handleKeyDown = (e) => {
    if (!showSuggestions || suggestions.length === 0) {
      if (e.key === 'Escape') {
        setShowSuggestions(false);
      }
      return;
    }

    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setActiveIndex((prev) => (prev < suggestions.length - 1 ? prev + 1 : 0));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setActiveIndex((prev) => (prev > 0 ? prev - 1 : suggestions.length - 1));
    } else if (e.key === 'Escape') {
      e.preventDefault();
      setShowSuggestions(false);
      setActiveIndex(-1);
    }
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
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px', cursor: 'pointer' }} onClick={() => onSearch('TP53', 'TP53')}>
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
          <div ref={searchContainerRef} style={{ position: 'relative', width: '100%', maxWidth: '560px' }}>
            <form onSubmit={handleSubmit} style={{ position: 'relative' }}>
              <Search
                size={18}
                style={{
                  position: 'absolute',
                  left: '14px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  color: 'var(--text-muted)',
                  pointerEvents: 'none'
                }}
              />
              <input
                ref={inputRef}
                type="text"
                value={searchTerm}
                onChange={handleInputChange}
                onKeyDown={handleKeyDown}
                onFocus={(e) => {
                  e.target.select();
                  if (suggestions.length > 0) {
                    setShowSuggestions(true);
                  } else if (searchTerm.trim().length >= 1) {
                    triggerAutocomplete(searchTerm);
                  }
                }}
                placeholder="Gen, protein veya hastalık ara (örn. TP53, İnsülin, HER2, BRCA1, Hemoglobin)..."
                style={{
                  width: '100%',
                  background: 'rgba(15, 23, 42, 0.75)',
                  border: '1px solid rgba(56, 189, 248, 0.3)',
                  borderRadius: '12px',
                  padding: '12px 124px 12px 42px',
                  color: '#fff',
                  fontSize: '0.9rem',
                  outline: 'none',
                  boxShadow: '0 4px 15px rgba(0, 0, 0, 0.3)',
                  transition: 'all 0.2s'
                }}
              />

              {/* Clear input button */}
              {searchTerm && (
                <button
                  type="button"
                  onClick={handleClearSearch}
                  title="Aramayı temizle"
                  style={{
                    position: 'absolute',
                    right: '88px',
                    top: '50%',
                    transform: 'translateY(-50%)',
                    background: 'rgba(255, 255, 255, 0.08)',
                    border: 'none',
                    borderRadius: '50%',
                    width: '22px',
                    height: '22px',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--text-muted)',
                    cursor: 'pointer',
                    padding: 0
                  }}
                >
                  <X size={13} />
                </button>
              )}

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
            {showSuggestions && (suggestions.length > 0 || searchingSuggestions || searchTerm.trim().length >= 2) && (
              <div style={{
                position: 'absolute',
                top: 'calc(100% + 6px)',
                left: 0,
                right: 0,
                background: 'rgba(10, 16, 28, 0.98)',
                backdropFilter: 'blur(16px)',
                border: '1px solid var(--border-hover)',
                borderRadius: '12px',
                boxShadow: 'var(--shadow-lg)',
                zIndex: 100,
                maxHeight: '380px',
                overflowY: 'auto'
              }}>
                {suggestions.map((hit, idx) => {
                  const isActive = idx === activeIndex;
                  const aliases = (hit.allGenes || []).filter((g) => g && g.toUpperCase() !== (hit.geneSymbol || '').toUpperCase()).slice(0, 3);

                  return (
                    <div
                      key={hit.accession || `${hit.geneSymbol}-${idx}`}
                      onClick={() => handleSelectSuggestion(hit)}
                      onMouseEnter={() => setActiveIndex(idx)}
                      style={{
                        padding: '10px 16px',
                        borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
                        cursor: 'pointer',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'space-between',
                        gap: '12px',
                        background: isActive ? 'rgba(56, 189, 248, 0.14)' : 'transparent',
                        transition: 'background 0.12s'
                      }}
                    >
                      <div style={{ minWidth: 0, flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', flexWrap: 'wrap' }}>
                          <span style={{ fontWeight: 700, color: '#38bdf8', fontSize: '0.9rem' }}>
                            {hit.geneSymbol}
                          </span>
                          {hit.accession && (
                            <span className="font-mono" style={{ fontSize: '0.72rem', color: 'var(--text-muted)', background: 'rgba(255,255,255,0.05)', padding: '1px 6px', borderRadius: '4px' }}>
                              {hit.accession}
                            </span>
                          )}
                          {hit.reviewed && (
                            <span style={{ display: 'inline-flex', alignItems: 'center', gap: '3px', fontSize: '0.66rem', color: '#34d399', background: 'rgba(16, 185, 129, 0.12)', padding: '1px 6px', borderRadius: '4px' }}>
                              <CheckCircle2 size={10} />
                              Swiss-Prot
                            </span>
                          )}
                          {aliases.length > 0 && (
                            <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                              ({aliases.join(', ')})
                            </span>
                          )}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-primary)', marginTop: '2px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>
                          {hit.turkishName ? (
                            <>
                              <span style={{ color: '#e2e8f0', fontWeight: 500 }}>{hit.turkishName}</span>
                              {hit.proteinName && hit.proteinName !== hit.turkishName && (
                                <span style={{ color: 'var(--text-muted)', marginLeft: '6px', fontSize: '0.75rem' }}>
                                  • {hit.proteinName}
                                </span>
                              )}
                            </>
                          ) : (
                            hit.proteinName
                          )}
                        </div>
                      </div>
                      <div style={{ textAlign: 'right', flexShrink: 0 }}>
                        {hit.length > 0 && (
                          <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                            {hit.length} aa
                          </div>
                        )}
                        {hit.organism && (
                          <div style={{ fontSize: '0.66rem', color: 'var(--text-muted)', opacity: 0.8 }}>
                            {hit.organism === 'Homo sapiens' ? 'İnsan' : hit.organism.split(' ').slice(0, 2).join(' ')}
                          </div>
                        )}
                      </div>
                    </div>
                  );
                })}

                {searchingSuggestions && (
                  <div style={{ padding: '10px 16px', fontSize: '0.78rem', color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <div style={{
                      width: '12px',
                      height: '12px',
                      borderRadius: '50%',
                      border: '2px solid rgba(56, 189, 248, 0.25)',
                      borderTopColor: '#38bdf8',
                      animation: 'spinSlow 0.8s linear infinite'
                    }} />
                    <span>UniProtKB ve biyomedikal katalog taranıyor...</span>
                  </div>
                )}

                {!searchingSuggestions && suggestions.length === 0 && searchTerm.trim().length >= 2 && (
                  <div style={{ padding: '14px 16px', textAlign: 'center' }}>
                    <div style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '8px' }}>
                      &ldquo;{searchTerm.trim()}&rdquo; için doğrudan eşleşme bulunamadı.
                    </div>
                    <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginBottom: '8px' }}>
                      Örnek gen sembolleri veya protein adlarıyla arayabilirsiniz:
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '6px' }}>
                      {['TP53', 'EGFR', 'BRCA1', 'INS', 'APOE', 'HBB'].map((sym) => (
                        <button
                          key={sym}
                          type="button"
                          onClick={() => handleSelectSuggestion({ geneSymbol: sym, accession: '' })}
                          style={{
                            background: 'rgba(56, 189, 248, 0.12)',
                            border: '1px solid rgba(56, 189, 248, 0.3)',
                            borderRadius: '6px',
                            padding: '3px 8px',
                            color: '#38bdf8',
                            fontSize: '0.73rem',
                            fontWeight: 600,
                            cursor: 'pointer'
                          }}
                        >
                          {sym}
                        </button>
                      ))}
                    </div>
                  </div>
                )}
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

        {/* Quick select example protein pills & Recent searches */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          overflowX: 'auto',
          paddingBottom: '4px'
        }}>
          {recentSearches && recentSearches.length > 0 && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexShrink: 0 }}>
              <span style={{ fontSize: '0.73rem', color: '#38bdf8', display: 'flex', alignItems: 'center', gap: '4px', fontWeight: 600 }}>
                <History size={13} />
                Son:
              </span>
              {recentSearches.map((item, idx) => (
                <button
                  key={`rec-${idx}`}
                  onClick={() => onSearch(item, item)}
                  style={{
                    background: currentQuery && currentQuery.toUpperCase() === item ? 'rgba(56, 189, 248, 0.25)' : 'rgba(56, 189, 248, 0.08)',
                    border: '1px solid rgba(56, 189, 248, 0.25)',
                    borderRadius: '6px',
                    padding: '3px 8px',
                    color: '#38bdf8',
                    fontSize: '0.74rem',
                    fontWeight: 600,
                    cursor: 'pointer',
                    transition: 'all 0.15s'
                  }}
                  title={`${item} verilerini yükle`}
                >
                  {item}
                </button>
              ))}
              <div style={{ width: '1px', height: '16px', background: 'var(--border-subtle)', margin: '0 4px' }}></div>
            </div>
          )}

          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', flexShrink: 0 }}>
            Hızlı İncele:
          </span>
          {examples && examples.map((ex, idx) => {
            const IconComponent = ICON_MAP[ex.icon] || Dna;
            const isSelected = currentQuery && currentQuery.toUpperCase() === ex.symbol;

            return (
              <button
                key={idx}
                onClick={() => onSearch(ex.symbol, ex.symbol)}
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
