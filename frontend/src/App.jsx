import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import ProteinOverview from './components/ProteinOverview';
import ProteinViewer3D from './components/ProteinViewer3D';
import AlphaFoldConfidenceCard from './components/AlphaFoldConfidenceCard';
import ProteinDomainMap from './components/ProteinDomainMap';
import AISummaryCard from './components/AISummaryCard';
import DiseaseSpectrumSection from './components/DiseaseSpectrumSection';
import MutationTable from './components/MutationTable';
import LiteratureSection from './components/LiteratureSection';
import { Sparkles, Dna, GitPullRequest, ArrowRight, ShieldCheck, Database, Cpu, Compass } from 'lucide-react';

export default function App() {
  const [lang, setLang] = useState(() => {
    try {
      return localStorage.getItem('biolens_lang') || 'en';
    } catch {
      return 'en';
    }
  });
  const [currentQuery, setCurrentQuery] = useState('TP53');
  const [proteinData, setProteinData] = useState(null);
  const [examples, setExamples] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [highlightResidue, setHighlightResidue] = useState(null);
  const [showRoadmapModal, setShowRoadmapModal] = useState(false);

  const handleToggleLang = (nextLang) => {
    setLang(nextLang);
    try {
      localStorage.setItem('biolens_lang', nextLang);
    } catch {}
  };

  // Fetch examples on mount
  useEffect(() => {
    async function loadExamples() {
      try {
        const res = await fetch('/api/examples');
        if (res.ok) {
          const data = await res.json();
          setExamples(data);
        }
      } catch (e) {
        console.error('Failed to load examples:', e);
      }
    }
    loadExamples();
  }, []);

  // Fetch protein data
  const fetchProtein = async (query, displayLabel = null) => {
    const cleanQuery = (query || '').trim();
    if (!cleanQuery) return;
    setLoading(true);
    setError(null);
    setHighlightResidue(null);
    if (displayLabel) {
      setCurrentQuery(displayLabel);
    }
    try {
      const res = await fetch(`/api/protein/${encodeURIComponent(cleanQuery)}`);
      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || `'${displayLabel || cleanQuery}' bulunamadı. Lütfen geçerli bir gen adı veya accession girin.`);
      }
      const data = await res.json();
      setProteinData(data);
      setCurrentQuery(data.geneSymbol || displayLabel || cleanQuery);
    } catch (err) {
      console.error('Fetch protein error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProtein(currentQuery);
  }, []);

  const handleSelectMutationResidue = (item) => {
    setHighlightResidue(item);
    // Smooth scroll to 3D viewer if on mobile
    window.scrollTo({ top: 180, behavior: 'smooth' });
  };

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Top Header */}
      <Header
        onSearch={fetchProtein}
        currentQuery={currentQuery}
        loading={loading}
        examples={examples}
        lang={lang}
        onChangeLang={handleToggleLang}
      />

      {/* Main Content Area */}
      <main style={{ flex: 1, maxWidth: '1440px', width: '100%', margin: '0 auto', padding: '24px' }}>
        {/* Loading Overlay */}
        {loading && (
          <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            gap: '16px',
            padding: '80px 20px'
          }}>
            <div style={{
              width: '50px',
              height: '50px',
              borderRadius: '50%',
              border: '3px solid rgba(56, 189, 248, 0.2)',
              borderTopColor: '#38bdf8',
              animation: 'spinSlow 1s linear infinite'
            }}></div>
            <div style={{ textAlign: 'center' }}>
              <h3 style={{ fontSize: '1.2rem', fontWeight: 600, color: '#f8fafc' }}>
                {lang === 'en'
                  ? `Compiling Scientific Data for ${currentQuery}...`
                  : `${currentQuery} Bilimsel Verileri Derleniyor...`}
              </h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                {lang === 'en'
                  ? 'Fetching multi-source data from UniProt, AlphaFold DB, ClinVar & PubMed APIs and synthesizing biomedical summary.'
                  : "UniProt, AlphaFold DB, ClinVar ve PubMed API'lerinden veri toplanıp Türkçe özet hazırlanıyor."}
              </p>
            </div>
          </div>
        )}

        {/* Error State */}
        {error && !loading && (
          <div className="glass-panel" style={{
            padding: '36px',
            textAlign: 'center',
            maxWidth: '600px',
            margin: '40px auto',
            border: '1px solid rgba(244, 63, 94, 0.3)'
          }}>
            <div style={{
              width: '48px',
              height: '48px',
              borderRadius: '50%',
              background: 'rgba(244, 63, 94, 0.15)',
              color: '#fb7185',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              margin: '0 auto 16px'
            }}>
              !
            </div>
            <h3 style={{ fontSize: '1.15rem', color: '#f8fafc', marginBottom: '8px' }}>
              {lang === 'en' ? 'Protein Not Found' : 'Protein Bulunamadı'}
            </h3>
            <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: '20px' }}>
              {error}
            </p>
            <div style={{ display: 'flex', justifyContent: 'center', gap: '10px' }}>
              <button
                onClick={() => fetchProtein('TP53')}
                style={{
                  background: 'linear-gradient(135deg, #0ea5e9, #2563eb)',
                  color: '#fff',
                  border: 'none',
                  borderRadius: '8px',
                  padding: '8px 16px',
                  fontSize: '0.85rem',
                  fontWeight: 600,
                  cursor: 'pointer'
                }}
              >
                {lang === 'en' ? 'Continue with TP53' : 'TP53 ile Devam Et'}
              </button>
            </div>
          </div>
        )}

        {/* Dashboard Display */}
        {proteinData && !loading && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
            {/* Top Row: Overview + 3D Structure Viewer + AlphaFold Confidence */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
              gap: '24px'
            }}>
              {/* Left Column: Protein Overview & AlphaFold Confidence Score */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
                <ProteinOverview 
                  protein={proteinData.uniprot} 
                  fullData={proteinData}
                  lang={lang}
                />
                <AlphaFoldConfidenceCard
                  alphafold={proteinData.alphafold}
                  accession={proteinData.accession}
                  lang={lang}
                />
              </div>

              {/* Right Column: Interactive 3Dmol.js Viewer */}
              <div>
                <ProteinViewer3D
                  accession={proteinData.accession}
                  geneSymbol={proteinData.geneSymbol}
                  plddtScore={proteinData.alphafold?.globalMetricValue}
                  highlightResidue={highlightResidue}
                  onClearHighlight={() => setHighlightResidue(null)}
                  lang={lang}
                />
              </div>
            </div>

            {/* 1D Functional Domain Architecture, Mutation Lollipop Track & Biophysical Profile */}
            <ProteinDomainMap
              protein={proteinData.uniprot}
              clinvarVariants={proteinData.clinvar}
              onSelectResidue={handleSelectMutationResidue}
              activeResidue={highlightResidue}
              lang={lang}
            />

            {/* Middle Row: Biomedical AI Summary Card */}
            <AISummaryCard
              aiSummary={proteinData.aiSummary}
              geneSymbol={proteinData.geneSymbol}
              lang={lang}
            />

            {/* Comprehensive Clinical Disease Spectrum, Syndromes & Pathophysiology */}
            <DiseaseSpectrumSection
              diseaseProfile={proteinData.diseaseProfile}
              geneSymbol={proteinData.geneSymbol}
              onSelectResidue={handleSelectMutationResidue}
              lang={lang}
            />

            {/* Bottom Row: ClinVar Mutations & Scientific Literature */}
            <div style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))',
              gap: '24px'
            }}>
              <MutationTable
                clinvarVariants={proteinData.clinvar}
                uniprotVariants={proteinData.uniprot?.variants}
                onSelectResidue={handleSelectMutationResidue}
                activeResidue={highlightResidue}
                lang={lang}
              />

              <LiteratureSection
                literature={proteinData.literature}
                geneSymbol={proteinData.geneSymbol}
                lang={lang}
              />
            </div>
          </div>
        )}
      </main>

      {/* Floating Roadmap / Architecture Button */}
      <button
        onClick={() => setShowRoadmapModal(true)}
        style={{
          position: 'fixed',
          bottom: '24px',
          right: '24px',
          background: 'linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)',
          color: '#fff',
          border: 'none',
          borderRadius: '9999px',
          padding: '12px 20px',
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          boxShadow: '0 8px 24px rgba(14, 165, 233, 0.4)',
          cursor: 'pointer',
          fontWeight: 600,
          fontSize: '0.85rem',
          zIndex: 40,
          transition: 'all 0.2s'
        }}
      >
        <Compass size={18} />
        <span>{lang === 'en' ? 'Development Roadmap & Architecture' : 'Geliştirme Yol Haritası & Mimari'}</span>
      </button>

      {/* Roadmap Modal */}
      {showRoadmapModal && (
        <div style={{
          position: 'fixed',
          inset: 0,
          background: 'rgba(0, 0, 0, 0.75)',
          backdropFilter: 'blur(8px)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '20px',
          zIndex: 100
        }}>
          <div className="glass-panel" style={{
            maxWidth: '780px',
            width: '100%',
            maxHeight: '90vh',
            overflowY: 'auto',
            padding: '30px',
            background: '#0a0f1d'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
              <div>
                <h3 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#f8fafc' }}>
                  {lang === 'en' ? 'BioLens AI System Architecture & Roadmap' : 'BioLens AI Sistem Mimarisi & Yol Haritası'}
                </h3>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>
                  {lang === 'en' ? 'Computational Biology & Deep Learning Integration Plan' : 'Hesaplamalı Biyoloji & Derin Öğrenme Entegrasyon Planı'}
                </p>
              </div>
              <button
                onClick={() => setShowRoadmapModal(false)}
                style={{
                  background: 'rgba(255, 255, 255, 0.08)',
                  border: 'none',
                  color: '#fff',
                  borderRadius: '50%',
                  width: '32px',
                  height: '32px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center'
                }}
              >
                ✕
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
              <div style={{
                background: 'rgba(16, 185, 129, 0.1)',
                border: '1px solid rgba(16, 185, 129, 0.3)',
                borderRadius: '12px',
                padding: '16px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#34d399', fontWeight: 600, marginBottom: '6px' }}>
                  <ShieldCheck size={18} />
                  <span>{lang === 'en' ? 'Phase 1: Data Aggregator & API (Active)' : 'Faz 1: Veri Toplayıcı & API (Aktif)'}</span>
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {lang === 'en'
                    ? 'FastAPI backend connected to UniProt REST, AlphaFold DB, ClinVar, and Europe PMC endpoints with automatic ID resolution and PDB coordinate streaming.'
                    : 'FastAPI backend ile UniProt REST, AlphaFold DB, ClinVar ve Europe PMC uç noktaları bağlandı. Otomatik ID çözümleme ve PDB streaming aktiftir.'}
                </p>
              </div>

              <div style={{
                background: 'rgba(56, 189, 248, 0.1)',
                border: '1px solid rgba(56, 189, 248, 0.3)',
                borderRadius: '12px',
                padding: '16px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#38bdf8', fontWeight: 600, marginBottom: '6px' }}>
                  <Dna size={18} />
                  <span>{lang === 'en' ? 'Phase 2: 3D Molecular Interface & Client (Active)' : 'Faz 2: 3D Arayüz & İstemci (Aktif)'}</span>
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {lang === 'en'
                    ? 'React + 3Dmol.js WebGL integration with pLDDT confidence coloring, ribbon/surface/sphere styles, and interactive residue focusing from the clinical mutation table.'
                    : 'React + 3Dmol.js entegrasyonu; pLDDT renk kodlaması, şerit/yüzey/küre stilleri ve mutasyon tablosundan 3B yapıda doğrudan kalıntı işaretleme (focus & label).'}
                </p>
              </div>

              <div style={{
                background: 'rgba(168, 85, 247, 0.1)',
                border: '1px solid rgba(168, 85, 247, 0.3)',
                borderRadius: '12px',
                padding: '16px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#c084fc', fontWeight: 600, marginBottom: '6px' }}>
                  <Sparkles size={18} />
                  <span>{lang === 'en' ? 'Phase 3: Biomedical Intelligence Layer (Active)' : 'Faz 3: Zekâ Katmanı (Aktif)'}</span>
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {lang === 'en'
                    ? 'PubMed/Europe PMC literature mining + bilingual AI biomedical synthesis engine combining biological function, clinical impact, and structural analysis.'
                    : 'PubMed/Europe PMC literatür analizi + Türkçe Biyomedikal Yapay Zekâ özetleyici motoru. Biyolojik rol, klinik etki ve yapısal analiz sentezi.'}
                </p>
              </div>

              <div style={{
                background: 'rgba(245, 158, 11, 0.1)',
                border: '1px solid rgba(245, 158, 11, 0.3)',
                borderRadius: '12px',
                padding: '16px'
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#fbbf24', fontWeight: 600, marginBottom: '6px' }}>
                  <Cpu size={18} />
                  <span>{lang === 'en' ? 'Next Step: ESM-2 Protein Language Model (Upcoming)' : 'Sonraki Adım: ESM-2 Protein Dil Modeli (İleri Aşama)'}</span>
                </div>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  {lang === 'en'
                    ? "Integration of Meta AI's ESM-2 (Evolutionary Scale Modeling) protein language model for zero-shot log-likelihood variant effect prediction on custom amino acid substitutions."
                    : "Meta AI'nin ESM-2 (Evolutionary Scale Modeling) protein dil modelini ekleyerek; kullanıcının girdiği özel amino asit değişiminde log-likelihood skoruyla \"Zero-shot variant effect\" tahmini yapma servisi."}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <footer style={{
        borderTop: '1px solid var(--border-subtle)',
        background: 'rgba(6, 9, 17, 0.95)',
        padding: '24px',
        marginTop: '40px',
        textAlign: 'center'
      }}>
        <div style={{ maxWidth: '1440px', margin: '0 auto', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px' }}>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
            <strong>BioLens AI</strong> • {lang === 'en' ? 'Computational Biology & Protein Research Platform' : 'Hesaplamalı Biyoloji & Protein Araştırma Platformu'}
          </p>
          <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
            AlphaFold EBI Database • UniProtKB • NCBI ClinVar • Europe PMC / PubMed
          </p>
        </div>
      </footer>
    </div>
  );
}
