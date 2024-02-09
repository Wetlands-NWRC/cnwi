import ee


from . import rsd


def image_processing(aoi, datasets) -> ee.Image:
    """
    Process remote sensing datasets and generate a composite image.

    Args:
        aoi (ee.Geometry): Area of interest for the processing.
        datasets (dict): Dictionary containing dataset IDs for different remote sensing datasets.

    Returns:
        ee.Image: Composite image generated from the processed datasets.
    """

    # set up the datasets
    s1_rsd = rsd.RemoteSensingDataset(dataset_id=datasets.s1, aoi=aoi)
    dc_rsd = rsd.RemoteSensingDataset(dataset_id=datasets.data_cube, aoi=aoi)
    al_rsd = rsd.RemoteSensingDataset(dataset_id="JAXA/ALOS/PALSAR/YEARLY/SAR", aoi=aoi)
    ta_rsd = rsd.RemoteSensingDataset(dataset_id=datasets.ta, aoi=aoi)
    ft_rsd = rsd.RemoteSensingDataset(dataset_id=datasets.ft, aoi=aoi)

    # invoke processing pipelines
    s1_es, s1_ls = rsd.RemoteSensingDatasetProcessing().s1_processing(s1_rsd)
    data_cube = rsd.RemoteSensingDatasetProcessing().data_cube_processing(dc_rsd)
    alos = rsd.RemoteSensingDatasetProcessing().alos_processing(al_rsd)
    terrain = rsd.RemoteSensingDatasetProcessing().terrain_processing(ta_rsd)
    fourier = rsd.RemoteSensingDatasetProcessing().fourier_processing(ft_rsd)

    return ee.Image.cat(
        s1_es.mosaic(),
        s1_ls.mosaic(),
        data_cube.mosaic(),
        alos.median(),
        terrain.mosaic(),
        fourier.mosaic(),
    )


def monitor_task(task: ee.batch.Task) -> int:
    import time

    while task.status()["state"] in ["READY", "RUNNING"]:
        time.sleep(5)

    status_code = {"COMPLETED": 0, "FAILED": 1, "CANCELLED": 2}
    exit_code = status_code[task.status()["state"]]

    if exit_code == 1:
        print(task.status()["error_message"])

    return exit_code
