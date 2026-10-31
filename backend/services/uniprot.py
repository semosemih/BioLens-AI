import re
import unicodedata
from difflib import SequenceMatcher
import requests
from typing import Dict, Any, List, Optional

UNIPROT_SEARCH_URL = "https://rest.uniprot.org/uniprotkb/search"
UNIPROT_ENTRY_URL = "https://rest.uniprot.org/uniprotkb/{accession}.json"

HEADERS = {
    "User-Agent": "BioLens-AI/1.0 (academic-computational-biology-tool)"
}

# Strict UniProtKB primary accession regex (6 or 10 characters)
UNIPROT_ACC_REGEX = re.compile(
    r"^(?:[OPQ][0-9][A-Z0-9]{3}[0-9]|[A-NR-Z][0-9](?:[A-Z][A-Z0-9]{2}[0-9]){1,2})(?:-\d+)?$",
    re.IGNORECASE
)

# Curated & commonly searched biomedical protein catalog for instant, typo-tolerant,
# bilingual (Turkish + English) and alias-aware matching.
KNOWN_PROTEINS_CATALOG: List[Dict[str, Any]] = [
    {
        "accession": "P04637",
        "entryName": "P53_HUMAN",
        "geneSymbol": "TP53",
        "allGenes": ["TP53", "P53", "LFS1", "TUMOR PROTEIN P53"],
        "proteinName": "Cellular tumor antigen p53",
        "turkishName": "Hücresel Tümör Antijeni p53",
        "keywords": ["kanser", "tümör baskılayıcı", "dna tamiri", "apoptoz", "li-fraumeni", "onkoloji"],
        "organism": "Homo sapiens",
        "length": 393,
        "reviewed": True
    },
    {
        "accession": "P00533",
        "entryName": "EGFR_HUMAN",
        "geneSymbol": "EGFR",
        "allGenes": ["EGFR", "ERBB", "ERBB1", "HER1", "NISBD2"],
        "proteinName": "Epidermal growth factor receptor",
        "turkishName": "Epidermal Büyüme Faktörü Reseptörü",
        "keywords": ["akciğer kanseri", "tirozin kinaz", "büyüme faktörü", "reseptör", "onkoloji", "glioblastoma"],
        "organism": "Homo sapiens",
        "length": 1210,
        "reviewed": True
    },
    {
        "accession": "P38398",
        "entryName": "BRCA1_HUMAN",
        "geneSymbol": "BRCA1",
        "allGenes": ["BRCA1", "RNF53", "BREAST CANCER 1"],
        "proteinName": "Breast cancer type 1 susceptibility protein",
        "turkishName": "Meme Kanseri Tip 1 Duyarlılık Proteini",
        "keywords": ["meme kanseri", "yumurtalık kanseri", "dna onarımı", "homolog rekombinasyon", "genetik risk"],
        "organism": "Homo sapiens",
        "length": 1863,
        "reviewed": True
    },
    {
        "accession": "P51587",
        "entryName": "BRCA2_HUMAN",
        "geneSymbol": "BRCA2",
        "allGenes": ["BRCA2", "FACD", "FANCD1", "BREAST CANCER 2"],
        "proteinName": "Breast cancer type 2 susceptibility protein",
        "turkishName": "Meme Kanseri Tip 2 Duyarlılık Proteini",
        "keywords": ["meme kanseri", "yumurtalık kanseri", "dna tamiri", "fanconi anemisi"],
        "organism": "Homo sapiens",
        "length": 3418,
        "reviewed": True
    },
    {
        "accession": "P01308",
        "entryName": "INS_HUMAN",
        "geneSymbol": "INS",
        "allGenes": ["INS", "INSULIN", "IDDM", "IDDM2", "MODY10"],
        "proteinName": "Insulin",
        "turkishName": "İnsülin Hormonu",
        "keywords": ["insülin", "diyabet", "şeker hastalığı", "glikoz", "metabolizma", "pankreas", "endokrin"],
        "organism": "Homo sapiens",
        "length": 110,
        "reviewed": True
    },
    {
        "accession": "P06213",
        "entryName": "INSR_HUMAN",
        "geneSymbol": "INSR",
        "allGenes": ["INSR", "CD220", "INSULIN RECEPTOR"],
        "proteinName": "Insulin receptor",
        "turkishName": "İnsülin Reseptörü",
        "keywords": ["insülin reseptörü", "diyabet", "insülin direnci", "glikoz", "tirozin kinaz"],
        "organism": "Homo sapiens",
        "length": 1382,
        "reviewed": True
    },
    {
        "accession": "P13569",
        "entryName": "CFTR_HUMAN",
        "geneSymbol": "CFTR",
        "allGenes": ["CFTR", "ABCC7", "MRP7"],
        "proteinName": "Cystic fibrosis transmembrane conductance regulator",
        "turkishName": "Kistik Fibrozis Transmembran İletkenlik Regülatörü",
        "keywords": ["kistik fibrozis", "klor kanalı", "iyon kanalı", "delta-f508", "akciğer", "nadir hastalık"],
        "organism": "Homo sapiens",
        "length": 1480,
        "reviewed": True
    },
    {
        "accession": "Q9BYF1",
        "entryName": "ACE2_HUMAN",
        "geneSymbol": "ACE2",
        "allGenes": ["ACE2", "UNQ868"],
        "proteinName": "Angiotensin-converting enzyme 2",
        "turkishName": "Anjiyotensin Dönüştürücü Enzim 2",
        "keywords": ["anjiyotensin", "hipertansiyon", "kardiyovasküler", "sars-cov-2", "covid-19", "koronavirüs", "reseptör"],
        "organism": "Homo sapiens",
        "length": 805,
        "reviewed": True
    },
    {
        "accession": "P12821",
        "entryName": "ACE_HUMAN",
        "geneSymbol": "ACE",
        "allGenes": ["ACE", "DCP", "DCP1", "CD143"],
        "proteinName": "Angiotensin-converting enzyme",
        "turkishName": "Anjiyotensin Dönüştürücü Enzim (ACE)",
        "keywords": ["anjiyotensin", "kan basıncı", "hipertansiyon", "kalp", "damar"],
        "organism": "Homo sapiens",
        "length": 1306,
        "reviewed": True
    },
    {
        "accession": "P02649",
        "entryName": "APOE_HUMAN",
        "geneSymbol": "APOE",
        "allGenes": ["APOE", "APO-E", "APOLIPOPROTEIN E"],
        "proteinName": "Apolipoprotein E",
        "turkishName": "Apolipoprotein E",
        "keywords": ["alzheimer", "demans", "nörodejenerasyon", "kolesterol", "lipid", "beyin"],
        "organism": "Homo sapiens",
        "length": 317,
        "reviewed": True
    },
    {
        "accession": "P15056",
        "entryName": "BRAF_HUMAN",
        "geneSymbol": "BRAF",
        "allGenes": ["BRAF", "B-RAF", "BRAF1", "RAFB1"],
        "proteinName": "Serine/threonine-protein kinase B-raf",
        "turkishName": "B-Raf Proto-Onkojen Serin/Treonin Kinaz",
        "keywords": ["melanom", "kanser", "v600e", "mapk", "kinaz", "onkoloji"],
        "organism": "Homo sapiens",
        "length": 766,
        "reviewed": True
    },
    {
        "accession": "P01116",
        "entryName": "RASK_HUMAN",
        "geneSymbol": "KRAS",
        "allGenes": ["KRAS", "K-RAS", "KRAS2", "RASK2", "C-K-RAS"],
        "proteinName": "GTPase KRas",
        "turkishName": "GTPaz KRas Proto-Onkojen Proteini",
        "keywords": ["pankreas kanseri", "kolorektal kanser", "akciğer kanseri", "gtpaz", "onkoloji", "g12d", "g12c"],
        "organism": "Homo sapiens",
        "length": 189,
        "reviewed": True
    },
    {
        "accession": "P04626",
        "entryName": "ERBB2_HUMAN",
        "geneSymbol": "ERBB2",
        "allGenes": ["ERBB2", "HER2", "HER-2", "NEU", "NGL", "CD340"],
        "proteinName": "Receptor tyrosine-protein kinase erbB-2",
        "turkishName": "HER2 / ErbB-2 Reseptör Tirozin Kinaz",
        "keywords": ["her2", "meme kanseri", "trastuzumab", "tirozin kinaz", "reseptör"],
        "organism": "Homo sapiens",
        "length": 1255,
        "reviewed": True
    },
    {
        "accession": "P60484",
        "entryName": "PTEN_HUMAN",
        "geneSymbol": "PTEN",
        "allGenes": ["PTEN", "MMAC1", "TEP1"],
        "proteinName": "Phosphatidylinositol 3,4,5-trisphosphate 3-phosphatase and dual-specificity protein phosphatase PTEN",
        "turkishName": "PTEN Tümör Baskılayıcı Fosfataz",
        "keywords": ["tümör baskılayıcı", "fosfataz", "pi3k", "akt", "kanser", "cowden"],
        "organism": "Homo sapiens",
        "length": 403,
        "reviewed": True
    },
    {
        "accession": "P31749",
        "entryName": "AKT1_HUMAN",
        "geneSymbol": "AKT1",
        "allGenes": ["AKT1", "PKB", "RAC", "AKT"],
        "proteinName": "RAC-alpha serine/threonine-protein kinase",
        "turkishName": "AKT1 / Protein Kinaz B",
        "keywords": ["akt", "kinaz", "hücre sağkalımı", "pi3k", "metabolizma", "kanser"],
        "organism": "Homo sapiens",
        "length": 480,
        "reviewed": True
    },
    {
        "accession": "P42336",
        "entryName": "PK3CA_HUMAN",
        "geneSymbol": "PIK3CA",
        "allGenes": ["PIK3CA", "PI3K", "P110ALPHA"],
        "proteinName": "Phosphatidylinositol 4,5-bisphosphate 3-kinase catalytic subunit alpha isoform",
        "turkishName": "PI3K Katalitik Alt Birimi Alfa (PIK3CA)",
        "keywords": ["pi3k", "meme kanseri", "kinaz", "onkoloji", "sinyal iletimi"],
        "organism": "Homo sapiens",
        "length": 1068,
        "reviewed": True
    },
    {
        "accession": "P42345",
        "entryName": "MTOR_HUMAN",
        "geneSymbol": "MTOR",
        "allGenes": ["MTOR", "FRAP", "FRAP1", "FRAP2", "RAFT1", "RAPT1"],
        "proteinName": "Serine/threonine-protein kinase mTOR",
        "turkishName": "mTOR Serin/Treonin Protein Kinaz",
        "keywords": ["mtor", "otofaji", "hücre büyümesi", "yaşlanma", "rapamisin", "metabolizma"],
        "organism": "Homo sapiens",
        "length": 2549,
        "reviewed": True
    },
    {
        "accession": "P01106",
        "entryName": "MYC_HUMAN",
        "geneSymbol": "MYC",
        "allGenes": ["MYC", "C-MYC", "CMYC", "BHLHE39"],
        "proteinName": "Myc proto-oncogene protein",
        "turkishName": "c-Myc Proto-Onkojen Transkripsiyon Faktörü",
        "keywords": ["myc", "lenfoma", "transkripsiyon faktörü", "onkogen", "hücre döngüsü"],
        "organism": "Homo sapiens",
        "length": 439,
        "reviewed": True
    },
    {
        "accession": "P06400",
        "entryName": "RB_HUMAN",
        "geneSymbol": "RB1",
        "allGenes": ["RB1", "RB", "RETINOBLASTOMA"],
        "proteinName": "Retinoblastoma-associated protein",
        "turkishName": "Retinoblastom Tümör Baskılayıcı Proteini (pRb)",
        "keywords": ["retinoblastom", "göz kanseri", "hücre döngüsü", "tümör baskılayıcı"],
        "organism": "Homo sapiens",
        "length": 928,
        "reviewed": True
    },
    {
        "accession": "P68871",
        "entryName": "HBB_HUMAN",
        "geneSymbol": "HBB",
        "allGenes": ["HBB", "HEMOGLOBIN", "BETA-GLOBIN", "HB"],
        "proteinName": "Hemoglobin subunit beta",
        "turkishName": "Hemoglobin Beta Alt Birimi",
        "keywords": ["hemoglobin", "kan", "oksijen", "orak hücreli anemi", "talasemi", "eritrosit", "alyuvar"],
        "organism": "Homo sapiens",
        "length": 147,
        "reviewed": True
    },
    {
        "accession": "P69905",
        "entryName": "HBA_HUMAN",
        "geneSymbol": "HBA1",
        "allGenes": ["HBA1", "HBA2", "ALPHA-GLOBIN", "HEMOGLOBIN ALPHA"],
        "proteinName": "Hemoglobin subunit alpha",
        "turkishName": "Hemoglobin Alfa Alt Birimi",
        "keywords": ["hemoglobin", "kan", "oksijen", "talasemi", "alyuvar"],
        "organism": "Homo sapiens",
        "length": 142,
        "reviewed": True
    },
    {
        "accession": "P02768",
        "entryName": "ALBU_HUMAN",
        "geneSymbol": "ALB",
        "allGenes": ["ALB", "ALBUMIN", "HSA", "SERUM ALBUMIN"],
        "proteinName": "Albumin",
        "turkishName": "Serum Albümin",
        "keywords": ["albümin", "albumin", "kan plazması", "taşıyıcı protein", "karaciğer", "ozmotik basınç"],
        "organism": "Homo sapiens",
        "length": 609,
        "reviewed": True
    },
    {
        "accession": "P05067",
        "entryName": "A4_HUMAN",
        "geneSymbol": "APP",
        "allGenes": ["APP", "A4", "AD1", "AMYLOID BETA", "ABETA"],
        "proteinName": "Amyloid-beta precursor protein",
        "turkishName": "Amiloid Beta Öncül Proteini (APP)",
        "keywords": ["amiloid", "alzheimer", "demans", "nörodejenerasyon", "beyin", "plak"],
        "organism": "Homo sapiens",
        "length": 770,
        "reviewed": True
    },
    {
        "accession": "P10636",
        "entryName": "TAU_HUMAN",
        "geneSymbol": "MAPT",
        "allGenes": ["MAPT", "TAU", "MTBT1", "STD"],
        "proteinName": "Microtubule-associated protein tau",
        "turkishName": "Mikrotübül İlişkili Tau Proteini",
        "keywords": ["tau", "alzheimer", "demans", "mikrotübül", "nöron", "nörodejenerasyon"],
        "organism": "Homo sapiens",
        "length": 758,
        "reviewed": True
    },
    {
        "accession": "P37840",
        "entryName": "SYUA_HUMAN",
        "geneSymbol": "SNCA",
        "allGenes": ["SNCA", "NACP", "PARK1", "PARK4", "ALPHA-SYNUCLEIN", "SYNUCLEIN"],
        "proteinName": "Alpha-synuclein",
        "turkishName": "Alfa-Sinüklein (Alpha-Synuclein)",
        "keywords": ["parkinson", "sinüklein", "lewy cisimciği", "nörodejenerasyon", "dopamin", "beyin"],
        "organism": "Homo sapiens",
        "length": 140,
        "reviewed": True
    },
    {
        "accession": "O60260",
        "entryName": "PRKN_HUMAN",
        "geneSymbol": "PRKN",
        "allGenes": ["PRKN", "PARK2", "PARKIN"],
        "proteinName": "E3 ubiquitin-protein ligase parkin",
        "turkishName": "Parkin E3 Ubikuitin Ligaz",
        "keywords": ["parkin", "parkinson", "mitofaji", "ubikuitin", "mitokondri"],
        "organism": "Homo sapiens",
        "length": 465,
        "reviewed": True
    },
    {
        "accession": "P42858",
        "entryName": "HD_HUMAN",
        "geneSymbol": "HTT",
        "allGenes": ["HTT", "HD", "IT15", "HUNTINGTIN"],
        "proteinName": "Huntingtin",
        "turkishName": "Huntingtin Proteini",
        "keywords": ["huntington", "huntingtin", "poliglutamin", "nörodejenerasyon", "kore"],
        "organism": "Homo sapiens",
        "length": 3144,
        "reviewed": True
    },
    {
        "accession": "P00441",
        "entryName": "SODC_HUMAN",
        "geneSymbol": "SOD1",
        "allGenes": ["SOD1", "ALS1", "SUPEROXIDE DISMUTASE"],
        "proteinName": "Superoxide dismutase [Cu-Zn]",
        "turkishName": "Süperoksit Dismutaz [Cu-Zn] (SOD1)",
        "keywords": ["als", "amyotrofik lateral skleroz", "antioksidan", "serbest radikal", "motor nöron"],
        "organism": "Homo sapiens",
        "length": 154,
        "reviewed": True
    },
    {
        "accession": "Q15116",
        "entryName": "PDCD1_HUMAN",
        "geneSymbol": "PDCD1",
        "allGenes": ["PDCD1", "PD1", "PD-1", "CD279", "SLEB2"],
        "proteinName": "Programmed cell death protein 1",
        "turkishName": "Programlanmış Hücre Ölümü Proteini 1 (PD-1)",
        "keywords": ["immünoterapi", "pd-1", "pd1", "bağışıklık", "t hücresi", "kanser", "pembrolizumab", "nivolumab"],
        "organism": "Homo sapiens",
        "length": 288,
        "reviewed": True
    },
    {
        "accession": "Q9NZQ7",
        "entryName": "PD1L1_HUMAN",
        "geneSymbol": "CD274",
        "allGenes": ["CD274", "PDL1", "PD-L1", "B7H1", "B7-H1", "PDCD1L1", "PDCD1LG1"],
        "proteinName": "Programmed cell death 1 ligand 1",
        "turkishName": "PD-L1 İmmün Kontrol Noktası Ligandı",
        "keywords": ["pd-l1", "pdl1", "immünoterapi", "kanser", "bağışıklık"],
        "organism": "Homo sapiens",
        "length": 290,
        "reviewed": True
    },
    {
        "accession": "P16410",
        "entryName": "CTLA4_HUMAN",
        "geneSymbol": "CTLA4",
        "allGenes": ["CTLA4", "CTLA-4", "CD152"],
        "proteinName": "Cytotoxic T-lymphocyte protein 4",
        "turkishName": "Sitotoksik T-Lenfosit Proteini 4 (CTLA-4)",
        "keywords": ["immünoterapi", "ctla-4", "t hücresi", "bağışıklık"],
        "organism": "Homo sapiens",
        "length": 223,
        "reviewed": True
    },
    {
        "accession": "P01375",
        "entryName": "TNFA_HUMAN",
        "geneSymbol": "TNF",
        "allGenes": ["TNF", "TNFA", "TNF-ALPHA", "TNFSF2", "CACHECTIN"],
        "proteinName": "Tumor necrosis factor",
        "turkishName": "Tümör Nekroz Faktörü Alfa (TNF-α)",
        "keywords": ["tnf", "enflamasyon", "iltihap", "sitokin", "romatoid artrit", "bağışıklık"],
        "organism": "Homo sapiens",
        "length": 233,
        "reviewed": True
    },
    {
        "accession": "P05231",
        "entryName": "IL6_HUMAN",
        "geneSymbol": "IL6",
        "allGenes": ["IL6", "IL-6", "IFNB2", "INTERLEUKIN 6"],
        "proteinName": "Interleukin-6",
        "turkishName": "İnterlökin-6 (IL-6)",
        "keywords": ["interlökin", "sitokin", "sitokin fırtınası", "enflamasyon", "ateş", "bağışıklık"],
        "organism": "Homo sapiens",
        "length": 212,
        "reviewed": True
    },
    {
        "accession": "P15692",
        "entryName": "VEGFA_HUMAN",
        "geneSymbol": "VEGFA",
        "allGenes": ["VEGFA", "VEGF", "VEGF-A", "VPF"],
        "proteinName": "Vascular endothelial growth factor A",
        "turkishName": "Vasküler Endotelyal Büyüme Faktörü A (VEGF)",
        "keywords": ["vegf", "anjiyogenez", "damar oluşumu", "kanser", "retinopati", "bevacizumab"],
        "organism": "Homo sapiens",
        "length": 232,
        "reviewed": True
    },
    {
        "accession": "P10415",
        "entryName": "BCL2_HUMAN",
        "geneSymbol": "BCL2",
        "allGenes": ["BCL2", "BCL-2"],
        "proteinName": "Apoptosis regulator Bcl-2",
        "turkishName": "Apoptoz Düzenleyici Bcl-2",
        "keywords": ["apoptoz", "hücre ölümü", "lenfoma", "lösemi", "venetoklaks"],
        "organism": "Homo sapiens",
        "length": 239,
        "reviewed": True
    },
    {
        "accession": "P42574",
        "entryName": "CASP3_HUMAN",
        "geneSymbol": "CASP3",
        "allGenes": ["CASP3", "CPP32", "CASPASE-3", "CASPASE 3"],
        "proteinName": "Caspase-3",
        "turkishName": "Kaspaz-3 (Apoptoz Proteazı)",
        "keywords": ["kaspaz", "apoptoz", "hücre ölümü", "proteaz"],
        "organism": "Homo sapiens",
        "length": 277,
        "reviewed": True
    },
    {
        "accession": "P60709",
        "entryName": "ACTB_HUMAN",
        "geneSymbol": "ACTB",
        "allGenes": ["ACTB", "ACTIN", "BETA-ACTIN"],
        "proteinName": "Actin, cytoplasmic 1",
        "turkishName": "Beta-Aktin (Hücre İskeleti Proteini)",
        "keywords": ["aktin", "actin", "hücre iskeleti", "hareket", "sitoplazma"],
        "organism": "Homo sapiens",
        "length": 375,
        "reviewed": True
    },
    {
        "accession": "P12883",
        "entryName": "MYH7_HUMAN",
        "geneSymbol": "MYH7",
        "allGenes": ["MYH7", "MYOSIN", "CMD1S", "CMH1"],
        "proteinName": "Myosin-7",
        "turkishName": "Miyozin-7 (Kalp Kası Ağır Zinciri)",
        "keywords": ["miyozin", "myosin", "kas", "kalp kası", "kardiyomiyopati"],
        "organism": "Homo sapiens",
        "length": 1935,
        "reviewed": True
    },
    {
        "accession": "P02452",
        "entryName": "CO1A1_HUMAN",
        "geneSymbol": "COL1A1",
        "allGenes": ["COL1A1", "COLLAGEN", "OI1", "OI2", "OI3", "OI4"],
        "proteinName": "Collagen alpha-1(I) chain",
        "turkishName": "Kollajen Tip I Alfa-1 Zinciri",
        "keywords": ["kollajen", "kolajen", "collagen", "bağ dokusu", "kemik", "cilt", "osteogenesis imperfecta"],
        "organism": "Homo sapiens",
        "length": 1464,
        "reviewed": True
    },
    {
        "accession": "P11532",
        "entryName": "DMD_HUMAN",
        "geneSymbol": "DMD",
        "allGenes": ["DMD", "DYSTROPHIN", "BMD", "CMD3B"],
        "proteinName": "Dystrophin",
        "turkishName": "Distrofin (Duchenne Kas Distrofisi Proteini)",
        "keywords": ["distrofin", "duchenne", "kas distrofisi", "iskelet kası"],
        "organism": "Homo sapiens",
        "length": 3685,
        "reviewed": True
    },
    {
        "accession": "P00451",
        "entryName": "FA8_HUMAN",
        "geneSymbol": "F8",
        "allGenes": ["F8", "F8C", "FACTOR VIII", "HEMA"],
        "proteinName": "Coagulation factor VIII",
        "turkishName": "Pıhtılaşma Faktörü VIII (Hemofili A)",
        "keywords": ["hemofili", "kan pıhtılaşması", "koagülasyon", "faktör 8"],
        "organism": "Homo sapiens",
        "length": 2351,
        "reviewed": True
    },
    {
        "accession": "P01130",
        "entryName": "LDLR_HUMAN",
        "geneSymbol": "LDLR",
        "allGenes": ["LDLR", "FH", "FHC", "LDL RECEPTOR"],
        "proteinName": "Low-density lipoprotein receptor",
        "turkishName": "Düşük Yoğunluklu Lipoprotein (LDL) Reseptörü",
        "keywords": ["kolesterol", "ldl", "hiperkolesterolemi", "ateroskleroz", "kalp krizi"],
        "organism": "Homo sapiens",
        "length": 860,
        "reviewed": True
    },
    {
        "accession": "Q8NBP7",
        "entryName": "PCSK9_HUMAN",
        "geneSymbol": "PCSK9",
        "allGenes": ["PCSK9", "NARC1", "FH3"],
        "proteinName": "Proprotein convertase subtilisin/kexin type 9",
        "turkishName": "PCSK9 Kolesterol Düzenleyici Enzim",
        "keywords": ["kolesterol", "ldl", "kalp", "hiperkolesterolemi"],
        "organism": "Homo sapiens",
        "length": 692,
        "reviewed": True
    },
    {
        "accession": "P10635",
        "entryName": "CP2D6_HUMAN",
        "geneSymbol": "CYP2D6",
        "allGenes": ["CYP2D6", "CYP2D", "P450DB1"],
        "proteinName": "Cytochrome P450 2D6",
        "turkishName": "Sitokrom P450 2D6 (İlaç Metabolizması Enzimi)",
        "keywords": ["sitokrom", "farmakogenetik", "ilaç metabolizması", "karaciğer", "p450"],
        "organism": "Homo sapiens",
        "length": 497,
        "reviewed": True
    },
    {
        "accession": "P08684",
        "entryName": "CP3A4_HUMAN",
        "geneSymbol": "CYP3A4",
        "allGenes": ["CYP3A4", "CYP3A3", "P450PCN1"],
        "proteinName": "Cytochrome P450 3A4",
        "turkishName": "Sitokrom P450 3A4",
        "keywords": ["sitokrom", "ilaç metabolizması", "karaciğer", "p450"],
        "organism": "Homo sapiens",
        "length": 503,
        "reviewed": True
    },
    {
        "accession": "P42898",
        "entryName": "MTHFR_HUMAN",
        "geneSymbol": "MTHFR",
        "allGenes": ["MTHFR"],
        "proteinName": "Methylenetetrahydrofolate reductase",
        "turkishName": "Metilentetrahidrofolat Redüktaz (MTHFR)",
        "keywords": ["folat", "homosistein", "trombofili", "pıhtılaşma", "vitamin b9"],
        "organism": "Homo sapiens",
        "length": 656,
        "reviewed": True
    },
    {
        "accession": "Q9UM73",
        "entryName": "ALK_HUMAN",
        "geneSymbol": "ALK",
        "allGenes": ["ALK", "CD246"],
        "proteinName": "ALK tyrosine kinase receptor",
        "turkishName": "Anaplastik Lenfoma Kinaz Reseptörü (ALK)",
        "keywords": ["akciğer kanseri", "lenfoma", "tirozin kinaz", "onkoloji"],
        "organism": "Homo sapiens",
        "length": 1620,
        "reviewed": True
    },
    {
        "accession": "P00519",
        "entryName": "ABL1_HUMAN",
        "geneSymbol": "ABL1",
        "allGenes": ["ABL1", "ABL", "JTK7", "BCR-ABL", "C-ABL"],
        "proteinName": "Tyrosine-protein kinase ABL1",
        "turkishName": "ABL1 Tirozin Kinaz (BCR-ABL / KML Hedefi)",
        "keywords": ["lösemi", "kml", "imatinib", "philadelphia kromozomu", "tirozin kinaz"],
        "organism": "Homo sapiens",
        "length": 1130,
        "reviewed": True
    },
    {
        "accession": "O60674",
        "entryName": "JAK2_HUMAN",
        "geneSymbol": "JAK2",
        "allGenes": ["JAK2", "JTK10"],
        "proteinName": "Tyrosine-protein kinase JAK2",
        "turkishName": "Janus Kinaz 2 (JAK2)",
        "keywords": ["polisitemi", "miyeloproliferatif", "hematoloji", "v617f", "kinaz"],
        "organism": "Homo sapiens",
        "length": 1132,
        "reviewed": True
    },
    {
        "accession": "Q13315",
        "entryName": "ATM_HUMAN",
        "geneSymbol": "ATM",
        "allGenes": ["ATM"],
        "proteinName": "Serine-protein kinase ATM",
        "turkishName": "ATM DNA Hasar Yanıtı Kinazı",
        "keywords": ["dna kırığı", "ataksi telenjiektazi", "dna tamiri", "kanser"],
        "organism": "Homo sapiens",
        "length": 3056,
        "reviewed": True
    },
    {
        "accession": "P09874",
        "entryName": "PARP1_HUMAN",
        "geneSymbol": "PARP1",
        "allGenes": ["PARP1", "ADPRT", "PPOL", "PARP"],
        "proteinName": "Poly [ADP-ribose] polymerase 1",
        "turkishName": "Poli [ADP-riboz] Polimeraz 1 (PARP1)",
        "keywords": ["parp", "olaparib", "dna tamiri", "meme kanseri", "yumurtalık kanseri"],
        "organism": "Homo sapiens",
        "length": 1014,
        "reviewed": True
    },
    {
        "accession": "Q00987",
        "entryName": "MDM2_HUMAN",
        "geneSymbol": "MDM2",
        "allGenes": ["MDM2", "HDM2"],
        "proteinName": "E3 ubiquitin-protein ligase Mdm2",
        "turkishName": "Mdm2 E3 Ubikuitin Ligaz (p53 Negatif Regülatörü)",
        "keywords": ["mdm2", "p53", "sarkom", "ubikuitin", "kanser"],
        "organism": "Homo sapiens",
        "length": 491,
        "reviewed": True
    },
    {
        "accession": "P05109",
        "entryName": "S10A8_HUMAN",
        "geneSymbol": "S100A8",
        "allGenes": ["S100A8", "CAGA", "CFAG", "MRP8", "CALPROTECTIN"],
        "proteinName": "Protein S100-A8",
        "turkishName": "Kalprotektin Alt Birimi S100-A8",
        "keywords": ["kalprotektin", "enflamasyon", "bağışıklık", "kalsiyum"],
        "organism": "Homo sapiens",
        "length": 93,
        "reviewed": True
    },
    {
        "accession": "Q9H244",
        "entryName": "P2Y12_HUMAN",
        "geneSymbol": "P2RY12",
        "allGenes": ["P2RY12", "P2Y12", "HORK3"],
        "proteinName": "P2Y purinoceptor 12",
        "turkishName": "Trombosit ADP Reseptörü P2Y12",
        "keywords": ["trombosit", "pıhtılaşma", "klopidogrel", "kalp krizi"],
        "organism": "Homo sapiens",
        "length": 342,
        "reviewed": True
    },
    {
        "accession": "P43220",
        "entryName": "GLP1R_HUMAN",
        "geneSymbol": "GLP1R",
        "allGenes": ["GLP1R", "GLP-1R", "GLP1"],
        "proteinName": "Glucagon-like peptide 1 receptor",
        "turkishName": "GLP-1 Reseptörü (Semaglutid / Diyabet & Obezite Hedefi)",
        "keywords": ["glp-1", "glp1", "diyabet", "obezite", "semaglutid", "ozempic", "insülin"],
        "organism": "Homo sapiens",
        "length": 463,
        "reviewed": True
    },
    {
        "accession": "P0DTC2",
        "entryName": "SPIKE_SARS2",
        "geneSymbol": "S",
        "allGenes": ["S", "SPIKE", "SURFACE GLYCOPROTEIN", "SARS-COV-2 SPIKE"],
        "proteinName": "Spike glycoprotein",
        "turkishName": "SARS-CoV-2 Spike (Başak) Glikoproteini",
        "keywords": ["covid-19", "koronavirüs", "sars-cov-2", "spike", "aşı", "ace2"],
        "organism": "Severe acute respiratory syndrome coronavirus 2",
        "length": 1273,
        "reviewed": True
    },
    {
        "accession": "P42212",
        "entryName": "GFP_AEQVI",
        "geneSymbol": "GFP",
        "allGenes": ["GFP", "GREEN FLUORESCENT PROTEIN"],
        "proteinName": "Green fluorescent protein",
        "turkishName": "Yeşil Floresan Protein (GFP)",
        "keywords": ["floresan", "biyolüminesans", "raportör", "gfp"],
        "organism": "Aequorea victoria",
        "length": 238,
        "reviewed": True
    },
    {
        "accession": "Q99ZW2",
        "entryName": "CAS9_STRP1",
        "geneSymbol": "CAS9",
        "allGenes": ["CAS9", "CSN1", "CRISPR"],
        "proteinName": "CRISPR-associated endonuclease Cas9",
        "turkishName": "CRISPR İlişkili Endonükleaz Cas9",
        "keywords": ["crispr", "cas9", "gen düzenleme", "dna kesimi", "biyoteknoloji"],
        "organism": "Streptococcus pyogenes",
        "length": 1368,
        "reviewed": True
    }
]

