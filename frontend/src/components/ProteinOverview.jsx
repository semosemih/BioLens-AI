import React, { useState } from 'react';
import { Dna, MapPin, Tag, Copy, Check, ChevronDown, ChevronUp, Layers, FileDown } from 'lucide-react';

export default function ProteinOverview({ protein, fullData }) {
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

  const handleExportReport = () => {
    const dateStr = new Date().toLocaleDateString('tr-TR', { year: 'numeric', month: 'long', day: 'numeric' });
    const gene = geneSymbol || accession;

    let report = `# 🧬 BioLens AI Biyomedikal Araştırma Raporu: ${gene}\n\n`;
    report += `> **Oluşturulma Tarihi:** ${dateStr}  \n`;
    report += `> **Rapor Kaynağı:** BioLens AI (Hesaplamalı Biyoloji & Yapısal Genomik Platformu)\n\n`;
    report += `---\n\n`;

    // 1. Genel Tanımlayıcılar
    report += `## 📋 1. Genel Bilgiler ve Tanımlayıcılar\n\n`;
    report += `- **Gen Sembolü:** \`${geneSymbol}\`\n`;
    report += `- **UniProt Accession:** [${accession}](https://www.uniprot.org/uniprotkb/${accession})\n`;
    report += `- **Protein Adı:** ${proteinName}\n`;
    report += `- **Organizma:** ${organism} (${commonOrganism || 'Belirtilmemiş'})\n`;
    report += `- **Dizi Uzunluğu:** ${length} amino asit\n`;
    report += `- **Moleküler Kütle:** ${mass ? (mass / 1000).toFixed(1) + ' kDa' : 'Bilinmiyor'}\n\n`;

    // 2. Biyolojik İşlev ve Hücresel Konum
    report += `## 🔬 2. Biyolojik İşlev ve Gen Ontolojisi (GO)\n\n`;
    if (functions && functions.length > 0) {
      report += `### Birincil Biyolojik İşlev\n${functions.join('\n\n')}\n\n`;
    }
    if (subcellularLocations && subcellularLocations.length > 0) {
      report += `### Hücresel Yerleşim\n${subcellularLocations.map(l => `- ${l}`).join('\n')}\n\n`;
    }
    if (goTerms && goTerms.biologicalProcess && goTerms.biologicalProcess.length > 0) {
      report += `### Gen Ontolojisi (Biyolojik Süreçler)\n`;
      report += goTerms.biologicalProcess.slice(0, 8).map(t => `- **${t.name}** (\`${t.id}\`)`).join('\n') + '\n\n';
    }

    // 3. AlphaFold 3B Yapı Analizi
    if (fullData?.alphafold) {
      const af = fullData.alphafold;
      report += `## 📐 3. AlphaFold 3B Yapısal Tahmin Analizi\n\n`;
      report += `- **Global Ortalama pLDDT Güven Skoru:** **${af.globalMetricValue || '--'}** / 100 (${af.confidenceTier || 'Bilinmiyor'})\n`;
      report += `- **AlphaFold DB Model Kodu:** \`${af.entryId || 'AF-' + accession + '-F1'}\`\n`;
      report += `- **PDB Koordinat Bağlantısı:** [AlphaFold DB PDB Dosyası](${af.pdbUrl || '#'})\n\n`;
    }

    // 4. Klinik Mutasyonlar (ClinVar)
    if (fullData?.clinvar && fullData.clinvar.length > 0) {
      report += `## ⚠️ 4. Klinik Olarak Bildirilen Patojenik Mutasyonlar (ClinVar)\n\n`;
      report += `| Pozisyon | Mutasyon / Değişim | Klinik Önem | İlişkili Hastalık / Klinik Durum |\n`;
      report += `| :---: | :--- | :--- | :--- |\n`;
      fullData.clinvar.slice(0, 15).forEach(v => {
        const pos = v.position || '-';
        const change = v.proteinChange || v.title || '-';
        const sig = v.clinicalSignificance || 'Pathogenic';
        const dis = (v.conditions && v.conditions.length > 0) ? v.conditions.join(', ') : 'Belirtilmemiş';
        report += `| ${pos} | ${change} | ${sig} | ${dis} |\n`;
      });
      report += `\n*Not: Toplam ${fullData.clinvar.length} ClinVar varyantı tespit edilmiştir; raporda ilk 15 varyant listelenmiştir.*\n\n`;
    }

    // 5. Biyomedikal Yapay Zekâ Analizi
    if (fullData?.aiSummary) {
      report += `## 🤖 5. Biyomedikal Yapay Zekâ Sentezi (Türkçe)\n\n`;
      const ai = fullData.aiSummary;
      if (ai.sections) {
        if (ai.sections.biologicalRole) report += `### 🧬 Temel Biyolojik Rol\n${ai.sections.biologicalRole}\n\n`;
        if (ai.sections.clinicalSignificance) report += `### ⚠️ Hastalık ve Klinik İlişkisi\n${ai.sections.clinicalSignificance}\n\n`;
        if (ai.sections.structureAnalysis) report += `### 🔬 3B Yapı ve AlphaFold Analizi\n${ai.sections.structureAnalysis}\n\n`;
        if (ai.sections.mutationInsights) report += `### ⚡ Öne Çıkan Mutasyon ve Literatür Bulguları\n${ai.sections.mutationInsights}\n\n`;
      } else if (ai.content) {
        report += `${ai.content}\n\n`;
      }
    }

    // 6. Bilimsel Literatür
    if (fullData?.literature && fullData.literature.length > 0) {
      report += `## 📚 6. Hakemli Bilimsel Literatür (Europe PMC / PubMed)\n\n`;
      fullData.literature.slice(0, 5).forEach((paper, i) => {
        report += `### ${i + 1}. ${paper.title}\n`;
        report += `- **Yazarlar:** ${paper.authorString || 'Belirtilmemiş'}\n`;
        report += `- **Dergi & Yıl:** *${paper.journalTitle || 'Bilinmiyor'}* (${paper.pubYear || '--'})\n`;
        report += `- **Atıf Sayısı:** ${paper.citedByCount || 0}\n`;
        if (paper.doi) report += `- **DOI:** https://doi.org/${paper.doi}\n`;
        if (paper.abstractText) report += `\n> **Özet:** ${paper.abstractText.substring(0, 350)}...\n`;
        report += `\n`;
      });
    }

    // 7. FASTA
    report += `## 🧬 7. FASTA Dizi Koordinatı\n\n`;
    report += `\`\`\`fasta\n>${accession}|${geneSymbol}|${proteinName} [${organism}]\n${sequence}\n\`\`\`\n\n`;
    report += `---\n*Bu rapor BioLens AI Otomatik Biyomedikal Analiz Sistemi tarafından oluşturulmuştur.*`;

    // Download file
    const blob = new Blob([report], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${gene}_BioLens_Arastirma_Raporu.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
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

        {/* Action Buttons: FASTA & Export Report */}
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
          <button
            onClick={handleExportReport}
            title="Kapsamlı Araştırma Raporunu Markdown formatında indir"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              background: 'rgba(56, 189, 248, 0.12)',
              border: '1px solid rgba(56, 189, 248, 0.3)',
              borderRadius: '8px',
              padding: '8px 14px',
              color: '#38bdf8',
              fontSize: '0.8rem',
              fontWeight: 500,
              cursor: 'pointer',
              transition: 'all 0.2s'
            }}
          >
            <FileDown size={15} />
            <span>Raporu İndir (.md)</span>
          </button>

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
