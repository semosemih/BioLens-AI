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
        confidence_desc = ""
        badge_color = "#3b82f6"
        
        if global_plddt is not None:
            if global_plddt >= 90:
                confidence_tier = "Çok Yüksek Güven (Very High)"
                confidence_desc = "Omurga ve yan zincir koordinatları yüksek doğrulukta tahmin edilmiştir. Aktif bölge ve ligand etkileşim analizleri için uygundur."
                badge_color = "#1d4ed8"  # Dark blue
            elif global_plddt >= 70:
                confidence_tier = "Güvenilir (Confident)"
                confidence_desc = "Genel omurga katlanması ve ikincil yapı elemanları (alfa heliks, beta tabaka) yüksek oranda güvenilirdir."
                badge_color = "#0284c7"  # Sky blue
            elif global_plddt >= 50:
                confidence_tier = "Düşük Güven (Low)"
                confidence_desc = "Dinamik döngüler (loops) veya esnek yüzey bölgeleri içerebilir. İkincil yapı tahmini dikkatle ele alınmalıdır."
                badge_color = "#eab308"  # Yellow
            else:
                confidence_tier = "Çok Düşük Güven (Very Low / Disordered)"
                confidence_desc = "Muhtemelen yapısal olarak düzensiz (IDR - Intrinsically Disordered Region) veya izole halde stabil katlanmayan dinamik segmenttir."
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
            "confidenceDesc": confidence_desc,
            "badgeColor": badge_color,
            "plddtScale": [
                {
                    "range": "> 90",
                    "level": "Çok Yüksek",
                    "color": "#1d4ed8",
                    "meaning": "Yüksek doğrulukta omurga ve yan zincirler"
                },
                {
                    "range": "70 - 90",
                    "level": "Güvenilir",
                    "color": "#0284c7",
                    "meaning": "Genel üçüncül katlanma doğru"
                },
                {
                    "range": "50 - 70",
                    "level": "Düşük",
                    "color": "#eab308",
                    "meaning": "Esnek bölgeler ve yüzey döngüleri"
                },
                {
                    "range": "< 50",
                    "level": "Çok Düşük",
                    "color": "#f97316",
                    "meaning": "Yapısal olarak düzensiz (IDR) bölgeler"
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
