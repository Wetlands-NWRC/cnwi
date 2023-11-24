from __future__ import annotations
from abc import ABC, abstractmethod

import ee


####################################################################################################
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


####################################################################################################


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


####################################################################################################


class ImageBuilder:
    def __init__(self) -> None:
        self.image = None

    # TODO need to refactor this to have only one add_calculation method lot of duplication
    def add_calculator(self, calculator: Calculator) -> ImageBuilder:
        if not issubclass(calculator, Calculator):
            raise TypeError("calculator must be Calculator Object")
        self.image = self.image.addBands(calculator.compute(self.image))
        return self

    def add_box_car(self, radius: int = 1) -> ImageBuilder:
        self.image = self.image.convolve(ee.Kernel.square(radius, "pixels"))
        return self

    def select_dv(self) -> ImageBuilder:
        """selects dual pol bands VV and VH"""
        self.image = self.image.select("V.*")
        return self

    def select_dh(self) -> ImageBuilder:
        """selects dual pol bands HH and HV"""
        self.image = self.image.select("H.*")
        return self

    def select_data_cube_bands(self) -> ImageBuilder:
        # TODO Implement
        """selects only the spectral bands from the data cube, and removes the rest b1 is omitted"""
        pattern = "a_spri_b0[2-9].*|a_spri_b[1-2].*|b_summ_b0[2-9].*|b_summ_b[1-2].*|c_fall_b0[2-9].*|c_fall_b[1-2].*"
        self.image = self.image.select(pattern)
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

    def build_data_cube(self, image: ee.Image) -> ImageBuilder:
        # TODO Implement datacube
        # set the image to build
        self.builder.image = image

        # set up calculators

        # add ndvi
        # TODO update to use data cube band names
        spring_ndvi = NDVICalculator("a_spri_b08_10m", "a_spri_b04_10m", "NDVI")
        summer_ndvi = NDVICalculator("b_summ_b08_10m", "b_summ_b04_10m", "NDVI")
        fall_ndvi = NDVICalculator("c_fall_b08_10m", "c_fall_b04_10m", "NDVI")

        # add savis
        spring_savi = SAVICalculator("a_spri_b08_10m", "a_spri_b04_10m", "SAVI")
        summer_savi = SAVICalculator("b_summ_b08_10m", "b_summ_b04_10m", "SAVI")
        fall_savi = SAVICalculator("c_fall_b08_10m", "c_fall_b04_10m", "SAVI")

        # add tassled cap
        spring_tassled_cap = TasseledCapCalculator(
            blue="a_spri_b02_10m",
            green="a_spri_b03_10m",
            red="a_spri_b04_10m",
            nir="a_spri_b08_10m",
            swir1="a_spri_b11_10m",
            swir2="a_spri_b12_10m",
        )

        summer_tassled_cap = TasseledCapCalculator(
            blue="b_summ_b02_10m",
            green="b_summ_b03_10m",
            red="b_summ_b04_10m",
            nir="b_summ_b08_10m",
            swir1="b_summ_b11_10m",
            swir2="b_summ_b12_10m",
        )

        fall_tassled_cap = TasseledCapCalculator(
            blue="c_fall_b02_10m",
            green="c_fall_b03_10m",
            red="c_fall_b04_10m",
            nir="c_fall_b08_10m",
            swir1="c_fall_b11_10m",
            swir2="c_fall_b12_10m",
        )

        # start the build process
        self.builder = (
            self.builder.add_calculator(spring_ndvi)
            .add_calculator(summer_ndvi)
            .add_calculator(fall_ndvi)
            .add_calculator(spring_savi)
            .add_calculator(summer_savi)
            .add_calculator(fall_savi)
            .add_calculator(spring_tassled_cap)
            .add_calculator(summer_tassled_cap)
            .add_calculator(fall_tassled_cap)
            .select_data_cube_bands()
            .build()
        )
        return self._builder

    def build_land_sat_8(self, image: ee.Image) -> ImageBuilder:
        # TODO Implement datacube
        raise NotImplementedError

    def build_sentinel_1(self, image: ee.Image) -> ImageBuilder:
        # set the build image
        self.builder.image = image

        # set up calcs
        ratio = RatioCalculator("VV", "VH", "VV/VH")
        # raito

        # start the build process
        self.builder = self.builder.add_box_car().add_calculator(ratio).select_dv()
        return self._builder

    def build_alos(self, image: ee.Image) -> ImageBuilder:
        # set the build image
        self.builder.image = image
        # set up calcs
        ratio = RatioCalculator("HH", "HV", "HH/HV")
        # raito

        # start the build process
        self.builder = self.builder.add_box_car().add_calculator(ratio).select_dh()

        return self._builder


####################################################################################################
