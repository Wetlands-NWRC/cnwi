# fourier transform
# Times Series Collection
# need phase and amplitude calcs
import ee

from cnwi.cnwilib.image_collection import TimeSeries


def compute_fourier_transform(
    optical: ee.ImageCollection, dependent_variable: str, modes: int = 3
) -> ee.Image:
    """
    Compute the Fourier Transform of the data.
    :param data: the data to transform
    :param sample_rate: the sample rate of the data
    :return: the Fourier Transform of the data
    """

    # build the time series
    time_series = TimeSeries(optical, dependent=dependent_variable, modes=modes).build()
    # compute the trend from the time series
    lin_reges = time_series.linear_regression()
    # compute the residuals from the time series
    residuals = time_series.residuals(trend)
    # compute the Fourier Transform of the residuals
    fourier_transform = residuals.fourier_transform()
