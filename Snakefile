import alcohol
import geopandas as gpd

chains = [
    "APPLEBEE",
    "OUTBACK",
    "BUFFALO WILD WINGS",
    "CHEESECAKE FACTORY",
    "TEXAS ROADHOUSE",
    "RED ROBIN",
]


rule all:
    input:
        "data/distance_matrix.feather",


rule download_data:
    output:
        "data/raw.feather",
    run:
        alcohol.txdata.download_data(output[0], chains)


rule geocode_data:
    input:
        "data/raw.feather",
    output:
        "data/geocoded.geojson",
    run:
        alcohol.gis.geocode_data(input[0], output[0])


rule distance_matrix:
    input:
        "data/geocoded.geojson",
    output:
        "data/distance_matrix.feather",
    run:
        gdf = gpd.read_file(input[0])
        mat = alcohol.gis.build_distance_matrix(gdf)
        mat.to_feather(output[0])