# Turkish-to-English biomedical keyword dictionary for general UniProt search translation
TURKISH_BIOMED_TRANSLATIONS = {
    "insülin": "insulin",
    "insulin": "insulin",
    "tümör": "tumor",
    "tumor": "tumor",
    "kanser": "cancer",
    "meme kanseri": "breast cancer",
    "akciğer kanseri": "lung cancer",
    "kistik fibrozis": "cystic fibrosis",
    "büyüme faktörü": "growth factor",
    "reseptörü": "receptor",
    "reseptör": "receptor",
    "reseptor": "receptor",
    "enzim": "enzyme",
    "kinaz": "kinase",
    "fosfataz": "phosphatase",
    "proteaz": "protease",
    "kaspaz": "caspase",
    "kollajen": "collagen",
    "kolajen": "collagen",
    "albümin": "albumin",
    "albumin": "albumin",
    "aktin": "actin",
    "miyozin": "myosin",
    "sitokrom": "cytochrome",
    "interlökin": "interleukin",
    "interlokin": "interleukin",
    "anjiyotensin": "angiotensin",
    "hemoglobin": "hemoglobin",
    "distrofin": "dystrophin",
    "amiloid": "amyloid",
    "sinüklein": "synuclein",
    "ubikuitin": "ubiquitin",
    "pıhtılaşma": "coagulation",
    "faktör": "factor",
    "faktor": "factor",
    "antijen": "antigen",
    "antijeni": "antigen",
    "hormon": "hormone",
    "hormonu": "hormone",
    "kanal": "channel",
    "kanalı": "channel",
    "taşıyıcı": "transporter",
    "proteini": "protein",
    "protein": "protein",
    "hücresel": "cellular",
    "epidermal": "epidermal",
    "vasküler": "vascular",
}


