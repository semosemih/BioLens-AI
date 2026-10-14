from fastapi import FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from services.uniprot import search_proteins, get_protein_details
from services.alphafold import get_alphafold_prediction, fetch_pdb_file
from services.clinvar import get_clinvar_variants
from services.literature import get_scientific_literature
from services.summarizer import generate_turkish_summary

app = FastAPI(
    title="BioLens AI API",
    description="Proteinleri keşfetme, AlphaFold 3B yapılarını ve hastalık ilişkilerini araştırma platformu",
    version="1.0.0"
)

# Allow CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CURATED_EXAMPLES = [
    {
        "symbol": "TP53",
        "name": "Hücresel Tümör Antijeni p53",
        "category": "Onkoloji / DNA Tamiri",
        "description": "Genomun koruyucusu olarak bilinen, insan kanserlerinin %50'sinden fazlasında mutasyona uğrayan anahtar tümör baskılayıcı.",
        "icon": "shield"
    },
    {
        "symbol": "EGFR",
        "name": "Epidermal Büyüme Faktörü Reseptörü",
        "category": "Hedefe Yönelik Tedavi / Onkoloji",
        "description": "Akciğer kanserinde hedefe yönelik tirozin kinaz inhibitörlerinin (TKI) birincil hedefi olan hücre yüzeyi reseptörü.",
        "icon": "activity"
    },
    {
        "symbol": "BRCA1",
        "name": "Meme Kanseri Tip 1 Duyarlılık Proteini",
        "category": "Genetik Risk / DNA Çift Kol Kırığı",
        "description": "Homolog rekombinasyon ve DNA hasar onarımında rol alan, kalıtsal meme ve yumurtalık kanseri ile ilişkili protein.",
        "icon": "dna"
    },
    {
        "symbol": "INS",
        "name": "İnsülin",
        "category": "Metabolizma / Endokrinoloji",
        "description": "Glikoz homeostazını yöneten, beta hücrelerinde sentezlenen ve diyabet patogenezinin merkezindeki peptit hormon.",
        "icon": "zap"
    },
    {
        "symbol": "CFTR",
        "name": "Kistik Fibrozis Transmembran İletkenlik Regülatörü",
        "category": "Nadir Hastalıklar / İyon Kanalı",
        "description": "Klor ve tiyosiyanat iyonlarını taşıyan ABC taşıyıcı kanalı; mutasyonları kistik fibrozise yol açar (özellikle delta-F508).",
        "icon": "filter"
    },
    {
        "symbol": "ACE2",
        "name": "Anjiyotensin Dönüştürücü Enzim 2",
        "category": "Kardiyovasküler / İnfeksiyon",
        "description": "Renin-anjiyotensin sisteminde vazodilatör etki gösteren ve SARS-CoV-2 spike proteininin hücreye giriş reseptörü.",
        "icon": "heart"
    },
    {
        "symbol": "APOE",
        "name": "Apolipoprotein E",
        "category": "Nörodejenerasyon / Lipid Metabolizması",
        "description": "Kolesterol ve lipid taşınmasında görevli; APOE-ε4 alleli geç başlangıçlı Alzheimer hastalığı için en güçlü genetik risk faktörüdür.",
        "icon": "brain"
    },
    {
        "symbol": "BRAF",
        "name": "B-Raf Proto-Onkojen Serin/Treonin Kinaz",
        "category": "Onkoloji / MAPK Yolağı",
        "description": "MAPK/ERK sinyal yolağını kontrol eden kinaz; V600E mutasyonu melanom ve kolorektal kanserlerde aşırı proliferasyona neden olur.",
        "icon": "flame"
    }
]

@app.get("/api/health")
def health_check():
    return {"status": "ok", "service": "BioLens AI Backend", "version": "1.0.0"}

@app.get("/api/examples")
def get_examples():
    return CURATED_EXAMPLES

@app.get("/api/search")
def search(q: str = Query(..., min_length=1, description="Protein veya gen adı")):
    hits = search_proteins(q)
    return {"query": q, "count": len(hits), "results": hits}

@app.get("/api/protein/{identifier}")
def get_protein(identifier: str):
    """
    Kullanıcının girdiği gen/protein adı veya accession kodu için tüm bilimsel verileri birleştirir:
    1. UniProt: Fonksiyon, Dizi, GO Terimleri, Doğal Varyantlar
    2. AlphaFold DB: 3B Koordinatlar (.pdb/.cif), pLDDT Güven Skoru
    3. ClinVar / NCBI: Klinik Patojenik Mutasyonlar
    4. Europe PMC / PubMed: Hakemli Bilimsel Makaleler ve Özetler
    5. Yapay Zekâ Biyomedikal Özet Katmanı (Türkçe)
    """
    uniprot_data = get_protein_details(identifier)
    if not uniprot_data:
        raise HTTPException(
            status_code=404,
            detail=f"'{identifier}' için UniProt veritabanında kayıt bulunamadı. Lütfen gen adını veya accession kodunu kontrol edin."
        )

    accession = uniprot_data["accession"]
    gene_symbol = uniprot_data["geneSymbol"]
    protein_name = uniprot_data["proteinName"]

    # 1. Fetch AlphaFold prediction
    alphafold_data = get_alphafold_prediction(accession)

    # 2. Fetch ClinVar pathogenic variants
    clinvar_variants = get_clinvar_variants(gene_symbol)

    # 3. Fetch Europe PMC / PubMed scientific papers
    literature = get_scientific_literature(gene_symbol, protein_name)

    # 4. Generate Turkish AI / Biomedical summary
    ai_summary = generate_turkish_summary(
        protein_data=uniprot_data,
        alphafold_data=alphafold_data,
        clinvar_variants=clinvar_variants,
        literature=literature
    )

    return {
        "success": True,
        "accession": accession,
        "geneSymbol": gene_symbol,
        "proteinName": protein_name,
        "organism": uniprot_data["organism"],
        "uniprot": uniprot_data,
        "alphafold": alphafold_data,
        "clinvar": clinvar_variants,
        "literature": literature,
        "aiSummary": ai_summary
    }

@app.get("/api/pdb/{accession}")
def get_pdb(accession: str, pdb_url: Optional[str] = None):
    """
    AlphaFold PDB koordinat dosyasını çeker ve doğrudan tarayıcıya döndürür (CORS sorunlarını önler).
    """
    if not pdb_url:
        af_data = get_alphafold_prediction(accession)
        if not af_data or not af_data.get("pdbUrl"):
            raise HTTPException(status_code=404, detail="AlphaFold PDB koordinat dosyası bulunamadı.")
        pdb_url = af_data["pdbUrl"]

    pdb_content = fetch_pdb_file(pdb_url)
    if not pdb_content:
        raise HTTPException(status_code=502, detail="PDB koordinat dosyası AlphaFold sunucularından indirilemedi.")

    return Response(content=pdb_content, media_type="chemical/x-pdb")
