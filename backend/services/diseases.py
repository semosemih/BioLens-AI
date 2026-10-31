import re
import requests
from typing import Dict, Any, List, Optional

OPENTARGETS_GRAPHQL_URL = "https://api.platform.opentargets.org/api/v4/graphql"

# Comprehensive Physician-Grade Clinical Disease, Syndrome & Pathophysiology Atlas (Turkish)
# Covers germline syndromes, somatic malignancies, metabolic, neurological, cardiovascular,
# immunological, infectious, and pharmacogenetic conditions for major human proteins.
CLINICAL_DISEASE_ATLAS: Dict[str, List[Dict[str, Any]]] = {
    "TP53": [
        {
            "name": "Li-Fraumeni Sendromu (LFS)",
            "englishName": "Li-Fraumeni Syndrome",
            "acronym": "LFS",
            "category": "Tıbbi Genetik & Kalıtsal Onkoloji",
            "inheritance": "Otozomal Dominant (Germline)",
            "omimId": "151623",
            "orphaId": "524",
            "pathophysiology": "Germline heterozigot TP53 mutasyonları (özellikle R175H, R248Q, R273H, R249S, G245S sıcak nokta mutasyonları) DNA hasar kontrol noktasını ve p53 aracılı apoptozu bozarak erken yaşta çoklu primer malignitelere (SBLA sendromu: Sarkom, Meme, Lösemi, Adrenokortikal karsinom) yüksek penetranlı yatkınlık oluşturur.",
            "clinicalManagement": "Toronto Protokolü kapsamında yıllık tüm vücut ve beyin MRG, erken yaş meme MRG taraması, kolonoskopi ve radyoterapi maruziyetinden kaçınılması (ikincil malignite riski nedeniyle) önerilir."
        },
        {
            "name": "Meme Karsinomu (Özellikle Triple-Negatif ve HER2+ Alt Tipler)",
            "englishName": "Breast Adenocarcinoma / Triple-Negative Breast Cancer (TNBC)",
            "acronym": "TNBC / BC",
            "category": "Tıbbi Onkoloji",
            "inheritance": "Somatik (%80 TNBC) veya Germline",
            "omimId": "114480",
            "pathophysiology": "Bazal-benzeri / üçlü negatif meme kanserlerinin (TNBC) %80'inden fazlasında somatik TP53 kaybı veya dominant-negatif missense mutasyonları görülür; genomik instabilite, anöploidi ve kemoterapi direnci ile ilişkilidir.",
            "clinicalManagement": "Genç yaşta (<31 yaş) meme kanseri tanısı alan hastalarda BRCA1/2 ile eş zamanlı germline TP53 genetik testi endikedir."
        },
        {
            "name": "Yüksek Dereceli Seröz Over Karsinomu (HGSOC)",
            "englishName": "High-Grade Serous Ovarian Carcinoma",
            "acronym": "HGSOC",
            "category": "Tıbbi Onkoloji & Jinekolojik Onkoloji",
            "inheritance": "Somatik (>%95)",
            "pathophysiology": "Yüksek dereceli seröz over ve fallop tüpü karsinomlarının %96'sında erken sürücü (driver) olay olarak somatik TP53 mutasyonu (seröz tubal intraepitelyal karsinom - STIC lezyonlarından itibaren) saptanır.",
            "clinicalManagement": "İmmünohistokimyasal p53 aşırı ekspresyonu veya tam kaybı (null patern) HGSOC ayırıcı tanısında temel patolojik biyobelirteçtir."
        },
        {
            "name": "Küçük Hücreli ve Küçük Hücreli Dışı Akciğer Kanseri (SCLC / NSCLC)",
            "englishName": "Small Cell & Non-Small Cell Lung Cancer",
            "acronym": "SCLC / NSCLC",
            "category": "Tıbbi Onkoloji & Göğüs Hastalıkları",
            "inheritance": "Somatik",
            "omimId": "211980",
            "pathophysiology": "Küçük hücreli akciğer kanserlerinin (SCLC) %90'ında (RB1 kaybı ile birlikte) ve KHDAK/NSCLC vakalarının >%50'sinde tütün karsinojenlerine (benzo[a]piren kaynaklı G>T transversiyonları) bağlı TP53 mutasyonları bulunur.",
            "clinicalManagement": "EGFR-mutant akciğer kanserinde eşlik eden TP53 ko-mutasyonu, TKI tedavisine daha kısa yanıt süresi ve nöroendokrin dönüşüm riski ile ilişkilidir."
        },
        {
            "name": "Kolorektal Adenokarsinom (CRC)",
            "englishName": "Colorectal Carcinoma",
            "acronym": "CRC",
            "category": "Tıbbi Onkoloji & Gastroenteroloji",
            "inheritance": "Somatik",
            "omimId": "114500",
            "pathophysiology": "Fearon-Vogelstein adenom-karsinom sekansında (APC -> KRAS -> SMAD4 -> TP53) geç adenomdan invaziv karsinoma geçişi tetikleyen anahtar genetik basamaktır (~%60 vakada 17p delesyonu ve nokta mutasyonu).",
            "clinicalManagement": "Sol kolon ve rektum tümörlerinde kromozomal instabilite (CIN) yolağının temel göstergesidir."
        },
        {
            "name": "Glioblastoma Multiforme (GBM) ve Astrositomlar",
            "englishName": "Glioblastoma & Diffuse Astrocytoma",
            "acronym": "GBM / GLM1",
            "category": "Nöro-Onkoloji & Nöroloji",
            "inheritance": "Somatik / Germline",
            "omimId": "137800",
            "pathophysiology": "IDH-mutant diffüz astrositomlarda (ATRX ve IDH1 mutasyonları ile birlikte >%85) ve sekonder glioblastomlarda temel sürücü mutasyondur; ayrıca çocukluk çağı koroid pleksus karsinomu ve SHH-grup medulloblastomlarda görülür.",
            "clinicalManagement": "DSÖ (WHO) MSS tümör sınıflamasında IDH, ATRX ve p53 durumu tümör derecelendirmesinde kullanılır."
        },
        {
            "name": "Osteosarkom ve Yumuşak Doku Sarkomları",
            "englishName": "Osteosarcoma & Rhabdomyosarcoma",
            "acronym": "OSRC",
            "category": "Tıbbi Onkoloji & Ortopedik Onkoloji",
            "inheritance": "Somatik veya Germline (LFS)",
            "omimId": "259500",
            "pathophysiology": "Mezenkimal kök hücrelerde TP53 inaktivasyonu kromotripsis ve kompleks karyotipik yeniden düzenlenmelere yol açarak osteosarkom, leiyomiyosarkom ve anaplastik rabdomiyosarkom gelişimini hızlandırır.",
            "clinicalManagement": "Pediatrik anaplastik rabdomiyosarkom ve osteosarkomda germline TP53 taraması önerilir."
        },
        {
            "name": "Akut Miyeloid Lösemi (AML), MDS ve KLL (17p Delesyonu)",
            "englishName": "AML, Myelodysplastic Syndrome & CLL with del(17p)",
            "acronym": "AML / CLL",
            "category": "Hematoloji & Hemato-Onkoloji",
            "inheritance": "Somatik (Klonale Edinsel)",
            "pathophysiology": "Kronik Lenfositik Lösemi (KLL) ve kompleks karyotipli AML/MDS'de del(17p) ve/veya TP53 mutasyonu, konvansiyonel kemoimmünoterapiye (FCR vb.) direnç ve çok yüksek riskli klinik seyir oluşturur.",
            "clinicalManagement": "del(17p)/TP53-mutant KLL'de kemoterapi yerine BTK inhibitörleri (İbrutinib, Akalabrutinib) ve BCL-2 inhibitörü (Venetoklaks) standart tedavidir; AML'de hipometile edici ajanlar + Venetoklaks kullanılır."
        },
        {
            "name": "Adrenokortikal Karsinom (ADCC)",
            "englishName": "Adrenocortical Carcinoma",
            "acronym": "ADCC",
            "category": "Endokrinoloji & Onkoloji",
            "inheritance": "Germline veya Somatik",
            "omimId": "202300",
            "pathophysiology": "Pediatrik adrenokortikal karsinom vakalarının %50-80'inde germline TP53 mutasyonu (özellikle R337H kurucu mutasyonu) saptanır; kortizol ve androjen aşırı üretimi (Cushing + virilizasyon) ile seyreder.",
            "clinicalManagement": "Çocukluk çağı ADCC tanısı tek başına Li-Fraumeni genetik testi endikasyonudur."
        },
        {
            "name": "Özofagus, Baş-Boyun (HNSCC), Pankreas ve Hepatosellüler Karsinom",
            "englishName": "Esophageal, Head & Neck, Pancreatic and Hepatocellular Carcinoma",
            "acronym": "ESCC / HNSCC / HCC / PDAC",
            "category": "Tıbbi Onkoloji",
            "inheritance": "Somatik",
            "omimId": "133239",
            "pathophysiology": "HPV-negatif baş-boyun yassı hücreli karsinomu, özofagus kanseri, pankreas duktal adenokarsinomu (%70) ve aflatoksin B1 ilişkili hepatosellüler karsinomda (karakteristik R249S mutasyonu) anahtar tümör baskılayıcı kaybıdır.",
            "clinicalManagement": "Aflatoksin maruziyeti olan bölgelerde HCC'de TP53 R249S sıvı biyopsi (ctDNA) biyobelirteci olarak izlenir."
        },
        {
            "name": "Kemik İliği Yetmezliği Sendromu Tip 5 (BMFS5)",
            "englishName": "Bone Marrow Failure Syndrome 5",
            "acronym": "BMFS5",
            "category": "Hematoloji & Tıbbi Genetik",
            "inheritance": "Otozomal Dominant (De novo)",
            "omimId": "618165",
            "pathophysiology": "TP53'ün C-terminal bölgesini etkileyen spesifik gain-of-function varyantları aşırı p53 aktivasyonuna yol açarak pansitopeni, Diamond-Blackfan benzeri eritroid aplazi, mikrosefali ve büyüme geriliği yapar.",
            "clinicalManagement": "Klasik tümör yatkınlığından farklı olarak hematopoetik kök hücre tükenmesi ön plandadır."
        }
    ],
    "EGFR": [
        {
            "name": "Küçük Hücreli Dışı Akciğer Kanseri (KHDAK / NSCLC - Adenokarsinom)",
            "englishName": "Non-Small Cell Lung Cancer (Adenocarcinoma)",
            "acronym": "NSCLC",
            "category": "Tıbbi Onkoloji & Göğüs Hastalıkları",
            "inheritance": "Somatik (Edinsel) veya Nadir Germline (T790M)",
            "omimId": "211980",
            "pathophysiology": "Tirozin kinaz alanında (Ekzon 18-21) görülen somatik aktive edici mutasyonlar (Ekzon 19 delesyonları ve Ekzon 21 L858R nokta mutasyonu) liganddan bağımsız konstitütif reseptör dimerizasyonu ve MAPK/PI3K-AKT/STAT3 sinyal aktivasyonu ile tümör proliferasyonu sağlar.",
            "clinicalManagement": "1. basamakta 3. kuşak EGFR TKI (Osimertinib) standart tedavidir; Ekzon 20 insersiyonlarında Amivantamab veya Mobocertinib kullanılır."
        },
        {
            "name": "Glioblastoma Multiforme (GBM - EGFRvIII ve Amplifikasyon)",
            "englishName": "Glioblastoma Multiforme",
            "acronym": "GBM",
            "category": "Nöro-Onkoloji & Nöroloji",
            "inheritance": "Somatik",
            "pathophysiology": "Primer (IDH-wildtype) glioblastomların %40-50'sinde EGFR gen amplifikasyonu ve ekzon 2-7 delesyonu sonucu oluşan konstitütif aktif EGFRvIII trunkasyonu görülür.",
            "clinicalManagement": "Primer GBM moleküler tanısında kromozom 7 kazanımı / 10 kaybı (+7/-10) ve TERT promotör mutasyonu ile birlikte değerlendirilir."
        },
        {
            "name": "Metastatik Kolorektal Kanser (mCRC)",
            "englishName": "Metastatic Colorectal Cancer",
            "acronym": "mCRC",
            "category": "Tıbbi Onkoloji & Gastroenteroloji",
            "inheritance": "Somatik (Aşırı Ekspresyon)",
            "pathophysiology": "Kolorektal adenokarsinomlarda EGFR aşırı ekspresyonu, tümör anjiyogenezi, invazyon ve metastatik büyümeyi yönlendirir.",
            "clinicalManagement": "KRAS, NRAS ve BRAF wild-type (doğal tip) sol kolon tümörlerinde anti-EGFR monoklonal antikorlar (Setuksimab, Panitumumab) kemoterapi ile kombine edilir."
        },
        {
            "name": "Baş ve Boyun Yassı Hücreli Karsinomu (HNSCC)",
            "englishName": "Head and Neck Squamous Cell Carcinoma",
            "acronym": "HNSCC",
            "category": "Tıbbi Onkoloji & KBB",
            "inheritance": "Somatik",
            "pathophysiology": "HNSCC vakalarının %80-90'ında EGFR aşırı ekspresyonu saptanır ve radyoterapi direnci ile kötü prognoza katkıda bulunur.",
            "clinicalManagement": "Lokal ileri veya rekürren/metastatik HNSCC tedavisinde Setuksimab (Cetuximab) radyoterapi veya platin bazlı kemoterapi ile uygulanır."
        },
        {
            "name": "Neonatal İnflamatuar Deri ve Bağırsak Hastalığı Tip 2 (NISBD2)",
            "englishName": "Neonatal Inflammatory Skin and Bowel Disease 2",
            "acronym": "NISBD2",
            "category": "Tıbbi Genetik, Dermatoloji & Pediatrik Gastroenteroloji",
            "inheritance": "Otozomal Resesif",
            "omimId": "616069",
            "orphaId": "431166",
            "pathophysiology": "Biallelik fonksiyon kaybı (loss-of-function) EGFR mutasyonları epidermal bariyer bütünlüğünü ve intestinal epitel rejenerasyonunu bozarak yaşamın ilk aylarında püstüler dermatit, alopesi, kronik malabsorptif diyare ve enfeksiyonlara yol açar.",
            "clinicalManagement": "Sıvı-elektrolit desteği, cilt bariyeri bakımı ve sekonder bakteriyel sepsis profilaksisi gerektirir."
        }
    ],
    "BRCA1": [
        {
            "name": "Kalıtsal Meme ve Yumurtalık Kanseri Sendromu Tip 1 (HBOC)",
            "englishName": "Hereditary Breast and Ovarian Cancer Syndrome 1",
            "acronym": "HBOC / BROVCA1",
            "category": "Tıbbi Genetik & Tıbbi Onkoloji",
            "inheritance": "Otozomal Dominant",
            "omimId": "604370",
            "orphaId": "145",
            "pathophysiology": "Çift zincir DNA kırıklarının (DSB) hatasız homolog rekombinasyon (HR) ile onarımında görevli BRCA1'in patojenik varyantları homolog rekombinasyon eksikliğine (HRD) yol açar; yaşam boyu %65-75 meme kanseri (çoğunlukla TNBC) ve %40-50 seröz over kanseri riski taşır.",
            "clinicalManagement": "PARP inhibitörleri (Olaparib, Talazoparib, Niraparib) ve platin ajanları sentetik letalite mekanizmasıyla yüksek etkinlik gösterir; yoğun MRG taraması ve risk azaltıcı bilateral salpingo-ooferektomi / mastektomi seçenekleri sunulur."
        },
        {
            "name": "Fanconi Anemisi Tamamlayıcı Grup S (FANCS)",
            "englishName": "Fanconi Anemia, Complementation Group S",
            "acronym": "FANCS",
            "category": "Hematoloji & Tıbbi Genetik",
            "inheritance": "Otozomal Resesif (Biallelik)",
            "omimId": "617883",
            "pathophysiology": "Her iki BRCA1 allelinde bileşik heterozigot veya homozigot hipomorfik mutasyon bulunması durumunda kromozomal kırılganlık, mikrosefali, büyüme geriliği, konjenital anomaliler ve erken başlangıçlı solid/hematolojik tümörler gelişir.",
            "clinicalManagement": "DNA çapraz bağlayıcı ajanlara aşırı hücresel duyarlılık mevcuttur; multidisipliner genetik ve hematolojik izlem gerekir."
        },
        {
            "name": "Kalıtsal Pankreas Duktal Adenokarsinomu",
            "englishName": "Familial Pancreatic Cancer",
            "acronym": "PNCA4",
            "category": "Tıbbi Onkoloji & Gastroenteroloji",
            "inheritance": "Otozomal Dominant",
            "pathophysiology": "BRCA1/2 mutasyon taşıyıcılarında pankreas adenokarsinomu gelişim riski genel popülasyona kıyasla 2-4 kat artmıştır.",
            "clinicalManagement": "Metastatik BRCA-mutant pankreas kanserinde platin kemoterapisi sonrası Olaparib idame tedavisi kullanılır."
        },
        {
            "name": "Prostat Kanseri (Agresif / Metastatik Kastrasyona Dirençli)",
            "englishName": "Hereditary & Metastatic Castration-Resistant Prostate Cancer",
            "acronym": "mCRPC",
            "category": "Tıbbi Onkoloji & Üroloji",
            "inheritance": "Germline veya Somatik",
            "pathophysiology": "Homolog rekombinasyon onarım (HRR) gen kusuru olarak BRCA1/2 mutasyonları yüksek Gleason skorlu ve erken metastaz yapan prostat karsinomuna zemin hazırlar.",
            "clinicalManagement": "HRR/BRCA-mutant mCRPC hastalarında Olaparib veya Rucaparib hedefe yönelik tedavi seçeneğidir."
        }
    ],
    "BRCA2": [
        {
            "name": "Kalıtsal Meme ve Yumurtalık Kanseri Sendromu Tip 2 (BROVCA2)",
            "englishName": "Familial Breast-Ovarian Cancer Susceptibility 2",
            "acronym": "BROVCA2",
            "category": "Tıbbi Genetik & Tıbbi Onkoloji",
            "inheritance": "Otozomal Dominant",
            "omimId": "612555",
            "pathophysiology": "RAD51 filamentlerinin hasarlı DNA'ya yüklenmesini sağlayan BRCA2 kaybı homolog rekombinasyon yetmezliğine (HRD) yol açar; kadın meme kanseri (%60-70, çoğunlukla ER+ luminal tip), erkek meme kanseri (%6-8) ve over kanseri (%15-25) riskini artırır.",
            "clinicalManagement": "PARP inhibitörleri (Olaparib, Niraparib, Talazoparib) ile hedefli tedavi ve yüksek riskli genetik tarama protokolleri uygulanır."
        },
        {
            "name": "Fanconi Anemisi Tamamlayıcı Grup D1 (FANCD1)",
            "englishName": "Fanconi Anemia, Complementation Group D1",
            "acronym": "FANCD1",
            "category": "Hematoloji & Pediatrik Onkoloji",
            "inheritance": "Otozomal Resesif",
            "omimId": "605724",
            "pathophysiology": "Biallelik BRCA2 mutasyonları ağır kemik iliği yetmezliği ve yaşamın ilk 5 yılında medulloblastom, Wilms tümörü ve akut lösemi gelişimine neden olur.",
            "clinicalManagement": "Hematopoetik kök hücre nakli ve erken pediatrik onkolojik sürveyans gerektirir."
        },
        {
            "name": "Metastatik Prostat ve Pankreas Adenokarsinomu",
            "englishName": "Prostate & Pancreatic Adenocarcinoma",
            "acronym": "PRCA / PNCA2",
            "category": "Tıbbi Onkoloji",
            "inheritance": "Otozomal Dominant / Somatik",
            "omimId": "613029",
            "pathophysiology": "BRCA2, kalıtsal pankreas kanseri ve agresif prostat kanserinde en sık saptanan yüksek penetranlı DNA onarım genidir.",
            "clinicalManagement": "Platin bazlı kemoterapi ve PARP inhibitörlerine yüksek klinik duyarlılık gösterir."
        }
    ],
    "INS": [
        {
            "name": "Tip 1 Diabetes Mellitus (T1DM - Otoimmün Beta Hücre Yıkımı)",
            "englishName": "Type 1 Diabetes Mellitus & Diabetic Ketoacidosis",
            "acronym": "T1DM",
            "category": "Endokrinoloji ve Metabolizma",
            "inheritance": "Poligenik / Otoimmün (IDDM2 lokusu)",
            "omimId": "125852",
            "pathophysiology": "Pankreas Langerhans adacıklarındaki beta hücrelerinin T-hücre aracılı otoimmün yıkımı (anti-GAD, anti-insülin/IAA, anti-IA2 otoantikorları) sonucu mutlak endojen insülin eksikliği, hiperglisemi ve tedavi edilmezse diyabetik ketoasidoz (DKA) gelişir; INS gen promotör VNTR polimorfizmleri (IDDM2) timik insülin toleransını etkiler.",
            "clinicalManagement": "Bazal-bolus rekombinant insülin analogları (Glargin, Detemir, Degludek, Lispro, Aspart) veya sürekli cilt altı insülin infüzyonu (pompa) ve sürekli glikoz izlemi (CGM) zorunludur."
        },
        {
            "name": "Tip 2 Diabetes Mellitus (T2DM) ve İnsülin Sekresyon Kusuru",
            "englishName": "Type 2 Diabetes Mellitus & Metabolic Syndrome",
            "acronym": "T2DM",
            "category": "Endokrinoloji ve Metabolizma",
            "inheritance": "Poligenik / Multifaktöriyel",
            "pathophysiology": "Periferik dokularda (iskelet kası, karaciğer, adipoz doku) insülin direnci ile başlayan süreçte zamanla pankreatik beta hücrelerinde glikoza yanıt olarak birinci faz insülin sekresyonunun bozulması ve rölatif insülin yetmezliği gelişir.",
            "clinicalManagement": "Yaşam tarzı değişikliği, Metformin, SGLT2 inhibitörleri, GLP-1 reseptör agonistleri ve ileri evrede bazal/yoğun insülin replasmanı uygulanır."
        },
        {
            "name": "Kalıcı Neonatal Diabetes Mellitus Tip 4 (PNDM4)",
            "englishName": "Permanent Neonatal Diabetes Mellitus 4",
            "acronym": "PNDM4",
            "category": "Pediatrik Endokrinoloji & Tıbbi Genetik",
            "inheritance": "Otozomal Dominant veya Otozomal Resesif",
            "omimId": "618858",
            "orphaId": "99885",
            "pathophysiology": "Preproinsülin sinyal peptidi veya A/B zincirleri arasındaki disülfit bağlarını (örn. C96Y Akita mutasyonu) bozan INS gen mutasyonları, yanlış katlanmış proinsülinin endoplazmik retikulumda birikmesine, şiddetli ER stresine ve yaşamın ilk 6 ayında beta hücre apoptozuna yol açar.",
            "clinicalManagement": "Otoantikor-negatif bebeklerde (<6 ay) genetik tanı konulur ve ömür boyu insülin replasmanı yapılır."
        },
        {
            "name": "Gençlerin Erişkin Tipi Diyabeti Tip 10 (MODY10)",
            "englishName": "Maturity-Onset Diabetes of the Young, Type 10",
            "acronym": "MODY10",
            "category": "Endokrinoloji & Tıbbi Genetik",
            "inheritance": "Otozomal Dominant",
            "omimId": "613370",
            "pathophysiology": "Heterozigot INS mutasyonları proinsülin işlenmesini veya reseptör bağlanma afinitesini kısmen bozarak çocukluk veya genç erişkin dönemde obezite olmaksızın otozomal dominant kalıtılan monogenik diyabete neden olur.",
            "clinicalManagement": "Ailesel erken başlangıçlı otoantikor-negatif diyabet olgularında MODY paneli ile tanı konur."
        },
        {
            "name": "Ailesel Hiperproinsülinemi ve Mutant İnsülin Sendromu",
            "englishName": "Familial Hyperproinsulinemia",
            "acronym": "HPRI",
            "category": "Endokrinoloji ve Metabolizma",
            "inheritance": "Otozomal Dominant",
            "omimId": "616214",
            "pathophysiology": "Proinsülinin C-peptit ayrılma bölgelerindeki (Arg65 veya His34) nokta mutasyonları prohormon konvertaz kesimini engelleyerek dolaşımda biyolojik aktivitesi düşük proinsülin birikimine ve hafif/orta diyabete yol açar.",
            "clinicalManagement": "Yüksek serum proinsülin/insülin oranı ile karakterizedir; oral antidiyabetikler veya düşük doz insülin ile izlenir."
        }
    ],
    "CFTR": [
        {
            "name": "Kistik Fibrozis (Klasik Multiorgan Fenotip)",
            "englishName": "Cystic Fibrosis",
            "acronym": "CF",
            "category": "Göğüs Hastalıkları, Pediatri & Tıbbi Genetik",
            "inheritance": "Otozomal Resesif",
            "omimId": "219700",
            "orphaId": "586",
            "pathophysiology": "Epitel hücre apikal membranındaki cAMP-bağımlı klor ve bikarbonat kanalını kodlayan CFTR geninde biallelik mutasyonlar (en sık Sınıf II p.Phe508del / ΔF508) mukus dehidratasyonuna yol açar; kronik bronşektazi, Pseudomonas aeruginosa kolonizasyonu, ekzokrin pankreas yetmezliği, mekonyum ileusu ve biliyer siroz gelişir.",
            "clinicalManagement": "Ter testi (Cl > 60 mmol/L) ve genetik analizle tanı konur; CFTR modülatör tedavileri (Elexacaftor / Tezacaftor / Ivacaftor - Trikafta; G551D için Ivacaftor) kanal fonksiyonunu doğrudan restore eder."
        },
        {
            "name": "Konjenital Bilateral Vas Deferens Yokluğu (CBAVD)",
            "englishName": "Congenital Bilateral Absence of the Vas Deferens",
            "acronym": "CBAVD",
            "category": "Üroloji & Tıbbi Genetik",
            "inheritance": "Otozomal Resesif (CFTR İlişkili Bozukluk)",
            "omimId": "277180",
            "orphaId": "48",
            "pathophysiology": "Hafif CFTR varyantları (örn. IVS8-5T alleli ile birlikte ağır mutasyon) akciğer veya pankreas tutulumu olmaksızın Wolff kanalı türevlerinin gelişimini bozarak obstrüktif azoospermi ve erkek infertilitesine neden olur.",
            "clinicalManagement": "Testiküler sperm ekstraksiyonu (TESE) + ICSI öncesi eşlere mutlaka CFTR taşıyıcılık taraması ve genetik danışmanlık verilir."
        },
        {
            "name": "İdiyopatik Kronik ve Rekürren Akut Pankreatit",
            "englishName": "Hereditary / Idiopathic Chronic Pancreatitis",
            "acronym": "ICP",
            "category": "Gastroenteroloji",
            "inheritance": "Otozomal Resesif / Kompleks",
            "pathophysiology": "Pankreas duktal hücrelerinde CFTR aracılı bikarbonat sekresyonunun azalması, duktal lümen pH'sını düşürerek sindirim zimojenlerinin erken aktivasyonuna, protein tıkaçlarına ve tekrarlayan pankreatit ataklarına yol açar.",
            "clinicalManagement": "PRSS1, SPINK1 ve CTRC genleri ile birlikte CFTR varyant analizi yapılır."
        },
        {
            "name": "Yaygın Bronşektazi ve Kronik Rinosinüzit (CFTR-RD)",
            "englishName": "CFTR-Related Disseminated Bronchiectasis & Chronic Rhinosinusitis",
            "acronym": "CFTR-RD",
            "category": "Göğüs Hastalıkları & KBB",
            "inheritance": "Otozomal Resesif / Heterozigot Risk",
            "pathophysiology": "Rezidüel CFTR fonksiyonu korunan atipik mutasyonlarda erişkin yaşta başlayan izole silindirik bronşektazi, nazal polipozis ve alerjik bronkopulmoner aspergillozis (ABPA) yatkınlığı görülür.",
            "clinicalManagement": "Mukolitik tedavi (Dornaz alfa, hipertonik salin) ve hava yolu temizleme teknikleri uygulanır."
        }
    ],
    "ACE2": [
        {
            "name": "COVID-19 (SARS-CoV-2 Enfeksiyonu) ve Akut Respiratuar Distres Sendromu (ARDS)",
            "englishName": "COVID-19 Viral Entry & Severe Acute Respiratory Distress Syndrome",
            "acronym": "COVID-19 / ARDS",
            "category": "Enfeksiyon Hastalıkları & Göğüs Hastalıkları",
            "inheritance": "Edinsel Enfeksiyon / Konak Genetik Duyarlılığı",
            "pathophysiology": "ACE2, SARS-CoV-2 ve SARS-CoV-1 spike (S) glikoproteininin tip II pnömositler, vasküler endotel ve enterositlere girişi için birincil fonksiyonel reseptördür. Virüs bağlanması yüzey ACE2'yi aşağı regüle ederek koruyucu Ang-(1-7)/Mas eksenini baskılar, Angiotensin II birikimiyle pulmoner ödem, endotelit, mikrotromboz ve ARDS'yi tetikler.",
            "clinicalManagement": "Rekombinant çözünür insan ACE2 (hrsACE2) tuzak reseptör çalışmaları ve spike-ACE2 bağlanmasını bloke eden nötralizan monoklonal antikorlar/aşılar temel hedeftir."
        },
        {
            "name": "Esansiyel Hipertansiyon ve Renin-Anjiyotensin-Aldosteron Sistemi (RAAS) Dengesizliği",
            "englishName": "Essential Hypertension & Vascular Remodeling",
            "acronym": "HT",
            "category": "Kardiyoloji & Nefroloji",
            "inheritance": "Poligenik / X Kromozomu (Xp22.2)",
            "pathophysiology": "ACE2, vazokonstriktör ve profibrotik Angiotensin II'yi vazodilatör, natriüretik ve antiproliferatif Angiotensin-(1-7) peptidine dönüştürerek klasik ACE/Ang-II/AT1R eksenini dengeler. Azalmış ACE2 ekspresyonu sistemik hipertansiyon, endotel disfonksiyonu ve damar sertliğine yol açar.",
            "clinicalManagement": "ACE inhibitörleri ve Anjiyotensin Reseptör Blokerleri (ARB) kompansatuar olarak doku ACE2 ekspresyonunu ve kardiyovasküler korumayı destekler."
        },
        {
            "name": "Kalp Yetmezliği (HFrEF / HFpEF) ve Miyokardiyal Fibrozis",
            "englishName": "Heart Failure, Myocardial Hypertrophy & Fibrosis",
            "acronym": "HF",
            "category": "Kardiyoloji",
            "inheritance": "Poligenik / Edinsel",
            "pathophysiology": "Kardiyomiyosit ve kardiyak fibroblastlarda ACE2 eksikliği, Angiotensin II aracılı TGF-β aktivasyonunu artırarak sol ventrikül hipertrofisi, interstisyel fibrozis ve diyastolik/sistolik kalp yetmezliğini hızlandırır; plazma çözünür ACE2 (sACE2) düzeyi kalp yetmezliğinde prognostik biyobelirteçtir.",
            "clinicalManagement": "RAAS blokajı (ARNI, ACEi, ARB, MRA) ile patolojik ventriküler yeniden şekillenme (remodeling) baskılanır."
        },
        {
            "name": "Diyabetik Nefropati ve Kronik Böbrek Hastalığı (KBH)",
            "englishName": "Diabetic Nephropathy & Glomerulosclerosis",
            "acronym": "DN / CKD",
            "category": "Nefroloji & Endokrinoloji",
            "inheritance": "Poligenik / Metabolik",
            "pathophysiology": "Glomerüler podositler ve proksimal tübül epitelinde yüksek düzeyde eksprese edilen ACE2'nin diyabette kaybı, intraglomerüler hipertansiyon, mezangiyal matriks artışı, proteinüri (albüminüri) ve progresif glomerüloskleroza neden olur.",
            "clinicalManagement": "RAAS blokerleri ve SGLT2 inhibitörleri ile intraglomerüler basınç düşürülerek nefron koruması sağlanır."
        },
        {
            "name": "Pulmoner Arteriyel Hipertansiyon (PAH)",
            "englishName": "Pulmonary Arterial Hypertension",
            "acronym": "PAH",
            "category": "Göğüs Hastalıkları & Kardiyoloji",
            "inheritance": "Edinsel / Poligenik",
            "pathophysiology": "Pulmoner vasküler endotelde ACE2/Ang-(1-7) aktivitesinin azalması pulmoner arter düz kas proliferasyonu ve pulmoner vasküler direnç artışına katkıda bulunur.",
            "clinicalManagement": "ACE2 aktivatörleri ve rekombinant ACE2 pulmoner vasküler direnci azaltmaya yönelik klinik araştırmalarda incelenmektedir."
        }
    ],
    "APOE": [
        {
            "name": "Geç Başlangıçlı Alzheimer Hastalığı (LOAD - APOE ε4 Risk Alleli)",
            "englishName": "Late-Onset Alzheimer Disease (Susceptibility 2)",
            "acronym": "AD2 / LOAD",
            "category": "Nöroloji & Nörodejenerasyon",
            "inheritance": "Kompleks / Semidominant Genetik Risk",
            "omimId": "104310",
            "pathophysiology": "APOE-ε4 izoformu (Cys112Arg), beyinde Amiloid-beta (Aβ42) peptitlerinin kan-beyin bariyeri ve mikroglial temizlenmesini bozarak senil amiloid plak birikimini, tau hiperfosforilasyonunu ve sinaptik kaybı hızlandırır. Tek ε4 alleli riski 3-4 kat, homozigot ε4/ε4 genotipi ise 12-15 kat artırır (ε2 alleli ise koruyucudur).",
            "clinicalManagement": "Anti-amiloid monoklonal antikor (Lecanemab, Donanemab) tedavisi öncesi ARIA (Amiloid İlişkili Görüntüleme Anormallikleri - beyin ödemi/mikrokanama) riski ε4 homozigotlarında yüksek olduğundan APOE genotiplemesi zorunlu klinik testtir."
        },
        {
            "name": "Tip III Hiperlipoproteinemi (Ailesel Disbetalipoproteinemi)",
            "englishName": "Hyperlipoproteinemia, Type III (Familial Dysbetalipoproteinemia)",
            "acronym": "HLPP3",
            "category": "Endokrinoloji, Kardiyoloji & Metabolizma",
            "inheritance": "Otozomal Resesif (APOE ε2/ε2) veya Nadir Dominant",
            "omimId": "617347",
            "orphaId": "412",
            "pathophysiology": "APOE-ε2 (Arg158Cys) homozigotluğunda ApoE'nin hepatik LDL ve LRP1 reseptörlerine bağlanma afinitesi <%2'ye düşer; dolaşımda kolesterolce zengin şilomikron ve VLDL kalıntıları (IDL / beta-VLDL) birikir, palmar/tüberöz ksantomlar ve erken koroner/periferik arter hastalığı gelişir.",
            "clinicalManagement": "Statin + Fibrat kombinasyonu, diyetle doymuş yağ/alkol kısıtlaması ve eşlik eden diyabet/hipotiroidinin tedavisi ile lipid düzeyleri kontrol altına alınır."
        },
        {
            "name": "Serebral Amiloid Anjiyopati (CAA) ve Lober İntraserebral Kanama",
            "englishName": "Cerebral Amyloid Angiopathy",
            "acronym": "CAA",
            "category": "Nöroloji & Serebrovasküler Hastalıklar",
            "inheritance": "Genetik Risk (APOE ε4 ve ε2)",
            "pathophysiology": "Serebral korteks ve leptomeningeal arteriyol duvarlarında amiloid-beta birikimini hızlandırarak damar duvarı frajilitesi, kortikal mikrokanamalar, yüzeyel siderozis ve tekrarlayan lober intraserebral hemorajilere yol açar.",
            "clinicalManagement": "Yaşlı hastalarda antikoagülan kullanımı ve anti-amiloid tedavilerde beyin MRG (SWI/GRE sekansları) ile yakın mikrokanama takibi gerektirir."
        },
        {
            "name": "Aterosklerotik Kardiyovasküler Hastalık ve Koroner Arter Hastalığı (KAH)",
            "englishName": "Coronary Artery Disease & Hypercholesterolemia",
            "acronym": "CAD / ASCVD",
            "category": "Kardiyoloji",
            "inheritance": "Poligenik / Multifaktöriyel",
            "pathophysiology": "APOE-ε4 alleli plazma toplam kolesterol, LDL-kolesterol ve ApoB düzeylerini artırarak koroner ateroskleroz, miyokard enfarktüsü ve karotis plak progresyonu riskini yükseltir.",
            "clinicalManagement": "LDL-K hedeflerine ulaşmak için yüksek yoğunluklu statin, Ezetimib ve PCSK9 inhibitörleri kullanılır."
        },
        {
            "name": "Lewy Cisimcikli Demans (DLB) ve Parkinson Hastalığı Demansı",
            "englishName": "Dementia with Lewy Bodies",
            "acronym": "DLB",
            "category": "Nöroloji",
            "inheritance": "Genetik Risk Faktörü",
            "pathophysiology": "APOE-ε4 alleli, amiloid patolojisinden bağımsız olarak alfa-sinüklein (Lewy cisimciği) agregasyonunu da doğrudan artırarak Lewy cisimcikli demans ve Parkinson demansı gelişimini hızlandırır.",
            "clinicalManagement": "Kognitif semptomlar için kolinesteraz inhibitörleri (Rivastigmin, Donepezil) kullanılır; tipik antipsikotiklerden kaçınılır."
        },
        {
            "name": "Lipoprotein Glomerülopatisi (LPG) ve Deniz Mavisi Histiyosit Sendromu",
            "englishName": "Lipoprotein Glomerulopathy & Sea-Blue Histiocytosis",
            "acronym": "LPG",
            "category": "Nefroloji & Hematoloji",
            "inheritance": "Otozomal Dominant (Nadir Varyantlar: ApoE Sendai, Kyoto)",
            "omimId": "611771",
            "orphaId": "84065",
            "pathophysiology": "Spesifik nadir APOE missense mutasyonları glomerüler kapiller lümende lipoprotein trombüsleri oluşturarak nefrotik sendrom ve böbrek yetmezliğine, veya dalak/kemik iliğinde lipid yüklü makrofaj birikimine (splenomegali, trombositopeni) yol açar.",
            "clinicalManagement": "Renal biyopsi ve APOE sekanslaması ile tanı konur; fenofibrat tedavisi proteinüriyi azaltabilir."
        }
    ],
    "BRAF": [
        {
            "name": "Kutanöz Malign Melanom (V600E / V600K Mutasyonu)",
            "englishName": "Cutaneous Malignant Melanoma",
            "acronym": "CMM",
            "category": "Tıbbi Onkoloji & Dermatoloji",
            "inheritance": "Somatik (~%50)",
            "omimId": "155600",
            "pathophysiology": "Kinaz aktivasyon halkasındaki somatik p.Val600Glu (V600E) veya p.Val600Lys (V600K) mutasyonu, B-Raf kinaz aktivitesini 500 kat artırarak RAS'tan bağımsız monomerik MEK/ERK (MAPK) sinyalizasyonu ve kontrolsüz melanosit proliferasyonu sağlar.",
            "clinicalManagement": "BRAF inhibitörü + MEK inhibitörü kombinasyon tedavisi (Dabrafenib + Trametinib, Vemurafenib + Kobimetinib veya Enkorafenib + Binimetinib) ve İmmün Kontrol Noktası İnhibitörleri (Nivolumab + İpilimumab) standarttır."
        },
        {
            "name": "Papiller ve Anaplastik Tiroid Karsinomu (PTC / ATC)",
            "englishName": "Papillary & Anaplastic Thyroid Carcinoma",
            "acronym": "PTC / ATC",
            "category": "Endokrinoloji & Tıbbi Onkoloji",
            "inheritance": "Somatik (%45-60)",
            "pathophysiology": "BRAF V600E, papiller tiroid karsinomunda en sık saptanan onkojenik mutasyondur; sodyum-iyodür simporter (NIS) ekspresyonunu baskılayarak radyoaktif iyot (RAİ) tedavisine direnç, ekstratiroidal yayılım ve lenf nodu metastazı ile ilişkilidir.",
            "clinicalManagement": "BRAF V600E-mutant anaplastik tiroid karsinomunda Dabrafenib + Trametinib kombinasyonu dramatik klinik yanıt sağlar; tiroid İİAB sitolojisinde moleküler tanı belirtecidir."
        },
        {
            "name": "Metastatik Kolorektal Kanser (BRAF V600E & MSI-H Spektrumu)",
            "englishName": "Metastatic Colorectal Adenocarcinoma",
            "acronym": "mCRC",
            "category": "Tıbbi Onkoloji & Gastroenteroloji",
            "inheritance": "Somatik (%8-12)",
            "omimId": "114500",
            "pathophysiology": "Özellikle sağ kolon yerleşimli, sapsız tırtıklı adenom (sessile serrated) kökenli tümörlerde görülür; MLH1 promotör hipermetilasyonu yoluyla sporadik mikrosatellit instabilitesi (MSI-H) ile güçlü birliktelik gösterir.",
            "clinicalManagement": "Tek başına BRAF inhibisyonu EGFR geri bildirim aktivasyonu nedeniyle etkisizdir; Enkorafenib (BRAFi) + Setuksimab (anti-EGFR) kombinasyonu standart hedefli tedavidir. Ayrıca Lynch sendromu ayırıcı tanısında MLH1 kaybı olan tümörlerde BRAF V600E pozitifliği sporadik kökeni kanıtlar."
        },
        {
            "name": "Tüylü Hücreli Lösemi (Hairy Cell Leukemia - HCL)",
            "englishName": "Hairy Cell Leukemia",
            "acronym": "HCL",
            "category": "Hematoloji & Hemato-Onkoloji",
            "inheritance": "Somatik (~%100)",
            "pathophysiology": "Klasik Tüylü Hücreli Lösemi olgularının neredeyse tamamında (%97-100) tanımlayıcı moleküler genetik lezyon olarak somatik BRAF V600E mutasyonu bulunur; splenomegali, pansitopeni ve kemik iliği fibrozisi (dry tap) yapar.",
            "clinicalManagement": "Tanıda altın standart moleküler doğrulama testidir; pürin analoglarına (Kladribin) dirençli/nüks vakalarda Vemurafenib + Rituksimab çok yüksek tam remisyon sağlar."
        },
        {
            "name": "Küçük Hücreli Dışı Akciğer Kanseri (KHDAK / NSCLC)",
            "englishName": "Non-Small Cell Lung Cancer (BRAF-mutant)",
            "acronym": "NSCLC",
            "category": "Tıbbi Onkoloji & Göğüs Hastalıkları",
            "inheritance": "Somatik (%2-4)",
            "pathophysiology": "Akciğer adenokarsinomlarının %2-4'ünde BRAF V600E ve non-V600 mutasyonları saptanır.",
            "clinicalManagement": "BRAF V600E pozitif metastatik KHDAK'de Dabrafenib + Trametinib onaylı hedefe yönelik tedavidir."
        },
        {
            "name": "Erdheim-Chester Hastalığı ve Langerhans Hücreli Histiyositoz (LCH)",
            "englishName": "Erdheim-Chester Disease & Langerhans Cell Histiocytosis",
            "acronym": "ECD / LCH",
            "category": "Hematoloji & Romatoloji",
            "inheritance": "Somatik (%50-60)",
            "pathophysiology": "Miyeloid öncül hücrelerde BRAF V600E mutasyonu sonucu klonal histiyositik infiltrasyon, osteosklerotik kemik lezyonları, perinefrik tutulum ('hairy kidney'), diyabetes insipidus ve kardiyovasküler infiltrasyon gelişir.",
            "clinicalManagement": "Vemurafenib, BRAF-mutant Erdheim-Chester hastalığı için FDA onaylı hedefe yönelik tedavidir."
        },
        {
            "name": "Pediatrik Düşük ve Yüksek Dereceli Gliomlar (Pilositik Astrositom, PXA)",
            "englishName": "Pilocytic Astrocytoma, Pleomorphic Xanthoastrocytoma & Ganglioglioma",
            "acronym": "LGG / HGG",
            "category": "Nöro-Onkoloji & Pediatrik Nöroloji",
            "inheritance": "Somatik (KIAA1549-BRAF Füzyonu veya V600E)",
            "pathophysiology": "Serebellar pilositik astrositomlarda KIAA1549-BRAF gen füzyonu, pleomorfik ksantoastrositom ve gangliogliomlarda ise BRAF V600E mutasyonu temel sürücüdür.",
            "clinicalManagement": "BRAF V600E mutant pediatrik gliomlarda Dabrafenib + Trametinib yüksek objektif yanıt oranı sağlar."
        },
        {
            "name": "Kardiyofasiyokutanöz Sendrom (CFC), Noonan Sendromu Tip 7 ve LEOPARD Sendromu Tip 3",
            "englishName": "Cardiofaciocutaneous Syndrome, Noonan Syndrome 7 & LEOPARD Syndrome 3",
            "acronym": "CFC1 / NS7",
            "category": "Tıbbi Genetik, Pediatrik Kardiyoloji & Nöroloji",
            "inheritance": "Otozomal Dominant (De novo Germline RASopati)",
            "omimId": "115150",
            "orphaId": "1340",
            "pathophysiology": "Germline BRAF mutasyonları gelişimsel RAS-MAPK yolağı hiperaktivasyonuna (RASopati) neden olarak pulmoner kapak stenozu, hipertrofik kardiyomiyopati, tipik kraniyofasiyal dismorfizm, boy kısalığı, ektodermal/deri anomalileri ve nörogelişimsel gerilik tablosu oluşturur.",
            "clinicalManagement": "Ekokardiyografik izlem, büyüme/beslenme desteği ve multidisipliner genetik takip yapılır."
        }
    ],
    "KRAS": [
        {
            "name": "Pankreas Duktal Adenokarsinomu (PDAC)",
            "englishName": "Pancreatic Ductal Adenocarcinoma",
            "acronym": "PDAC",
            "category": "Tıbbi Onkoloji & Gastroenteroloji",
            "inheritance": "Somatik (>%90)",
            "omimId": "260350",
            "pathophysiology": "Pankreas kanserlerinin %90-95'inde (en sık G12D, G12V ve G12R) GTPaz aktivitesini bozarak KRAS'ı kalıcı aktif GTP-bağlı formda kilitleyen kurucu somatik mutasyonlardır.",
            "clinicalManagement": "G12C alt tipinde Sotorasib/Adagrasib, G12D ve pan-KRAS inhibitörleri klinik geliştirme/uygulama aşamasındadır."
        },
        {
            "name": "Metastatik Kolorektal Karsinom (mCRC)",
            "englishName": "Colorectal Adenocarcinoma",
            "acronym": "CRC",
            "category": "Tıbbi Onkoloji",
            "inheritance": "Somatik (%40-45)",
            "omimId": "114500",
            "pathophysiology": "Ekzon 2 (kodon 12/13), Ekzon 3 (kodon 61) ve Ekzon 4 (kodon 146) mutasyonları EGFR'den bağımsız aşağı akış sinyalizasyonu başlatır.",
            "clinicalManagement": "KRAS mutasyonu varlığı anti-EGFR antikorlara (Setuksimab, Panitumumab) primer direnç göstergesidir; tedavi öncesi zorunlu prediktif biyobelirteçtir."
        },
        {
            "name": "Küçük Hücreli Dışı Akciğer Kanseri (KHDAK - KRAS G12C)",
            "englishName": "Non-Small Cell Lung Cancer (Lung Adenocarcinoma)",
            "acronym": "NSCLC",
            "category": "Tıbbi Onkoloji & Göğüs Hastalıkları",
            "inheritance": "Somatik (%25-30)",
            "omimId": "211980",
            "pathophysiology": "Sigara ilişkili akciğer adenokarsinomlarında en sık görülen sürücü onkogendir; özellikle p.Gly12Cys (G12C) mutasyonu vakaların ~%13'ünü oluşturur.",
            "clinicalManagement": "KRAS G12C spesifik kovalent inhibitörler (Sotorasib ve Adagrasib) ileri evre KHDAK'de onaylı hedefe yönelik tedavilerdir."
        },
        {
            "name": "Noonan Sendromu Tip 3 ve Kardiyofasiyokutanöz Sendrom Tip 2 (RASopati)",
            "englishName": "Noonan Syndrome 3 & CFC Syndrome 2",
            "acronym": "NS3 / CFC2",
            "category": "Tıbbi Genetik & Pediatrik Kardiyoloji",
            "inheritance": "Otozomal Dominant (Germline)",
            "omimId": "609942",
            "pathophysiology": "Germline KRAS mutasyonları konjenital kalp hastalıkları, hipertrofik kardiyomiyopati, boy kısalığı ve Juvenil Miyelomonositik Lösemi (JMML) yatkınlığına yol açar.",
            "clinicalManagement": "Pediatrik kardiyoloji ve hematoloji sürveyansı gerektirir."
        }
    ],
    "ERBB2": [
        {
            "name": "HER2-Pozitif Meme Karsinomu",
            "englishName": "HER2-Positive Breast Cancer",
            "acronym": "HER2+ BC",
            "category": "Tıbbi Onkoloji",
            "inheritance": "Somatik (Amplifikasyon / Aşırı Ekspresyon)",
            "pathophysiology": "Meme kanserlerinin %15-20'sinde 17q12 kromozom bölgesindeki ERBB2 (HER2) gen amplifikasyonu reseptör sayısını 40-100 kat artırarak agresif tümör büyümesi ve beyin/visseral metastaz eğilimi yaratır.",
            "clinicalManagement": "Trastuzumab, Pertuzumab, Trastuzumab Derukstekan (T-DXd - HER2-low dahil), T-DM1 ve Tukatinib/Lapatinib ile hedefe yönelik anti-HER2 tedavi uygulanır."
        },
        {
            "name": "HER2-Pozitif Mide ve Gastroözofageal Bileşke Adenokarsinomu",
            "englishName": "Gastric & Gastroesophageal Junction Adenocarcinoma",
            "acronym": "GC / GEJ",
            "category": "Tıbbi Onkoloji & Gastroenteroloji",
            "inheritance": "Somatik",
            "pathophysiology": "İleri evre gastrik/GÖB adenokarsinomlarının %15-20'sinde (özellikle intestinal tipte) HER2 amplifikasyonu görülür.",
            "clinicalManagement": "1. basamakta Trastuzumab + Pembrolizumab + Kemoterapi ve 2. basamakta Trastuzumab Derukstekan standarttır."
        },
        {
            "name": "ERBB2 Ekzon 20 Mutant Küçük Hücreli Dışı Akciğer Kanseri",
            "englishName": "HER2-Mutant Non-Small Cell Lung Cancer",
            "acronym": "NSCLC",
            "category": "Tıbbi Onkoloji",
            "inheritance": "Somatik",
            "omimId": "211980",
            "pathophysiology": "Sigara içmeyen akciğer adenokarsinomu hastalarının %2-4'ünde ERBB2 tirozin kinaz alanı (Ekzon 20 YVMA insersiyonları) aktive edici mutasyonları saptanır.",
            "clinicalManagement": "Trastuzumab Derukstekan (T-DXd), HER2-mutant metastatik KHDAK için onaylı antikor-ilaç konjugatıdır."
        }
    ],
    "HBB": [
        {
            "name": "Orak Hücreli Anemi (Sickle Cell Disease - HbS)",
            "englishName": "Sickle Cell Anemia",
            "acronym": "SCD / HbSS",
            "category": "Hematoloji & Tıbbi Genetik",
            "inheritance": "Otozomal Resesif",
            "omimId": "603903",
            "orphaId": "232",
            "pathophysiology": "Beta-globin 6. kodonunda hidrofilik glutamik asidin hidrofobik valine dönüşümü (p.Glu6Val / E6V) sonucu oluşan HbS, deoksijene durumda polimerize olarak eritrositlerin oraklaşmasına, kronik hemolitik anemiye, vazo-oklüzif ağrılı krizlere, akut göğüs sendromuna, fonksiyonel aspleniye ve inmeye neden olur.",
            "clinicalManagement": "Hidroksiüre (HbF indüksiyonu), L-glutamin, Voxelotor, Crizanlizumab, eritrosit değişim transfüzyonu, allojenik kök hücre nakli ve CRISPR/Cas9 gen düzenleme tedavisi (Exagamglogene autotemcel - Casgevy) kullanılır."
        },
        {
            "name": "Beta-Talasemi (Majör / İntermedia / Minör)",
            "englishName": "Beta-Thalassemia Major, Intermedia & Minor",
            "acronym": "β-Talasemi",
            "category": "Hematoloji & Tıbbi Genetik",
            "inheritance": "Otozomal Resesif (Nadir Dominant)",
            "omimId": "613985",
            "orphaId": "848",
            "pathophysiology": "HBB genindeki сплайсинг (IVS-I-110 vb.), promotör veya anlamsız (nonsense) mutasyonlar beta-globin sentezini azaltır (β+) veya tamamen durdurur (β0). Eşleşmeyen alfa-globin zincirleri eritroid öncüllerde çökerek inefektif eritropoez, ağır hipokrom mikrositer anemi, ekstramedüller hematopoez, hepatosplenomegali ve demir yüklenmesine yol açar.",
            "clinicalManagement": "Düzenli eritrosit transfüzyonu + demir şelasyonu (Deferasiroks, Deferoksamin), Luspatercept, kök hücre nakli ve gen tedavisi (Betibeglogene autotemcel / Casgevy) uygulanır."
        },
        {
            "name": "Methemoglobinemi (Beta-Globin Tipi - HbM Hastalığı)",
            "englishName": "Methemoglobinemia, Beta-Globin Type",
            "acronym": "HbM",
            "category": "Hematoloji",
            "inheritance": "Otozomal Dominant",
            "omimId": "617971",
            "pathophysiology": "Hem cebindeki proksimal veya distal histidin kalıntılarının tirozine dönüşmesi, demir atomunu ferrik (Fe3+) formda stabilize ederek oksijen taşınmasını bozar ve doğuştan siyanoza neden olur.",
            "clinicalManagement": "Kardiyopulmoner siyanoz nedenlerinden ayırıcı tanısı hemoglobin elektroforezi ve ko-oksimetri ile yapılır."
        },
        {
            "name": "Hemoglobin C, E, D Hastalıkları ve Kararsız (Unstable) Hemoglobinopatiler",
            "englishName": "Hemoglobin C / E Disease & Unstable Hemoglobin Hemolytic Anemia",
            "acronym": "HbC / HbE / Heinz Body Anemia",
            "category": "Hematoloji",
            "inheritance": "Otozomal Resesif / Dominant",
            "pathophysiology": "HbC (p.Glu6Lys) ve HbE (p.Glu26Lys) varyantları hedef hücreli (target cell) hemolitik anemi veya HbE/β-talasemi bileşik sendromuna; kararsız varyantlar (örn. Hb Köln) ise Heinz cisimcikli oksidatif hemolize yol açar.",
            "clinicalManagement": "Folik asit desteği, oksidan ilaçlardan kaçınma ve ağır formlarda splenektomi değerlendirilir."
        }
    ],
    "PTEN": [
        {
            "name": "Cowden Sendromu Tip 1 (PTEN Hamartom Tümör Sendromu - PHTS)",
            "englishName": "Cowden Syndrome 1",
            "acronym": "CWS1 / PHTS",
            "category": "Tıbbi Genetik & Tıbbi Onkoloji",
            "inheritance": "Otozomal Dominant",
            "omimId": "158350",
            "orphaId": "201",
            "pathophysiology": "PIP3 fosfataz aktivitesinin kaybı PI3K/AKT/mTOR yolağının dizginsiz aktivasyonuna yol açarak makrosefali, mukokutanöz trikolemmomlar, gastrointestinal hamartomatöz polipler ve yüksek yaşam boyu meme (%85), foliküler tiroid (%35), endometriyum (%28) ve renal hücreli karsinom riski oluşturur.",
            "clinicalManagement": "Erken yaş meme MRG, yıllık tiroid ultrasonografisi, kolonoskopi ve renal görüntüleme ile ömür boyu kanser sürveyansı yapılır."
        },
        {
            "name": "Endometrioid Endometriyum Karsinomu, Glioblastom ve Prostat Kanseri",
            "englishName": "Endometrial Carcinoma, Glioblastoma & Prostate Cancer",
            "acronym": "EC / GBM / PCa",
            "category": "Tıbbi Onkoloji",
            "inheritance": "Somatik",
            "omimId": "608089",
            "pathophysiology": "Endometrioid tip rahim kanserlerinin >%80'inde, primer glioblastomların %30-40'ında ve kastrasyona dirençli metastatik prostat kanserlerinin %40'ında somatik PTEN delesyonu veya trunkasyon mutasyonu görülür.",
            "clinicalManagement": "PTEN kaybı olan tümörlerde AKT/mTOR inhibitörleri (Kapivasertib, Everolimus) klinik etkinlik gösterir."
        },
        {
            "name": "Lhermitte-Duclos Hastalığı, Bannayan-Riley-Ruvalcaba Sendromu ve Makrosefalik Otizm",
            "englishName": "Lhermitte-Duclos Disease, Bannayan-Riley-Ruvalcaba Syndrome & Macrocephaly/Autism",
            "acronym": "LDD / BRRS / ASD",
            "category": "Nöroloji & Pediatrik Genetik",
            "inheritance": "Otozomal Dominant",
            "omimId": "158350",
            "pathophysiology": "Serebellar granül hücre hipertrofisine bağlı displastik gangliositom (LDD), çocukluk çağı makrosefalisi, lipomatozis, pigmente penil maküller (BRRS) ve makrosefali eşlikli otizm spektrum bozukluğu (ASD) yapar.",
            "clinicalManagement": "Belirgin makrosefalisi (>+2.5 SD) olan otizmli çocuklarda PTEN genetik analizi standart tanı basamağıdır."
        }
    ],
    "PIK3CA": [
        {
            "name": "HR+/HER2- İleri Evre Meme Karsinomu",
            "englishName": "Hormone Receptor-Positive Breast Cancer",
            "acronym": "HR+ BC",
            "category": "Tıbbi Onkoloji",
            "inheritance": "Somatik (~%40)",
            "omimId": "114480",
            "pathophysiology": "Helikal (E542K, E545K) ve kinaz (H1047R) alanlarındaki somatik aktive edici mutasyonlar p110α katalitik alt birimini uyararak östrojen reseptörü pozitif meme kanserinde endokrin tedavi direncine neden olur.",
            "clinicalManagement": "PIK3CA-mutant HR+/HER2- ileri evre meme kanserinde Alpelisib (PI3Kα inhibitörü) veya İnavolisib + Fulvestrant standart hedefe yönelik tedavidir."
        },
        {
            "name": "PIK3CA İlişkili Aşırı Büyüme Spektrumu (PROS: CLOVES ve Klippel-Trenaunay Sendromu)",
            "englishName": "PIK3CA-Related Overgrowth Spectrum (CLOVES / MCAP)",
            "acronym": "PROS / CLOVES",
            "category": "Tıbbi Genetik, Pediatri & Vasküler Cerrahi",
            "inheritance": "Somatik Mozaik (Postzigotik)",
            "omimId": "612918",
            "orphaId": "530313",
            "pathophysiology": "Embriyonik gelişim sırasında ortaya çıkan postzigotik somatik mozaik PIK3CA mutasyonları asimetrik doku/ekstremite aşırı büyümesi, lipomatöz kitleler, vasküler/lenfatik malformasyonlar ve megalensefali-kapiller malformasyon (MCAP) tablosu oluşturur.",
            "clinicalManagement": "Düşük doz selektif PI3Kα inhibitörü Alpelisib (Vijoice), PROS hastalarında vasküler malformasyonları ve doku hipertrofisini küçültmek için onaylanmıştır."
        },
        {
            "name": "Kolorektal, Endometriyal, Servikal ve Baş-Boyun Karsinomları",
            "englishName": "Colorectal, Endometrial, Cervical & Head/Neck Carcinomas",
            "acronym": "CRC / EC / CC",
            "category": "Tıbbi Onkoloji",
            "inheritance": "Somatik",
            "pathophysiology": "Endometriyum (%50), serviks (%25), kolorektal (%15-20) ve HPV-pozitif baş-boyun kanserlerinde en sık saptanan onkojenik sinyal mutasyonlarındandır.",
            "clinicalManagement": "PIK3CA-mutant kolorektal kanserde düşük doz aspirin kullanımının nüks riskini azalttığı klinik çalışmalarda gösterilmiştir."
        }
    ],
    "SNCA": [
        {
            "name": "Parkinson Hastalığı (PARK1 / PARK4 ve Sporadik Parkinson)",
            "englishName": "Parkinson Disease 1 & 4",
            "acronym": "PD / PARK1",
            "category": "Nöroloji & Nörodejenerasyon",
            "inheritance": "Otozomal Dominant (Nokta Mutasyonu / Gen Duplikasyonu-Triplikasyonu) & Poligenik",
            "omimId": "168601",
            "orphaId": "2828",
            "pathophysiology": "SNCA missense mutasyonları (A53T, A30P, E46K) veya gen kopya sayısı artışları (duplikasyon/triplikasyon), alfa-sinüklein proteininin yanlış katlanarak oligomer ve amiloid fibrillere (Lewy cisimcikleri) dönüşmesine ve substantia nigra pars compacta'daki dopaminerjik nöronların kaybına yol açar; bradikinezi, rijidite, istirahat tremoru ve postural instabilite gelişir.",
            "clinicalManagement": "Levodopa/Karbidopa, dopamin agonistleri (Pramipeksol, Ropinirol), MAO-B inhibitörleri (Rasajilin) ve ileri evrede Derin Beyin Stimülasyonu (DBS) uygulanır."
        },
        {
            "name": "Lewy Cisimcikli Demans (DLB) ve Çoklu Sistem Atrofisi (MSA - Sinükleinopatiler)",
            "englishName": "Dementia with Lewy Bodies & Multiple System Atrophy",
            "acronym": "DLB / MSA",
            "category": "Nöroloji",
            "inheritance": "Otozomal Dominant / Sporadik",
            "omimId": "127750",
            "pathophysiology": "Kortikal nöronlarda alfa-sinüklein birikimi dalgalı kognitif bozukluk, görsel halüsinasyonlar ve REM uykusu davranış bozukluğu ile karakterize Lewy cisimcikli demansa; oligodendrositlerde (glial sitoplazmik inklüzyonlar) birikimi ise otonom yetmezlik, parkinsonizm ve serebellar ataksi ile seyreden Çoklu Sistem Atrofisine (MSA) neden olur.",
            "clinicalManagement": "BOS veya deri biyopsisinde alfa-sinüklein tohumlama amplifikasyon testi (SAA / RT-QuIC) ile erken biyobelirteç tanısı konulabilmektedir."
        }
    ],
    "APP": [
        {
            "name": "Erken Başlangıçlı Ailesel Alzheimer Hastalığı Tip 1 (FAD / AD1)",
            "englishName": "Early-Onset Familial Alzheimer Disease 1",
            "acronym": "AD1 / EOAD",
            "category": "Nöroloji & Tıbbi Genetik",
            "inheritance": "Otozomal Dominant",
            "omimId": "104760",
            "orphaId": "1020",
            "pathophysiology": "Beta- veya gama-sekretaz kesim bölgelerindeki APP mutasyonları (İsveç, Londra, Arktik mutasyonları) veya Trizomi 21'deki (Down sendromu) APP gen dozaj artışı, nörotoksik Aβ42 peptit üretimini artırarak 40-60 yaşlarında başlayan progresif amnestik demansa yol açar (İzlanda A673T varyantı ise koruyucudur).",
            "clinicalManagement": "Amiloid PET / BOS Aβ42/40 oranı ile tanı doğrulanır; anti-amiloid antikorlar (Lecanemab, Donanemab) ve semptomatik kolinesteraz inhibitörleri/Memantin kullanılır."
        },
        {
            "name": "Kalıtsal Serebral Amiloid Anjiyopati (Hollanda, İtalyan ve Iowa Tipleri)",
            "englishName": "Hereditary Cerebral Amyloid Angiopathy",
            "acronym": "CAA",
            "category": "Nöroloji & Serebrovasküler Hastalıklar",
            "inheritance": "Otozomal Dominant",
            "omimId": "605714",
            "pathophysiology": "APP E693Q (Hollanda tipi) gibi Aβ dizisi içi mutasyonlar parankimal plaktan ziyade serebral arteriyol duvarlarında ağır amiloid birikimi yaparak tekrarlayan lober beyin kanamaları ve vasküler kognitif yıkıma neden olur.",
            "clinicalManagement": "Sıkı kan basıncı kontrolü ve antitrombotik ajanlardan kaçınılması hayati önem taşır."
        }
    ],
    "MAPT": [
        {
            "name": "Frontotemporal Demans ve Parkinsonizm (FTDP-17) & Primer Tauopatiler (PSP, CBD, Pick Hastalığı)",
            "englishName": "Frontotemporal Dementia, Progressive Supranuclear Palsy & Corticobasal Degeneration",
            "acronym": "FTD / PSP / CBD",
            "category": "Nöroloji & Nörodejenerasyon",
            "inheritance": "Otozomal Dominant / H1 Haplotip Riski",
            "omimId": "600274",
            "orphaId": "282",
            "pathophysiology": "MAPT ekzon 10 сплайсинг veya missense mutasyonları (P301L, R406W) 3R/4R tau izoform oranını bozarak mikrotübül stabilizasyonunu engeller ve nörofibriler yumak birikimiyle davranışsal varyant Frontotemporal Demans (bvFTD), Progresif Supranükleer Palsi (PSP - dikey bakış felci ve erken düşmeler), Kortikobazal Dejenerasyon (CBD) ve Alzheimer'daki nöronal ölüme yol açar.",
            "clinicalManagement": "Multidisipliner nörodavranışsal yönetim, konuşma/yutma terapisi ve tau-hedefli antisens oligonükleotit (ASO) / antikor klinik çalışmaları yürütülmektedir."
        }
    ],
    "HTT": [
        {
            "name": "Huntington Hastalığı (HD) ve Juvenil Huntington (Westphal Varyantı)",
            "englishName": "Huntington Disease",
            "acronym": "HD",
            "category": "Nöroloji & Tıbbi Genetik",
            "inheritance": "Otozomal Dominant (CAG Trinükleotit Tekrar Artışı & Antisipasyon)",
            "omimId": "143100",
            "orphaId": "399",
            "pathophysiology": "HTT ekzon 1'deki CAG trinükleotit tekrarının ≥36'ya (tam penetrans ≥40; juvenil başlangıç >60 tekrar) çıkması, poliglutamin (polyQ) uzaması taşıyan mutant Huntingtin proteininin striatum (kaudat ve putamen) orta boy dikenli GABAerjik nöronlarında toksik intranükleer agregatlar oluşturmasına; koreiform istemsiz hareketler, psikiyatrik bozukluklar ve subkortikal demansa yol açar.",
            "clinicalManagement": "Kore tedavisi için VMAT2 inhibitörleri (Tetrabenazin, Deutetrabenazin, Valbenazin) kullanılır; presemptomatik bireylere genetik danışmanlık protokolü ile test yapılır."
        }
    ],
    "SOD1": [
        {
            "name": "Amyotrofik Lateral Skleroz Tip 1 (ALS1 - Motor Nöron Hastalığı)",
            "englishName": "Amyotrophic Lateral Sclerosis 1",
            "acronym": "ALS1",
            "category": "Nöroloji & Nöromüsküler Hastalıklar",
            "inheritance": "Otozomal Dominant (Nadir Resesif D90A)",
            "omimId": "105400",
            "orphaId": "803",
            "pathophysiology": "SOD1 mutasyonları (A4V, G93A, D90A) antioksidan enzim kaybından ziyade toksik gain-of-function mekanizmasıyla yanlış katlanmış SOD1 agregatları oluşturarak üst ve alt motor nöronlarda mitokondriyal hasar, aksonal transport bozukluğu, ilerleyici kas güçsüzlüğü, fasikülasyonlar ve solunum yetmezliği yapar.",
            "clinicalManagement": "SOD1-mutant ALS hastalarında intratekal antisens oligonükleotit tedavisi Tofersen (Qalsody), SOD1 mRNA'sını yıkarak nörofilament hafif zincir (NfL) düzeylerini düşüren onaylı hedefe yönelik tedavidir."
        }
    ],
    "PDCD1": [
        {
            "name": "Kanser İmmünoterapisi Hedefi (Melanom, KHDAK, RCC, Hodgkin Lenfoma, MSI-H Tümörler)",
            "englishName": "Tumor Immune Evasion & Anti-PD-1 Checkpoint Blockade Indications",
            "acronym": "Anti-PD-1",
            "category": "Tıbbi Onkoloji & İmmünoloji",
            "inheritance": "Edinsel İmmün Kaçış / Poligenik Otoimmün Duyarlılık",
            "omimId": "600244",
            "pathophysiology": "Tümör mikroçevresinde kronik antijen uyarımı altındaki CD8+ sitotoksik T lenfositlerinde PD-1 reseptörü aşırı eksprese olur; tümör hücrelerindeki PD-L1 ile bağlandığında SHP-2 fosfataz aracılığıyla TCR sinyalini susturarak T-hücre tükenmesine (exhaustion) ve tümörün immün sistemden kaçışına neden olur.",
            "clinicalManagement": "Anti-PD-1 monoklonal antikorlar (Pembrolizumab, Nivolumab, Cemiplimab) T-hücre antitümör yanıtını yeniden aktive eder; dMMR/MSI-H veya yüksek TMB (≥10 mut/Mb) olan tüm solid tümörlerde doku-bağımsız (tumor-agnostic) onaylıdır."
        },
        {
            "name": "Sistemik Lupus Eritematozus Duyarlılığı Tip 2 (SLEB2) ve Otoimmün Endokrinopatiler",
            "englishName": "Systemic Lupus Erythematosus Susceptibility 2 & Immune-Related Adverse Events",
            "acronym": "SLEB2 / irAE",
            "category": "Romatoloji & İmmünoloji",
            "inheritance": "Poligenik / İmmünoterapi İlişkili",
            "omimId": "605218",
            "pathophysiology": "PDCD1 düzenleyici polimorfizmleri periferik self-toleransı zayıflatarak Sistemik Lupus Eritematozus (SLE), Tip 1 diyabet ve otoimmün tiroidit yatkınlığını artırır; klinik anti-PD-1 blokajı da benzer şekilde immün ilişkili kolit, pnömonit, hipofizit ve tiroidit tablosu tetikleyebilir.",
            "clinicalManagement": "İmmün ilişkili yan etkilerde (irAE) dereceye göre sistemik kortikosteroidler veya İnfliksimab kullanılır."
        }
    ],
    "CD274": [
        {
            "name": "PD-L1 Pozitif Solid Tümörler (KHDAK, Ürotelyal Karsinom, TNBC, Hepatosellüler Karsinom)",
            "englishName": "PD-L1 Expressing Malignancies & Immune Escape",
            "acronym": "PD-L1+ Cancers",
            "category": "Tıbbi Onkoloji & İmmünoloji",
            "inheritance": "Somatik Amplifikasyon (9p24.1) / İndüklenebilir Ekspresyon",
            "pathophysiology": "Tümör hücreleri IFN-γ uyarımıyla veya 9p24.1 kromozom amplifikasyonu (klasik Hodgkin lenfoma ve primer mediastinal B-hücreli lenfomada tipik) ile yüzey PD-L1 (CD274) ekspresyonunu artırarak sitotoksik T hücrelerini inhibe eder.",
            "clinicalManagement": "İmmünohistokimyasal PD-L1 skorlaması (TPS ve CPS) Pembrolizumab yatkınlığını belirler; Atezolizumab, Durvalumab ve Avelumab doğrudan PD-L1'i bloke eden monoklonal antikorlardır."
        }
    ],
    "TNF": [
        {
            "name": "Romatoid Artrit, Ankilozan Spondilit ve Psöriyatik Artrit",
            "englishName": "Rheumatoid Arthritis, Ankylosing Spondylitis & Psoriatic Arthritis",
            "acronym": "RA / AS / PsA",
            "category": "Romatoloji & İmmünoloji",
            "inheritance": "Poligenik / Kronik Otoimmün İnflamasyon",
            "pathophysiology": "Aktive makrofaj ve T hücrelerinden salınan aşırı TNF-alfa, sinoviyal fibroblast proliferasyonu (pannus oluşumu), NF-κB/MAPK aktivasyonu, IL-1/IL-6 salınımı ve RANKL aracılı osteoklastogenez ile eklem kıkırdak ve kemik erozyonuna yol açar.",
            "clinicalManagement": "Anti-TNF biyolojik ajanlar (Adalimumab, İnfliksimab, Etanersept, Golimumab, Sertolizumab pegol) romatolojik hastalık modifiye edici tedavinin temel taşıdır (tedavi öncesi latent tüberküloz taraması zorunludur)."
        },
        {
            "name": "İnflamatuar Bağırsak Hastalıkları (Crohn Hastalığı ve Ülseratif Kolit) & Plak Psöriyazis",
            "englishName": "Crohn Disease, Ulcerative Colitis & Psoriasis",
            "acronym": "IBD / CD / UC",
            "category": "Gastroenteroloji & Dermatoloji",
            "inheritance": "Poligenik / Multifaktöriyel",
            "pathophysiology": "Bağırsak mukozasında TNF-alfa aracılı enterosit apoptozu, sıkı bağlantı (tight junction) bariyer yıkımı ve transmural granülomatöz inflamasyon (Crohn) veya epidermal keratinosit hiperproliferasyonu (Psöriyazis) gelişir.",
            "clinicalManagement": "Orta-ağır ve fistülizan Crohn hastalığında İnfliksimab ve Adalimumab mukozal iyileşme sağlar."
        }
    ],
    "IL6": [
        {
            "name": "Sitokin Salınım Sendromu (CRS), Romatoid Artrit, Dev Hücreli Arterit ve Castleman Hastalığı",
            "englishName": "Cytokine Release Syndrome, Rheumatoid Arthritis, Giant Cell Arteritis & Castleman Disease",
            "acronym": "CRS / GCA / RA",
            "category": "Romatoloji, İmmünoloji & Yoğun Bakım",
            "inheritance": "Edinsel / Poligenik",
            "pathophysiology": "IL-6, gp130/JAK/STAT3 yolağı üzerinden karaciğerde akut faz reaktanlarını (CRP, SAA, fibrinojen, hepsidin -> kronik hastalık anemisi) uyarır, Th17 farklılaşmasını tetikler ve CAR-T tedavisi veya ağır viral enfeksiyonlarda yaşamı tehdit eden Sitokin Fırtınasına (CRS) yol açar.",
            "clinicalManagement": "Anti-IL-6R (Tosilizumab, Sarilumab) ve anti-IL-6 (Siltuksimab) antikorları Sitokin Salınım Sendromu, Dev Hücreli Arterit, Sistemik Jüvenil İdiyopatik Artrit ve Multicentric Castleman hastalığında standart tedavidir."
        }
    ],
    "VEGFA": [
        {
            "name": "Tümör Anjiyogenezi (Metastatik Kolorektal, Renal Hücreli, Over, Serviks Karsinomu ve GBM)",
            "englishName": "Pathological Tumor Angiogenesis & Solid Malignancies",
            "acronym": "RCC / mCRC / OC",
            "category": "Tıbbi Onkoloji",
            "inheritance": "Somatik Hipoksi Yanıtı (HIF-1α Bağımlı)",
            "pathophysiology": "Tümör içi hipoksi ve VHL kaybı (özellikle berrak hücreli böbrek kanserinde) HIF-1α aracılığıyla VEGFA ekspresyonunu artırarak geçirgenliği yüksek, kaotik yeni damar oluşumu (neoanjiyogenez), peritümöral ödem ve hematojen metastazı destekler.",
            "clinicalManagement": "Anti-VEGF monoklonal antikor (Bevasizumab) ve VEGFR tirozin kinaz inhibitörleri (Sunitinib, Pazopanib, Aksitinib, Kabozantinib, Lenvatinib) standart anti-anjiyogenik tedavilerdir."
        },
        {
            "name": "Yaş Tip Yaşa Bağlı Makula Dejenerasyonu (nAMD) ve Diyabetik Makula Ödemi / Retinopati",
            "englishName": "Neovascular Age-Related Macular Degeneration & Diabetic Retinopathy",
            "acronym": "nAMD / DME / DR",
            "category": "Göz Hastalıkları (Oftalmoloji)",
            "inheritance": "Poligenik / Metabolik",
            "pathophysiology": "Retina iskemisi sonucu vitreus içine salınan VEGFA, koroidal neovaskülarizasyon, kan-retina bariyerinin bozulması, makula ödemi ve vitreus içi kanama ile santral görme kaybına neden olur.",
            "clinicalManagement": "İntravitreal anti-VEGF enjeksiyonları (Ranibizumab, Aflibersept, Farisimal, Bevasizumab) görme keskinliğini koruyan ve geri kazandıran birincil tedavidir."
        }
    ],
    "BCL2": [
        {
            "name": "Foliküler Lenfoma (t(14;18) Translokasyonu), KLL ve Akut Miyeloid Lösemi (AML)",
            "englishName": "Follicular Lymphoma, Chronic Lymphocytic Leukemia & AML",
            "acronym": "FL / CLL / AML",
            "category": "Hematoloji & Hemato-Onkoloji",
            "inheritance": "Somatik Kromozomal Translokasyon t(14;18)(q32;q21)",
            "omimId": "151430",
            "pathophysiology": "Foliküler lenfomaların %85-90'ında görülen t(14;18) translokasyonu BCL2 genini immünoglobulin ağır zincir (IGH) güçlendiricisinin kontrolüne sokar; KLL'de ise miR-15a/16-1 kaybı BCL-2 aşırı ekspresyonu yaparak BAX/BAK aracılı mitokondriyal apoptozu bloke eder ve malign B lenfositlerinin ölümsüzleşmesini sağlar.",
            "clinicalManagement": "Selektif BH3-mimetik oral BCL-2 inhibitörü Venetoklaks, KLL ve yaşlı/komorbid AML hastalarında apoptozu doğrudan yeniden başlatan hedefe yönelik tedavidir (tümör lizis sendromu profilaksisi ile başlanır)."
        }
    ],
    "COL1A1": [
        {
            "name": "Osteogenesis İmperfekta Tip I-IV (Cam Kemik Hastalığı)",
            "englishName": "Osteogenesis Imperfecta Types I, II, III and IV",
            "acronym": "OI1-4",
            "category": "Tıbbi Genetik, Ortopedi & Pediatrik Endokrinoloji",
            "inheritance": "Otozomal Dominant",
            "omimId": "166200",
            "orphaId": "666",
            "pathophysiology": "COL1A1 null allelleri tip I kollajen miktarını yarıya indirerek hafif form OI Tip I'e (mavi sklera, tekrarlayan kırıklar, presenil iletim tipi işitme kaybı); Gly-X-Y üçlü heliks dizisindeki glisin yerine başka amino asit geçişleri ise heliks katlanmasını bozarak (dominant-negatif etki) perinatal ölümcül Tip II veya ağır deformiteli Tip III/IV tablolarına yol açar.",
            "clinicalManagement": "İntravenöz bisfosfonat tedavisi (Pamidronat, Zoledronik asit), intramedüller teleskopik çivileme cerrahisi ve fizik tedavi uygulanır."
        },
        {
            "name": "Ehlers-Danlos Sendromu (Artrokalazi Tipi / Klasik Tip) ve Caffey Hastalığı",
            "englishName": "Ehlers-Danlos Syndrome, Arthrochalasia Type 1 & Caffey Disease",
            "acronym": "EDSARTH1",
            "category": "Tıbbi Genetik & Romatoloji",
            "inheritance": "Otozomal Dominant",
            "omimId": "130060",
            "pathophysiology": "Prokollajen N-propeptit kesim bölgesini etkileyen ekzon 6 mutasyonları konjenital bilateral kalça çıkığı ve ağır eklem hipermobilitesine; R836C mutasyonu ise infantil kortikal hiperostozise (Caffey hastalığı) neden olur.",
            "clinicalManagement": "Eklem stabilizasyonu, ortopedik takip ve kardiyovasküler değerlendirme yapılır."
        }
    ],
    "DMD": [
        {
            "name": "Duchenne ve Becker Kas Distrofisi (DMD / BMD) & X'e Bağlı Dilate Kardiyomiyopati",
            "englishName": "Duchenne Muscular Dystrophy, Becker Muscular Dystrophy & Dilated Cardiomyopathy 3B",
            "acronym": "DMD / BMD / CMD3B",
            "category": "Nöroloji, Pediatri & Kardiyoloji",
            "inheritance": "X'e Bağlı Resesif (Xp21.2)",
            "omimId": "310200",
            "orphaId": "98896",
            "pathophysiology": "Okuma çerçevesini bozan (out-of-frame) delesyon/duplikasyon veya anlamsız mutasyonlar distrofin proteininin tam kaybına ve sarkolemma yıkımına yol açarak Duchenne Kas Distrofisine (Gowers belirtisi, baldır psödohipertrofisi, CK yüksekliği, 12 yaş civarı yürüme kaybı); okuma çerçevesini koruyan (in-frame) mutasyonlar ise kısmi fonksiyonel distrofin ile daha hafif Becker Kas Distrofisine ve dilate kardiyomiyopatiye neden olur.",
            "clinicalManagement": "Kortikosteroidler (Deflazakort, Prednizon), ekzon atlama (exon-skipping) antisens tedavileri (Eteplirsen, Golodirsen, Viltolarsen), anlamsız mutasyonlarda Ataluren, mikro-distrofin gen tedavisi (Delandistrogene moxeparvovec) ve kardiyopulmoner destek uygulanır."
        }
    ],
    "F8": [
        {
            "name": "Hemofili A (Konjenital Faktör VIII Eksikliği)",
            "englishName": "Hemophilia A",
            "acronym": "HEMA",
            "category": "Hematoloji & Tıbbi Genetik",
            "inheritance": "X'e Bağlı Resesif",
            "omimId": "306700",
            "orphaId": "98878",
            "pathophysiology": "İntrinsik koagülasyon kaskadında Faktör IXa'nın kofaktörü olan Faktör VIII genindeki mutasyonlar (ağır olguların %45'inde İntron 22 inversiyonu) sekonder hemostazı bozarak derin doku/kas içi hematomlar, tekrarlayan hemartrozlar (hedef eklem artropatisi) ve cerrahi/travma sonrası durdurulamayan kanamalara neden olur (aPTT uzamış, PT normaldir).",
            "clinicalManagement": "Rekombinant Faktör VIII konsantreleri ile profilaksi, FVIII'i taklit eden bispesifik antikor Emisizumab (Hemlibra - inhibitörlü hastalarda da etkili) ve AAV5 tabanlı gen tedavisi (Valoctocogene roxaparvovec) kullanılır."
        }
    ],
    "LDLR": [
        {
            "name": "Ailesel Hiperkolesterolemi (Heterozigot HeFH ve Homozigot HoFH)",
            "englishName": "Familial Hypercholesterolemia 1",
            "acronym": "FH / FHC",
            "category": "Kardiyoloji, Endokrinoloji & Tıbbi Genetik",
            "inheritance": "Otozomal Dominant (Semidominant)",
            "omimId": "143890",
            "orphaId": "409",
            "pathophysiology": "Hepatosit yüzeyindeki LDL reseptörünün sentez, transport, bağlanma veya endositozunu bozan LDLR mutasyonları plazma LDL-kolesterol klirensini azaltır; tendon ksantomları, korneal arkus, supravalvüler aort stenozu ve çocukluk/genç erişkinlikte erken miyokard enfarktüsü gelişir.",
            "clinicalManagement": "Yüksek yoğunluklu statin + Ezetimib + PCSK9 inhibitörleri (Evolokumab, Alirokumab, İnklisiran); homozigot FH'de ise LDLR'den bağımsız çalışan Evinakumab (ANGPTL3 antikoru), Lomitapid ve LDL aferezi uygulanır."
        }
    ],
    "PCSK9": [
        {
            "name": "Otozomal Dominant Hiperkolesterolemi Tip 3 (ADH3) ve Hipobetalipoproteinemi",
            "englishName": "Familial Hypercholesterolemia 3 & Hypobetalipoproteinemia",
            "acronym": "FH3",
            "category": "Kardiyoloji & Endokrinoloji",
            "inheritance": "Otozomal Dominant",
            "omimId": "603776",
            "pathophysiology": "PCSK9 fonksiyon kazanımı (gain-of-function, örn. D374Y) mutasyonları hepatik LDL reseptörlerinin lizozomal yıkımını hızlandırarak ağır hiperkolesterolemi ve erken koroner arter hastalığı yapar; fonksiyon kaybı (loss-of-function) mutasyonları ise yaşam boyu düşük LDL-K ve miyokard enfarktüsüne karşı %80 koruma sağlar.",
            "clinicalManagement": "PCSK9 monoklonal antikorları (Evolokumab, Alirokumab) ve siRNA tedavisi (İnklisiran) LDL reseptör yıkımını engelleyerek LDL-K'yi %50-60 düşürür."
        }
    ],
    "ALK": [
        {
            "name": "ALK-Pozitif Küçük Hücreli Dışı Akciğer Kanseri (EML4-ALK Füzyonu), ALCL ve Nöroblastom",
            "englishName": "ALK-Rearranged Non-Small Cell Lung Cancer, Anaplastic Large Cell Lymphoma & Neuroblastoma",
            "acronym": "ALK+ NSCLC / ALCL / NB",
            "category": "Tıbbi Onkoloji, Hematoloji & Pediatrik Onkoloji",
            "inheritance": "Somatik Translokasyon (EML4-ALK, NPM1-ALK) veya Germline (Nöroblastom)",
            "omimId": "613014",
            "pathophysiology": "Genç ve sigara içmeyen akciğer adenokarsinomu hastalarının %5'inde görülen inv(2)(p21p23) EML4-ALK gen füzyonu, Anaplastik Büyük Hücreli Lenfomada t(2;5) NPM1-ALK füzyonu ve pediatrik nöroblastomda nokta mutasyonları (F1174L, R1275Q) konstitütif tirozin kinaz aktivasyonu yapar.",
            "clinicalManagement": "ALK inhibitörleri (Alektinib, Brigatinib, Lorlatinib, Krizotinib) beyin metastazları dahil yüksek ve uzun süreli yanıt sağlar."
        }
    ],
    "ABL1": [
        {
            "name": "Kronik Miyeloid Lösemi (KML) ve Philadelphia-Pozitif Akut Lenfoblastik Lösemi (Ph+ ALL)",
            "englishName": "Chronic Myeloid Leukemia & Ph+ Acute Lymphoblastic Leukemia (BCR-ABL1)",
            "acronym": "CML / Ph+ ALL",
            "category": "Hematoloji & Hemato-Onkoloji",
            "inheritance": "Somatik Translokasyon t(9;22)(q34;q11) (Philadelphia Kromozomu)",
            "omimId": "608232",
            "pathophysiology": "9. ve 22. kromozomlar arasındaki resiprokal translokasyon sonucu oluşan BCR-ABL1 kimerik onkoproteini (p210 veya p190) konstitütif tirozin kinaz aktivitesiyle granülositik seride kontrolsüz klonal proliferasyon ve apoptoz direnci oluşturur.",
            "clinicalManagement": "Tirozin kinaz inhibitörleri (İmatinib, Dasatinib, Nilotinib, Bosutinib) ile normale yakın yaşam beklentisi sağlanır; T315I 'gatekeeper' direnç mutasyonunda Ponatinib veya STAMP inhibitörü Asiminib kullanılır."
        }
    ],
    "JAK2": [
        {
            "name": "Polisitemia Vera (PV), Esansiyel Trombositemi (ET) ve Primer Miyelofibrozis (PMF)",
            "englishName": "Polycythemia Vera, Essential Thrombocythemia & Primary Myelofibrosis",
            "acronym": "PV / ET / PMF (MPN)",
            "category": "Hematoloji",
            "inheritance": "Somatik (p.Val617Phe / V617F ve Ekzon 12) & Budd-Chiari Sendromu",
            "omimId": "263300",
            "pathophysiology": "Psödokinaz (JH2) oto-inhibitör alanındaki somatik JAK2 V617F mutasyonu (Polisitemia Vera'da >%95, ET ve PMF'de %50-60) eritropoietin ve trombopoietinden bağımsız JAK-STAT sinyalizasyonu başlatarak eritrositoz, trombositoz, splenomegali, akuajenik pruritus ve splanknik ven trombozuna (Budd-Chiari sendromu) yol açar.",
            "clinicalManagement": "PV ve miyelofibroziste JAK1/2 inhibitörü Ruksolitinib, Fedratinib, Hidroksiüre, ropeginterferon alfa-2b, flebotomi ve düşük doz aspirin kullanılır."
        }
    ],
    "PARP1": [
        {
            "name": "Homolog Rekombinasyon Eksikliği (HRD) Gösteren Meme, Over, Prostat ve Pankreas Kanserlerinde Sentetik Letalite Hedefi",
            "englishName": "Synthetic Lethality Target in BRCA/HRD-Mutant Cancers",
            "acronym": "HRD / PARPi",
            "category": "Tıbbi Onkoloji & Farmakoloji",
            "inheritance": "Terapötik Hedef",
            "pathophysiology": "Tek zincir DNA kırıklarının baz eksizyon onarımında (BER) görevli PARP1 enzimi inhibe edildiğinde ve DNA üzerinde tuzaklandığında (PARP trapping), replikasyon çatalı çöker ve çift zincir kırıkları oluşur; BRCA1/2 veya ATM/PALB2 mutant tümör hücreleri bu kırıkları onaramayarak seçici olarak apoptoza gider (sentetik letalite).",
            "clinicalManagement": "Olaparib, Niraparib, Rukaparib ve Talazoparib; over, meme, prostat ve pankreas kanserlerinde onaylı PARP1/2 inhibitörleridir."
        }
    ],
    "GLP1R": [
        {
            "name": "Tip 2 Diabetes Mellitus, Obezite, Kardiyovasküler Risk Azaltımı ve MASH (Metabolik Steatohepatit)",
            "englishName": "Type 2 Diabetes Mellitus, Obesity & Cardiometabolic Syndrome",
            "acronym": "T2DM / Obezite",
            "category": "Endokrinoloji, Kardiyoloji & Gastroenteroloji",
            "inheritance": "Metabolik Hedef / Poligenik",
            "pathophysiology": "Pankreas beta hücreleri ve hipotalamik tokluk merkezlerinde bulunan GLP-1 reseptörü; glikoza bağımlı insülin sekresyonunu artırır, glukagonu baskılar, mide boşalmasını yavaşlatır ve merkezi iştah kontrolü ile kilo kaybı ve kardiyorenal koruma sağlar.",
            "clinicalManagement": "GLP-1 reseptör agonistleri (Semaglutid, Liraglutid, Dulaglutid) ve dual GIP/GLP-1 agonisti (Tirzepatid) diyabet, obezite ve majör advers kardiyovasküler olayların (MACE) önlenmesinde kullanılır."
        }
    ]
}

