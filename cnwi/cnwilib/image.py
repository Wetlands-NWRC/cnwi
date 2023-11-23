from __future__ import annotations
import ee


class NDVICalculator:
    pass


class SAVICalculator:
    pass


class RatioCalculator:
    pass


class TasseledCapCalculator:
    pass


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

    @property
    def image(self) -> ee.Image:
        return self._image

    @image.setter
    def image(self, image: ee.Image) -> None:
        if not isinstance(image, ee.Image):
            raise TypeError("image must be ee.Image")
        self._image = image

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
