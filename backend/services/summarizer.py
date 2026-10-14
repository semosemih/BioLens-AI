import os
from typing import Dict, Any, List, Optional

def generate_turkish_summary(
    protein_data: Dict[str, Any],
    alphafold_data: Optional[Dict[str, Any]],
    clinvar_variants: List[Dict[str, Any]],
    literature: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Synthesizes complex biochemical data, literature abstracts, and AlphaFold predictions
    into a clear, structured Turkish biomedical briefing.
    Supports Google Gemini if API key is provided, with an intelligent biomedical domain synthesizer fallback.
    """
    gene = protein_data.get("geneSymbol", "")
    protein_name = protein_data.get("proteinName", "")
    functions = protein_data.get("functions", [])
    diseases = protein_data.get("diseases", [])
    variants = protein_data.get("variants", [])
    go_bp = [p["name"] for p in protein_data.get("goTerms", {}).get("biologicalProcess", [])]
    subcells = protein_data.get("subcellularLocations", [])

    # Check for Gemini API key
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if api_key:
        try:
            from google import genai
            client = genai.Client(api_key=api_key)
            prompt = f"""
Sen uzman bir hesaplamalı biyolog ve hekimsin. Aşağıdaki protein ve gen verilerini, AlphaFold 3B yapı tahminini, ClinVar klinik varyasyonlarını ve literatür özetlerini analiz ederek araştırmacılar ve biyomedikal meraklıları için anlaşılır, akıcı, bilimsel olarak tutarlı Türkçe bir özet hazırla.

Protein: {protein_name} ({gene})
Hücresel Konum: {', '.join(subcells)}
Biyolojik Süreçler: {', '.join(go_bp[:5])}
UniProt Fonksiyon Özeti: {' '.join(functions[:2])}
Hastalıklar: {', '.join([d.get('description', '') for d in diseases[:3]])}
AlphaFold Ortalama pLDDT Güven Skoru: {alphafold_data.get('globalMetricValue') if alphafold_data else 'Yok'} ({alphafold_data.get('confidenceTier') if alphafold_data else ''})
Klinik Mutasyon Örnekleri: {', '.join([v.get('title', '') for v in clinvar_variants[:4]])}
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
                    "content": response.text,
                    "sections": parse_llm_sections(response.text)
                }
        except Exception as e:
            print(f"Gemini generation error, falling back to rule-based synthesizer: {e}")

    # Domain-specific scientific Turkish synthesizer fallback
    return build_rule_based_summary(gene, protein_name, functions, diseases, subcells, go_bp, alphafold_data, clinvar_variants, variants, literature)

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
    literature: List[Dict[str, Any]]
) -> Dict[str, Any]:
    
    # 1. Biological Role
    bio_role_points = []
    if functions:
        main_func = functions[0]
        # Clean up very long text
        if len(main_func) > 280:
            main_func = main_func[:277] + "..."
        bio_role_points.append(f"{protein_name} ({gene}), hücrede kritik düzenleyici süreçlerde yer alır: {main_func}")
    else:
        bio_role_points.append(f"{gene} geni tarafından kodlanan {protein_name}, temel hücresel homeostaz ve sinyal iletiminde görev yapar.")

    if subcells:
        bio_role_points.append(f"Hücresel yerleşim: Başlıca {', '.join(subcells[:3])} bölgelerinde lokalizedir.")

    if go_bp:
        bio_role_points.append(f"İlgili biyolojik yolaklar: {', '.join(go_bp[:4])}.")

    # 2. Disease Links
    disease_points = []
    if diseases:
        for d in diseases[:3]:
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
        top_vars = [f"{v.get('title', '')} ({v.get('clinicalSignificance', '')})" for v in clinvar_variants[:3]]
        mutation_lit_points.append(f"ClinVar Veritabanı Bulguları: {'; '.join(top_vars)}.")
    elif variants:
        top_uniprot = [f"{v.get('change')} ({v.get('description')})" for v in variants[:3]]
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

    return {
        "source": "BioLens Biyomedikal Yapay Zekâ Analiz Motoru",
        "sections": sections
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
