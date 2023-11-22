# fourier transform
# Times Series Collection
# need phase and amplitude calcs
import ee

from cnwi.cnwilib.image_collection import TimeSeries


def compute_fourier_transform(
    optical: ee.ImageCollection,
) -> ee.Image:
    """
    Compute the Fourier Transform of the data.
    :param data: the data to transform
    :param sample_rate: the sample rate of the data
    :return: the Fourier Transform of the data
    """

    # build the time series

    # compute the trend from the time series

    # compute the residuals from the time series

    # compute the Fourier Transform of the residuals
