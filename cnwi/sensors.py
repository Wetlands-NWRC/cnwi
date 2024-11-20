import ee

# -- collections

# -- Optical Sensors
class DataCube(ee.ImageCollection):
    def __init__(self, arg=None) -> None:
        super().__init__(arg)


class Sentinel2TOA(ee.ImageCollection):
    def __init__(self, arg=None) -> None:
        super().__init__(arg or "COPERNICUS/S2_HARMONIZED")


# -- Radar Sensors
class Sentinel1(ee.ImageCollection):
    def __init__(self, arg=None) -> None:
        super().__init__(arg or "COPERNICUS/S1_GRD")


class PalsarAlos(ee.ImageCollection):
    def __init__(self, arg=None) -> None:
        super().__init__(arg or "JAXA/ALOS/PALSAR")


# -- Image Datasets
class Fourier(ee.Image):
    def __init__(self, arg=None) -> None:
        super().__init__(arg)


class TerrainAnalysis(ee.Image):
    def __init__(self, arg=None) -> None:
        super().__init__(arg)