# Medical specialty classification rules based on keywords in English & Turkish
SPECIALTY_RULES = [
    ("Tıbbi Onkoloji", [
        "cancer", "carcinoma", "sarcoma", "tumor", "tumour", "melanoma", "glioma",
        "glioblastoma", "adenocarcinoma", "neoplasm", "malign", "onkoloji", "kanser",
        "karsinom", "tümör", "medulloblastoma", "neuroblastoma", "mesothelioma",
        "osteosarcoma", "pheochromocytoma", "paraganglioma", "retinoblastoma", "wilms",
        "papilloma", "schwannoma", "meningioma", "astrocytoma", "chordoma", "seminoma"
    ]),
    ("Hematoloji & Hemato-Onkoloji", [
        "leukemia", "leukaemia", "lymphoma", "myeloma", "anemia", "anaemia", "thalassemia",
        "sickle", "hemophilia", "haemophilia", "thrombocy", "bleeding", "coagulation",
        "bone marrow", "myelodysplas", "polycythemia", "myeloproliferative", "histiocyt",
        "methemoglobin", "neutropenia", "pancytopenia", "lösemi", "lenfoma", "anemi",
        "talasemi", "pıhtılaşma", "hemofili", "tromboz", "trombosit"
    ]),
    ("Nöroloji & Nörodejenerasyon", [
        "alzheimer", "parkinson", "dementia", "neuropath", "epilep", "seizure", "ataxia",
        "amyotrophic", "huntington", "myasthen", "migraine", "encephalopath", "spastic",
        "paraplegia", "dystonia", "charcot-marie-tooth", "schizophrenia", "autism",
        "intellectual disability", "microcephaly", "lissencephaly", "cerebral", "stroke",
        "demans", "nöropati", "epilepsi", "ataksi", "beyin", "nöron", "felç", "inme"
    ]),
    ("Kardiyoloji & Vasküler", [
        "cardiomyopathy", "arrhythmia", "long qt", "brugada", "hypertension", "coronary",
        "myocardial", "aortic", "aneurysm", "heart failure", "atrial fibrillation",
        "atherosclero", "hypercholesterolemia", "hyperlipoproteinemia", "dyslipidemia",
        "marfan", "vascular", "kardiyomiyopati", "hipertansiyon", "aritmi", "kalp",
        "damar", "kolesterol", "ateroskleroz"
    ]),
    ("Endokrinoloji & Metabolizma", [
        "diabetes", "insulin", "hyperinsulin", "obesity", "thyroid", "hypothyroid",
        "hyperparathyroid", "adrenal", "cushing", "lipodystrophy", "metabolic",
        "glycogen", "mucopolysaccharid", "gaucher", "fabry", "phenylketonuria",
        "porphyria", "diyabet", "insülin", "obezite", "tiroid", "metabolizma"
    ]),
    ("Göğüs Hastalıkları (Pulmonoloji)", [
        "cystic fibrosis", "bronchiectasis", "pulmonary", "asthma", "emphysema",
        "pneumonia", "respiratory", "kistik fibrozis", "akciğer", "bronşektazi", "solunum"
    ]),
    ("Romatoloji & İmmünoloji", [
        "immunodeficiency", "autoimmune", "lupus", "arthritis", "autoinflammatory",
        "inflammatory bowel", "crohn", "psoriasis", "vasculitis", "allergy",
        "bağışıklık", "otoimmün", "artrit", "enflamasyon", "immün"
    ]),
    ("Nefroloji & Ürogenital", [
        "renal", "kidney", "nephropathy", "glomerul", "nephrotic", "polycystic kidney",
        "alport", "bartter", "vas deferens", "infertility", "böbrek", "nefropati"
    ]),
    ("Kas-İskelet & Bağ Dokusu", [
        "muscular dystrophy", "myopathy", "duchenne", "osteogenesis imperfecta",
        "ehlers-danlos", "skeletal", "dysplasia", "chondrodysplasia", "arthrogryposis",
        "myotonia", "kas distrofisi", "miyopati", "kemik", "kollajen"
    ])
]