def normalize_turkish(text: str) -> str:
    """
    Normalizes Turkish characters and case to clean ASCII lowercase for robust comparison.
    """
    if not text:
        return ""
    tr_map = str.maketrans({
        "İ": "i", "I": "i", "ı": "i",
        "Ş": "s", "ş": "s",
        "Ğ": "g", "ğ": "g",
        "Ü": "u", "ü": "u",
        "Ö": "o", "ö": "o",
        "Ç": "c", "ç": "c",
    })
    mapped = text.translate(tr_map).lower()
    norm = unicodedata.normalize("NFKD", mapped)
    return "".join(c for c in norm if not unicodedata.combining(c)).strip()


def translate_turkish_query(query: str) -> str:
    """
    Translates Turkish biomedical phrases or words into English equivalents for UniProt API search.
    """
    q_low = query.strip().lower().replace("İ", "i")
    for tr_phrase, en_phrase in sorted(TURKISH_BIOMED_TRANSLATIONS.items(), key=lambda x: -len(x[0])):
        if tr_phrase in q_low:
            q_low = q_low.replace(tr_phrase, en_phrase)
    return normalize_turkish(q_low)


def sanitize_lucene_term(term: str) -> str:
    """
    Removes characters that break UniProt's Lucene query syntax.
    """
    cleaned = re.sub(r'[+\-&|!(){}\[\]^"~*?:\\/]', " ", term)
    return " ".join(cleaned.split()).strip()


