import os
import sys

import ee

from .features import Features
from .helpers import image_processing, monitor_task
from .modeling import SmileRandomForest


def main(args: list[str]) -> int:
    # needs to args a 2 asset ids, one that represents features and one the aoi
    if len(args) != 1:
        print("<Usage>: main.py <payload.json>")
        return 1

    feature_id, region_id = args

    features = Features(feature_id)
    stack = image_processing()

    samples = features.extract(stack)
    samples_task = samples.save_to_asset()

    samples_status = monitor_task(samples_task)
    if samples_status > 1:
        return samples_status

    # model and assess
    features = Features()
    train = features.get_training()
    test = features.get_testing()

    rfm = SmileRandomForest()
    rfm.fit(features=train, predictors=[])
    metrics = rfm.assess(test)

    metrics.add_accuracy().add_consumers().add_producers().add_order().save_table_to_drive()

    # save model export asseessment to drive
    rfm.save_model()
    # classify and export to drive for now

    classify = image_processing(aoi=aoi)
    rfm.load_model()
    img = rfm.predict(classify)

    ## export to drive

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