# English-to-Turkish medical disease name translation helper for common clinical terms
DISEASE_NAME_TRANSLATIONS = {
    "breast cancer": "Meme Kanseri (Breast Cancer)",
    "breast-ovarian cancer, familial, susceptibility to, 1": "Kalıtsal Meme ve Yumurtalık Kanseri Sendromu Tip 1 (HBOC1)",
    "breast-ovarian cancer, familial, susceptibility to, 2": "Kalıtsal Meme ve Yumurtalık Kanseri Sendromu Tip 2 (HBOC2)",
    "ovarian cancer": "Yumurtalık (Over) Kanseri",
    "lung cancer": "Akciğer Kanseri (Lung Cancer)",
    "non-small cell lung cancer": "Küçük Hücreli Dışı Akciğer Kanseri (KHDAK / NSCLC)",
    "small cell lung cancer": "Küçük Hücreli Akciğer Kanseri (SCLC)",
    "colorectal cancer": "Kolorektal Kanser (Kalın Bağırsak Kanseri)",
    "colon cancer": "Kolon Kanseri",
    "gastric cancer": "Mide (Gastrik) Kanseri",
    "stomach cancer": "Mide Kanseri",
    "pancreatic cancer": "Pankreas Kanseri",
    "prostate cancer": "Prostat Kanseri",
    "hepatocellular carcinoma": "Hepatosellüler Karsinom (Karaciğer Kanseri)",
    "liver cancer": "Karaciğer Kanseri",
    "esophageal cancer": "Özofagus (Yemek Borusu) Kanseri",
    "head and neck squamous cell carcinoma": "Baş ve Boyun Yassı Hücreli Karsinomu (HNSCC)",
    "nasopharyngeal carcinoma": "Nazofarenks Karsinomu",
    "adrenocortical carcinoma": "Adrenokortikal Karsinom (Böbreküstü Bezi Kanseri)",
    "osteosarcoma": "Osteosarkom (Kemik Kanseri)",
    "glioblastoma": "Glioblastoma Multiforme (GBM)",
    "glioma susceptibility 1": "Gliom Duyarlılığı Tip 1 (Beyin Tümörü)",
    "papilloma of choroid plexus": "Koroid Pleksus Papillomu / Karsinomu",
    "basal cell carcinoma 7": "Bazal Hücreli Karsinom Tip 7",
    "melanoma": "Malign Melanom",
    "thyroid cancer": "Tiroid Karsinomu",
    "bladder cancer": "Mesane Karsinomu",
    "renal cell carcinoma": "Renal Hücreli Karsinom (Böbrek Kanseri)",
    "endometrial cancer": "Endometriyum (Rahim) Kanseri",
    "cervical cancer": "Serviks (Rahim Ağzı) Kanseri",
    "acute myeloid leukemia": "Akut Miyeloid Lösemi (AML)",
    "chronic lymphocytic leukemia": "Kronik Lenfositik Lösemi (KLL)",
    "hairy cell leukemia": "Tüylü Hücreli Lösemi (HCL)",
    "li-fraumeni syndrome": "Li-Fraumeni Sendromu (Kalıtsal Çoklu Kanser Sendromu)",
    "cowden syndrome 1": "Cowden Sendromu Tip 1 (PTEN Hamartom Tümör Sendromu)",
    "lhermitte-duclos disease": "Lhermitte-Duclos Hastalığı (Displastik Serebellar Gangliositom)",
    "bannayan-riley-ruvalcaba syndrome": "Bannayan-Riley-Ruvalcaba Sendromu",
    "proteus syndrome": "Proteus Sendromu (Mozaik Aşırı Büyüme Sendromu)",
    "noonan syndrome": "Noonan Sendromu (RASopati)",
    "cardiofaciocutaneous syndrome": "Kardiyofasiyokutanöz (CFC) Sendrom",
    "leopard syndrome": "LEOPARD Sendromu (Çoklu Lentigo Sendromu)",
    "cystic fibrosis": "Kistik Fibrozis (CF)",
    "congenital bilateral absence of the vas deferens": "Konjenital Bilateral Vas Deferens Yokluğu (CBAVD)",
    "alzheimer disease": "Alzheimer Hastalığı",
    "alzheimer disease 2": "Geç Başlangıçlı Alzheimer Hastalığı (Tip 2 / APOE İlişkili)",
    "parkinson disease": "Parkinson Hastalığı",
    "huntington disease": "Huntington Hastalığı",
    "amyotrophic lateral sclerosis": "Amyotrofik Lateral Skleroz (ALS)",
    "sickle cell anemia": "Orak Hücreli Anemi (Sickle Cell Disease)",
    "beta-thalassemia": "Beta-Talasemi (Akdeniz Anemisi)",
    "alpha-thalassemia": "Alfa-Talasemi",
    "hemophilia a": "Hemofili A (Faktör VIII Eksikliği)",
    "hemophilia b": "Hemofili B (Faktör IX Eksikliği)",
    "duchenne muscular dystrophy": "Duchenne Kas Distrofisi (DMD)",
    "becker muscular dystrophy": "Becker Kas Distrofisi (BMD)",
    "familial hypercholesterolemia": "Ailesel Hiperkolesterolemi (FH)",
    "hyperlipoproteinemia 3": "Tip III Hiperlipoproteinemi (Ailesel Disbetalipoproteinemi)",
    "diabetes mellitus": "Diabetes Mellitus (Şeker Hastalığı)",
    "diabetes mellitus, permanent neonatal 4": "Kalıcı Neonatal Diabetes Mellitus Tip 4",
    "maturity-onset diabetes of the young, type 10": "Gençlerin Erişkin Tipi Diyabeti Tip 10 (MODY10)",
    "hypertrophic cardiomyopathy": "Hipertrofik Kardiyomiyopati (HKMP)",
    "dilated cardiomyopathy": "Dilate Kardiyomiyopati (DKMP)",
    "osteogenesis imperfecta": "Osteogenesis İmperfekta (Cam Kemik Hastalığı)",
    "ehlers-danlos syndrome": "Ehlers-Danlos Sendromu (EDS)",
    "marfan syndrome": "Marfan Sendromu",
    "ataxia-telangiectasia": "Ataksi-Telenjiektazi Sendromu (Louis-Bar Sendromu)",
    "retinoblastoma": "Retinoblastom (Pediatrik Göz Tümörü)",
}


