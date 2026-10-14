import requests
from typing import Dict, Any, List, Optional

UNIPROT_SEARCH_URL = "https://rest.uniprot.org/uniprotkb/search"
UNIPROT_ENTRY_URL = "https://rest.uniprot.org/uniprotkb/{accession}.json"

HEADERS = {
    "User-Agent": "BioLens-AI/1.0 (academic-computational-biology-tool)"
}

def search_proteins(query: str, limit: int = 8) -> List[Dict[str, Any]]:
    """
    Search UniProtKB for gene names or protein names.
    Prioritizes human (organism_id:9606) and reviewed (Swiss-Prot) records.
    """
    query_clean = query.strip()
    if not query_clean:
        return []

    # First attempt: exact gene or high priority reviewed human entry
    search_query = f"(gene_exact:{query_clean} OR gene:{query_clean} OR protein_name:{query_clean} OR {query_clean}) AND (organism_id:9606) AND (reviewed:true)"
    
    try:
        resp = requests.get(
            UNIPROT_SEARCH_URL,
            params={"query": search_query, "format": "json", "size": limit},
            headers=HEADERS,
            timeout=8
        )
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            if results:
                return [format_search_hit(item) for item in results]
    except Exception as e:
        print(f"UniProt targeted search error: {e}")

    # Fallback broader search if no hits found
    broad_query = f"({query_clean}) AND (organism_id:9606)"
    try:
        resp = requests.get(
            UNIPROT_SEARCH_URL,
            params={"query": broad_query, "format": "json", "size": limit},
            headers=HEADERS,
            timeout=8
        )
        if resp.status_code == 200:
            data = resp.json()
            results = data.get("results", [])
            if results:
                return [format_search_hit(item) for item in results]
    except Exception as e:
        print(f"UniProt fallback search error: {e}")

    return []

def format_search_hit(item: Dict[str, Any]) -> Dict[str, Any]:
    acc = item.get("primaryAccession", "")
    id_name = item.get("uniProtkbId", "")
    
    # Gene names
    genes = []
    for g in item.get("genes", []):
        if "geneName" in g:
            genes.append(g["geneName"].get("value", ""))
        for syn in g.get("synonyms", []):
            genes.append(syn.get("value", ""))
    gene_symbol = genes[0] if genes else id_name.split("_")[0]

    # Protein description
    desc = item.get("proteinDescription", {})
    rec_name = desc.get("recommendedName", {}).get("fullName", {}).get("value")
    if not rec_name:
        sub_names = desc.get("submissionNames", [])
        if sub_names:
            rec_name = sub_names[0].get("fullName", {}).get("value")
    if not rec_name:
        rec_name = gene_symbol

    organism = item.get("organism", {}).get("scientificName", "Homo sapiens")
    seq_len = item.get("sequence", {}).get("length", 0)

    return {
        "accession": acc,
        "entryName": id_name,
        "geneSymbol": gene_symbol,
        "allGenes": genes[:4],
        "proteinName": rec_name,
        "organism": organism,
        "length": seq_len,
        "reviewed": item.get("entryType") == "UniProtKB reviewed (Swiss-Prot)"
    }

def get_protein_details(accession_or_gene: str) -> Optional[Dict[str, Any]]:
    """
    Fetch comprehensive entry details from UniProt.
    If a gene name is passed, first resolve it to canonical primary accession.
    """
    acc = accession_or_gene.strip().upper()
    
    # If not in accession format (e.g., TP53 instead of P04637), search first
    if not (len(acc) in [6, 10] and acc[0].isalpha() and acc[1].isdigit()):
        hits = search_proteins(acc, limit=1)
        if hits:
            acc = hits[0]["accession"]
        else:
            return None

    try:
        resp = requests.get(
            UNIPROT_ENTRY_URL.format(accession=acc),
            headers=HEADERS,
            timeout=10
        )
        if resp.status_code != 200:
            return None
        
        entry = resp.json()
        return parse_uniprot_entry(entry)
    except Exception as e:
        print(f"Error fetching UniProt entry {acc}: {e}")
        return None

def parse_uniprot_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    acc = entry.get("primaryAccession", "")
    id_name = entry.get("uniProtkbId", "")
    
    # Genes
    genes = []
    primary_gene = ""
    for g in entry.get("genes", []):
        if "geneName" in g:
            primary_gene = g["geneName"].get("value", "")
            genes.append(primary_gene)
        for syn in g.get("synonyms", []):
            genes.append(syn.get("value", ""))
    if not primary_gene and genes:
        primary_gene = genes[0]
    if not primary_gene:
        primary_gene = id_name.split("_")[0]

    # Names
    desc = entry.get("proteinDescription", {})
    rec_name = desc.get("recommendedName", {}).get("fullName", {}).get("value")
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
    pathways = []
    
    for comment in entry.get("comments", []):
        c_type = comment.get("commentType", "")
        if c_type == "FUNCTION":
            for text_obj in comment.get("texts", []):
                raw_func = text_obj.get("value", "")
                import re
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
            
            note_obj = comment.get("note") or {}
            note_texts = note_obj.get("texts", []) if isinstance(note_obj, dict) else []
            d_text = " ".join([t.get("value", "") for t in note_texts if isinstance(t, dict)]) if note_texts else d_desc
            
            diseases.append({
                "diseaseId": d_name or "Klinik Patoloji",
                "description": d_text or d_desc,
                "acronym": disease_obj.get("acronym", "")
            })
        elif c_type == "PATHWAY":
            for text_obj in comment.get("texts", []):
                pathways.append(text_obj.get("value", ""))

    # Gene Ontology (GO terms)
    go_terms = {"biological_process": [], "molecular_function": [], "cellular_component": []}
    for ref in entry.get("uniProtKBCrossReferences", []):
        if ref.get("database") == "GO":
            go_id = ref.get("id", "")
            properties = {p.get("key"): p.get("value") for p in ref.get("properties", [])}
            term_str = properties.get("GoTerm", "")
            if term_str.startswith("P:"):
                go_terms["biological_process"].append({"id": go_id, "name": term_str[2:]})
            elif term_str.startswith("F:"):
                go_terms["molecular_function"].append({"id": go_id, "name": term_str[2:]})
            elif term_str.startswith("C:"):
                go_terms["cellular_component"].append({"id": go_id, "name": term_str[2:]})

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
        "geneSymbol": primary_gene,
        "synonyms": genes,
        "proteinName": rec_name or primary_gene,
        "alternativeNames": alt_names[:4],
        "organism": organism,
        "commonOrganism": common_organism,
        "length": length,
        "mass": mass,
        "sequence": sequence,
        "functions": functions,
        "subcellularLocations": list(dict.fromkeys(subcellular_locations))[:6],
        "diseases": diseases,
        "pathways": pathways[:4],
        "goTerms": {
            "biologicalProcess": go_terms["biological_process"][:8],
            "molecularFunction": go_terms["molecular_function"][:8],
            "cellularComponent": go_terms["cellular_component"][:8]
        },
        "variants": variants[:25]
    }
