# fourier transform
# Times Series Collection
# need phase and amplitude calcs
import ee

from cnwi.cnwilib.image_collection import TimeSeries
from cnwi.cnwilib.image_math import LinearRegression


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
    fourier_transform = time_series.fourier_transform(lin_reges)
    return fourier_transform
