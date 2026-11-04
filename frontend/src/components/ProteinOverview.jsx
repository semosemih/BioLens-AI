import React, { useState } from 'react';
import { Dna, MapPin, Tag, Copy, Check, ChevronDown, ChevronUp, Layers, FileDown, GitBranch, Zap } from 'lucide-react';

export default function ProteinOverview({ protein, fullData, lang = 'en' }) {
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
    pathways,
    goTerms,
    functions,
    structuralFeatures
  } = protein;

  const handleCopyFasta = () => {
    const fasta = `>${accession}|${geneSymbol}|${proteinName} [${organism}]\n${sequence}`;
    navigator.clipboard.writeText(fasta);
    setCopiedFasta(true);
    setTimeout(() => setCopiedFasta(false), 2000);
  };

  const handleExportReport = () => {
    const isEn = lang === 'en';
    const dateStr = new Date().toLocaleDateString(isEn ? 'en-US' : 'tr-TR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
    const gene = geneSymbol || accession;

    let report = isEn
      ? `# 🧬 BioLens AI Biomedical Research Report: ${gene}\n\n`
      : `# 🧬 BioLens AI Biyomedikal Araştırma Raporu: ${gene}\n\n`;
    report += isEn
      ? `> **Generated On:** ${dateStr}  \n> **Source:** BioLens AI (Computational Biology & Structural Genomics Platform)\n\n---\n\n`
      : `> **Oluşturulma Tarihi:** ${dateStr}  \n> **Rapor Kaynağı:** BioLens AI (Hesaplamalı Biyoloji & Yapısal Genomik Platformu)\n\n---\n\n`;

    // 1. General Identifiers
    report += isEn
      ? `## 📋 1. General Overview & Identifiers\n\n`
      : `## 📋 1. Genel Bilgiler ve Tanımlayıcılar\n\n`;
    report += `- **${isEn ? 'Gene Symbol' : 'Gen Sembolü'}:** \`${geneSymbol}\`\n`;
    report += `- **UniProt Accession:** [${accession}](https://www.uniprot.org/uniprotkb/${accession})\n`;
    report += `- **${isEn ? 'Protein Name' : 'Protein Adı'}:** ${proteinName}\n`;
    report += `- **${isEn ? 'Organism' : 'Organizma'}:** ${organism} (${commonOrganism || (isEn ? 'Unspecified' : 'Belirtilmemiş')})\n`;
    report += `- **${isEn ? 'Sequence Length' : 'Dizi Uzunluğu'}:** ${length} ${isEn ? 'amino acids' : 'amino asit'}\n`;
    report += `- **${isEn ? 'Molecular Mass' : 'Moleküler Kütle'}:** ${mass ? (mass / 1000).toFixed(1) + ' kDa' : (isEn ? 'Unknown' : 'Bilinmiyor')}\n\n`;

    // 2. Biological Function & GO
    report += isEn
      ? `## 🔬 2. Biological Function, Pathways & Gene Ontology (GO)\n\n`
      : `## 🔬 2. Biyolojik İşlev, Yolaklar ve Gen Ontolojisi (GO)\n\n`;
    if (functions && functions.length > 0) {
      report += `### ${isEn ? 'Primary Biological Function' : 'Birincil Biyolojik İşlev'}\n${functions.join('\n\n')}\n\n`;
    }
    if (subcellularLocations && subcellularLocations.length > 0) {
      report += `### ${isEn ? 'Subcellular Localization' : 'Hücresel Yerleşim'}\n${subcellularLocations.map(l => `- ${l}`).join('\n')}\n\n`;
    }
    if (pathways && pathways.length > 0) {
      report += `### ${isEn ? 'Biological Pathways (Reactome / UniProt)' : 'Biyolojik Sinyal Yolakları (Reactome / UniProt)'}\n${pathways.map(p => `- ${p}`).join('\n')}\n\n`;
    }
    if (goTerms && goTerms.biologicalProcess && goTerms.biologicalProcess.length > 0) {
      report += `### ${isEn ? 'Gene Ontology (Biological Processes)' : 'Gen Ontolojisi (Biyolojik Süreçler)'}\n`;
      report += goTerms.biologicalProcess.slice(0, 8).map(t => `- **${t.name}** (\`${t.id}\`)`).join('\n') + '\n\n';
    }
    if (structuralFeatures && structuralFeatures.length > 0) {
      report += `### ${isEn ? 'Structural Domains & Functional Sites' : 'Yapısal Domainler ve Fonksiyonel Bölgeler'}\n`;
      report += structuralFeatures.slice(0, 15).map(f => `- **${f.type}** (${f.start}-${f.end}): ${f.description}`).join('\n') + '\n\n';
    }

    // 3. AlphaFold 3D Structure Analysis
    if (fullData?.alphafold) {
      const af = fullData.alphafold;
      const tier = isEn ? (af.confidenceTierEn || af.confidenceTier) : af.confidenceTier;
      report += isEn
        ? `## 📐 3. AlphaFold 3D Structural Prediction Analysis\n\n`
        : `## 📐 3. AlphaFold 3B Yapısal Tahmin Analizi\n\n`;
      report += `- **${isEn ? 'Global Mean pLDDT Confidence Score' : 'Global Ortalama pLDDT Güven Skoru'}:** **${af.globalMetricValue || '--'}** / 100 (${tier || '--'})\n`;
      report += `- **${isEn ? 'AlphaFold DB Model ID' : 'AlphaFold DB Model Kodu'}:** \`${af.entryId || 'AF-' + accession + '-F1'}\`\n`;
      report += `- **${isEn ? 'PDB Coordinates Link' : 'PDB Koordinat Bağlantısı'}:** [AlphaFold DB PDB](${af.pdbUrl || '#'})\n\n`;
    }

    // 4. Comprehensive Clinical Disease Spectrum
    if (fullData?.diseaseProfile?.diseases && fullData.diseaseProfile.diseases.length > 0) {
      const dp = fullData.diseaseProfile;
      report += isEn
        ? `## 🩺 4. Comprehensive Clinical Disease Spectrum & Pathophysiology (${dp.diseases.length} Conditions)\n\n`
        : `## 🩺 4. Kapsamlı Klinik Hastalık Spektrumu ve Patofizyoloji (${dp.diseases.length} Hastalık)\n\n`;
      dp.diseases.forEach((d, i) => {
        const dTitle = isEn ? (d.englishName || d.name) : d.name;
        const dCat = isEn ? (d.categoryEn || d.primarySpecialtyEn || d.category) : d.category;
        const dInh = isEn ? (d.inheritanceEn || d.inheritance) : d.inheritance;
        const dPath = isEn ? (d.pathophysiologyEn || d.pathophysiology) : d.pathophysiology;
        const dMgmt = isEn ? (d.clinicalManagementEn || d.clinicalManagement) : d.clinicalManagement;

        report += `### 4.${i + 1}. ${dTitle}${d.acronym ? ` (${d.acronym})` : ''}\n`;
        report += `- **${isEn ? 'Medical Specialty' : 'Tıbbi Branş'}:** ${dCat || (isEn ? 'Clinical Pathology' : 'Klinik Patoloji')}\n`;
        if (dInh) report += `- **${isEn ? 'Inheritance / Mechanism' : 'Kalıtım / Genetik Mekanizma'}:** ${dInh}\n`;
        if (d.omimId) report += `- **OMIM:** [OMIM #${d.omimId}](https://www.omim.org/entry/${d.omimId})\n`;
        if (d.orphaId) report += `- **Orphanet:** [ORPHA:${d.orphaId}](https://www.orpha.net/en/disease/detail/${d.orphaId})\n`;
        if (dPath) report += `- **${isEn ? 'Pathophysiology & Clinical Presentation' : 'Patofizyoloji & Klinik Tablo'}:** ${dPath}\n`;
        if (dMgmt) report += `- **${isEn ? 'Clinical Management & Targeted Therapy' : 'Klinik Yaklaşım & Hedefli Tedavi'}:** ${dMgmt}\n`;
        if (d.relatedMutations && d.relatedMutations.length > 0) {
          report += `- **${isEn ? 'Associated Variants' : 'İlişkili Varyantlar'}:** \`${d.relatedMutations.join('`, `')}\`\n`;
        }
        report += `\n`;
      });
    }

    // 5. Clinical Variants (ClinVar)
    if (fullData?.clinvar && fullData.clinvar.length > 0) {
      report += isEn
        ? `## ⚠️ 5. Clinically Reported Pathogenic Variants (ClinVar)\n\n| Position | Variant / Change | Clinical Significance | Associated Condition |\n| :---: | :--- | :--- | :--- |\n`
        : `## ⚠️ 5. Klinik Olarak Bildirilen Patojenik Mutasyonlar (ClinVar)\n\n| Pozisyon | Mutasyon / Değişim | Klinik Önem | İlişkili Hastalık / Klinik Durum |\n| :---: | :--- | :--- | :--- |\n`;
      fullData.clinvar.slice(0, 20).forEach(v => {
        const pos = v.position || '-';
        const change = v.proteinChange || v.title || '-';
        const sig = v.clinicalSignificance || 'Pathogenic';
        const dis = (v.conditions && v.conditions.length > 0) ? v.conditions.join(', ') : (isEn ? 'Unspecified' : 'Belirtilmemiş');
        report += `| ${pos} | ${change} | ${sig} | ${dis} |\n`;
      });
      report += isEn
        ? `\n*Note: Total ${fullData.clinvar.length} ClinVar variants identified.*\n\n`
        : `\n*Not: Toplam ${fullData.clinvar.length} ClinVar varyantı tespit edilmiştir.*\n\n`;
    }

    // 6. Biomedical AI Analysis
    if (fullData?.aiSummary) {
      report += isEn
        ? `## 🤖 6. Biomedical AI Synthesis\n\n`
        : `## 🤖 6. Biyomedikal Yapay Zekâ Sentezi\n\n`;
      const ai = fullData.aiSummary;
      const sectionsToUse = (isEn && Array.isArray(ai.sectionsEn)) ? ai.sectionsEn : ai.sections;
      if (Array.isArray(sectionsToUse)) {
        sectionsToUse.forEach(sec => {
          report += `### ${sec.title}\n`;
          (sec.items || []).forEach(it => {
            report += `- ${it}\n`;
          });
          report += `\n`;
        });
      } else if (ai.content) {
        report += `${ai.content}\n\n`;
      }
    }

    // 7. Scientific Literature (Fixed field names: authors, journal, year, citations, abstract, url)
    if (fullData?.literature && fullData.literature.length > 0) {
      report += isEn
        ? `## 📚 7. Peer-Reviewed Scientific Literature (Europe PMC / PubMed)\n\n`
        : `## 📚 7. Hakemli Bilimsel Literatür (Europe PMC / PubMed)\n\n`;
      fullData.literature.slice(0, 5).forEach((paper, i) => {
        const authors = paper.authors || paper.authorString || (isEn ? 'Unspecified' : 'Belirtilmemiş');
        const journal = paper.journal || paper.journalTitle || (isEn ? 'Unknown' : 'Bilinmiyor');
        const year = paper.year || paper.pubYear || '--';
        const citations = paper.citations ?? paper.citedByCount ?? 0;
        const abstract = paper.abstract || paper.abstractText || '';

        report += `### ${i + 1}. ${paper.title}\n`;
        report += `- **${isEn ? 'Authors' : 'Yazarlar'}:** ${authors}\n`;
        report += `- **${isEn ? 'Journal & Year' : 'Dergi & Yıl'}:** *${journal}* (${year})\n`;
        report += `- **${isEn ? 'Citations' : 'Atıf Sayısı'}:** ${citations}\n`;
        if (paper.url) report += `- **URL:** ${paper.url}\n`;
        else if (paper.doi) report += `- **DOI:** https://doi.org/${paper.doi}\n`;
        if (abstract) report += `\n> **${isEn ? 'Abstract' : 'Özet'}:** ${abstract.substring(0, 400)}${abstract.length > 400 ? '...' : ''}\n`;
        report += `\n`;
      });
    }

    // 8. FASTA
    report += isEn
      ? `## 🧬 8. FASTA Sequence\n\n`
      : `## 🧬 8. FASTA Dizi Koordinatı\n\n`;
    report += `\`\`\`fasta\n>${accession}|${geneSymbol}|${proteinName} [${organism}]\n${sequence}\n\`\`\`\n\n`;
    report += isEn
      ? `---\n*Generated automatically by BioLens AI Biomedical Analysis System.*`
      : `---\n*Bu rapor BioLens AI Otomatik Biyomedikal Analiz Sistemi tarafından oluşturulmuştur.*`;

    // Download file
    const blob = new Blob([report], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = isEn ? `${gene}_BioLens_Research_Report.md` : `${gene}_BioLens_Arastirma_Raporu.md`;
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
            {organism} • {length} {lang === 'en' ? 'Amino Acids' : 'Amino Asit'} • {(mass ? (mass / 1000).toFixed(1) + ' kDa' : '--')}
          </p>
        </div>

        {/* Action Buttons: FASTA & Export Report */}
        <div style={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: '8px' }}>
          <button
            onClick={handleExportReport}
            title={lang === 'en' ? 'Download comprehensive research report in Markdown format' : 'Kapsamlı Araştırma Raporunu Markdown formatında indir'}
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
            <span>{lang === 'en' ? 'Download Report (.md)' : 'Raporu İndir (.md)'}</span>
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
            <span>{lang === 'en' ? 'FASTA Sequence' : 'FASTA Dizisi'}</span>
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
              {copiedFasta
                ? (lang === 'en' ? 'Copied' : 'Kopyalandı')
                : (lang === 'en' ? 'Copy' : 'Kopyala')}
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
            {lang === 'en' ? 'Biological Function' : 'Biyolojik İşlev Açıklaması'}
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
            {lang === 'en' ? 'Subcellular Location' : 'Hücresel Yerleşim (Subcellular Location)'}
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

      {/* Biological Pathways (Reactome / UniProt) */}
      {pathways && pathways.length > 0 && (
        <div style={{ marginBottom: '18px' }}>
          <h4 style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <GitBranch size={14} />
            {lang === 'en' ? 'Signaling & Metabolic Pathways (Reactome)' : 'Sinyal & Metabolik Yolaklar (Reactome)'}
          </h4>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
            {pathways.slice(0, 5).map((pw, idx) => (
              <span
                key={idx}
                style={{
                  background: 'rgba(14, 165, 233, 0.1)',
                  border: '1px solid rgba(14, 165, 233, 0.25)',
                  color: '#7dd3fc',
                  padding: '4px 10px',
                  borderRadius: '8px',
                  fontSize: '0.76rem'
                }}
              >
                {pw}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Gene Ontology (GO) Processes & Molecular Functions */}
      {goTerms && (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
          {goTerms.biologicalProcess && goTerms.biologicalProcess.length > 0 && (
            <div>
              <h4 style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Layers size={14} />
                {lang === 'en' ? 'Gene Ontology (Biological Processes)' : 'Gen Ontolojisi (Biyolojik Süreçler)'}
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {goTerms.biologicalProcess.slice(0, 6).map((term, idx) => (
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

          {goTerms.molecularFunction && goTerms.molecularFunction.length > 0 && (
            <div>
              <h4 style={{ fontSize: '0.82rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.04em', marginBottom: '8px', display: 'flex', alignItems: 'center', gap: '6px' }}>
                <Zap size={14} />
                {lang === 'en' ? 'Molecular Functions (GO)' : 'Moleküler İşlevler (GO)'}
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                {goTerms.molecularFunction.slice(0, 5).map((term, idx) => (
                  <span
                    key={idx}
                    style={{
                      background: 'rgba(245, 158, 11, 0.1)',
                      border: '1px solid rgba(245, 158, 11, 0.22)',
                      color: '#fcd34d',
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
      )}
    </div>
  );
}
