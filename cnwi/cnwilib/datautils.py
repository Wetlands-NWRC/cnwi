import pandas as pd
import ee


def ee_features_manifest(root: str) -> pd.DataFrame:
    sever_assets = ee.data.listAssets({"parent": root})
    server_df = pd.DataFrame(sever_assets["assets"])

    # split name into root and asset_name
    server_df["root"] = server_df["name"].apply(lambda x: x.split("/")[-2])
    server_df["asset_name"] = server_df["name"].apply(lambda x: x.split("/")[-1])
    server_df["data_type"] = server_df["asset_name"].apply(lambda x: x.split("_")[0])
    server_df["region_id"] = server_df["asset_name"].apply(lambda x: x.split("_")[1])

    return server_df
