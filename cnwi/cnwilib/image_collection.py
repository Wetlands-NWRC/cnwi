from __future__ import annotations
import ee

from math import pi
from cnwi.cnwilib.calculators import Amplitude, Phase
from cnwi.cnwilib.image import LinearRegression


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

    def fourier_transform(self, coefficients: LinearRegression) -> ee.Image:
        """computes the fourier transform of the time series"""

        # add coefficients to each image in the collection
        self.collection = self.collection.map(
            lambda image: image.addBands(coefficients.get_coefficients())
        )

        for mode in range(1, self.modes + 1):
            phase = Phase(mode)
            amplitude = Amplitude(mode)
            self.collection = self.collection.map(phase.compute)
            self.collection = self.collection.map(amplitude.compute)

        selectors = f"{self.model.time_series.dependent}|.*coef|amp.*|phase.*"
        return self.collection.select(selectors).median().unitScale(-1, 1)
