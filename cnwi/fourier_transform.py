from __future__ import annotations
from math import pi
import ee


class TimeSeries:
    """
    A class representing a time series analysis on an image collection.

    Parameters:
    - collection (ee.ImageCollection): The image collection to perform the analysis on.
    - dependent (str): The dependent variable.
    - modes (int, optional): The number of harmonic modes to include. Defaults to 3.
    """

    def __init__(
        self, collection: ee.ImageCollection, dependent: str, modes: int = 3
    ) -> None:
        self.collection = collection
        self.dependent = dependent
        self.independent = []
        self.modes = modes

    def __add_independent(self, independent: str | list[str]) -> None:
        """
        Add an independent variable to the time series analysis.

        Parameters:
        - independent (str or list[str]): The independent variable(s) to add.

        Raises:
        - TypeError: If the independent variable is not a string or a list of strings.
        """
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
        """
        Generate a list of frequency names.

        Parameters:
        - name (str): The base name for the frequencies.

        Returns:
        - list[str]: The list of frequency names.
        """
        return [f"{name}_{i}" for i in range(1, self.modes + 1)]

    def add_constant(self) -> TimeSeries:
        """
        Add a constant independent variable to the time series analysis.

        Returns:
        - TimeSeries: The updated TimeSeries object.
        """

        def _add_const_inner(image):
            return image.addBands(ee.Image(1))

        self.__add_independent("constant")
        self.collection = self.collection.map(_add_const_inner)
        return self

    def add_time(self) -> TimeSeries:
        """
        Add a time independent variable to the time series analysis.

        Returns:
        - TimeSeries: The updated TimeSeries object.
        """

        def add_time_inner(image):
            date = image.date()
            years = date.difference(ee.Date("1970-01-01"), "year")
            time_radians = ee.Image(years.multiply(2 * pi))
            return image.addBands(time_radians.rename("t").float())

        self.__add_independent("t")
        self.collection = self.collection.map(add_time_inner)
        return self

    def add_harmonics(self) -> TimeSeries:
        """
        Add harmonic independent variables to the time series analysis.

        Returns:
        - TimeSeries: The updated TimeSeries object.
        """
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

    def create(self) -> TimeSeries:
        """
        Create the time series analysis by adding all independent variables.

        Returns:
        - TimeSeries: The updated TimeSeries object.
        """
        self.add_constant()
        self.add_time()
        self.add_harmonics()
        return self


class LinearRegression:
    """
    Class representing a linear regression model for time series analysis.
    """

    def __init__(self, time_series: TimeSeries) -> None:
        self.trend = time_series

    @property
    def trend(self) -> ee.Image:
        return self._trend

    @trend.setter
    def trend(self, time_series: TimeSeries) -> None:
        self._trend = self._compute_linear_regression(time_series)

    @staticmethod
    def _compute_linear_regression(time_series: TimeSeries) -> ee.Image:
        """Helper function to compute the linear regression.

        Args:
            time_series (TimeSeries): The input time series data.

        Returns:
            ee.Image: The computed linear regression coefficients.
        """
        # build the linear regression
        linear_regression = (
            time_series.collection.select(
                time_series.independent + [time_series.dependent]
            )
            .reduce(ee.Reducer.linearRegression(len(time_series.independent), 1))
            .select("coefficients")
            .arrayFlatten([time_series.independent, ["coef"]])
        )
        return linear_regression

    def get_coefficients(self) -> ee.Image:
        """Get the coefficients of the linear regression model.

        Returns:
            ee.Image: The coefficients of the linear regression model.
        """
        return self.trend.select(".*coef")


class Phase:
    def __init__(self, mode: int) -> None:
        self.mode = mode
        self.name = mode

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = f"phase_{value}"

    @property
    def sin(self) -> str:
        return f"sin_{self.mode}_coef"

    @property
    def cos(self) -> str:
        return f"cos_{self.mode}_coef"

    def compute(self, image: ee.Image) -> ee.Image:
        cos = image.select(self.cos)
        sin = image.select(self.sin)
        return sin.atan2(cos).rename(self.name)


class Amplitude:
    def __init__(self, mode: int) -> None:
        self.mode = mode
        self.name = mode

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, value: str) -> None:
        self._name = f"amp_{value}"

    @property
    def sin(self) -> str:
        return f"sin_{self.mode}_coef"

    @property
    def cos(self) -> str:
        return f"cos_{self.mode}_coef"

    def compute(self, image: ee.Image) -> ee.Image:
        return image.select(self.cos).hypot(image.select(self.sin)).rename(self.name)


class FourierTransform:
    """
    Represents a Fourier Transform of a time series using the trend from linear regression.
    """

    def __init__(self, time_series: TimeSeries, trend: LinearRegression) -> None:
        self.time_series = time_series
        self.trend = trend

    def add_phase(self, mode: int) -> FourierTransform:
        """
        Adds the phase component to the Fourier Transform for a given mode.

        Args:
            mode (int): The mode of the Fourier Transform.

        Returns:
            FourierTransform: The FourierTransform instance with the phase component added.
        """
        calc = Phase(mode)
        self.time_series.collection = self.time_series.collection.map(
            lambda image: image.addBands(calc.compute(image))
        )
        return self

    def add_amplitude(self, mode: int) -> FourierTransform:
        """
        Adds the amplitude component to the Fourier Transform for a given mode.

        Args:
            mode (int): The mode of the Fourier Transform.

        Returns:
            FourierTransform: The FourierTransform instance with the amplitude component added.
        """
        calc = Amplitude(mode)
        self.time_series.collection = self.time_series.collection.map(
            lambda image: image.addBands(calc.compute(image))
        )
        return self

    def compute(self) -> ee.Image:
        """
        Computes the Fourier Transform of the time series using the trend from the linear regression.

        Returns:
            ee.Image: The computed Fourier Transform image.
        """
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


## helper function for computation of Fourier Transform
def compute_fourier_transform(
    optical: ee.ImageCollection, dependent_variable: str, modes: int = 3
) -> ee.Image:
    """
    Compute the Fourier Transform of the given optical image collection.

    Args:
        optical (ee.ImageCollection): The optical image collection.
        dependent_variable (str): The dependent variable to be used in the time series.
        modes (int, optional): The number of Fourier modes to compute. Defaults to 3.

    Returns:
        ee.Image: The Fourier Transform of the optical image collection.
    """

    # build the time series
    time_series = TimeSeries(
        optical, dependent=dependent_variable, modes=modes
    ).create()
    # compute the trend from the time series
    lin_reges = LinearRegression(time_series)
    # compute the Fourier Transform of the residuals
    fourier_transform = FourierTransform(time_series, lin_reges).compute()
    return fourier_transform
