import ee

"""
ee.FeatureCollection.errorMartix
prameters: actual, predicted, classOrder

Question how do i get all of that data into the confusion matrix object below?



"""


def compute_assessment_products(
    predictions: ee.FeatureCollection,
    actual: str,
    predicted: str,
    class_order: list[int] | ee.List,
) -> ee.FeatureCollection:
    """Compute the assessment products for a given model and feature collection"""
    # TODO need to process this to be feature collection that contains the confusion matrix and the accuracy metrics
    components: list[ee.Feature] = []
    matrix = predictions.errorMatrix(actual, predicted, class_order)

    overall = None
    producers = None
    consumers = None

    return ee.FeatureCollection(components)