def classify_medical_specialty(name: str, description: str = "") -> str:
    """
    Classifies a disease into a medical specialty based on its name and description.
    """
    combined = f"{name} {description}".lower()
    for specialty, keywords in SPECIALTY_RULES:
        if any(kw in combined for kw in keywords):
            return specialty
    return "Tıbbi Genetik & Klinik Patoloji"


def translate_disease_title(raw_title: str) -> str:
    """
    Provides a Turkish + International medical title for an English disease name if known,
    or formats it cleanly for clinical presentation.
    """
    if not raw_title:
        return "Klinik Patoloji"
    low = raw_title.strip().lower()
    if low in DISEASE_NAME_TRANSLATIONS:
        return DISEASE_NAME_TRANSLATIONS[low]
    for en_key, tr_val in sorted(DISEASE_NAME_TRANSLATIONS.items(), key=lambda x: -len(x[0])):
        if low == en_key or low.startswith(en_key + " "):
            return f"{tr_val} ({raw_title})" if raw_title.lower() not in tr_val.lower() else tr_val
    return raw_title


def infer_inheritance(text: str) -> str:
    """
    Infers inheritance or mutation origin from clinical text.
    """
    low = (text or "").lower()
    if "autosomal dominant" in low and "autosomal recessive" in low:
        return "Otozomal Dominant / Resesif"
    if "autosomal dominant" in low:
        return "Otozomal Dominant"
    if "autosomal recessive" in low:
        return "Otozomal Resesif"
    if "x-linked" in low:
        return "X'e Bağlı Kalıtım"
    if "somatic" in low:
        return "Somatik (Edinsel)"
    if "multifactorial" in low or "susceptibility" in low or "polygenic" in low:
        return "Poligenik / Genetik Duyarlılık"
    return "Genetik / Klinik İlişkili"


