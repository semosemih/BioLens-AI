import React, { useEffect, useRef, useState } from 'react';
import { 
  RotateCw, 
  ZoomIn, 
  Layers, 
  Eye, 
  Maximize2, 
  Minimize2,
  Camera, 
  Sparkles, 
  Info, 
  Palette, 
  Target,
  Download
} from 'lucide-react';

export default function ProteinViewer3D({ 
  accession, 
  geneSymbol, 
  plddtScore, 
  highlightResidue, 
  onClearHighlight 
}) {
  const panelRef = useRef(null);
  const containerRef = useRef(null);
  const viewerRef = useRef(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isSpinning, setIsSpinning] = useState(true);
  const [renderStyle, setRenderStyle] = useState('cartoon'); // cartoon, stick, sphere, surface
  const [colorScheme, setColorScheme] = useState('plddt'); // plddt, rainbow, ss, chain
  const [showSurface, setShowSurface] = useState(false);
  const [selectedResidueInfo, setSelectedResidueInfo] = useState(null);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [customResidue, setCustomResidue] = useState('');
  const [activeCustomResidue, setActiveCustomResidue] = useState(null);

  // Sync fullscreen state & resize viewer on change
  useEffect(() => {
    const handleFullscreenChange = () => {
      const full = !!document.fullscreenElement;
      setIsFullscreen(full);
      setTimeout(() => {
        if (viewerRef.current) {
          viewerRef.current.resize();
          viewerRef.current.render();
        }
      }, 150);
    };

    document.addEventListener('fullscreenchange', handleFullscreenChange);
    return () => document.removeEventListener('fullscreenchange', handleFullscreenChange);
  }, []);

  // Initialize or re-render 3Dmol viewer
  useEffect(() => {
    let isCancelled = false;

    async function loadStructure() {
      if (!accession) return;
      setLoading(true);
      setError(null);

      // Check if 3Dmol is loaded in window
      if (!window.$3Dmol) {
        setError('3Dmol.js kütüphanesi yüklenemedi. Lütfen internet bağlantınızı kontrol edin.');
        setLoading(false);
        return;
      }

      try {
        // Fetch PDB coordinate content from our backend endpoint
        const response = await fetch(`/api/pdb/${accession}`);
        if (!response.ok) {
          throw new Error('AlphaFold PDB koordinat dosyası alınamadı');
        }
        const pdbData = await response.text();

        if (isCancelled) return;

        // Clear previous viewer if any
        if (containerRef.current) {
          containerRef.current.innerHTML = '';
        }

        const config = { backgroundColor: '#060911' };
        const viewer = window.$3Dmol.createViewer(containerRef.current, config);
        viewerRef.current = viewer;

        // Add model to viewer
        viewer.addModel(pdbData, 'pdb');

        // Apply primary styles
        applyStyling(viewer, renderStyle, colorScheme, showSurface);

        viewer.zoomTo();
        viewer.render();

        // Enable auto-spin if active
        if (isSpinning) {
          viewer.spin('y', 0.8);
        }

        // Add atom/residue click handler
        viewer.setClickable({}, true, (atom) => {
          if (atom) {
            setSelectedResidueInfo({
              resn: atom.resn,
              resi: atom.resi,
              chain: atom.chain,
              b: atom.b // b-factor represents pLDDT in AlphaFold models
            });
          }
        });

        setLoading(false);
      } catch (err) {
        console.error('Error loading 3D protein structure:', err);
        if (!isCancelled) {
          setError(err.message || '3B yapı yüklenirken bir hata oluştu');
          setLoading(false);
        }
      }
    }

    loadStructure();

    return () => {
      isCancelled = true;
      if (viewerRef.current) {
        viewerRef.current.spin(false);
      }
    };
  }, [accession]);

  // Apply styling whenever style/color changes
  const applyStyling = (viewer, style, color, surface) => {
    if (!viewer) return;

    // Reset styles
    viewer.setStyle({}, {});
    viewer.removeAllSurfaces();

    // Color logic
    let colorObj = {};
    if (color === 'plddt') {
      // AlphaFold pLDDT coloring using b-factor
      // >90: #0053d6 (royal blue), 70-90: #65cbf3 (cyan), 50-70: #ffdb13 (yellow), <50: #ff7d45 (orange)
      colorObj = {
        prop: 'b',
        gradient: 'rwb',
        map: {
          0: '#ff7d45',
          50: '#ffdb13',
          70: '#65cbf3',
          90: '#0053d6',
          100: '#0053d6'
        }
      };
    } else if (color === 'rainbow') {
      colorObj = { color: 'spectrum' };
    } else if (color === 'ss') {
      colorObj = {
        ss: {
          'helix': '#ec4899',
          'sheet': '#eab308',
          'coil': '#64748b'
        }
      };
    } else {
      colorObj = { color: 'cyan' };
    }

    // Secondary representation
    if (style === 'cartoon') {
      viewer.setStyle({}, { cartoon: colorObj });
    } else if (style === 'stick') {
      viewer.setStyle({}, { stick: { colorscheme: 'amino', radius: 0.25 } });
    } else if (style === 'sphere') {
      viewer.setStyle({}, { sphere: { colorscheme: 'amino', scale: 0.6 } });
    }

    // Optional translucent molecular surface
    if (surface) {
      viewer.addSurface(window.$3Dmol.SurfaceType.VDW, {
        opacity: 0.65,
        color: '#0ea5e9'
      });
    }

    viewer.render();
  };

  // Update styles on state changes
  useEffect(() => {
    if (viewerRef.current && !loading) {
      applyStyling(viewerRef.current, renderStyle, colorScheme, showSurface);
    }
  }, [renderStyle, colorScheme, showSurface, loading]);

  // Toggle rotation
  const toggleSpin = () => {
    if (!viewerRef.current) return;
    const nextState = !isSpinning;
    setIsSpinning(nextState);
    if (nextState) {
      viewerRef.current.spin('y', 0.8);
    } else {
      viewerRef.current.spin(false);
    }
  };

  // Reset camera view
  const handleResetView = () => {
    if (!viewerRef.current) return;
    viewerRef.current.zoomTo();
    viewerRef.current.render();
  };

  // Download snapshot
  const handleSnapshot = () => {
    if (!viewerRef.current) return;
    const canvas = containerRef.current?.querySelector('canvas');
    if (canvas) {
      const image = canvas.toDataURL('image/png');
      const a = document.createElement('a');
      a.href = image;
      a.download = `${geneSymbol || accession}_alphafold_3d.png`;
      a.click();
    }
  };

  // Download PDB coordinates file
  const handleDownloadPDB = () => {
    if (!accession) return;
    const a = document.createElement('a');
    a.href = `/api/pdb/${accession}`;
    a.download = `${geneSymbol || accession}_alphafold.pdb`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
  };

  // Toggle Fullscreen
  const toggleFullscreen = () => {
    if (!panelRef.current) return;
    if (!document.fullscreenElement) {
      panelRef.current.requestFullscreen().catch((err) => {
        console.error('Fullscreen request failed:', err);
      });
    } else {
      document.exitFullscreen().catch((err) => {
        console.error('Exit fullscreen failed:', err);
      });
    }
  };

  // Jump to custom residue position
  const handleJumpToResidue = (e) => {
    e?.preventDefault();
    const pos = parseInt(customResidue.trim(), 10);
    if (isNaN(pos) || pos <= 0) return;

    if (viewerRef.current) {
      const viewer = viewerRef.current;
      viewer.spin(false);
      setIsSpinning(false);
      viewer.removeAllLabels();

      // Highlight target residue
      viewer.setStyle({ resi: pos }, {
        stick: { color: '#f43f5e', radius: 0.4 },
        sphere: { color: '#fb7185', scale: 0.5 }
      });

      viewer.addLabel(`Kalıntı Pos ${pos}`, {
        fontSize: 14,
        fontColor: '#ffffff',
        backgroundColor: '#e11d48',
        backgroundOpacity: 0.85,
        inFront: true
      }, { resi: pos });

      viewer.zoomTo({ resi: pos }, 800);
      viewer.render();

      setActiveCustomResidue(pos);
      onClearHighlight && onClearHighlight();
    }
  };

  const handleClearCustomResidue = () => {
    setActiveCustomResidue(null);
    setCustomResidue('');
    if (viewerRef.current) {
      viewerRef.current.removeAllLabels();
      applyStyling(viewerRef.current, renderStyle, colorScheme, showSurface);
      viewerRef.current.zoomTo();
    }
  };

  // Focus and highlight specific residue from mutation selection
  useEffect(() => {
    if (!viewerRef.current || !highlightResidue) return;

    // Reset custom residue highlight when prop changes
    setActiveCustomResidue(null);
    setCustomResidue('');

    const viewer = viewerRef.current;
    const resi = highlightResidue.position;

    if (resi) {
      // Pause spin to observe residue
      viewer.spin(false);
      setIsSpinning(false);

      // Remove existing custom labels
      viewer.removeAllLabels();

      // Highlight target residue with spheres and bright magenta stick
      viewer.setStyle({ resi: resi }, {
        stick: { color: '#f43f5e', radius: 0.4 },
        sphere: { color: '#fb7185', scale: 0.5 }
      });

      // Add 3D text label above residue
      viewer.addLabel(`${highlightResidue.change || 'Mutasyon'} (Pos ${resi})`, {
        fontSize: 14,
        fontColor: '#ffffff',
        backgroundColor: '#e11d48',
        backgroundOpacity: 0.85,
        inFront: true
      }, { resi: resi });

      // Zoom focus on this residue
      viewer.zoomTo({ resi: resi }, 800);
      viewer.render();
    }
  }, [highlightResidue]);

  return (
    <div 
      ref={panelRef}
      className="glass-panel" 
      style={{ 
        position: 'relative', 
        overflow: 'hidden', 
        display: 'flex', 
        flexDirection: 'column',
        ...(isFullscreen ? { background: '#060911', borderRadius: 0 } : {})
      }}
    >
      {/* Top Header Bar */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
        padding: '14px 20px',
        borderBottom: '1px solid var(--border-subtle)',
        background: 'rgba(10, 15, 28, 0.7)',
        backdropFilter: 'blur(8px)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
          <div style={{
            width: '10px',
            height: '10px',
            borderRadius: '50%',
            background: '#10b981',
            boxShadow: '0 0 10px #10b981'
          }}></div>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '8px' }}>
              AlphaFold 3B Yapısal Tahmin
              <span className="badge badge-cyan" style={{ fontSize: '0.7rem' }}>
                {geneSymbol || accession}
              </span>
            </h3>
            <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
              Etkileşimli 3Dmol.js WebGL Görüntüleyici • Döndürmek için sürükleyin, yakınlaştırmak için kaydırın
            </p>
          </div>
        </div>

        {/* Action Controls & Jump Input */}
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
          {/* Jump to Residue Form */}
          <form onSubmit={handleJumpToResidue} style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <div style={{ position: 'relative', display: 'flex', alignItems: 'center' }}>
              <Target size={13} style={{ position: 'absolute', left: '8px', color: 'var(--text-muted)', pointerEvents: 'none' }} />
              <input
                type="number"
                min="1"
                placeholder="Kalıntı No (örn: 175)"
                value={customResidue}
                onChange={(e) => setCustomResidue(e.target.value)}
                style={{
                  width: '135px',
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: '8px',
                  padding: '6px 8px 6px 26px',
                  color: '#fff',
                  fontSize: '0.78rem',
                  outline: 'none'
                }}
              />
            </div>
            <button
              type="submit"
              title="Girilen amino asit kalıntısına 3D odaklan"
              style={{
                background: 'rgba(244, 63, 94, 0.15)',
                border: '1px solid rgba(244, 63, 94, 0.3)',
                color: '#fb7185',
                borderRadius: '8px',
                padding: '6px 10px',
                fontSize: '0.78rem',
                fontWeight: 500,
                cursor: 'pointer',
                whiteSpace: 'nowrap',
                transition: 'all 0.2s'
              }}
            >
              Odaklan
            </button>
          </form>

          <div style={{ width: '1px', height: '24px', background: 'var(--border-subtle)', margin: '0 2px' }}></div>

          <button
            onClick={toggleSpin}
            title={isSpinning ? "Dönüşü Durdur" : "Otomatik Döndür"}
            style={{
              background: isSpinning ? 'rgba(56, 189, 248, 0.2)' : 'rgba(255, 255, 255, 0.05)',
              color: isSpinning ? '#38bdf8' : 'var(--text-secondary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              padding: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s'
            }}
          >
            <RotateCw size={16} className={isSpinning ? "spin-slow" : ""} />
          </button>

          <button
            onClick={handleResetView}
            title="Görünümü Sıfırla"
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              color: 'var(--text-secondary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              padding: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s'
            }}
          >
            <ZoomIn size={16} />
          </button>

          <button
            onClick={handleDownloadPDB}
            title="AlphaFold .PDB Koordinat Dosyasını İndir"
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              color: 'var(--text-secondary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              padding: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s'
            }}
          >
            <Download size={16} />
          </button>

          <button
            onClick={handleSnapshot}
            title="Yüksek Çözünürlüklü Görüntü İndir (PNG)"
            style={{
              background: 'rgba(255, 255, 255, 0.05)',
              color: 'var(--text-secondary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              padding: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s'
            }}
          >
            <Camera size={16} />
          </button>

          <button
            onClick={toggleFullscreen}
            title={isFullscreen ? "Tam Ekrandan Çık" : "Tam Ekran Yap"}
            style={{
              background: isFullscreen ? 'rgba(56, 189, 248, 0.2)' : 'rgba(255, 255, 255, 0.05)',
              color: isFullscreen ? '#38bdf8' : 'var(--text-secondary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: '8px',
              padding: '8px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              transition: 'all 0.2s'
            }}
          >
            {isFullscreen ? <Minimize2 size={16} /> : <Maximize2 size={16} />}
          </button>
        </div>
      </div>

      {/* 3D Canvas Container */}
      <div style={{ 
        position: 'relative', 
        width: '100%', 
        height: isFullscreen ? 'calc(100vh - 125px)' : '480px', 
        background: '#050811',
        transition: 'height 0.2s'
      }}>
        {loading && (
          <div style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '12px',
            background: 'rgba(6, 9, 17, 0.85)',
            zIndex: 10
          }}>
            <div style={{
              width: '40px',
              height: '40px',
              border: '3px solid rgba(56, 189, 248, 0.2)',
              borderTopColor: '#38bdf8',
              borderRadius: '50%',
              animation: 'spinSlow 1s linear infinite'
            }}></div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              AlphaFold .PDB Koordinatları Çözümleniyor...
            </p>
          </div>
        )}

        {error && (
          <div style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '12px',
            padding: '20px',
            textAlign: 'center',
            background: 'rgba(6, 9, 17, 0.95)',
            zIndex: 10
          }}>
            <Info size={32} color="#f43f5e" />
            <p style={{ color: '#fb7185', fontSize: '0.9rem' }}>{error}</p>
          </div>
        )}

        {/* 3Dmol element */}
        <div
          ref={containerRef}
          style={{ width: '100%', height: '100%', cursor: 'grab' }}
        ></div>

        {/* Highlight Banner if Mutation is selected from table */}
        {highlightResidue && (
          <div style={{
            position: 'absolute',
            top: '16px',
            left: '16px',
            background: 'rgba(225, 29, 72, 0.9)',
            backdropFilter: 'blur(10px)',
            color: '#fff',
            padding: '8px 14px',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontSize: '0.8rem',
            boxShadow: '0 4px 15px rgba(225, 29, 72, 0.4)',
            zIndex: 5
          }}>
            <Target size={16} />
            <span>
              <strong>Seçili Mutasyon:</strong> {highlightResidue.change} (Pozisyon: {highlightResidue.position})
            </span>
            <button
              onClick={() => {
                onClearHighlight && onClearHighlight();
                if (viewerRef.current) {
                  viewerRef.current.removeAllLabels();
                  applyStyling(viewerRef.current, renderStyle, colorScheme, showSurface);
                  viewerRef.current.zoomTo();
                }
              }}
              style={{
                background: 'rgba(0, 0, 0, 0.25)',
                border: 'none',
                color: '#fff',
                borderRadius: '6px',
                padding: '2px 8px',
                cursor: 'pointer',
                fontSize: '0.75rem'
              }}
            >
              Temizle
            </button>
          </div>
        )}

        {/* Custom Residue Jump Banner */}
        {activeCustomResidue && !highlightResidue && (
          <div style={{
            position: 'absolute',
            top: '16px',
            left: '16px',
            background: 'rgba(225, 29, 72, 0.9)',
            backdropFilter: 'blur(10px)',
            color: '#fff',
            padding: '8px 14px',
            borderRadius: '10px',
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            fontSize: '0.8rem',
            boxShadow: '0 4px 15px rgba(225, 29, 72, 0.4)',
            zIndex: 5
          }}>
            <Target size={16} />
            <span>
              <strong>Özel Kalıntı:</strong> Pozisyon {activeCustomResidue}
            </span>
            <button
              onClick={handleClearCustomResidue}
              style={{
                background: 'rgba(0, 0, 0, 0.25)',
                border: 'none',
                color: '#fff',
                borderRadius: '6px',
                padding: '2px 8px',
                cursor: 'pointer',
                fontSize: '0.75rem'
              }}
            >
              Temizle
            </button>
          </div>
        )}

        {/* Clicked Residue Tooltip */}
        {selectedResidueInfo && (
          <div style={{
            position: 'absolute',
            bottom: '16px',
            left: '16px',
            background: 'rgba(15, 23, 42, 0.85)',
            backdropFilter: 'blur(10px)',
            border: '1px solid var(--border-subtle)',
            borderRadius: '10px',
            padding: '8px 14px',
            fontSize: '0.8rem',
            color: 'var(--text-primary)',
            zIndex: 5
          }}>
            Kalıntı: <strong>{selectedResidueInfo.resn} {selectedResidueInfo.resi}</strong> (Zincir {selectedResidueInfo.chain}) • pLDDT Güven: <strong style={{ color: selectedResidueInfo.b >= 70 ? '#38bdf8' : '#fbbf24' }}>{selectedResidueInfo.b}</strong>
          </div>
        )}

        {/* pLDDT Legend overlay in bottom right */}
        <div style={{
          position: 'absolute',
          bottom: '16px',
          right: '16px',
          background: 'rgba(8, 12, 22, 0.85)',
          backdropFilter: 'blur(12px)',
          border: '1px solid var(--border-subtle)',
          borderRadius: '12px',
          padding: '10px 14px',
          fontSize: '0.75rem',
          zIndex: 5
        }}>
          <div style={{ fontWeight: 600, color: 'var(--text-secondary)', marginBottom: '6px' }}>
            AlphaFold Model Güveni (pLDDT)
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#0053d6' }}></span>
              <span>&gt; 90: Çok Yüksek</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#65cbf3' }}></span>
              <span>70 - 90: Güvenilir</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#ffdb13' }}></span>
              <span>50 - 70: Düşük</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '12px', height: '12px', borderRadius: '3px', background: '#ff7d45' }}></span>
              <span>&lt; 50: Çok Düşük (Düzensiz/IDR)</span>
            </div>
          </div>
        </div>
      </div>

      {/* Viewer Control Bar (Styles & Color Selection) */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
        padding: '12px 20px',
        background: 'rgba(10, 15, 28, 0.85)',
        borderTop: '1px solid var(--border-subtle)',
        fontSize: '0.8rem'
      }}>
        {/* Render Style Buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <span style={{ color: 'var(--text-muted)', marginRight: '4px' }}>Stil:</span>
          {['cartoon', 'stick', 'sphere'].map((style) => (
            <button
              key={style}
              onClick={() => setRenderStyle(style)}
              style={{
                padding: '4px 10px',
                borderRadius: '6px',
                background: renderStyle === style ? 'rgba(56, 189, 248, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                color: renderStyle === style ? '#38bdf8' : 'var(--text-secondary)',
                border: renderStyle === style ? '1px solid rgba(56, 189, 248, 0.4)' : '1px solid var(--border-subtle)',
                cursor: 'pointer',
                fontWeight: renderStyle === style ? 600 : 400,
                textTransform: 'capitalize'
              }}
            >
              {style === 'cartoon' ? 'Şerit (Ribbon)' : style === 'stick' ? 'Çubuk (Stick)' : 'Küre (Sphere)'}
            </button>
          ))}

          {/* Molecular Surface toggle */}
          <button
            onClick={() => setShowSurface(!showSurface)}
            style={{
              padding: '4px 10px',
              borderRadius: '6px',
              background: showSurface ? 'rgba(16, 185, 129, 0.2)' : 'rgba(255, 255, 255, 0.05)',
              color: showSurface ? '#34d399' : 'var(--text-secondary)',
              border: showSurface ? '1px solid rgba(16, 185, 129, 0.4)' : '1px solid var(--border-subtle)',
              cursor: 'pointer',
              marginLeft: '6px',
              display: 'flex',
              alignItems: 'center',
              gap: '4px'
            }}
          >
            <Layers size={13} />
            Moleküler Yüzey
          </button>
        </div>

        {/* Color Palette Selector */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
          <Palette size={14} style={{ color: 'var(--text-muted)' }} />
          <span style={{ color: 'var(--text-muted)', marginRight: '4px' }}>Renklendirme:</span>
          {[
            { id: 'plddt', label: 'AlphaFold pLDDT' },
            { id: 'rainbow', label: 'Spektrum (N-C)' },
            { id: 'ss', label: 'İkincil Yapı' }
          ].map((c) => (
            <button
              key={c.id}
              onClick={() => setColorScheme(c.id)}
              style={{
                padding: '4px 10px',
                borderRadius: '6px',
                background: colorScheme === c.id ? 'rgba(56, 189, 248, 0.2)' : 'rgba(255, 255, 255, 0.05)',
                color: colorScheme === c.id ? '#38bdf8' : 'var(--text-secondary)',
                border: colorScheme === c.id ? '1px solid rgba(56, 189, 248, 0.4)' : '1px solid var(--border-subtle)',
                cursor: 'pointer',
                fontWeight: colorScheme === c.id ? 600 : 400
              }}
            >
              {c.label}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
