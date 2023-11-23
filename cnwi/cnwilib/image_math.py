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
from abc import ABC, abstractmethod


class Calculator(ABC):
    @abstractmethod
    def compute(self, image: ee.Image) -> ee.Image:
        pass


class NDVICalculator(Calculator):
    def __init__(self, nir: str, red: str, name: str = None) -> None:
        self.nir = nir
        self.red = red
        self.name = name or "NDVI"

    def compute(self, image: ee.Image) -> ee.Image:
        return image.normalizedDifference([self.nir, self.red]).rename(self.name)


class SAVICalculator(Calculator):
    def __init__(self, nir: str, red: str, name: str = None) -> None:
        self.nir = nir
        self.red = red
        self.name = name or "SAVI"

    def compute(self, image: ee.Image) -> ee.Image:
        return image.expression(
            "((NIR - RED) / (NIR + RED + 0.5)) * (1.5)",
            {"NIR": image.select(self.nir), "RED": image.select(self.red)},
        ).rename(self.name)


class TasseledCapCalculator(Calculator):
    def __init__(self, **kwargs) -> None:
        self.keys = list(kwargs.keys())
        self.values = list(kwargs.values())

    # TODO validate band names if len != 5 rasie ValueError

    # TODO validate kwargs keys need to be blue green red nir swir swir2

    # TODO Implement calculation


class RatioCalculator(Calculator):
    def __init__(self, numerator: str, denominator: str, name: str = None) -> None:
        self.numerator = numerator
        self.denominator = denominator
        self.name = name or "Ratio"

    def compute(self, image: ee.Image) -> ee.Image:
        return image.expression(
            "(NUM / DEN)",
            {
                "NUM": image.select(self.numerator),
                "DEN": image.select(self.denominator),
            },
        ).rename(self.name)
