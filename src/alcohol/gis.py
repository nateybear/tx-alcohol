import os
from itertools import combinations

import folium
import geopandas as gpd
import numpy as np
import osrm
import pandas as pd
from haversine import Unit, haversine
from matplotlib import cm


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
    geom = gdf.geometry.unique()
    coords = [(p.x, p.y) for p in geom]
    coords.sort()
    out = np.zeros((len(geom), len(geom)))
    for (i, (x1, y1)), (j, (x2, y2)) in combinations(enumerate(coords), 2):
        out[i, j] = out[j, i] = haversine((y1, x1), (y2, x2), unit=Unit.MILES)

    return pd.DataFrame(out)


def build_duration_matrix(gdf, osrm_file):
    geom = gdf.geometry.unique()
    coords = [(p.x, p.y) for p in geom]
    coords.sort()
    o = osrm.OSRM(osrm_file)
    durations = (
        np.array(o.Table(osrm.TableParameters(coordinates=coords))["durations"]) / 60
    )

    return pd.DataFrame(durations)


def build_sales_data(gdf):
    gdf["sales"] = gdf.total_sales_receipts.astype(np.float64)
    gdf["pt"] = [(p.x, p.y) for p in gdf.geometry]
    out = gdf.groupby("geometry", as_index=False).agg(
        {"sales": "mean", "pt": "first", "location_name": "first"}
    )
    out.sort_values("pt", inplace=True)
    return gpd.GeoDataFrame(
        out[["location_name", "sales", "geometry"]].reset_index(drop=True),
    )


def make_map(gdf, clustering):
    map_center = gdf.geometry.union_all().centroid
    gdf["label"] = clustering.labels_.astype(str)
    gdf["cluster_size"] = gdf.groupby("label")["label"].transform("count")
    plot_df = gdf[gdf["cluster_size"] > 1]
    plot_df["share"] = (
        100 * plot_df.groupby("label")["sales"].transform(lambda x: x / x.sum())
    ).round(2)
    plot_df["hhi"] = (
        plot_df.groupby("label")["share"].transform(lambda x: (x**2).sum()).astype(int)
    )
    m = folium.Map(location=[map_center.y, map_center.x], zoom_start=6)
    folium.TileLayer(
        tiles=f"https://tiles.stadiamaps.com/tiles/stamen_toner/{{z}}/{{x}}/{{y}}{{r}}.png?api_key={os.environ.get('STADIA_API_KEY')}",
        attr="&copy; Stadia Maps, &copy; OpenMapTiles, &copy; OpenStreetMap contributors",
        name="Stadia",
        max_zoom=20,
    ).add_to(m)
    min_sales = plot_df.sales.min()
    max_sales = plot_df.sales.max()
    n_clusters = len(set(clustering.labels_))
    for _, row in plot_df.iterrows():
        label = int(row["label"])
        color = cm.hsv(label / n_clusters)
        radius = 5 + 15 * (row["sales"] - min_sales) / (max_sales - min_sales)
        folium.CircleMarker(
            location=[row.geometry.y, row.geometry.x],
            radius=radius,
            fill_color=f"rgba({int(color[0]) * 255}, {int(color[1] * 255)}, {int(color[2] * 255)}, {color[3]})",
            color="black",
            fill=True,
            fill_opacity=0.8,
            weight=1,
            tooltip=f"{row.location_name}<br>Avg Sales: ${row.sales:.2f}<br>Share: {row['share']}%<br>HHI: {row['hhi']}",
        ).add_to(m)

    return m
