import os
import sys
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, FastAPI, HTTPException, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

# Ensure backend directory is in sys.path for both local and Vercel serverless imports
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from services.uniprot import search_proteins, get_protein_details
from services.alphafold import get_alphafold_prediction, fetch_pdb_file
from services.clinvar import get_clinvar_variants
from services.literature import get_scientific_literature
from services.summarizer import generate_turkish_summary
from services.diseases import build_comprehensive_disease_profile

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
        "nameEn": "Cellular Tumor Antigen p53",
        "category": "Onkoloji / DNA Tamiri",
        "categoryEn": "Oncology / DNA Repair",
        "description": "Genomun koruyucusu olarak bilinen, insan kanserlerinin %50'sinden fazlasında mutasyona uğrayan anahtar tümör baskılayıcı.",
        "descriptionEn": "Known as the guardian of the genome; key tumor suppressor mutated in over 50% of human cancers.",
        "icon": "shield"
    },
    {
        "symbol": "EGFR",
        "name": "Epidermal Büyüme Faktörü Reseptörü",
        "nameEn": "Epidermal Growth Factor Receptor",
        "category": "Hedefe Yönelik Tedavi / Onkoloji",
        "categoryEn": "Targeted Therapy / Oncology",
        "description": "Akciğer kanserinde hedefe yönelik tirozin kinaz inhibitörlerinin (TKI) birincil hedefi olan hücre yüzeyi reseptörü.",
        "descriptionEn": "Cell surface receptor and primary target of tyrosine kinase inhibitors (TKIs) in non-small cell lung cancer.",
        "icon": "activity"
    },
    {
        "symbol": "BRCA1",
        "name": "Meme Kanseri Tip 1 Duyarlılık Proteini",
        "nameEn": "Breast Cancer Type 1 Susceptibility Protein",
        "category": "Genetik Risk / DNA Çift Kol Kırığı",
        "categoryEn": "Genetic Risk / Double-Strand DNA Repair",
        "description": "Homolog rekombinasyon ve DNA hasar onarımında rol alan, kalıtsal meme ve yumurtalık kanseri ile ilişkili protein.",
        "descriptionEn": "Involved in homologous recombination and DNA damage repair; linked to hereditary breast and ovarian cancer.",
        "icon": "dna"
    },
    {
        "symbol": "INS",
        "name": "İnsülin",
        "nameEn": "Insulin",
        "category": "Metabolizma / Endokrinoloji",
        "categoryEn": "Metabolism / Endocrinology",
        "description": "Glikoz homeostazını yöneten, beta hücrelerinde sentezlenen ve diyabet patogenezinin merkezindeki peptit hormon.",
        "descriptionEn": "Peptide hormone synthesized in pancreatic beta cells that regulates glucose homeostasis and diabetes pathogenesis.",
        "icon": "zap"
    },
    {
        "symbol": "CFTR",
        "name": "Kistik Fibrozis Transmembran İletkenlik Regülatörü",
        "nameEn": "Cystic Fibrosis Transmembrane Conductance Regulator",
        "category": "Nadir Hastalıklar / İyon Kanalı",
        "categoryEn": "Rare Diseases / Ion Channel",
        "description": "Klor ve tiyosiyanat iyonlarını taşıyan ABC taşıyıcı kanalı; mutasyonları kistik fibrozise yol açar (özellikle delta-F508).",
        "descriptionEn": "ABC transporter chloride channel; mutations (especially F508del) cause cystic fibrosis.",
        "icon": "filter"
    },
    {
        "symbol": "ACE2",
        "name": "Anjiyotensin Dönüştürücü Enzim 2",
        "nameEn": "Angiotensin-Converting Enzyme 2",
        "category": "Kardiyovasküler / İnfeksiyon",
        "categoryEn": "Cardiovascular / Infectious Disease",
        "description": "Renin-anjiyotensin sisteminde vazodilatör etki gösteren ve SARS-CoV-2 spike proteininin hücreye giriş reseptörü.",
        "descriptionEn": "Vasodilator regulator in the renin-angiotensin system and host cell entry receptor for SARS-CoV-2 spike protein.",
        "icon": "heart"
    },
    {
        "symbol": "APOE",
        "name": "Apolipoprotein E",
        "nameEn": "Apolipoprotein E",
        "category": "Nörodejenerasyon / Lipid Metabolizması",
        "categoryEn": "Neurodegeneration / Lipid Metabolism",
        "description": "Kolesterol ve lipid taşınmasında görevli; APOE-ε4 alleli geç başlangıçlı Alzheimer hastalığı için en güçlü genetik risk faktörüdür.",
        "descriptionEn": "Mediates cholesterol and lipid transport; the APOE-ε4 allele is the strongest genetic risk factor for late-onset Alzheimer's disease.",
        "icon": "brain"
    },
    {
        "symbol": "BRAF",
        "name": "B-Raf Proto-Onkojen Serin/Treonin Kinaz",
        "nameEn": "Serine/Threonine-Protein Kinase B-raf",
        "category": "Onkoloji / MAPK Yolağı",
        "categoryEn": "Oncology / MAPK Pathway",
        "description": "MAPK/ERK sinyal yolağını kontrol eden kinaz; V600E mutasyonu melanom ve kolorektal kanserlerde aşırı proliferasyona neden olur.",
        "descriptionEn": "Kinase controlling the MAPK/ERK signaling cascade; V600E mutation drives proliferation in melanoma and colorectal cancer.",
        "icon": "flame"
    }
]

router = APIRouter()

@router.get("/health")
def health_check():
    return {"status": "ok", "service": "BioLens AI Backend", "version": "1.0.0"}

@router.get("/examples")
def get_examples():
    return CURATED_EXAMPLES

@router.get("/search")
def search(q: str = Query(..., min_length=1, description="Protein veya gen adı")):
    hits = search_proteins(q)
    return {"query": q, "count": len(hits), "results": hits}

@router.get("/protein/{identifier}")
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

    # 1-3. Fetch AlphaFold, ClinVar, and Europe PMC concurrently for fast serverless response
    with ThreadPoolExecutor(max_workers=3) as executor:
        af_future = executor.submit(get_alphafold_prediction, accession)
        cv_future = executor.submit(get_clinvar_variants, gene_symbol)
        lit_future = executor.submit(get_scientific_literature, gene_symbol, protein_name)

        alphafold_data = af_future.result()
        clinvar_variants = cv_future.result()
        literature = lit_future.result()

    # 4. Build comprehensive multi-source clinical disease & syndrome profile
    disease_profile = build_comprehensive_disease_profile(uniprot_data, clinvar_variants)

    # 5. Generate Turkish AI / Biomedical summary
    ai_summary = generate_turkish_summary(
        protein_data=uniprot_data,
        alphafold_data=alphafold_data,
        clinvar_variants=clinvar_variants,
        literature=literature,
        disease_profile=disease_profile
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
        "diseaseProfile": disease_profile,
        "literature": literature,
        "aiSummary": ai_summary
    }

@router.get("/pdb/{accession}")
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

# Mount under both /api and root so routes work whether or not the proxy/rewrite strips /api
app.include_router(router, prefix="/api")
app.include_router(router, prefix="", include_in_schema=False)
