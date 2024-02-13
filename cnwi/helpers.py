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

    stack = []

    # set up the datasets
    if datasets.s1 is not None:
        s1_rsd = rsd.RemoteSensingDataset(dataset_id=datasets.s1, aoi=aoi)
        s1_es, s1_ls = rsd.RemoteSensingDatasetProcessing().s1_processing(s1_rsd)
        stack.extend([s1_es.mosaic(), s1_ls.mosaic()])

    if datasets.dc is not None:
        dc_rsd = rsd.RemoteSensingDataset(dataset_id=datasets.dc, aoi=aoi)
        data_cube = rsd.RemoteSensingDatasetProcessing().data_cube_processing(dc_rsd)
        stack.append(data_cube.mosaic())

    al_rsd = rsd.RemoteSensingDataset(dataset_id="JAXA/ALOS/PALSAR/YEARLY/SAR", aoi=aoi)
    alos = rsd.RemoteSensingDatasetProcessing().alos_processing(al_rsd)
    stack.append(alos.median())

    if datasets.ta is not None:
        ta_rsd = rsd.RemoteSensingDataset(dataset_id=datasets.ta, aoi=aoi)
        terrain = rsd.RemoteSensingDatasetProcessing().terrain_processing(ta_rsd)
        stack.append(terrain.mosaic())

    if datasets.ft is not None:
        ft_rsd = rsd.RemoteSensingDataset(dataset_id=datasets.ft, aoi=aoi)
        fourier = rsd.RemoteSensingDatasetProcessing().fourier_processing(ft_rsd)
        stack.append(fourier.mosaic())

    # invoke processing pipelines
    return ee.Image.cat(*stack)


def monitor_task(task: ee.batch.Task) -> int:
    import time

    while task.status()["state"] in ["READY", "RUNNING"]:
        time.sleep(5)

    status_code = {"COMPLETED": 0, "FAILED": 1, "CANCELLED": 2}
    exit_code = status_code[task.status()["state"]]

    if exit_code == 1:
        print(task.status()["error_message"])

    return exit_code
