import ee

from cnwi.cnwilib.image_collection import TimeSeries


class LinearRegression:
    def __init__(self, time_series: TimeSeries) -> None:
        self.trend = time_series

    @property
    def trend(self) -> ee.Image:
        return self._trend

    @trend.setter
    def trend(self, time_series: TimeSeries) -> None:
        self._trend = self._compute_linear_regression(time_series)

    @staticmethod
    def _compute_linear_regression(time_series: TimeSeries) -> ee.Image:
        """helper function to compute the linear regression"""
        # build the linear regression
        linear_regression = (
            time_series.collection.select(
                time_series.independent + [time_series.dependent]
            )
            .reduce(ee.Reducer.linearRegression(time_series.independent.length, 1))
            .select("coefficients")
            .arrayProject([0])
            .arrayFlatten([time_series.time_series.independent, ["coef"]])
        )
        return linear_regression

    def get_coefficients(self) -> ee.Image:
        return self.trend.select("coef")
