# fourier transform
# Times Series Collection
# need phase and amplitude calcs
from __future__ import annotations

import ee

from cnwi.cnwilib.image_collection import TimeSeries
from cnwi.cnwilib.image_math import LinearRegression, Phase, Amplitude


class FourierTransform:
    def __init__(self, time_series: TimeSeries, trend: LinearRegression) -> None:
        self.time_series = time_series
        self.trend = trend

    def _add_phase(self, mode: int) -> FourierTransform:
        calc = Phase(mode)
        self.time_series.collection = self.time_series.collection.map(
            lambda image: image.addBands(calc.compute(image))
        )
        return self

    def _add_amplitude(self, mode: int) -> FourierTransform:
        calc = Amplitude(mode)
        self.time_series.collection = self.time_series.collection.map(
            lambda image: image.addBands(calc.compute(image))
        )
        return self

    def compute(self) -> ee.Image:
        """compute the fourier transform of the time series using the trend from the linear regression"""
        # add coefficients to each image in the collection
        self.time_series.collection = self.time_series.collection.map(
            lambda image: image.addBands(self.trend.get_coefficients())
        )

        # add phase and amplitude to each image in the collection
        for mode in range(1, self.time_series.modes + 1):
            self._add_phase(mode)
            self._add_amplitude(mode)

        selectors = f"{self.time_series.dependent}|.*coef|amp.*|phase.*"
        return self.time_series.collection.median().select(selectors).unitScale(-1, 1)


def compute_fourier_transform(
    optical: ee.ImageCollection, dependent_variable: str, modes: int = 3
) -> ee.Image:
    """
    Compute the Fourier Transform from a time series. A time sereis object is computed from the optical data.
    :param data: the data to transform
    :param sample_rate: the sample rate of the data
    :return: the Fourier Transform of the data
    """

    # build the time series
    time_series = TimeSeries(optical, dependent=dependent_variable, modes=modes).build()
    # compute the trend from the time series
    lin_reges = LinearRegression(time_series)
    # compute the Fourier Transform of the residuals
    fourier_transform = FourierTransform(time_series, lin_reges).compute()
    return fourier_transform
