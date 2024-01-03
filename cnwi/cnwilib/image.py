from __future__ import annotations
from abc import ABC, abstractmethod

import ee


####################################################################################################
class Calculator(ABC):
    def __call__(self, image) -> ee.Image:
        return image.addBands(self.compute(image))

    @abstractmethod
    def compute(self, image: ee.Image) -> ee.Image:
        pass


class NDVI(Calculator):
    """
    Calculates the Normalized Difference Vegetation Index (NDVI) for an image.

    Args:
        nir (str): The path to the NIR image file.
        red (str): The path to the red image file.
        name (str, optional): The name of the image. Defaults to "NDVI".
    """

    def __init__(self, nir: str, red: str, name: str = None) -> None:
        self.nir = nir
        self.red = red
        self.name = name or "NDVI"

    def compute(self, image: ee.Image) -> ee.Image:
        """
        Compute the NDVI for the given image.

        Args:
            image (ee.Image): The input image.

        Returns:
            ee.Image: The computed NDVI image.
        """
        return image.normalizedDifference([self.nir, self.red]).rename(self.name)


class SAVI(Calculator):
    """
    Calculates the Soil-Adjusted Vegetation Index (SAVI) for an image.

    Args:
        nir (str): The name of the near-infrared band.
        red (str): The name of the red band.
        name (str, optional): The name of the output band. Defaults to "SAVI".

    Returns:
        ee.Image: The computed SAVI image.
    """

    def __init__(self, nir: str, red: str, name: str = None) -> None:
        self.nir = nir
        self.red = red
        self.name = name or "SAVI"

    def compute(self, image: ee.Image) -> ee.Image:
        """
        Computes the desired expression on the given image and returns the result.

        Args:
            image (ee.Image): The input image.

        Returns:
            ee.Image: The computed image.
        """
        return image.expression(
            "((NIR - RED) / (NIR + RED + 0.5)) * (1.5)",
            {"NIR": image.select(self.nir), "RED": image.select(self.red)},
        ).rename(self.name)


class TasseledCap(Calculator):
    """
    A class representing the Tasseled Cap transformation calculator.

    This class computes the Tasseled Cap transformation on an input image.

    Args:
        **kwargs: Additional keyword arguments.

    Attributes:
        kwargs (dict): Additional keyword arguments.

    Methods:
        compute: Computes the Tasseled Cap transformation on an input image.

    """

    def __init__(self, **kwargs) -> None:
        self.kwargs = kwargs

    def compute(self, image: ee.Image) -> ee.Image:
        coefficients = ee.Array(
            [
                [0.3029, 0.2786, 0.4733, 0.5599, 0.508, 0.1872],
                [-0.2941, -0.243, -0.5424, 0.7276, 0.0713, -0.1608],
                [0.1511, 0.1973, 0.3283, 0.3407, -0.7117, -0.4559],
                [-0.8239, 0.0849, 0.4396, -0.058, 0.2013, -0.2773],
                [-0.3294, 0.0557, 0.1056, 0.1855, -0.4349, 0.8085],
                [0.1079, -0.9023, 0.4119, 0.0575, -0.0259, 0.0252],
            ]
        )

        image = image.select(list(self.kwargs.values()))
        array_image = image.toArray()
        array_image_2d = array_image.toArray(1)

        components = (
            ee.Image(coefficients)
            .matrixMultiply(array_image_2d)
            .arrayProject([0])
            .arrayFlatten(
                [["brightness", "greenness", "wetness", "fourth", "fifth", "sixth"]]
            )
        )
        components = components.select(["brightness", "greenness", "wetness"])
        return components


class Ratio(Calculator):
    def __init__(self, numerator: str, denominator: str, name: str = None) -> None:
        self.numerator = numerator
        self.denominator = denominator
        self.name = name or "Ratio"

    def compute(self, image: ee.Image) -> ee.Image:
        return image.expression(
            "(NUM / DEN)",
            {
                "NUM": image.select(self.numerator),
                "DEN": image.select(self.denominator),
            },
        ).rename(self.name)


####################################################################################################


class ImageStack:
    def __init__(self) -> None:
        self._image = []

    def __len__(self) -> int:
        return len(self._image)

    def add(self, image: ee.Image) -> None:
        self._image.append(image)
        return self

    def stack(self) -> ee.Image:
        img = self._image.pop(0)
        for _ in self._image:
            img = img.addBands(img)
        return img


####################################################################################################
