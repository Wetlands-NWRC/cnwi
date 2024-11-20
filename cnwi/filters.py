import ee


# -- sentinel 1 filters
def filter_iw() -> ee.Filter:
    return ee.Filter.eq("instrumentMode", "IW")

def filter_vv() -> ee.Filter:
    return ee.Filter.eq("polarisation", "VV")

def filter_vh() -> ee.Filter:
    return ee.Filter.eq("polarisation", "VH")

def filter_asc() -> ee.Filter:
    return ee.Filter.eq("orbitProperties_pass", "ASCENDING")

def filter_desc() -> ee.Filter:
    return ee.Filter.eq("orbitProperties_pass", "DESCENDING")


# -- specital filters
def boxcar(radius: int = 1) -> ee.Kernel:
    return ee.Kernel.square(radius)