def score_protein_hit(hit: Dict[str, Any], raw_query: str) -> float:
    """
    Computes a relevance score for a candidate protein hit against the user's query.
    Higher score = stronger match.
    """
    q_norm = normalize_turkish(raw_query)
    q_compact = re.sub(r"[\s\-_]+", "", q_norm)
    if not q_norm:
        return 0.0

    acc = normalize_turkish(hit.get("accession", ""))
    entry_name = normalize_turkish(hit.get("entryName", ""))
    gene = normalize_turkish(hit.get("geneSymbol", ""))
    gene_compact = re.sub(r"[\s\-_]+", "", gene)
    all_genes = [normalize_turkish(g) for g in hit.get("allGenes", []) if g]
    all_genes_compact = [re.sub(r"[\s\-_]+", "", g) for g in all_genes]
    prot_name = normalize_turkish(hit.get("proteinName", ""))
    tr_name = normalize_turkish(hit.get("turkishName", ""))
    keywords = [normalize_turkish(k) for k in hit.get("keywords", []) if k]

    score = 0.0

    # 1. Exact identifier matches
    if q_norm == acc or q_norm == entry_name:
        score = max(score, 1000.0)
    if q_norm == gene or (q_compact and q_compact == gene_compact):
        score = max(score, 960.0)
    if q_norm in all_genes or (q_compact and q_compact in all_genes_compact):
        score = max(score, 920.0)
    if q_norm == prot_name or (tr_name and q_norm == tr_name):
        score = max(score, 880.0)

    # 2. Prefix matches on gene symbol or aliases
    if score < 850.0:
        if gene.startswith(q_norm) or (len(q_compact) >= 2 and gene_compact.startswith(q_compact)):
            # Prefer shorter gene symbols when prefix matching (e.g. INS over INSR)
            length_penalty = min(len(gene) - len(q_norm), 15) * 2.0
            score = max(score, 800.0 - length_penalty)
        elif any(g.startswith(q_norm) or (len(q_compact) >= 2 and gc.startswith(q_compact)) for g, gc in zip(all_genes, all_genes_compact)):
            score = max(score, 730.0)
        elif acc.startswith(q_norm):
            score = max(score, 710.0)

    # 3. Protein name / Turkish name prefix or whole-word match
    if score < 700.0:
        q_words = [w for w in q_norm.split() if w]
        if prot_name.startswith(q_norm) or (tr_name and tr_name.startswith(q_norm)):
            score = max(score, 680.0 - min(len(prot_name) * 0.2, 30.0))
        elif q_words and all(w in prot_name or (tr_name and w in tr_name) for w in q_words):
            # Exact word boundary bonus
            word_boundary = any(w == q_norm for w in re.split(r"[\s\-/,()]+", f"{prot_name} {tr_name}"))
            score = max(score, 640.0 if word_boundary else 580.0)
        elif any(q_norm == kw or kw.startswith(q_norm) for kw in keywords):
            score = max(score, 560.0)
        elif any(q_norm in kw for kw in keywords):
            score = max(score, 500.0)
        elif q_norm in gene or (len(q_compact) >= 3 and q_compact in gene_compact):
            score = max(score, 540.0)
        elif any(q_norm in g for g in all_genes):
            score = max(score, 510.0)
        elif q_norm in prot_name or (tr_name and q_norm in tr_name):
            score = max(score, 480.0)

    # 4. Typo tolerance (fuzzy matching & transposition tolerance on gene symbols and protein names)
    if score < 450.0 and len(q_compact) >= 3:
        best_ratio = 0.0
        max_len_diff = max(1, len(q_compact) // 4)
        gene_candidates = [gene_compact] + all_genes_compact
        for cand in gene_candidates:
            if not cand or abs(len(q_compact) - len(cand)) > max_len_diff:
                continue
            ratio = SequenceMatcher(None, q_compact, cand).ratio()
            if len(q_compact) == len(cand) and sorted(q_compact) == sorted(cand):
                ratio = max(ratio, 0.90)
            if ratio > best_ratio:
                best_ratio = ratio

        for name_field in (prot_name, tr_name):
            if not name_field:
                continue
            if abs(len(q_norm) - len(name_field)) <= 3:
                ratio = SequenceMatcher(None, q_norm, name_field).ratio()
                if ratio > best_ratio:
                    best_ratio = ratio
            for word in name_field.split():
                if len(word) >= 4 and abs(len(q_norm) - len(word)) <= 2:
                    w_ratio = SequenceMatcher(None, q_norm, word).ratio()
                    if len(q_norm) == len(word) and sorted(q_norm) == sorted(word):
                        w_ratio = max(w_ratio, 0.90)
                    if w_ratio > best_ratio:
                        best_ratio = w_ratio

        if best_ratio >= 0.75:
            score = max(score, 300.0 + (best_ratio * 150.0))

    # 5. Quality bonuses (Reviewed Swiss-Prot + Human priority)
    if score > 0:
        if hit.get("reviewed"):
            score += 25.0
        if "homo sapiens" in (hit.get("organism") or "").lower():
            score += 15.0

    return score


def search_local_catalog(query: str) -> List[Dict[str, Any]]:
    """
    Searches the built-in biomedical catalog using exact, prefix, Turkish, keyword, and fuzzy matching.
    """
    scored = []
    for item in KNOWN_PROTEINS_CATALOG:
        s = score_protein_hit(item, query)
        if s >= 420.0:
            hit_copy = dict(item)
            hit_copy["_score"] = s
            scored.append(hit_copy)

    scored.sort(key=lambda x: x["_score"], reverse=True)
    strong = [h for h in scored if h["_score"] >= 500.0]
    if strong:
        return strong
    return scored


def build_uniprot_queries(raw_query: str) -> List[str]:
    """
    Builds ordered UniProtKB Lucene search queries from most specific to broad fallback.
    Safely handles single tokens, prefixes, hyphenated symbols, and multi-word queries.
    """
    en_query = translate_turkish_query(raw_query)
    clean_raw = sanitize_lucene_term(raw_query)
    clean_en = sanitize_lucene_term(en_query)

    # Also test compact form if hyphenated (e.g. "BRCA-1" -> "BRCA1", "TP-53" -> "TP53")
    compact_token = re.sub(r"[\s\-_]+", "", raw_query.strip())
    compact_clean = sanitize_lucene_term(compact_token)

    queries: List[str] = []
    tokens = [t for t in clean_en.split() if t]
    if not tokens:
        tokens = [t for t in clean_raw.split() if t]
    if not tokens:
        return []

    if len(tokens) == 1:
        tok = tokens[0]
        extra_gene = ""
        if compact_clean and compact_clean.lower() != tok.lower() and compact_clean.isalnum():
            extra_gene = f" OR (gene_exact:{compact_clean}) OR (gene:{compact_clean}*)"

        if len(tok) >= 2:
            # Stage 1: Reviewed human with exact gene, prefix gene, prefix protein name
            queries.append(
                f"((gene_exact:{tok}) OR (gene:{tok}) OR (gene:{tok}*){extra_gene} OR (protein_name:{tok}*) OR ({tok}*)) "
                f"AND (organism_id:9606) AND (reviewed:true)"
            )
            # Stage 2: Reviewed any organism (for Cas9, GFP, viral proteins, etc.) or broader human
            queries.append(
                f"((gene_exact:{tok}) OR (gene:{tok}*){extra_gene} OR (protein_name:{tok}*) OR ({tok}*)) "
                f"AND (reviewed:true)"
            )
        else:
            # 1-char query: exact or prefix gene in reviewed human
            queries.append(
                f"((gene:{tok}*)) AND (organism_id:9606) AND (reviewed:true)"
            )
    else:
        # Multi-word query (e.g. "epidermal growth factor", "insulin receptor", "breast cancer")
        phrase = " ".join(tokens)
        and_clause = " AND ".join(f"{t}*" if len(t) >= 3 else t for t in tokens)
        compact_clause = f"(gene_exact:{compact_clean}) OR (gene:{compact_clean}*) OR " if compact_clean.isalnum() else ""

        # Stage 1: Reviewed human matching phrase or all words
        queries.append(
            f"({compact_clause}(protein_name:\"{phrase}\") OR ({and_clause})) "
            f"AND (organism_id:9606) AND (reviewed:true)"
        )
        # Stage 2: Reviewed any organism or broader human
        queries.append(
            f"({compact_clause}(protein_name:\"{phrase}\") OR ({and_clause})) "
            f"AND (reviewed:true)"
        )

    return queries


def search_proteins(query: str, limit: int = 8) -> List[Dict[str, Any]]:
    """
    Search for proteins by gene symbol, alias, accession, English name, or Turkish name/keyword.
    Combines instant local catalog matching (with typo tolerance and Turkish support)
    with multi-stage UniProtKB REST search and intelligent relevance ranking.
    """
    query_clean = query.strip()
    if not query_clean:
        return []

    catalog_by_acc = {item["accession"]: item for item in KNOWN_PROTEINS_CATALOG}
    local_hits = search_local_catalog(query_clean)

    merged_by_acc: Dict[str, Dict[str, Any]] = {}
    for hit in local_hits:
        acc = hit["accession"]
        merged_by_acc[acc] = hit

    # If the user typed a 1-character query, local catalog hits are fast and sufficient
    if len(query_clean) == 1 and local_hits:
        return [
            {k: v for k, v in h.items() if not k.startswith("_")}
            for h in local_hits[:limit]
        ]

    # Query UniProt REST API
    uniprot_queries = build_uniprot_queries(query_clean)
    fetch_size = max(limit * 2, 16)

    for u_query in uniprot_queries:
        try:
            resp = requests.get(
                UNIPROT_SEARCH_URL,
                params={"query": u_query, "format": "json", "size": fetch_size},
                headers=HEADERS,
                timeout=6
            )
            if resp.status_code == 200:
                data = resp.json()
                results = data.get("results", [])
                for item in results:
                    formatted = format_search_hit(item, catalog_by_acc)
                    acc = formatted["accession"]
                    if not acc:
                        continue
                    # Calculate relevance score against both raw query and translated query
                    s_raw = score_protein_hit(formatted, query_clean)
                    en_q = translate_turkish_query(query_clean)
                    s_en = score_protein_hit(formatted, en_q) if en_q != normalize_turkish(query_clean) else 0.0
                    # Base score for UniProt search hit even if matched via deep annotation/synonym
                    hit_score = max(s_raw, s_en, 250.0 + (25.0 if formatted.get("reviewed") else 0.0))
                    formatted["_score"] = hit_score

                    if acc not in merged_by_acc or hit_score > merged_by_acc[acc].get("_score", 0):
                        merged_by_acc[acc] = formatted

                # If we already have strong reviewed matches, no need to run fallback query stages
                if any(h.get("_score", 0) >= 600.0 for h in merged_by_acc.values()) and len(merged_by_acc) >= 4:
                    break
        except Exception as e:
            print(f"UniProt search stage error ({u_query}): {e}")

    ranked = sorted(
        merged_by_acc.values(),
        key=lambda x: x.get("_score", 0),
        reverse=True
    )

    return [
        {k: v for k, v in item.items() if not k.startswith("_")}
        for item in ranked[:limit]
    ]


def format_search_hit(
    item: Dict[str, Any],
    catalog_by_acc: Optional[Dict[str, Dict[str, Any]]] = None
) -> Dict[str, Any]:
    acc = item.get("primaryAccession", "")
    id_name = item.get("uniProtkbId", "")

    # Gene names & synonyms
    genes = []
    primary_gene = ""
    for g in item.get("genes", []):
        if "geneName" in g:
            val = g["geneName"].get("value", "")
            if val:
                if not primary_gene:
                    primary_gene = val
                genes.append(val)
        for syn in g.get("synonyms", []):
            s_val = syn.get("value", "")
            if s_val and s_val not in genes:
                genes.append(s_val)
        for orf in g.get("orfNames", []):
            o_val = orf.get("value", "")
            if o_val and o_val not in genes:
                genes.append(o_val)

    gene_symbol = primary_gene if primary_gene else (genes[0] if genes else id_name.split("_")[0])

    # Protein description & alternative names
    desc = item.get("proteinDescription", {})
    rec_name = desc.get("recommendedName", {}).get("fullName", {}).get("value")
    if not rec_name:
        sub_names = desc.get("submissionNames", [])
        if sub_names:
            rec_name = sub_names[0].get("fullName", {}).get("value")
    if not rec_name:
        rec_name = gene_symbol

    # Also collect short names / alternative names into aliases so search scoring can match them
    for alt in desc.get("alternativeNames", []):
        full_alt = alt.get("fullName", {}).get("value")
        if full_alt and full_alt not in genes and len(full_alt) <= 25:
            genes.append(full_alt)
        for short_alt in alt.get("shortNames", []):
            s_alt = short_alt.get("value")
            if s_alt and s_alt not in genes:
                genes.append(s_alt)

    organism = item.get("organism", {}).get("scientificName", "Homo sapiens")
    seq_len = item.get("sequence", {}).get("length", 0)
    reviewed = item.get("entryType") == "UniProtKB reviewed (Swiss-Prot)"

    # Enrich with Turkish name & known aliases if present in catalog
    catalog_entry = (catalog_by_acc or {}).get(acc)
    turkish_name = catalog_entry.get("turkishName", "") if catalog_entry else ""
    if catalog_entry:
        for cg in catalog_entry.get("allGenes", []):
            if cg not in genes:
                genes.append(cg)

    return {
        "accession": acc,
        "entryName": id_name,
        "geneSymbol": gene_symbol,
        "allGenes": genes[:6],
        "proteinName": rec_name,
        "turkishName": turkish_name,
        "organism": organism,
        "length": seq_len,
        "reviewed": reviewed
    }


def fetch_uniprot_entry_by_acc(acc: str) -> Optional[Dict[str, Any]]:
    """
    Fetches a single UniProt entry JSON by primary accession.
    """
    try:
        resp = requests.get(
            UNIPROT_ENTRY_URL.format(accession=acc),
            headers=HEADERS,
            timeout=10
        )
        if resp.status_code == 200:
            return resp.json()
    except Exception as e:
        print(f"Error fetching UniProt entry {acc}: {e}")
    return None


def get_protein_details(accession_or_gene: str) -> Optional[Dict[str, Any]]:
    """
    Fetch comprehensive entry details from UniProt.
    Resolves gene symbols, aliases, Turkish names, or accessions reliably,
    with automatic fallback to ranked search if direct accession lookup fails.
    """
    raw = accession_or_gene.strip()
    if not raw:
        return None

    q_norm = normalize_turkish(raw)
    q_compact = re.sub(r"[\s\-_]+", "", q_norm)

    # 1. Check if input is an exact gene symbol or alias in our curated catalog
    for item in KNOWN_PROTEINS_CATALOG:
        if q_norm == normalize_turkish(item["accession"]):
            entry = fetch_uniprot_entry_by_acc(item["accession"])
            if entry:
                return parse_uniprot_entry(entry)
        gene_norm = normalize_turkish(item["geneSymbol"])
        aliases_norm = [normalize_turkish(a) for a in item.get("allGenes", [])]
        aliases_compact = [re.sub(r"[\s\-_]+", "", a) for a in aliases_norm]
        if (
            q_norm == gene_norm
            or q_compact == re.sub(r"[\s\-_]+", "", gene_norm)
            or q_norm in aliases_norm
            or (q_compact and q_compact in aliases_compact)
            or (item.get("turkishName") and q_norm == normalize_turkish(item["turkishName"]))
        ):
            entry = fetch_uniprot_entry_by_acc(item["accession"])
            if entry:
                return parse_uniprot_entry(entry)

    # 2. If it matches strict UniProt accession format, try direct fetch first
    acc_candidate = raw.upper()
    if UNIPROT_ACC_REGEX.match(acc_candidate):
        entry = fetch_uniprot_entry_by_acc(acc_candidate.split("-")[0])
        if entry:
            return parse_uniprot_entry(entry)

    # 3. Otherwise (or if direct accession fetch returned 404 for gene names like P2RY12),
    # perform ranked search and resolve top candidate's accession
    hits = search_proteins(raw, limit=8)
    if hits:
        best_acc = hits[0]["accession"]
        entry = fetch_uniprot_entry_by_acc(best_acc)
        if entry:
            return parse_uniprot_entry(entry)

    return None


def parse_uniprot_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    acc = entry.get("primaryAccession", "")
    id_name = entry.get("uniProtkbId", "")
    
    # Genes
    genes = []
    primary_gene = ""
    for g in entry.get("genes", []):
        if "geneName" in g:
            val = g["geneName"].get("value", "")
            if val:
                if not primary_gene:
                    primary_gene = val
                genes.append(val)
        for syn in g.get("synonyms", []):
            s_val = syn.get("value", "")
            if s_val and s_val not in genes:
                genes.append(s_val)
    if not primary_gene and genes:
        primary_gene = genes[0]
    if not primary_gene:
        primary_gene = id_name.split("_")[0]

    # Names
    desc = entry.get("proteinDescription", {})
    rec_name = desc.get("recommendedName", {}).get("fullName", {}).get("value")
    if not rec_name:
        sub_names = desc.get("submissionNames", [])
        if sub_names:
            rec_name = sub_names[0].get("fullName", {}).get("value")
    alt_names = [a.get("fullName", {}).get("value") for a in desc.get("alternativeNames", []) if "fullName" in a]
    
    # Organism
    organism = entry.get("organism", {}).get("scientificName", "Homo sapiens")
    common_organism = entry.get("organism", {}).get("commonName", "Human")

    # Sequence
    seq_info = entry.get("sequence", {})
    sequence = seq_info.get("value", "")
    length = seq_info.get("length", len(sequence))
    mass = seq_info.get("molWeight", 0)

    # Function comments and Disease comments
    functions = []
    subcellular_locations = []
    diseases = []
    general_disease_notes = []
    pharmaceutical_notes = []
    pathways = []
    
    for comment in entry.get("comments", []):
        c_type = comment.get("commentType", "")
        if c_type == "FUNCTION":
            for text_obj in comment.get("texts", []):
                raw_func = text_obj.get("value", "")
                clean_func = re.sub(r"\s*\(PubMed:[^)]+\)", "", raw_func).strip()
                functions.append(clean_func)
        elif c_type == "SUBCELLULAR LOCATION":
            for sub in comment.get("subcellularLocations", []):
                loc = sub.get("location", {}).get("value")
                if loc:
                    subcellular_locations.append(loc)
        elif c_type == "DISEASE":
            disease_obj = comment.get("disease") or {}
            d_name = disease_obj.get("diseaseId", "")
            d_desc_obj = disease_obj.get("description")
            d_desc = ""
            if isinstance(d_desc_obj, dict):
                d_desc = d_desc_obj.get("value", "")
            elif isinstance(d_desc_obj, str):
                d_desc = d_desc_obj
            d_desc = re.sub(r"\s*\(PubMed:[^)]+\)", "", d_desc).strip()

            xref = disease_obj.get("diseaseCrossReference") or {}
            omim_id = xref.get("id", "") if xref.get("database") == "MIM" else ""
            
            note_obj = comment.get("note") or {}
            note_texts = note_obj.get("texts", []) if isinstance(note_obj, dict) else []
            raw_notes = [
                re.sub(r"\s*\(PubMed:[^)]+\)", "", t.get("value", "")).strip()
                for t in note_texts if isinstance(t, dict) and t.get("value")
            ]
            # Filter out generic boilerplate sentence when building mechanism note
            meaningful_notes = [
                n for n in raw_notes
                if n.lower() != "the disease is caused by variants affecting the gene represented in this entry."
            ]
            mech_note = " ".join(meaningful_notes).strip()

            if d_name:
                diseases.append({
                    "diseaseId": d_name,
                    "description": d_desc or mech_note,
                    "mechanismNote": mech_note,
                    "acronym": disease_obj.get("acronym", ""),
                    "omimId": omim_id
                })
            elif mech_note or d_desc:
                general_disease_notes.append(mech_note or d_desc)
        elif c_type == "PHARMACEUTICAL":
            for text_obj in comment.get("texts", []):
                p_val = re.sub(r"\s*\(PubMed:[^)]+\)", "", text_obj.get("value", "")).strip()
                if p_val:
                    pharmaceutical_notes.append(p_val)
        elif c_type == "PATHWAY":
            for text_obj in comment.get("texts", []):
                pathways.append(text_obj.get("value", ""))

    # Cross-references: Gene Ontology (GO), Orphanet, Ensembl, DrugBank, Reactome
    go_terms = {"biological_process": [], "molecular_function": [], "cellular_component": []}
    orphanet_diseases = []
    drugs = []
    ensembl_id = ""

    for ref in entry.get("uniProtKBCrossReferences", []):
        db = ref.get("database", "")
        ref_id = ref.get("id", "")
        properties = {p.get("key"): p.get("value") for p in ref.get("properties", []) if isinstance(p, dict)}

        if db == "GO":
            term_str = properties.get("GoTerm", "")
            if term_str.startswith("P:"):
                go_terms["biological_process"].append({"id": ref_id, "name": term_str[2:]})
            elif term_str.startswith("F:"):
                go_terms["molecular_function"].append({"id": ref_id, "name": term_str[2:]})
            elif term_str.startswith("C:"):
                go_terms["cellular_component"].append({"id": ref_id, "name": term_str[2:]})
        elif db == "Orphanet":
            o_disease = properties.get("Disease", "")
            if o_disease:
                orphanet_diseases.append({"orphaId": ref_id, "name": o_disease})
        elif db == "Ensembl" and not ensembl_id:
            gene_id = properties.get("GeneId", "")
            if gene_id:
                ensembl_id = gene_id.split(".")[0]
        elif db == "DrugBank":
            drug_name = properties.get("GenericName", "")
            if drug_name:
                drugs.append({"id": ref_id, "name": drug_name})
        elif db == "Reactome" and len(pathways) < 8:
            p_name = properties.get("PathwayName", "")
            if p_name and p_name not in pathways:
                pathways.append(p_name)

    # Natural variants & Mutagenesis
    variants = []
    for feat in entry.get("features", []):
        feat_type = feat.get("type", "")
        if feat_type in ["Natural variant", "Mutagenesis"]:
            loc = feat.get("location", {})
            start = loc.get("start", {}).get("value")
            end = loc.get("end", {}).get("value")
            desc_val = feat.get("description", "")
            orig_seq = feat.get("alternativeSequence", {}).get("originalSequence", "")
            alt_seqs = feat.get("alternativeSequence", {}).get("alternativeSequences", [])
            alt_str = "/".join(alt_seqs) if alt_seqs else ""
            
            # Extract change like R175H if possible
            change = f"{orig_seq}{start}{alt_str}" if (orig_seq and start and alt_str) else f"Pos {start}"
            
            variants.append({
                "type": feat_type,
                "position": start,
                "endPosition": end,
                "originalSequence": orig_seq,
                "alternativeSequence": alt_str,
                "change": change,
                "description": desc_val,
                "featureId": feat.get("featureId", "")
            })

    return {
        "accession": acc,
        "entryName": id_name,
        "ensemblId": ensembl_id,
        "geneSymbol": primary_gene,
        "synonyms": genes,
        "proteinName": rec_name or primary_gene,
        "alternativeNames": alt_names[:6],
        "organism": organism,
        "commonOrganism": common_organism,
        "length": length,
        "mass": mass,
        "sequence": sequence,
        "functions": functions,
        "subcellularLocations": list(dict.fromkeys(subcellular_locations))[:8],
        "diseases": diseases,
        "generalDiseaseNotes": general_disease_notes,
        "orphanetDiseases": orphanet_diseases,
        "drugs": drugs[:20],
        "pharmaceuticalNotes": pharmaceutical_notes,
        "pathways": pathways[:6],
        "goTerms": {
            "biologicalProcess": go_terms["biological_process"][:10],
            "molecularFunction": go_terms["molecular_function"][:10],
            "cellularComponent": go_terms["cellular_component"][:10]
        },
        "variants": variants[:50],
        "allVariants": variants
    }
