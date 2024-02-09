from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


import ee


@dataclass
class RemoteSensingDataset:
    dataset_id: str | list[str]
    aoi: Any = field(default=None)


class RemoteSensingDatasetProcessor:
    def __init__(self, arg) -> None:
        self._dataset = arg

    @property
    def dataset(self):
        return self._dataset

    @dataset.setter
    def dataset(self, arg):
        if isinstance(arg, ee.ImageCollection):
            self._dataset = arg
        else:
            self._dataset = ee.ImageCollection(arg)

    def filter_dates(self, start, end):
        self._dataset = self._dataset.filterDate(start, end)
        return self

    def filter_bounds(self, geom):
        self._dataset = self._dataset.filterBounds(geom)
        return self

    def select(self, var_args: Any, remap: bool = False):
        if remap:
            self._dataset = self.dataset.select(
                self._dataset.first().bandNames(), var_args
            )
            return self
        self._dataset = self._dataset.select(var_args)
        return self

    def add_box_car(self, radius: int = 1):
        self._dataset = self._dataset.map(
            lambda x: x.convolve(ee.Kernel.square(radius))
        )
        return self

    def add_ratio(self, b1, b2):
        self._dataset = self._dataset.map(
            lambda x: x.addBands(x.select(b1).divide(x.select(b2)).rename(f"{b1}_{b2}"))
        )
        return self

    def add_ndvi(self, nir, red):
        self._dataset = self._dataset.map(
            lambda x: x.addBands(x.normalizedDifference([nir, red]).rename("NDVI"))
        )
        return self

    def add_savi(self, nir, red, L: float = 0.5):
        self._dataset = self._dataset.map(
            lambda image: image.addBands(
                image.expression(
                    "(1 + L) * (NIR - RED) / (NIR + RED + L)",
                    {"NIR": image.select(nir), "RED": image.select(red), "L": L},
                ).rename("SAVI")
            )
        )
        return self

    def add_tasseled_cap(
        self, blue: str, green: str, red: str, nir: str, swir1: str, swir2: str
    ):
        def compute(image: ee.Image):
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

            image_inpt = image.select([blue, green, red, nir, swir1, swir2])
            array_image = image_inpt.toArray()
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
            return image.addBands(components)

        self._dataset = self._dataset.map(compute)
        return self

    def build(self) -> ee.ImageCollection:
        return self._dataset


class RemoteSensingDatasetProcessing:
    def __init__(self) -> None:
        self.processor = RemoteSensingDatasetProcessor()

    def s1_processing(
        self, dataset: RemoteSensingDataset
    ) -> tuple[ee.ImageCollection, ee.ImageCollection]:
        self.processor.dataset = dataset.dataset_id

        BANDS = ["VV", "VH"]
        proc = (
            self.processor.filter_bounds(dataset.aoi)
            .select(BANDS)
            .add_box_car(1)
            .add_ratio(b1="VV", b2="VH")
            .build()
        )

        return proc.filterDate("2017-01-01", "2017-12-31"), proc.filterDate(
            "2018-01-01", "2018-12-31"
        )

    def data_cube_processing(self, dataset: RemoteSensingDataset) -> ee.ImageCollection:
        self.processor.dataset = dataset.dataset_id

        b_pattern = "a_spri_b0[2-9].*|a_spri_b[1-2].*|b_summ_b0[2-9].*|b_summ_b[1-2].*|c_fall_b0[2-9].*|c_fall_b[1-2].*"
        spring_bands = ["B2", "B3", "B4", "B5", "B6", "B7", "B8", "B8A", "B11", "B12"]
        summer_bands = [f"{band}_1" for band in spring_bands]
        fall_bands = [f"{band}_2" for band in spring_bands]
        new_band_names = spring_bands + summer_bands + fall_bands
        proc = (
            self.processor.filter_bounds(dataset.aoi)
            .select(b_pattern)
            .select(new_band_names, remap=True)
            .add_ndvi("B8", "B4")
            .add_ndvi("B8_1", "B4_1")
            .add_ndvi("B8_2", "B4_2")
            .add_savi("B8", "B4")
            .add_savi("B8_1", "B4_1")
            .add_savi("B8_2", "B4_2")
            .add_tasseled_cap("B2", "B3", "B4", "B8", "B11", "B12")
            .add_tasseled_cap("B2_1", "B3_1", "B4_1", "B8_1", "B11_1", "B12_1")
            .add_tasseled_cap("B2_2", "B3_2", "B4_2", "B8_2", "B11_2", "B12_2")
            .build()
        )
        return proc

    def alos_processing(self, dataset: RemoteSensingDataset) -> ee.ImageCollection:
        self.processor.dataset = dataset.dataset_id
        return (
            self.processor.filter_dates("2018", "2021")
            .filter_bounds(dataset.aoi)
            .select("H.*")
            .add_box_car(1)
            .add_ratio("HH", "HV")
            .build()
        )

    def terrain_processing(self, dataset: RemoteSensingDataset) -> ee.ImageCollection:
        self.processor.dataset = dataset.dataset_id
        return self.processor.filter_bounds(dataset.aoi).build()

    def fourier_processing(self, dataset: RemoteSensingDataset) -> ee.ImageCollection:
        self.processor.dataset = dataset.dataset_id
        return self.processor.filter_bounds(dataset.aoi).build()
