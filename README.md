# 🧬 BioLens AI

**Proteinleri Keşfetme, 3 Boyutlu Yapılarını Görselleştirme ve Hastalık İlişkilerini Araştırma Platformu**

BioLens AI; biyoloji ve tıp araştırmacıları, öğrenciler ve biyomedikal meraklıları için proteinlerin biyolojik işlevlerini, **AlphaFold 3B yapısal tahminlerini**, **ClinVar klinik patojenik varyasyonlarını** ve **PubMed / Europe PMC hakemli bilimsel literatürünü** tek bir modern ve etkileşimli çatı altında birleştiren hesaplamalı biyoloji platformudur.

---

## 🌟 Öne Çıkan Özellikler

1. **Akıllı Protein Arama & UniProt Entegrasyonu:**
   - Gen adı (ör. `TP53`, `EGFR`, `BRCA1`, `INS`, `CFTR`) veya UniProt Accession (`P04637`) ile anında arama ve otomatik tamamlama.
   - Biyolojik süreçler, Gene Ontology (GO terimleri), hücresel yerleşim (çekirdek, sitoplazma, membran vb.) ve FASTA dizisi görüntüleme/kopyalama.

2. **Etkileşimli 3 Boyutlu Yapı Görselleştirme (AlphaFold + 3Dmol.js):**
   - AlphaFold Protein Structure Database'den doğrudan çekilen `.pdb` koordinatları ile tarayıcıda WebGL tabanlı 3B modelleme.
   - **pLDDT Renklendirmesi:** 
     - 🟦 **> 90 (Koyu Mavi):** Çok yüksek güven (omurga ve yan zincirler yüksek doğrulukta).
     - 🔷 **70 - 90 (Açık Mavi):** Güvenilir (genel üçüncül katlanma doğru).
     - 🟨 **50 - 70 (Sarı):** Düşük güven (esnek döngüler ve yüzey bölgeleri).
     - 🟧 **< 50 (Turuncu):** Çok düşük güven (Doğal olarak düzensiz / IDR segmentleri).
   - Şerit (Ribbon), Çubuk (Stick), Küre (Sphere) ve Moleküler Yüzey (Surface) görünümleri.
   - Otomatik döndürme, kamera sıfırlama, tam ekran (fullscreen) modu, doğrudan AlphaFold `.pdb` koordinat dosyası indirme, kullanıcı tanımlı kalıntı pozisyonuna 3B odaklanma ve yüksek çözünürlüklü PNG görüntü kaydetme.

3. **Klinik Mutasyonlar & 3B Yapıda Doğrudan Kalıntı İşaretleme:**
   - **NCBI ClinVar** ve **UniProt** veritabanlarından patojenik varyasyonların listelenmesi (örn. p.Arg175His, p.Gly12Asp).
   - **3D Odaklan (Locate on 3D):** Tablodan bir mutasyona tıklandığında 3B görüntüleyici anında ilgili amino asit kalıntısına yakınlaşır, kalıntıyı küre ve çubuk formatında renklendirir ve 3B etiket ekler.

4. **Biyomedikal Yapay Zekâ Analiz Katmanı (Türkçe):**
   - Ham biyokimyasal ve literatür verilerini araştırmacılar için net, anlaşılır Türkçe formatta 4 ana başlığa dönüştürür:
     - 🧬 **Temel Biyolojik Rol**
     - ⚠️ **Hastalık ve Klinik İlişkisi**
     - 🔬 **3B Yapı ve AlphaFold Güven Analizi**
     - ⚡ **Öne Çıkan Mutasyon ve Literatür Bulguları**

5. **Hakemli Bilimsel Literatür (Europe PMC / PubMed):**
   - İlgili proteine ve hastalıklara dair en çok atıf alan güncel makaleler.
   - Dergi adı, yayın yılı, yazarlar, atıf sayısı ve genişletilebilir tam özet metinleri (Abstract).

---

## 🏛 Sistem Mimarisi

```text
[Kullanıcı Arayüzü: React + 3Dmol.js + Vite]
               │
               ▼  (HTTP / REST API)
      [FastAPI Backend Servisi]
   ┌───────────┼───────────┬──────────────┐
   ▼           ▼           ▼              ▼
[UniProt REST] [AlphaFold DB] [ClinVar/NCBI] [Europe PMC/PubMed]
 (Dizi/İşlev)   (.PDB / .CIF)  (Varyantlar)   (Literatür / DOI)
                           │              │
                           └──────┬───────┘
                                  ▼
                     [Biyomedikal Yapay Zekâ Katmanı]
                (Gemini API / Domain-Specific NLP Motoru)
```

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- **Python 3.9+**
- **Node.js 18+** ve **npm**

### Tek Komutla Başlatma

BioLens AI'ın backend ve frontend servislerini aynı anda başlatmak için proje kök dizininde:

```bash
python3 run_app.py
```

Bu komut:
- FastAPI backend servisini `http://127.0.0.1:8000` adresinde başlatır.
- React frontend arayüzünü `http://localhost:5173` adresinde başlatır.

### Manuel Başlatma

#### 1. Backend:
```bash
cd backend
python3 -m pip install -r requirements.txt
python3 -m uvicorn main:app --reload --port 8000
```
*API belgelerine `http://127.0.0.1:8000/docs` adresinden Swagger UI ile erişebilirsiniz.*

#### 2. Frontend:
```bash
cd frontend
npm install
npm run dev
```
*Tarayıcınızda `http://localhost:5173` adresini açın.*

---

## 🗺 Geliştirme Yol Haritası (Roadmap)

| Aşama | Durum | Kapsam |
| :--- | :---: | :--- |
| **Faz 1: Veri Toplayıcı & API** | ✅ Tamamlandı | UniProt REST, AlphaFold DB, ClinVar ve Europe PMC uç noktaları bağlandı. PDB streaming ve CORS desteği sağlandı. |
| **Faz 2: 3D Arayüz & İstemci** | ✅ Tamamlandı | React + 3Dmol.js WebGL entegrasyonu. pLDDT renklendirmesi, dönme/yakınlaştırma kontrolleri ve mutasyon kalıntı işaretleme. |
| **Faz 3: Zekâ Katmanı** | ✅ Tamamlandı | PubMed literatür sentezi + Türkçe Biyomedikal Yapay Zekâ özetleyici motoru. |
| **Gelecek Faz: ESM-2 Modeli** | 🔮 Planlanan | Hugging Face üzerinden Meta AI **ESM-2** (Evolutionary Scale Modeling) protein dil modelini entegre ederek, kullanıcı tanımlı amino asit mutasyonlarında zero-shot variant effect ve stabilite tahmini hesaplama. |

---

## 🔬 Bilimsel Kaynaklar ve Veri Sağlayıcılar

- **AlphaFold DB:** [alphafold.ebi.ac.uk](https://alphafold.ebi.ac.uk/) (DeepMind & EMBL-EBI)
- **UniProtKB:** [uniprot.org](https://www.uniprot.org/) (Universal Protein Resource)
- **ClinVar:** [ncbi.nlm.nih.gov/clinvar](https://www.ncbi.nlm.nih.gov/clinvar/) (NCBI)
- **Europe PMC:** [europepmc.org](https://europepmc.org/) (EBI)
