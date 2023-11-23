from __future__ import annotations
import ee


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

    def add_ndvi(self, nir: str, red: str, name: str = None) -> None:
        # TODO Implement calculation
        name = name or "NDVI"
        return self

    def add_savi(self, nir: str, red: str, name: str = None) -> None:
        # TODO Implement calculation
        name = name or "SAVI"
        return self

    def add_tasseled_cap(self, **kwargs) -> None:
        # TODO Implement calculation
        name = name or "Tasseled Cap"
        return self

    def add_ratio(self, numerator: str, denominator: str, name: str = None) -> None:
        # TODO Implement calculation
        name = name or "Ratio"
        return self

    def denoise(self, filter: callable) -> None:
        # TODO Implement filter
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