def normalize_disease_key(name: str) -> str:
    """
    Creates a canonical key for deduplicating diseases across UniProt, ClinVar, Orphanet, and OpenTargets.
    """
    if not name:
        return ""
    s = name.lower()
    # Remove parenthetical acronyms and punctuation
    s = re.sub(r"\([^)]*\)", "", s)
    s = re.sub(r"\b(type|tip|syndrome|sendromu|disease|hastalığı|disorder|susceptibility|to|familial|hereditary|ailesel|kalıtsal|of|the|and|ve|in)\b", " ", s)
    s = re.sub(r"[^a-z0-9ğüşıöç]+", "", s)
    return s.strip()


def fetch_opentargets_diseases(ensembl_id: str, limit: int = 18) -> List[Dict[str, Any]]:
    """
    Queries EMBL-EBI Open Targets Platform GraphQL API for clinically validated
    gene-disease associations (somatic oncology, GWAS, Orphanet, ClinVar, ChEMBL).
    """
    if not ensembl_id:
        return []

    query = """
    query TargetDiseases($ensemblId: String!, $size: Int!) {
      target(ensemblId: $ensemblId) {
        id
        approvedSymbol
        associatedDiseases(page: { index: 0, size: $size }) {
          rows {
            score
            disease {
              id
              name
              description
              therapeuticAreas {
                id
                name
              }
            }
          }
        }
      }
    }
    """
    try:
        resp = requests.post(
            OPENTARGETS_GRAPHQL_URL,
            json={"query": query, "variables": {"ensemblId": ensembl_id, "size": limit}},
            timeout=5
        )
        if resp.status_code != 200:
            return []
        data = resp.json()
        rows = (
            data.get("data", {})
            .get("target", {})
            .get("associatedDiseases", {})
            .get("rows", [])
        )
        results = []
        for row in rows:
            score = row.get("score", 0.0)
            if score < 0.15:
                continue
            d = row.get("disease") or {}
            d_name = d.get("name", "")
            if not d_name:
                continue
            # Skip overly generic umbrella terms from OpenTargets ontology
            if d_name.lower() in [
                "neoplasm", "cancer", "genetic disorder", "disease", "phenotype",
                "hereditary disease", "nervous system disease", "cardiovascular disease",
                "immune system disease", "metabolic disease", "digestive system disease"
            ]:
                continue
            areas = [ta.get("name", "") for ta in d.get("therapeuticAreas", []) if ta.get("name")]
            results.append({
                "id": d.get("id", ""),
                "name": d_name,
                "description": d.get("description", ""),
                "score": round(score, 2),
                "therapeuticAreas": areas
            })
        return results
    except Exception as e:
        print(f"OpenTargets fetch notice for {ensembl_id}: {e}")
        return []


