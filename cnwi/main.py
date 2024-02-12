import os
import sys

from dataclasses import dataclass
from pprint import pprint

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
    # Samples Work
    features = Features(feature_id)
    stack = image_processing(
        datasets=dataset,
        aoi=features.dataset,
    )  # the object we want to extract features from
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
    # load extracted features from the asset store
    buldt_features = Features(samples_asset_id)
    train = buldt_features.get_training("type", 1).dataset
    test = buldt_features.get_testing("type", 2).dataset

    # need to create our model, and fit
    rf = SmileRandomForest()
    rf.fit(features=train, label_col="class_name", predictors=stack.bandNames())
    rf_model_id = f"{project_root}/{name}_rf_model"
    rf_model_task = rf.save_model(rf_model_id)
    print(f"Exporting Model: {rf_model_task.id}")

    # do assessment
    confusion_matrix = rf.assess(test)

    (
        confusion_matrix.add_accuracy()
        .add_producers()
        .add_consumers()
        .add_order()
        .mk_components_table()
        .save_table_to_drive(name=f"{name}_confusion_matrix", folder_name=f"{name}")
    )

    # save model to asset store
    # save assessment table to
    rf_task = monitor_task(rf_model_task)
    if rf_task > 1:
        print("Error: Random Forest Task Non Zero status")
        return rf_task

    # Step 3: Classify the stack

    return 0


if __name__ == "__main__":
    ee.Initialize()
    sys.exit(main(sys.argv[1:]))
