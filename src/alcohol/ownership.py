import os

import requests


def open_corporates_lookup(name, active=True):
    api_token = os.environ.get("OPENCORPORATES_API_TOKEN", None)
    resp = requests.get(
        "https://api.opencorporates.com/companies/search",
        params={
            "q": name,
            "api_token": api_token,
            "jurisdiction_code": "us_tx",
            "order": "score",
            "normalise_company_name": "true",
            **({"inactive": "false"} if active else {}),
        },
    )
    results = resp.json()["results"]["companies"]
    if not results:
        raise ValueError(f"No results found for '{name}' in Texas.")

    company_id = results[0]["company"]["company_number"]
    if company_id is None:
        print(f"Warning: No company ID found for '{name}'. Assuming it's a person.")
        return None  # or handle as needed

    return results[0]
