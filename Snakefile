from alcohol import gis, txdata
import geopandas as gpd
import pandas as pd
import numpy as np
import sklearn.cluster as clstr

chains = [
    "APPLEBEE",
    "OUTBACK",
    "BUFFALO WILD WINGS",
    "CHEESECAKE FACTORY",
    "TEXAS ROADHOUSE",
    "RED ROBIN",
]

clusterings = {
    "meanshift": clstr.MeanShift(bandwidth=100),
    "hdbscan": clstr.HDBSCAN(min_cluster_size=2, min_samples=1),
}


rule all:
    input:
        "data/distance_matrix.feather",
        "data/duration_matrix.feather",
        expand("plots/maps/{clustering}.html", clustering=clusterings.keys()),


rule download_data:
    output:
        "data/raw.feather",
    run:
        txdata.download_data(output[0], chains)


rule geocode_data:
    input:
        "data/raw.feather",
    output:
        "data/geocoded.geojson",
    run:
        gis.geocode_data(input[0], output[0])


rule distance_matrix:
    input:
        "data/geocoded.geojson",
    output:
        "data/distance_matrix.feather",
    run:
        gdf = gpd.read_file(input[0])
        mat = gis.build_distance_matrix(gdf)
        mat.to_feather(output[0])

rule duration_matrix:
    input:
        "data/geocoded.geojson",
    output:
        "data/duration_matrix.feather",
    run:
        gdf = gpd.read_file(input[0])
        mat = gis.build_duration_matrix(gdf, "data/texas.osrm")
        mat.to_feather(output[0])

rule cluster_map:
    input:
        "data/geocoded.geojson",
        "data/duration_matrix.feather",
    output:
        "plots/maps/{clustering}.html",
    params:
        clustering=lambda wildcards: clusterings[wildcards.clustering],
    run:
        gdf = gpd.read_file(input[0])
        mat = pd.read_feather(input[1])
        m = gis.make_map(gis.build_sales_data(gdf), params.clustering.fit(mat))
        m.save(output[0])
