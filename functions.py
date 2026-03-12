import requests

RXNORM_BASE = "https://rxnav.nlm.nih.gov/REST"

# Define unique RxCUI ID from user input
def find_rxcui(drug_name):

    url = RXNORM_BASE + "/rxcui.json"
    params = {"name": drug_name}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return None

    data = response.json()

    try:
        rxcui = data["idGroup"]["rxnormId"][0]
        return rxcui
    except (KeyError, TypeError, IndexError):
        return None


# Takes the RxCUI and retrieves the basic drug properties from the RxNorm API
# (name, synonym, term type, and language)
def get_drug_properties(rxcui):

    url = RXNORM_BASE + "/rxcui/" + rxcui + "/properties.json"
    response = requests.get(url)

    if response.status_code != 200:
        return None

    data = response.json()

    try:
        props = data["properties"]
        return {
            "name": props.get("name", ""),
            "synonym": props.get("synonym", ""),
            "tty": props.get("tty", ""),
            "language": props.get("language", "")
        }
    except (KeyError, TypeError):
        return None


# Takes the RxCUI and retrieves the drug classification categories it belongs to
def get_drug_class(rxcui):

    url = RXNORM_BASE + "/rxclass/class/byRxcui.json"
    params = {"rxcui": rxcui}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return []

    data = response.json()

    try:
        classes = data["rxclassDrugInfoList"]["rxclassDrugInfo"]
        results = []
        seen = set()
        for c in classes:
            item = c["rxclassMinConceptItem"]
            name = item.get("className", "")
            class_type = item.get("classType", "")

            if name not in seen:
                seen.add(name)
                results.append({
                    "className": name,
                    "classType": class_type
                })
        return results
    except (KeyError, TypeError):
        return []


# Takes the RxCUI and returns all its related concepts
def get_related_concepts(rxcui):

    url = RXNORM_BASE + "/rxcui/" + rxcui + "/related.json"
    params = {"tty": "IN+BN+SBD"}
    response = requests.get(url, params=params)

    if response.status_code != 200:
        return []

    data = response.json()

    try:
        concept_groups = data["relatedGroup"]["conceptGroup"]
        related = []
        for group in concept_groups:
            if "conceptProperties" not in group:
                continue
            for concept in group["conceptProperties"]:
                related.append({
                    "name": concept.get("name", ""),
                    "rxcui": concept.get("rxcui", ""),
                    "tty": concept.get("tty", "")
                })
        return related
    except (KeyError, TypeError):
        return []


# Master function that will call all information provided to user based on the requested RxCUI
def get_all_drug_info(drug_name):

    rxcui = find_rxcui(drug_name)
    if rxcui is None:
        return None

    properties = get_drug_properties(rxcui)
    drug_class = get_drug_class(rxcui)
    related_concepts = get_related_concepts(rxcui)

    return {
        "rxcui": rxcui,
        "properties": properties,
        "drug_class": drug_class,
        "related_concepts": related_concepts
    }
