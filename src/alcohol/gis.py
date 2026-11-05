import os
from itertools import combinations

import geopandas as gpd
import numpy as np
import pandas as pd
from haversine import Unit, haversine


def geocode_data(infile, outfile):
    df = pd.read_feather(infile)
    df["location_full_address"] = df[
        ["location_address", "location_city", "location_zip"]
    ].apply(lambda x: f"{x.iloc[0]}, {x.iloc[1]}, TX {x.iloc[2]}", axis=1)
    unique_addresses = df["location_full_address"].unique()
    geometry = gpd.tools.geocode(
        unique_addresses,
        provider="google",
        api_key=os.environ.get("GOOGLE_API_KEY"),
        timeout=60,
    )
    geometry["location_full_address"] = unique_addresses
    gdf = df.merge(geometry, on="location_full_address", how="left")
    gdf = gpd.GeoDataFrame(gdf, geometry="geometry", crs=geometry.crs)
    gdf.to_file(outfile, driver="GeoJSON")


def build_distance_matrix(gdf):
    to_tuple = lambda p: (p.y, p.x)
    geom = gdf.geometry.unique()
    out = np.zeros((len(geom), len(geom)))
    for (i, p1), (j, p2) in combinations(enumerate(geom), 2):
        out[i, j] = out[j, i] = haversine(to_tuple(p1), to_tuple(p2), unit=Unit.MILES)

    return pd.DataFrame(out, index=geom, columns=geom)
