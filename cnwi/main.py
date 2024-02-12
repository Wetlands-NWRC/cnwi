import os
import sys

from dataclasses import dataclass

import ee

from .features import Features
from .helpers import image_processing, monitor_task
from .modeling import SmileRandomForest


@dataclass
class Datasets:
    s1: list[str] | None
    dc: str | None
    ft: str | None
    ta: str | None


def split_id(id: str) -> tuple[str, str]:
    splt = id.split("/")
    return "/".join(splt[:-1]), splt[-1]


def load_payload(filename: str) -> Datasets | int:
    import json

    with open(filename, "r") as d:
        data = json.load(d)

    return Datasets(data.get("s1"), data.get("dc"), data.get("ft"), data.get("ta"))


def main(args: list[str]) -> int:
    # needs to args a 2 asset ids, one that represents features and one the aoi
    if len(args) != 3:
        print("<Usage>: main.py <features_id> <regions_id> <payload.json>")
        return 1

    feature_id, region_id, payload = args
    dataset = load_payload(payload)

    # use the feature id b/c we are everything i.e. samples, model, assesment and classification
    # step from these input features. standard naming convention
    project_root, name = split_id(feature_id)

    # Step 1: Extract the features we want to model
    features = Features(feature_id)
    stack = image_processing(
        datasets=dataset,
        aoi=features.dataset,
    )  # the object we want to extract features from
    print("Extracting Features...")
    samples = features.extract(stack)
    # save the extracted features to asset store
    samples_asset_id = f"{project_root}/{name}_samples"
    samples_task = samples.save_to_asset(samples_asset_id)

    print(f"Exporting Features: {samples_task.id}")
    samples_status = monitor_task(samples_task)
    if samples_status > 1:
        print("Error: Samples Task Non Zero status")
        return samples_status

    # step 2: Model and asses the model
    print("Computing Random Forest Model...")
    # load extracted features from the asset store
    buldt_features = Features(samples_asset_id)
    train = buldt_features.get_training("type", 1).dataset
    test = buldt_features.get_testing("type", 2).dataset
    # need to create our model, and fit
    rf = SmileRandomForest()
    rf.fit(features=train, label_col="class_name", predictors=stack.bandNames())
    # do assessment
    confusion_matrix = rf.assess(test)
    # save model to asset store
    rf_model_id = f"{project_root}/{name}_rf_model"
    rf_model_task = rf.save_model(rf_model_id)
    # save assessment table to
    print("Saving Random Forest Model...")
    rf_task = monitor_task(rf_model_task)
    if rf_task > 1:
        print("Error: Random Forest Task Non Zero status")
        return rf_task

    # step 3: Classify and export
    print("Classifying...")
    server_aoi = ee.FeatureCollection(region_id).geometry()
    classify_stack = image_processing(aoi=server_aoi, datasets=dataset)
    rfm = rf.load_model(classify_stack)
    cls_img = rfm.predict(classify_stack)

    print("Exporting Classified Image...")
    classified_image_task = ee.batch.Export.image.toDrive(
        image=cls_img,
        description="",
        folder=f"{name}_classified",
        fileNamePrefix=f"{name}-",
        region=server_aoi,
        crs="EPSG:4326",
        maxPixels=1e13,
        fileDimensions=[2048, 2048],
        fileFormat="GeoTIFF",
        formatOptions={"cloudOptimized": True},
    )
    classified_image_task.start()

    # print("")

    return 0


if __name__ == "__main__":
    ee.Initialize()
    sys.exit(main(sys.argv[1:]))
