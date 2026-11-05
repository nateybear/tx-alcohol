import pandas as pd
import sodapy as sp

CLIENT = sp.Socrata("data.texas.gov", None)
DATASET_ID = "g5bj-yb6k"

PRIMARY_KEY = ["taxpayer_number", "location_address", "obligation_end_date"]


def download_data(where, chains):
    where_query = " OR ".join(f"(location_name LIKE '%{chain}%')" for chain in chains)
    result = pd.DataFrame(CLIENT.get_all(DATASET_ID, where=where_query))
    result = result.drop_duplicates(PRIMARY_KEY)
    result.sort_values(PRIMARY_KEY, inplace=True)
    result.reset_index(drop=True, inplace=True)
    for c in result.columns:
        if c.endswith("_date"):
            result[c] = pd.to_datetime(result[c])
    result.to_feather(where)
