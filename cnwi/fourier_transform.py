# fourier transform
# Times Series Collection
# need phase and amplitude calcs
import ee


class FourierTransform:
    def __init__(self, time_series: TimeSereis) -> None:
        self.time_series = time_series

    @property
    def coefficients(self) -> ee.Image:
        """
        Compute the Fourier coefficients for the time series.
        :return: the Fourier coefficients for the time series
        """
        pass


def compute_fourier_transform(data, sample_rate) -> ee.Image:
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
