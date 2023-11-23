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

    def compute(self, image: ee.Image) -> ee.Image:
        coefficients = ee.Array(
            [
                [0.3029, 0.2786, 0.4733, 0.5599, 0.508, 0.1872],
                [-0.2941, -0.243, -0.5424, 0.7276, 0.0713, -0.1608],
                [0.1511, 0.1973, 0.3283, 0.3407, -0.7117, -0.4559],
                [-0.8239, 0.0849, 0.4396, -0.058, 0.2013, -0.2773],
                [-0.3294, 0.0557, 0.1056, 0.1855, -0.4349, 0.8085],
                [0.1079, -0.9023, 0.4119, 0.0575, -0.0259, 0.0252],
            ]
        )

        image = image.select(self.values)
        array_image = image.toArray()
        array_image_2d = array_image.toArray(1)

        components = (
            ee.Image(coefficients)
            .matrixMultiply(array_image_2d)
            .arrayProject([0])
            .arrayFlatten(
                [["brightness", "greenness", "wetness", "fourth", "fifth", "sixth"]]
            )
        )
        components = components.select(["brightness", "greenness", "wetness"])
        return components


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
