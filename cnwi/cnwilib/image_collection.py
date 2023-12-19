from __future__ import annotations
import ee
from typing import Any

from math import pi

from cnwi.cnwilib.image import NDVI, SAVI, TasseledCap, Ratio


class TimeSeries:
    def __init__(
        self, collection: ee.ImageCollection, dependent: str, modes: int = 3
    ) -> None:
        self.collection = collection
        self.dependent = dependent
        self.independent = []
        self.modes = modes

    def __add_independent(self, independent: str | list[str]) -> None:
        if isinstance(independent, str) and independent not in self.independent:
            self.independent.append(independent)
        elif isinstance(independent, list) and all(
            isinstance(i, str) for i in independent
        ):
            self.independent.extend(independent)
        else:
            raise TypeError(
                "Independent variable must be a string or a list of strings."
            )

    def _mk_freq_name(self, name: str) -> list[str]:
        return [f"{name}_{i}" for i in range(1, self.modes + 1)]

    def _add_constant(self) -> TimeSeries:
        def _add_const_inner(image):
            return image.addBands(ee.Image(1))

        self.__add_independent("constant")
        self.collection = self.collection.map(_add_const_inner)
        return self

    def _add_time(self) -> TimeSeries:
        def _add_time_inner(image):
            date = image.date()
            years = date.difference(ee.Date("1970-01-01"), "year")
            time_radians = ee.Image(years.multiply(2 * pi))
            return image.addBands(time_radians.rename("t").float())

        self.__add_independent("t")
        self.collection = self.collection.map(_add_time_inner)
        return self

    def _add_harmonics(self) -> TimeSeries:
        cos = self._mk_freq_name("cos")
        sin = self._mk_freq_name("sin")

        def _add_harmonics_inner(image):
            frequencies = ee.Image.constant(list(range(1, self.modes + 1)))
            time = ee.Image(image).select("t")
            cos_img = time.multiply(frequencies).cos().rename(cos)
            sin_img = time.multiply(frequencies).sin().rename(sin)
            return image.addBands(cos_img).addBands(sin_img)

        self.__add_independent(cos)
        self.__add_independent(sin)
        self.collection = self.collection.map(_add_harmonics_inner)
        return self

    def build(self) -> TimeSeries:
        # TODO add property to set if build has been run
        self._add_constant()
        self._add_time()
        self._add_harmonics()
        return self


###############################################################################################
class OpticalPreProcessor:
    def __init__(self, args: Any) -> None:
        self.data = ee.ImageCollection(args)

    def set_date(self, start: str, end: str) -> OpticalCollectionProcessor:
        self.data = self.data.filterDate(start, end)
        return self

    def set_region(
        self, region: ee.Geometry | ee.Feature | ee.FeatureCollection
    ) -> OpticalCollectionProcessor:
        self.data = self.data.filterBounds(region)
        return self

    def select_bands(self, selector: Any) -> OpticalCollectionProcessor:
        self.data = self.data.select(selectors=selector)
        return self

    def set_band_names(self, names: list[str]) -> OpticalCollectionProcessor:
        self.data = self.data.select(self.data.first().bandNames(), names)
        return self

    def add_cloud_mask(self, func: Any) -> OpticalCollectionProcessor:
        self.data = self.data.map(func)
        return self

    def filter_cloud_cover(
        self, meta_flag: str, max: float
    ) -> OpticalCollectionProcessor:
        self.data = self.data.filter(ee.Filter.lt(meta_flag, max))
        return self

    def build(self) -> ee.ImageCollection:
        return self.data


# Collection Processing
class OpticalCollectionProcessor:
    def __init__(self, arg: Any) -> None:
        self.data = ee.ImageCollection(arg)

    @property
    def data(self) -> ee.ImageCollection:
        return self._data

    @data.setter
    def data(self, args: Any) -> None:
        if isinstance(args, ee.ImageCollection):
            self._data = args
        else:
            self._data = ee.ImageCollection(args)

    def add_ndvi(
        self, nir: str, red: str, name: str = "NDVI"
    ) -> OpticalCollectionProcessor:
        """Implement NDVI calculation for optical data."""
        self.data = self.data.map(NDVI(nir, red, name))
        return self

    def add_tasseled_cap(self, **kwargs) -> OpticalCollectionProcessor:
        bands = ["blue", "green", "red", "nir", "swir1", "swir2"]
        if not all(b in kwargs for b in bands):
            raise ValueError(
                f"Missing one or more bands. Required bands: {', '.join(bands)}"
            )
        self.data = self.data.map(TasseledCap(**kwargs))
        return self

    def add_savi(
        self, nir: str, red: str, name: str = "SAVI", L: float = 0.5
    ) -> OpticalCollectionProcessor:
        self.data = self.data.map(SAVI(nir, red, name))
        return self

    def build(self) -> ee.ImageCollection:
        return self.data


class SARCollectionProcessor:
    def __init__(self, args) -> None:  # collection id or list of images
        self.data = ee.ImageCollection(args)

    def set_date(self, start: str, end: str) -> SARCollectionProcessor:
        self.data = self.data.filterDate(start, end)
        return self

    def set_region(
        self, region: ee.Geometry | ee.Feature | ee.FeatureCollection
    ) -> SARCollectionProcessor:
        self.data = self.data.filterBounds(region)
        return self

    def select_bands(self, var_args: Any) -> SARCollectionProcessor:
        self.data = self.data.select(var_args)
        return self

    def denoise(self, radius: int = 1) -> SARCollectionProcessor:
        self.data = self.data.map(
            lambda image: image.convolve(ee.Kernel.square(radius))
        )
        return self

    def add_ratio(self, num: str, den: str, name: str) -> SARCollectionProcessor:
        self.data = self.data.map(Ratio(num, den, name))
        return self

    def build(self) -> ee.ImageCollection:
        return self.data


###############################################################################################