def extract_diseases_from_variant_notes(variants: List[Dict[str, Any]], general_notes: List[str]) -> List[Dict[str, Any]]:
    """
    Extracts somatic and germline tumor/disease mentions from UniProt natural variant descriptions
    and free-text disease notes (e.g., 'in breast cancer', 'in colorectal cancer', 'in melanoma').
    """
    extracted: Dict[str, Dict[str, Any]] = {}

    # 1. Scan variant descriptions like "in breast cancer; somatic" or "in LFS; dbSNP:..."
    pattern = re.compile(r"\bin\s+([A-Za-z0-9\-\s',/]+?)(?:;|\.|\(|$)", re.IGNORECASE)
    ignore_terms = {
        "dbsnp", "sporadic", "somatic", "germline", "patients", "a patient", "one patient",
        "two patients", "some patients", "general population", "polymorphism", "cancer",
        "tumors", "tumours", "samples", "cell lines", "combination", "vitro", "vivo"
    }

    for v in variants:
        desc = v.get("description", "")
        change = v.get("change", "")
        pos = v.get("position")
        if not desc:
            continue
        for match in pattern.finditer(desc):
            raw_cond = match.group(1).strip()
            low_cond = raw_cond.lower()
            if len(raw_cond) < 3 or len(raw_cond) > 65:
                continue
            if any(ig == low_cond or low_cond.startswith(ig + " ") for ig in ignore_terms):
                continue
            key = normalize_disease_key(raw_cond)
            if not key:
                continue
            if key not in extracted:
                extracted[key] = {
                    "rawName": raw_cond,
                    "variants": [],
                    "positions": []
                }
            if change and change not in extracted[key]["variants"]:
                extracted[key]["variants"].append(change)
            if pos and pos not in extracted[key]["positions"]:
                extracted[key]["positions"].append(pos)

    # 2. Scan general disease notes for tumor lists (e.g. "bladder carcinoma, brain tumors, breast carcinoma...")
    known_tumors = [
        ("bladder carcinoma", "Mesane Karsinomu (Bladder Carcinoma)"),
        ("brain tumors", "Beyin Tümörleri / Gliomlar (Brain Tumors)"),
        ("breast carcinoma", "Meme Karsinomu (Breast Carcinoma)"),
        ("cervical", "Serviks (Rahim Ağzı) Karsinomu"),
        ("colon", "Kolorektal Karsinom (Colon Carcinoma)"),
        ("esophageal", "Özofagus Karsinomu"),
        ("larynx", "Larinks (Gırtlak) Yassı Hücreli Karsinomu"),
        ("liver", "Hepatosellüler Karsinom (Karaciğer Kanseri)"),
        ("lung", "Akciğer Karsinomu (Lung Cancer)"),
        ("melanoma", "Malign Melanom"),
        ("ovary", "Over (Yumurtalık) Seröz Karsinomu"),
        ("pancreas", "Pankreas Adenokarsinomu"),
        ("prostate", "Prostat Karsinomu"),
        ("stomach", "Mide (Gastrik) Adenokarsinomu"),
        ("thyroid", "Tiroid Karsinomu")
    ]
    joined_notes = " ".join(general_notes).lower()
    for kw, tr_title in known_tumors:
        if kw in joined_notes:
            key = normalize_disease_key(tr_title)
            if key and key not in extracted:
                extracted[key] = {
                    "rawName": tr_title,
                    "variants": [],
                    "positions": []
                }

    return list(extracted.values())


