import ee


# -- Optical Calculations
def compute_ndvi_from_expression(image: ee.Image, nir: str, red: str, name: str = None) -> ee.Image:
    name = name or "NDVI"
    return image.expression(
            "(NIR - RED) / (NIR + RED)",
            {"NIR": image.select(nir), "RED": image.select(red)},
        ).rename(name)


def compute_savi_from_expression(nir: str, red: str, L: float = 0.5, name: str = None):
    name = name or "SAVI"
    return lambda image: image.addBands(
        image.expression(
            "(1 + L) * (NIR - RED) / (NIR + RED + L)",
            {"NIR": image.select(nir), "RED": image.select(red), "L": L},
        ).rename(name)
    )


# -- Radar Calculations
def compute_ratio_from_expression(b1: str, b2: str, name: str = None):
    name = name or f"{b1}_{b2}"
    return lambda image: image.addBands(
        image.select(b1).divide(image.select(b2)).rename(name)
    )