import re
import requests
from typing import Dict, Any, List

NCBI_ESEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
NCBI_ESUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

IGNORE_TRAITS = {
    "not provided",
    "not specified",
    "notprovided",
    "see cases",
    "allhighlypenetrant"
}


def get_clinvar_variants(gene_symbol: str, limit: int = 35) -> List[Dict[str, Any]]:
    """
    Query NCBI ClinVar for clinical variants of the specified gene.
    Focuses on pathogenic, likely pathogenic, and drug-response variants,
    extracting comprehensive disease/trait associations.
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
            
            # Extract clinical significance across germline, somatic clinical impact, or oncogenicity
            germline = v_info.get("germline_classification") or {}
            clin_impact = v_info.get("clinical_impact_classification") or {}
            oncogenicity = v_info.get("oncogenicity_classification") or {}

            sig_desc = (
                germline.get("description")
                or clin_impact.get("description")
                or oncogenicity.get("description")
                or "Pathogenic / Clinical"
            )
            review_status = (
                germline.get("review_status")
                or clin_impact.get("review_status")
                or oncogenicity.get("review_status")
                or ""
            )
            
            # Associated diseases / traits across germline and somatic classifications
            traits = []
            all_trait_sets = (
                list(v_info.get("trait_set") or [])
                + list(germline.get("trait_set") or [])
                + list(clin_impact.get("trait_set") or [])
                + list(oncogenicity.get("trait_set") or [])
            )
            for t in all_trait_sets:
                if not isinstance(t, dict):
                    continue
                t_name = (t.get("trait_name") or "").strip()
                if t_name and t_name.lower() not in IGNORE_TRAITS and t_name not in traits:
                    traits.append(t_name)
                    
            # Parse protein change (e.g. p.Arg175His, p.R175H, p.Arg248GlyfsTer22)
            p_change = ""
            pos = None
            if "p." in title:
                part = title.split("p.")[-1].split(")")[0].strip()
                p_change = f"p.{part}"
                m = re.search(r"[A-Za-z]{1,3}(\d+)", part) or re.search(r"(\d+)", part)
                if m:
                    try:
                        pos = int(m.group(1))
                    except ValueError:
                        pass

            variants.append({
                "clinvarId": uid,
                "title": title,
                "proteinChange": p_change,
                "position": pos,
                "clinicalSignificance": sig_desc,
                "conditions": traits[:6],
                "reviewStatus": review_status,
                "clinvarUrl": f"https://www.ncbi.nlm.nih.gov/clinvar/variation/{uid}/"
            })
            
        return variants
    except Exception as e:
        print(f"ClinVar search error for {gene_symbol}: {e}")
        return []