def build_comprehensive_disease_profile(
    uniprot_data: Dict[str, Any],
    clinvar_variants: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Aggregates, deduplicates, and enriches the complete disease spectrum for a protein from:
    1. Physician-curated Turkish Clinical Atlas (CLINICAL_DISEASE_ATLAS)
    2. All UniProtKB DISEASE comments (with OMIM IDs, full descriptions, and mechanism notes)
    3. All UniProtKB Orphanet rare disease cross-references
    4. All ClinVar clinical condition traits & associated pathogenic mutations
    5. UniProtKB Natural Variant & somatic tumor spectrum annotations
    6. EMBL-EBI Open Targets Platform live disease associations
    7. Approved drugs / pharmaceutical target data (DrugBank & UniProt Pharmaceutical)
    """
    gene = (uniprot_data.get("geneSymbol") or "").upper()
    protein_name = uniprot_data.get("proteinName", gene)
    ensembl_id = uniprot_data.get("ensemblId", "")

    diseases_by_key: Dict[str, Dict[str, Any]] = {}
    ordered_keys: List[str] = []

    def add_or_merge_disease(entry: Dict[str, Any]):
        raw_name = entry.get("name") or entry.get("englishName") or ""
        eng_name = entry.get("englishName") or raw_name
        key = normalize_disease_key(eng_name) or normalize_disease_key(raw_name)
        if not key or len(key) < 2:
            return

        if key not in diseases_by_key:
            diseases_by_key[key] = {
                "name": entry.get("name") or translate_disease_title(eng_name),
                "englishName": eng_name,
                "acronym": entry.get("acronym", ""),
                "category": entry.get("category") or classify_medical_specialty(eng_name, entry.get("pathophysiology", "")),
                "inheritance": entry.get("inheritance") or infer_inheritance(entry.get("pathophysiology", "")),
                "omimId": entry.get("omimId", ""),
                "orphaId": entry.get("orphaId", ""),
                "openTargetsScore": entry.get("openTargetsScore"),
                "pathophysiology": entry.get("pathophysiology", ""),
                "clinicalManagement": entry.get("clinicalManagement", ""),
                "relatedMutations": list(entry.get("relatedMutations", [])),
                "sources": list(entry.get("sources", []))
            }
            ordered_keys.append(key)
        else:
            existing = diseases_by_key[key]
            if not existing.get("acronym") and entry.get("acronym"):
                existing["acronym"] = entry["acronym"]
            if not existing.get("omimId") and entry.get("omimId"):
                existing["omimId"] = entry["omimId"]
            if not existing.get("orphaId") and entry.get("orphaId"):
                existing["orphaId"] = entry["orphaId"]
            if not existing.get("openTargetsScore") and entry.get("openTargetsScore"):
                existing["openTargetsScore"] = entry["openTargetsScore"]
            if not existing.get("clinicalManagement") and entry.get("clinicalManagement"):
                existing["clinicalManagement"] = entry["clinicalManagement"]
            if len(entry.get("pathophysiology", "")) > len(existing.get("pathophysiology", "")) and "Klinik Atlas" not in existing.get("sources", []):
                existing["pathophysiology"] = entry["pathophysiology"]
            for mut in entry.get("relatedMutations", []):
                if mut and mut not in existing["relatedMutations"] and len(existing["relatedMutations"]) < 10:
                    existing["relatedMutations"].append(mut)
            for src in entry.get("sources", []):
                if src and src not in existing["sources"]:
                    existing["sources"].append(src)

    # 1. Add Physician-Curated Clinical Atlas entries if available for this gene
    for item in CLINICAL_DISEASE_ATLAS.get(gene, []):
        item_copy = dict(item)
        item_copy["sources"] = ["Klinik Rehber", "UniProt / OMIM"]
        add_or_merge_disease(item_copy)

    # 2. Add ALL UniProt DISEASE entries (no truncation!)
    for u_dis in uniprot_data.get("diseases", []):
        d_id = u_dis.get("diseaseId", "")
        if not d_id or d_id == "Klinik Patoloji":
            continue
        desc = u_dis.get("description", "")
        mech = u_dis.get("mechanismNote", "")
        full_desc = desc
        if mech and mech not in desc:
            full_desc = f"{desc} {mech}".strip() if desc else mech

        add_or_merge_disease({
            "name": translate_disease_title(d_id),
            "englishName": d_id,
            "acronym": u_dis.get("acronym", ""),
            "category": classify_medical_specialty(d_id, full_desc),
            "inheritance": infer_inheritance(full_desc),
            "omimId": u_dis.get("omimId", ""),
            "pathophysiology": full_desc or f"{gene} genindeki patojenik varyasyonlarla ilişkili klinik sendrom.",
            "sources": ["UniProtKB"] + (["OMIM"] if u_dis.get("omimId") else [])
        })

    # 3. Add ALL Orphanet rare disease cross-references from UniProt
    for orpha in uniprot_data.get("orphanetDiseases", []):
        o_name = orpha.get("name", "")
        o_id = orpha.get("orphaId", "")
        if not o_name:
            continue
        add_or_merge_disease({
            "name": translate_disease_title(o_name),
            "englishName": o_name,
            "category": classify_medical_specialty(o_name, ""),
            "inheritance": infer_inheritance(o_name),
            "orphaId": o_id,
            "pathophysiology": f"Orphanet nadir hastalıklar veritabanında {gene} ({protein_name}) geni ile ilişkilendirilmiş klinik antite (OrphaCode: ORPHA:{o_id}).",
            "sources": ["Orphanet"]
        })

    # 4. Aggregate ALL distinct clinical conditions from ClinVar variants
    ignore_clinvar_traits = {
        "not provided", "not specified", "notprovided", "see cases", "allhighlypenetrant",
        "inborn genetic diseases", "hereditary cancer-predisposing syndrome"
    }
    clinvar_grouped: Dict[str, Dict[str, Any]] = {}
    for cv in clinvar_variants or []:
        p_change = cv.get("proteinChange") or cv.get("title", "")
        sig = cv.get("clinicalSignificance", "Pathogenic")
        for cond in cv.get("conditions", []):
            c_clean = cond.strip()
            c_low = c_clean.lower()
            if not c_clean or c_low in ignore_clinvar_traits:
                continue
            c_key = normalize_disease_key(c_clean)
            if not c_key:
                continue
            if c_key not in clinvar_grouped:
                clinvar_grouped[c_key] = {
                    "rawName": c_clean,
                    "mutations": [],
                    "significances": set(),
                    "count": 0
                }
            clinvar_grouped[c_key]["count"] += 1
            clinvar_grouped[c_key]["significances"].add(sig)
            if p_change and p_change not in clinvar_grouped[c_key]["mutations"]:
                clinvar_grouped[c_key]["mutations"].append(p_change)

    for c_key, c_info in sorted(clinvar_grouped.items(), key=lambda x: -x[1]["count"]):
        raw_cond = c_info["rawName"]
        mut_list = c_info["mutations"][:6]
        sigs_str = ", ".join(sorted(c_info["significances"]))
        add_or_merge_disease({
            "name": translate_disease_title(raw_cond),
            "englishName": raw_cond,
            "category": classify_medical_specialty(raw_cond, ""),
            "inheritance": infer_inheritance(raw_cond),
            "pathophysiology": (
                f"NCBI ClinVar klinik genetik veritabanında {gene} genindeki {c_info['count']} varyant "
                f"({sigs_str}) bu hastalık/fenotip ile doğrudan ilişkilendirilmiştir"
                + (f" (Örnek mutasyonlar: {', '.join(mut_list[:4])})." if mut_list else ".")
            ),
            "relatedMutations": mut_list,
            "sources": ["ClinVar"]
        })

    # 5. Extract somatic / germline diseases from UniProt Natural Variants & General Notes
    variant_diseases = extract_diseases_from_variant_notes(
        uniprot_data.get("allVariants", uniprot_data.get("variants", [])),
        uniprot_data.get("generalDiseaseNotes", [])
    )
    for vd in variant_diseases:
        raw_vd = vd["rawName"]
        muts = vd["variants"][:6]
        add_or_merge_disease({
            "name": translate_disease_title(raw_vd),
            "englishName": raw_vd,
            "category": classify_medical_specialty(raw_vd, ""),
            "inheritance": "Somatik / Germline Varyant",
            "pathophysiology": (
                f"UniProtKB doğal varyant ve tümör spektrumu kayıtlarında {gene} mutasyonlarının "
                f"saptandığı klinik patoloji"
                + (f" (Kaydedilen varyantlar: {', '.join(muts[:4])})." if muts else ".")
            ),
            "relatedMutations": muts,
            "sources": ["UniProt Varyant"]
        })

    # 6. Query Live EBI Open Targets Platform if we have an Ensembl ID (enriches any protein with up to 18 diseases)
    if ensembl_id and len(ordered_keys) < 18:
        ot_diseases = fetch_opentargets_diseases(ensembl_id, limit=20)
        for ot in ot_diseases:
            ot_name = ot["name"]
            ot_desc = ot.get("description") or ""
            areas_str = ", ".join(ot.get("therapeuticAreas", [])[:2])
            add_or_merge_disease({
                "name": translate_disease_title(ot_name),
                "englishName": ot_name,
                "category": classify_medical_specialty(ot_name, f"{ot_desc} {areas_str}"),
                "inheritance": infer_inheritance(ot_desc),
                "openTargetsScore": ot["score"],
                "pathophysiology": (
                    f"{ot_desc} (Open Targets Klinik İlişki Skoru: {ot['score']})"
                    if ot_desc
                    else f"Open Targets Platformu klinik/genomik kanıt veritabanında {gene} ({protein_name}) ile ilişkilendirilmiş patoloji (Kanıt Skoru: {ot['score']})."
                ),
                "sources": ["OpenTargets"]
            })

    all_diseases = [diseases_by_key[k] for k in ordered_keys]

    def normalize_primary_specialty(cat_str: str) -> str:
        low = (cat_str or "").lower()
        if "onkoloji" in low:
            return "Tıbbi Onkoloji"
        if "hematoloji" in low:
            return "Hematoloji"
        if "genetik" in low:
            return "Tıbbi Genetik"
        if "endokrinoloji" in low or "metabolizma" in low:
            return "Endokrinoloji & Metabolizma"
        if "nöroloji" in low or "nöro" in low:
            return "Nöroloji"
        if "kardiyoloji" in low or "vasküler" in low:
            return "Kardiyoloji"
        if "göğüs" in low or "pulmonoloji" in low:
            return "Göğüs Hastalıkları"
        if "romatoloji" in low or "immünoloji" in low:
            return "İmmünoloji & Romatoloji"
        if "enfeksiyon" in low:
            return "Enfeksiyon Hastalıkları"
        if "nefroloji" in low or "gastroenteroloji" in low or "üroloji" in low:
            return "İç Hastalıkları & Organ Sistemleri"
        return cat_str or "Klinik Patoloji"

    # Group counts by normalized primary medical specialty for clinical dashboard filter tabs
    specialty_counts: Dict[str, int] = {}
    for d in all_diseases:
        prim = normalize_primary_specialty(d.get("category", "Klinik Patoloji"))
        d["primarySpecialty"] = prim
        specialty_counts[prim] = specialty_counts.get(prim, 0) + 1

    return {
        "totalCount": len(all_diseases),
        "specialtyBreakdown": [
            {"specialty": k, "count": v}
            for k, v in sorted(specialty_counts.items(), key=lambda x: -x[1])
        ],
        "generalClinicalNotes": uniprot_data.get("generalDiseaseNotes", []),
        "targetedDrugs": uniprot_data.get("drugs", []),
        "pharmaceuticalNotes": uniprot_data.get("pharmaceuticalNotes", []),
        "diseases": all_diseases
    }
