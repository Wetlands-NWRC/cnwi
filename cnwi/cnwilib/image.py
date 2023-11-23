from __future__ import annotations
from abc import ABC, abstractmethod

import ee


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


class ImageStack:
    def __init__(self) -> None:
        self._image = []

    def __len__(self) -> int:
        return len(self._image)

    def add(self, image: ee.Image) -> None:
        self._image.append(image)
        return self

    def stack(self) -> ee.Image:
        return ee.Image.cat(*self._image)


class ImageBuilder:
    def __init__(self) -> None:
        self.image = None

    def add_ndvi(self, calculator: NDVICalculator) -> ImageBuilder:
        if not isinstance(calculator, NDVICalculator):
            raise TypeError("calculator must be NDVICalculator")
        self.image = self.image.addBands(calculator.compute(self.image))
        return self

    def add_savi(self, calculator: SAVICalculator) -> ImageBuilder:
        if not isinstance(calculator, SAVICalculator):
            raise TypeError("calculator must be SAVICalculator")
        self.image = self.image.addBands(calculator.compute(self.image))
        return self

    def add_tasseled_cap(self, calculator: TasseledCapCalculator) -> ImageBuilder:
        if not isinstance(calculator, TasseledCapCalculator):
            raise TypeError("calculator must be TasseledCapCalculator")
        self.image = self.image.addBands(calculator.compute(self.image))
        return self

    def add_ratio(self, calculator: RatioCalculator) -> ImageBuilder:
        if not isinstance(calculator, RatioCalculator):
            raise TypeError("calculator must be RatioCalculator")
        self.image = self.image.addBands(calculator.compute(self.image))
        return self

    def add_box_car(self, radius: int = 1) -> ImageBuilder:
        self.image = self.image.convolve(ee.Kernel.square(radius, "pixels"))
        return self

    def build(self) -> ImageBuilder:
        return self


class ImageDirector:
    def __init__(self, builder: ImageBuilder) -> None:
        self._builder = builder

    @property
    def builder(self) -> ImageBuilder:
        return self._builder

    @builder.setter
    def builder(self, builder: ImageBuilder) -> None:
        if not isinstance(builder, ImageBuilder):
            raise TypeError("builder must be ImageBuilder")
        self._builder = builder

    def build_data_cube(self, datacube: ee.ImageCollection) -> ImageBuilder:
        # TODO Implement datacube
        return self._builder

    def build_land_sat_8(self, datacube: ee.ImageCollection) -> ImageBuilder:
        # TODO Implement datacube
        return self._builder

    def build_sentinel_1(self, datacube: ee.ImageCollection) -> ImageBuilder:
        # TODO Implement datacube
        return self._builder

    def build_alos(self, datacube: ee.ImageCollection) -> ImageBuilder:
        # TODO Implement datacube
        return self._builder
