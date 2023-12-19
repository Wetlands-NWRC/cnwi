import ee

"""
ee.FeatureCollection.errorMartix
prameters: actual, predicted, classOrder

Question how do i get all of that data into the confusion matrix object below?

"""


class AssessmentTable:
    def __init__(
        self,
        predictions: ee.FeatureCollection,
        actual: str,
        predicted: str = None,
        class_order: list[str] | ee.List = None,
    ) -> None:
        self.actual = actual
        self.predicted = predicted or "classification"
        self.class_order = class_order
        self.matrix = predictions

    @property
    def matrix(self):
        return self._matrix

    @matrix.setter
    def matrix(self, predictions: ee.FeatureCollection) -> None:
        self._matrix = predictions.errorMatrix(
            self.actual, self.predicted, self.class_order
        )

    @property
    def producers(self) -> ee.List:
        return self.matrix.producersAccuracy()

    @property
    def consumers(self) -> ee.List:
        return self.matrix.consumersAccuracy()

    @property
    def overall(self) -> ee.Number:
        return self.matrix.accuracy()

    @property
    def kappa(self) -> ee.Number:
        return self.matrix.kappa()


# def compute_assessment_products(ee_components: AssessmentTable) -> ee.FeatureCollection:
#     """Compute the assessment products for a given model and feature collection"""
#     # TODO need to process this to be feature collection that contains the confusion matrix and the accuracy metrics
#     components: list[ee.Feature] = []
#     ##
#     cfm = ee.Feature(
#         None, {"matrix": matrix.confusion_matrix.array().slice(0, 1).slice(1, 1)}
#     )
#     components.append(cfm)
#     ##
#     overall = ee.Feature(None, {"overall": matrix.overall})
#     components.append(overall)
#     ##
#     producers = ee.Feature(
#         None, {"producers": matrix.producers.toList().flatten().slice(1)}
#     )
#     components.append(producers)
#     ##
#     consumers = ee.Feature(
#         None, {"consumers": matrix.consumers.toList().flatten().slice(1)}
#     )
#     components.append(consumers)
#     ##
#     return ee.FeatureCollection(components)
