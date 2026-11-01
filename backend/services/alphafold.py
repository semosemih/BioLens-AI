import requests
from typing import Dict, Any, Optional

ALPHAFOLD_API_URL = "https://alphafold.ebi.ac.uk/api/prediction/{accession}"
PDB_CACHE: Dict[str, str] = {}

def get_alphafold_prediction(accession: str) -> Optional[Dict[str, Any]]:
    """
    Fetch AlphaFold structure metadata from EBI AlphaFold Protein Structure Database.
    """
    try:
        url = ALPHAFOLD_API_URL.format(accession=accession)
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return None
        
        data = resp.json()
        if not data or not isinstance(data, list):
            return None
            
        pred = data[0]
        
        # Calculate or extract pLDDT summary
        global_plddt = pred.get("globalMetricValue")
        
        # pLDDT Confidence Tier explanations in Turkish and English
        confidence_tier = "Bilinmiyor"
        confidence_tier_en = "Unknown"
        confidence_desc = ""
        confidence_desc_en = ""
        badge_color = "#3b82f6"
        
        if global_plddt is not None:
            if global_plddt >= 90:
                confidence_tier = "Çok Yüksek Güven (Very High)"
                confidence_tier_en = "Very High Confidence"
                confidence_desc = "Omurga ve yan zincir koordinatları yüksek doğrulukta tahmin edilmiştir. Aktif bölge ve ligand etkileşim analizleri için uygundur."
                confidence_desc_en = "Backbone and side-chain coordinates are predicted with high accuracy. Suitable for active site and ligand interaction analysis."
                badge_color = "#1d4ed8"  # Dark blue
            elif global_plddt >= 70:
                confidence_tier = "Güvenilir (Confident)"
                confidence_tier_en = "Confident (Well-Modeled)"
                confidence_desc = "Genel omurga katlanması ve ikincil yapı elemanları (alfa heliks, beta tabaka) yüksek oranda güvenilirdir."
                confidence_desc_en = "Overall backbone fold and secondary structure elements (alpha-helices, beta-sheets) are modeled with good confidence."
                badge_color = "#0284c7"  # Sky blue
            elif global_plddt >= 50:
                confidence_tier = "Düşük Güven (Low)"
                confidence_tier_en = "Low Confidence"
                confidence_desc = "Dinamik döngüler (loops) veya esnek yüzey bölgeleri içerebilir. İkincil yapı tahmini dikkatle ele alınmalıdır."
                confidence_desc_en = "May contain flexible surface loops or dynamic linker regions. Secondary structure predictions should be interpreted with caution."
                badge_color = "#eab308"  # Yellow
            else:
                confidence_tier = "Çok Düşük Güven (Very Low / Disordered)"
                confidence_tier_en = "Very Low Confidence (Disordered / IDR)"
                confidence_desc = "Muhtemelen yapısal olarak düzensiz (IDR - Intrinsically Disordered Region) veya izole halde stabil katlanmayan dinamik segmenttir."
                confidence_desc_en = "Likely represents intrinsically disordered regions (IDRs) or dynamic segments that do not adopt a rigid fold in isolation."
                badge_color = "#f97316"  # Orange

        return {
            "entryId": pred.get("entryId"),
            "gene": pred.get("gene"),
            "uniprotAccession": pred.get("uniprotAccession"),
            "uniprotId": pred.get("uniprotId"),
            "uniprotDescription": pred.get("uniprotDescription"),
            "taxId": pred.get("taxId"),
            "organismScientificName": pred.get("organismScientificName"),
            "uniprotStart": pred.get("uniprotStart"),
            "uniprotEnd": pred.get("uniprotEnd"),
            "uniprotSequence": pred.get("uniprotSequence"),
            "pdbUrl": pred.get("pdbUrl"),
            "cifUrl": pred.get("cifUrl"),
            "bcifUrl": pred.get("bcifUrl"),
            "plddtDocUrl": pred.get("plddtDocUrl"),
            "globalMetricValue": round(global_plddt, 1) if global_plddt is not None else None,
            "confidenceTier": confidence_tier,
            "confidenceTierEn": confidence_tier_en,
            "confidenceDesc": confidence_desc,
            "confidenceDescEn": confidence_desc_en,
            "badgeColor": badge_color,
            "plddtScale": [
                {
                    "range": "> 90",
                    "level": "Çok Yüksek",
                    "levelEn": "Very High",
                    "color": "#1d4ed8",
                    "meaning": "Yüksek doğrulukta omurga ve yan zincirler",
                    "meaningEn": "High accuracy backbone and side chains"
                },
                {
                    "range": "70 - 90",
                    "level": "Güvenilir",
                    "levelEn": "Confident",
                    "color": "#0284c7",
                    "meaning": "Genel üçüncül katlanma doğru",
                    "meaningEn": "Generally accurate tertiary fold"
                },
                {
                    "range": "50 - 70",
                    "level": "Düşük",
                    "levelEn": "Low",
                    "color": "#eab308",
                    "meaning": "Esnek bölgeler ve yüzey döngüleri",
                    "meaningEn": "Flexible regions and surface loops"
                },
                {
                    "range": "< 50",
                    "level": "Çok Düşük",
                    "levelEn": "Very Low (IDR)",
                    "color": "#f97316",
                    "meaning": "Yapısal olarak düzensiz (IDR) bölgeler",
                    "meaningEn": "Intrinsically disordered regions (IDRs)"
                }
            ]
        }
    except Exception as e:
        print(f"Error fetching AlphaFold prediction: {e}")
        return None

def fetch_pdb_file(pdb_url: str) -> Optional[str]:
    """
    Download and cache PDB file text content for streaming to 3Dmol.js viewer.
    """
    if pdb_url in PDB_CACHE:
        return PDB_CACHE[pdb_url]
    
    try:
        resp = requests.get(pdb_url, timeout=15)
        if resp.status_code == 200:
            content = resp.text
            # Limit cache size to 10 entries
            if len(PDB_CACHE) > 10:
                PDB_CACHE.clear()
            PDB_CACHE[pdb_url] = content
            return content
    except Exception as e:
        print(f"Error downloading PDB file: {e}")
    return None
