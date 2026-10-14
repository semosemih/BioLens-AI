import requests
from typing import Dict, Any, List

EUROPE_PMC_SEARCH_URL = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"

def get_scientific_literature(gene_symbol: str, protein_name: str, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Fetch peer-reviewed articles from Europe PMC (PubMed and PMC open access).
    Searches for high-impact papers associating the protein/gene with mechanism and disease.
    """
    if not gene_symbol and not protein_name:
        return []
        
    keyword = gene_symbol or protein_name
    query = f'("{keyword}" OR "{protein_name}") AND (disease OR mutation OR structure OR function) AND (SRC:MED OR HAS_ABSTRACT:y)'
    
    params = {
        "query": query,
        "format": "json",
        "pageSize": limit,
        "sort": "CITED desc"  # Sort by citation count for high-impact papers
    }
    
    try:
        resp = requests.get(EUROPE_PMC_SEARCH_URL, params=params, timeout=10)
        if resp.status_code != 200:
            return []
            
        data = resp.json()
        results = data.get("resultList", {}).get("result", [])
        
        articles = []
        for item in results:
            pmid = item.get("pmid")
            doi = item.get("doi")
            title = item.get("title", "").strip().rstrip(".")
            # Clean HTML tags like <b>, <i> from title
            if title:
                for tag in ["<b>", "</b>", "<i>", "</i>", "<em>", "</em>"]:
                    title = title.replace(tag, "")
            abstract = item.get("abstractText", "")
            
            # Clean abstract tags like <b>, <i>, <p>
            if abstract:
                abstract = (abstract.replace("<b>", "")
                                    .replace("</b>", "")
                                    .replace("<i>", "")
                                    .replace("</i>", "")
                                    .replace("<p>", "")
                                    .replace("</p>", ""))

            journal = item.get("journalTitle") or item.get("journalInfo", {}).get("journal", {}).get("title", "")
            year = item.get("pubYear", "")
            authors = item.get("authorString", "")
            citations = item.get("citedByCount", 0)
            
            url = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else (f"https://doi.org/{doi}" if doi else "")
            
            articles.append({
                "pmid": pmid,
                "doi": doi,
                "title": title,
                "abstract": abstract,
                "journal": journal,
                "year": year,
                "authors": authors,
                "citations": citations,
                "url": url
            })
            
        return articles
    except Exception as e:
        print(f"Europe PMC search error for {keyword}: {e}")
        return []
