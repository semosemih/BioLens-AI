import os
from typing import Dict, Any, List, Optional

def generate_turkish_summary(
    protein_data: Dict[str, Any],
    alphafold_data: Optional[Dict[str, Any]],
    clinvar_variants: List[Dict[str, Any]],
    literature: List[Dict[str, Any]],
    disease_profile: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Synthesizes complex biochemical data, comprehensive clinical disease spectrum,
    literature abstracts, and AlphaFold predictions into a clear, structured Turkish biomedical briefing.
    Supports Google Gemini if API key is provided, with an intelligent biomedical domain synthesizer fallback.
    """
    gene = protein_data.get("geneSymbol", "")
    protein_name = protein_data.get("proteinName", "")
    functions = protein_data.get("functions", [])
    diseases = protein_data.get("diseases", [])
    variants = protein_data.get("variants", [])
    go_bp = [p["name"] for p in protein_data.get("goTerms", {}).get("biologicalProcess", [])]
    subcells = protein_data.get("subcellularLocations", [])

    enriched_diseases = (disease_profile or {}).get("diseases", [])

    # Build English & Turkish rule-based summaries so both languages are always available instantly
    base_summary = build_rule_based_summary(
        gene, protein_name, functions, diseases, subcells, go_bp,
        alphafold_data, clinvar_variants, variants, literature, disease_profile
    )

    # Check for Gemini API key
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            disease_prompt_str = "; ".join([
                f"{d.get('name')} ({d.get('category')}): {d.get('pathophysiology', '')[:180]}"
                for d in enriched_diseases[:10]
            ]) or ", ".join([d.get("diseaseId", "") for d in diseases[:8]])
            prompt = f"""
Sen uzman bir hesaplamalı biyolog ve tıp doktorusun. Aşağıdaki protein ve gen verilerini, kapsamlı klinik hastalık spektrumunu, AlphaFold 3B yapı tahminini, ClinVar klinik varyasyonlarını ve literatür özetlerini analiz ederek hekimler ve araştırmacılar için anlaşılır, akıcı, bilimsel olarak eksiksiz Türkçe bir özet hazırla.

Protein: {protein_name} ({gene})
Hücresel Konum: {', '.join(subcells)}
Biyolojik Süreçler: {', '.join(go_bp[:5])}
UniProt Fonksiyon Özeti: {' '.join(functions[:2])}
Kapsamlı İlişkili Hastalıklar ve Sendromlar: {disease_prompt_str}
AlphaFold Ortalama pLDDT Güven Skoru: {alphafold_data.get('globalMetricValue') if alphafold_data else 'Yok'} ({alphafold_data.get('confidenceTier') if alphafold_data else ''})
Klinik Mutasyon Örnekleri: {', '.join([v.get('title', '') for v in clinvar_variants[:6]])}
Literatür Başlıkları: {', '.join([a.get('title', '') for a in literature[:3]])}

Lütfen yanıtını aşağıdaki 4 ana başlık altında net, profesyonel maddeler halinde oluştur:
1. Temel Biyolojik Rol
2. Hastalık ve Klinik İlişkisi
3. 3B Yapı ve AlphaFold Analizi
4. Öne Çıkan Mutasyon ve Literatür Bulguları
            """
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            if response.text:
                return {
                    "source": "Gemini AI Biyomedikal Analiz Modeli",
                    "sourceEn": "Gemini AI Biomedical Analysis Engine",
                    "content": response.text,
                    "sections": parse_llm_sections(response.text),
                    "sectionsEn": base_summary["sectionsEn"]
                }
        except Exception as e:
            print(f"Gemini generation error, falling back to rule-based synthesizer: {e}")

    # Domain-specific scientific bilingual synthesizer fallback
    return base_summary


def build_rule_based_summary(
    gene: str,
    protein_name: str,
    functions: List[str],
    diseases: List[Dict[str, Any]],
    subcells: List[str],
    go_bp: List[str],
    alphafold_data: Optional[Dict[str, Any]],
    clinvar_variants: List[Dict[str, Any]],
    variants: List[Dict[str, Any]],
    literature: List[Dict[str, Any]],
    disease_profile: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    
    # 1. Biological Role
    bio_role_points = []
    if functions:
        main_func = functions[0]
        if len(main_func) > 300:
            main_func = main_func[:297] + "..."
        bio_role_points.append(f"{protein_name} ({gene}), hücrede kritik düzenleyici süreçlerde yer alır: {main_func}")
    else:
        bio_role_points.append(f"{gene} geni tarafından kodlanan {protein_name}, temel hücresel homeostaz ve sinyal iletiminde görev yapar.")

    if subcells:
        bio_role_points.append(f"Hücresel yerleşim: Başlıca {', '.join(subcells[:4])} bölgelerinde lokalizedir.")

    if go_bp:
        bio_role_points.append(f"İlgili biyolojik yolaklar: {', '.join(go_bp[:5])}.")

    # 2. Comprehensive Disease Links
    disease_points = []
    enriched = (disease_profile or {}).get("diseases", [])
    specialties = [s["specialty"] for s in (disease_profile or {}).get("specialtyBreakdown", [])]

    if enriched:
        total_d = len(enriched)
        spec_str = ", ".join(specialties[:4])
        disease_points.append(
            f"**Klinik Spektrum Özeti:** {gene} geni toplam **{total_d} farklı klinik hastalık/sendrom** ile ilişkilendirilmiştir "
            f"(Başlıca etkilenen branşlar: *{spec_str}*)."
        )
        for d in enriched[:4]:
            d_name = d.get("name") or "Patoloji"
            d_path = d.get("pathophysiology", "")
            if len(d_path) > 220:
                d_path = d_path[:217] + "..."
            disease_points.append(f"**{d_name}** (*{d.get('category', '')}*): {d_path}")
        if total_d > 4:
            other_names = [d.get("name", "").split("(")[0].strip() for d in enriched[4:12] if d.get("name")]
            if other_names:
                disease_points.append(
                    f"**Diğer İlişkili Klinik Tablolar ({total_d - 4} ek hastalık):** {', '.join(other_names)}"
                    + (" ve diğerleri (tüm detaylar aşağıdaki Klinik Hastalık Spektrumu panelinde listelenmiştir)." if total_d > 12 else ".")
                )
    elif diseases:
        for d in diseases[:5]:
            d_name = d.get("diseaseId") or "Patoloji"
            d_desc = d.get("description", "")
            if d_desc:
                disease_points.append(f"**{d_name}**: {d_desc}")
            else:
                disease_points.append(f"**{d_name}** ile doğrudan ilişkilidir.")
    else:
        disease_points.append(f"{gene} genindeki mutasyonlar ve ekspresyon dengesizlikleri çeşitli fenotipik patolojilerle ve klinik bozukluklarla bağlantılıdır.")

    # 3. Structural AlphaFold Analysis
    structure_points = []
    if alphafold_data:
        plddt = alphafold_data.get("globalMetricValue", "Bilinmiyor")
        tier = alphafold_data.get("confidenceTier", "")
        desc = alphafold_data.get("confidenceDesc", "")
        structure_points.append(f"AlphaFold 3B Yapı Güven Skoru: **{plddt} / 100** ({tier}).")
        structure_points.append(desc)
        structure_points.append("Model pLDDT renklendirmesinde lacivert/açık mavi bölgeler rijit kararlı üçüncül yapıları, sarı/turuncu bölgeler ise fleksibl veya içsel düzensiz (IDR) kısımları gösterir.")
    else:
        structure_points.append("AlphaFold veritabanında yapısal koordinat eşlemesi bekleniyor.")

    # 4. Mutations & Literature
    mutation_lit_points = []
    if clinvar_variants:
        top_vars = [f"{v.get('title', '')} ({v.get('clinicalSignificance', '')})" for v in clinvar_variants[:4]]
        mutation_lit_points.append(f"ClinVar Veritabanı Bulguları ({len(clinvar_variants)} klinik varyant): {'; '.join(top_vars)}.")
    elif variants:
        top_uniprot = [f"{v.get('change')} ({v.get('description')})" for v in variants[:4]]
        mutation_lit_points.append(f"UniProt Mutasyon Kayıtları: {'; '.join(top_uniprot)}.")
    else:
        mutation_lit_points.append("Klinik patojenik varyasyonlar veritabanında taranıyor.")

    if literature:
        top_paper = literature[0]
        mutation_lit_points.append(f"En Çok Atıf Alan Çalışma ({top_paper.get('year', '')}, {top_paper.get('journal', '')}): \"{top_paper.get('title', '')}\" - {top_paper.get('citations', 0)} atıf.")

    sections = [
        {
            "title": "🧬 Temel Biyolojik Rol",
            "items": bio_role_points
        },
        {
            "title": "⚠️ Hastalık ve Klinik İlişkisi",
            "items": disease_points
        },
        {
            "title": "🔬 3B Yapı ve AlphaFold Güven Analizi",
            "items": structure_points
        },
        {
            "title": "⚡ Öne Çıkan Mutasyon ve Literatür Bulguları",
            "items": mutation_lit_points
        }
    ]

    # Build English sections in parallel
    bio_role_en = []
    if functions:
        main_func_en = functions[0]
        if len(main_func_en) > 300:
            main_func_en = main_func_en[:297] + "..."
        bio_role_en.append(f"{protein_name} ({gene}) plays a key regulatory role in cellular pathways: {main_func_en}")
    else:
        bio_role_en.append(f"Encoded by the {gene} gene, {protein_name} mediates core cellular homeostasis and signaling pathways.")
    if subcells:
        bio_role_en.append(f"Subcellular localization: Primarily localized to {', '.join(subcells[:4])}.")
    if go_bp:
        bio_role_en.append(f"Associated biological processes: {', '.join(go_bp[:5])}.")

    disease_points_en = []
    specialties_en = [s.get("specialtyEn") or s["specialty"] for s in (disease_profile or {}).get("specialtyBreakdown", [])]
    if enriched:
        total_d = len(enriched)
        spec_en_str = ", ".join(specialties_en[:4])
        disease_points_en.append(
            f"**Clinical Spectrum Summary:** {gene} is associated with **{total_d} distinct clinical conditions/syndromes** "
            f"(Primary medical specialties: *{spec_en_str}*)."
        )
        for d in enriched[:4]:
            d_name_en = d.get("englishName") or d.get("name") or "Clinical Pathology"
            d_cat_en = d.get("categoryEn") or d.get("primarySpecialtyEn") or d.get("category", "")
            d_path_en = d.get("pathophysiologyEn") or d.get("pathophysiology", "")
            if len(d_path_en) > 220:
                d_path_en = d_path_en[:217] + "..."
            disease_points_en.append(f"**{d_name_en}** (*{d_cat_en}*): {d_path_en}")
        if total_d > 4:
            other_names_en = [(d.get("englishName") or d.get("name", "")).split("(")[0].strip() for d in enriched[4:12] if (d.get("englishName") or d.get("name"))]
            if other_names_en:
                disease_points_en.append(
                    f"**Additional Associated Conditions ({total_d - 4} more):** {', '.join(other_names_en)}"
                    + (" and others (see full Clinical Disease Spectrum panel below)." if total_d > 12 else ".")
                )
    elif diseases:
        for d in diseases[:5]:
            d_name = d.get("diseaseId") or "Pathology"
            d_desc = d.get("description", "")
            if d_desc:
                disease_points_en.append(f"**{d_name}**: {d_desc}")
            else:
                disease_points_en.append(f"Directly associated with **{d_name}**.")
    else:
        disease_points_en.append(f"Mutations and expression alterations in {gene} are linked to diverse phenotypic pathologies and clinical disorders.")

    structure_points_en = []
    if alphafold_data:
        plddt = alphafold_data.get("globalMetricValue", "Unknown")
        tier_en = alphafold_data.get("confidenceTierEn") or alphafold_data.get("confidenceTier", "")
        desc_en = alphafold_data.get("confidenceDescEn") or alphafold_data.get("confidenceDesc", "")
        structure_points_en.append(f"AlphaFold 3D Structure Confidence Score: **{plddt} / 100** ({tier_en}).")
        structure_points_en.append(desc_en)
        structure_points_en.append("In pLDDT coloring, dark/light blue regions indicate rigid, well-folded tertiary domains, while yellow/orange segments denote flexible loops or intrinsically disordered regions (IDRs).")
    else:
        structure_points_en.append("Awaiting structural coordinate mapping in the AlphaFold database.")

    mutation_lit_en = []
    if clinvar_variants:
        top_vars = [f"{v.get('title', '')} ({v.get('clinicalSignificance', '')})" for v in clinvar_variants[:4]]
        mutation_lit_en.append(f"ClinVar Database Findings ({len(clinvar_variants)} clinical variants): {'; '.join(top_vars)}.")
    elif variants:
        top_uniprot = [f"{v.get('change')} ({v.get('description')})" for v in variants[:4]]
        mutation_lit_en.append(f"UniProt Variant Records: {'; '.join(top_uniprot)}.")
    else:
        mutation_lit_en.append("Scanning clinical databases for pathogenic variants.")

    if literature:
        top_paper = literature[0]
        mutation_lit_en.append(f"Most Cited Publication ({top_paper.get('year', '')}, {top_paper.get('journal', '')}): \"{top_paper.get('title', '')}\" - {top_paper.get('citations', 0)} citations.")

    sections_en = [
        {
            "title": "🧬 Primary Biological Role",
            "items": bio_role_en
        },
        {
            "title": "⚠️ Disease & Clinical Associations",
            "items": disease_points_en
        },
        {
            "title": "🔬 3D Structure & AlphaFold Confidence Analysis",
            "items": structure_points_en
        },
        {
            "title": "⚡ Key Mutation & Literature Findings",
            "items": mutation_lit_en
        }
    ]

    return {
        "source": "BioLens Biyomedikal Yapay Zekâ Analiz Motoru",
        "sourceEn": "BioLens Biomedical AI Synthesis Engine",
        "sections": sections,
        "sectionsEn": sections_en
    }


def parse_llm_sections(text: str) -> List[Dict[str, Any]]:
    sections = []
    lines = text.strip().split("\n")
    current_title = "🧬 Biyolojik Değerlendirme"
    current_items = []

    for line in lines:
        line_clean = line.strip()
        if not line_clean:
            continue
        if line_clean.startswith("## ") or line_clean.startswith("### ") or (len(line_clean) < 50 and any(h in line_clean.lower() for h in ["rol", "hastalık", "yapı", "mutasyon", "literatür", "1.", "2.", "3.", "4."])):
            if current_items:
                sections.append({"title": current_title, "items": current_items})
                current_items = []
            current_title = line_clean.lstrip("#123456789. ")
        elif line_clean.startswith("- ") or line_clean.startswith("* "):
            current_items.append(line_clean.lstrip("-* "))
        else:
            current_items.append(line_clean)

    if current_items:
        sections.append({"title": current_title, "items": current_items})

    return sections
