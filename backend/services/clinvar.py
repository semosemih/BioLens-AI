import requests
from typing import Dict, Any, List

NCBI_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
NCBI_ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

def get_clinvar_variants(gene_symbol: str, limit: int = 15) -> List[Dict[str, Any]]:
    """
    Query NCBI ClinVar for clinical variants of the specified gene.
    Focuses on pathogenic, likely pathogenic, and drug-response variants.
    """
    if not gene_symbol:
        return []
        
    try:
        # Search ClinVar for gene with pathogenic or likely pathogenic variants
        search_term = f"{gene_symbol}[gene] AND (pathogenic[clinical_significance] OR likely pathogenic[clinical_significance])"
        params = {
            "db": "clinvar",
            "term": search_term,
            "retmode": "json",
            "retmax": limit,
            "sort": "clinical_significance"
        }
        
        search_resp = requests.get(NCBI_ESEARCH_URL, params=params, timeout=8)
        if search_resp.status_code != 200:
            return []
            
        id_list = search_resp.json().get("esearchresult", {}).get("idlist", [])
        if not id_list:
            # Fallback search with just the gene
            params["term"] = f"{gene_symbol}[gene]"
            search_resp = requests.get(NCBI_ESEARCH_URL, params=params, timeout=8)
            if search_resp.status_code == 200:
                id_list = search_resp.json().get("esearchresult", {}).get("idlist", [])
                
        if not id_list:
            return []

        # Fetch summaries for variant IDs
        sum_params = {
            "db": "clinvar",
            "id": ",".join(id_list),
            "retmode": "json"
        }
        sum_resp = requests.get(NCBI_ESUMMARY_URL, params=sum_params, timeout=10)
        if sum_resp.status_code != 200:
            return []
            
        sum_data = sum_resp.json().get("result", {})
        uids = sum_data.get("uids", [])
        
        variants = []
        for uid in uids:
            v_info = sum_data.get(uid, {})
            title = v_info.get("title", "")
            
            # Extract clinical significance
            germline = v_info.get("germline_classification", {})
            sig_desc = germline.get("description", "Unknown")
            
            # Associated diseases / traits
            traits = []
            for t in v_info.get("trait_set", []):
                t_name = t.get("trait_name")
                if t_name:
                    traits.append(t_name)
                    
            # Parse protein change (e.g. p.Arg175His or p.R175H)
            p_change = ""
            pos = None
            if "p." in title:
                part = title.split("p.")[-1].split(")")[0]
                p_change = f"p.{part}"
                # extract numeric position if present
                digits = "".join([c for c in part if c.isdigit()])
                if digits:
                    try:
                        pos = int(digits)
                    except ValueError:
                        pass

            variants.append({
                "clinvarId": uid,
                "title": title,
                "proteinChange": p_change,
                "position": pos,
                "clinicalSignificance": sig_desc,
                "conditions": traits[:3],
                "reviewStatus": germline.get("review_status", ""),
                "clinvarUrl": f"https://www.ncbi.nlm.nih.gov/clinvar/variation/{uid}/"
            })
            
        return variants
    except Exception as e:
        print(f"ClinVar search error for {gene_symbol}: {e}")
        return []
