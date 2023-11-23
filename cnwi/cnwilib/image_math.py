from __future__ import annotations
import ee


####################################################################################################
class TimeSeries:
    pass


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
            .reduce(ee.Reducer.linearRegression(len(time_series.independent), 1))
            .select("coefficients")
            .arrayFlatten([time_series.independent, ["coef"]])
        )
        return linear_regression

    def get_coefficients(self) -> ee.Image:
        return self.trend.select(".*coef")


####################################################################################################


class Phase:
    def __init__(self, mode: int) -> None:
        self.mode = mode
        self.name = mode

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = f"phase_{value}"

    @property
    def sin(self) -> str:
        return f"sin_{self.mode}_coef"

    @property
    def cos(self) -> str:
        return f"cos_{self.mode}_coef"

    def compute(self, image: ee.Image) -> ee.Image:
        cos = image.select(self.cos)
        sin = image.select(self.sin)
        return sin.atan2(cos).rename(self.name)


class Amplitude:
    def __init__(self, mode: int) -> None:
        self.mode = mode
        self.name = mode

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = f"amp_{value}"

    @property
    def sin(self) -> str:
        return f"sin_{self.mode}_coef"

    @property
    def cos(self) -> str:
        return f"cos_{self.mode}_coef"

    def compute(self, image: ee.Image) -> ee.Image:
        return image.select(self.cos).hypot(image.select(self.sin)).rename(self.name)


####################################################################################################
