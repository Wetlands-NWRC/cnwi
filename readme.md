# CNWI
Canadian National Wetland Inventory Classification Pipeline. It is a simple tool to classify wetlands using the Canadian National Wetland Inventory (CNWI) classification system. The tool uses Google Earth Engine to process the data and classify the region of interest.

## How it works
The tool takes in a feature id, region id, and a payload file. The feature id is the asset id of the feature you want to classify, the region id is the asset id of the region or area of interest you want to classify, and the payload file contains the asset ids for the images you want to include in the classification. The tool then processes the images and classifies the region of interest using the CNWI classification system. The classified image is then exported to the users google drive. It should be noted that this
tools is designed to use the Earth Engine asset store as a file system for reading and writing of data.

## Notes
- Smile Random Forest hyper parameters are NOT exposed to the user at this time

## Installation
```bash
pip install git+https://github.com/Wetlands-NWRC/cnwi.git
```

## Usage
```bash
cnwi <feature_id> <region_id> <payload.json>
```
- Feature ID: Asset ID of the features you want to classify
- Region ID: Asset ID of the Region or Area of Interest you want to classify
- Payload: JSON file containing the Asset ids for the Images you want to include

## Feature ID
- The feature id is the asset id of the feature you want to classify
- The trainingPoints and validationPoints files need to combined into a single file and uploaded to the asset store
- The file at a minimum needs to contain the following columns
    - `class_name` : The integer representation of the class (the class name has been overwritten by the integer representation) it is recommended to create a lookup table for reference
    - `split` : The split the point belongs to (training or validation), must be either `training` or `test` (str)
    - `geometry` : The geometry of the feature

## Region ID
- The region id is the asset id of the region or area of interest you want to classify
- The region file needs to be uploaded to the asset store

## Payload
- The payload file should contain the asset ids for the images you want to include in the classification
- The keys need to be the same as the ones below, if the key does not exist the variables that correspond with the image will be ignored
```json
    // payload.json example
    {
        "s1": ["S1 Asset ID", ...],
        "dc": "Data Cube Asset ID",
        "ft": "Fourier Transform Asset ID",
        "ta": "Terrain Analysis Asset ID"
    }
```

## Image Processing Processing
- The data processing is done in the following order
    1. Data Cube
    2. Fourier Transform
    3. Terrain Analysis
    4. Sentinel 1
    5. ALOS

### Data Cube Processing
- The data cube processing is done using the `ee.ImageCollection` classes
- bands with the prefix a_sprin b_summ and c_fall, and suffix b01 - b12 are used all other bands are ignored
- the bands are remapped to use the Sentinel 2 TOA band names: `B2, B3, B4, B5, B6, B7, B8, B8A, B11, B12`
    - `a_sprin_bXX` -> `BXX`
    - `b_summ_bXX` -> `BXX_1`
    - `c_fall_bXX` -> `BXX_2`
- The data cube is then filtered to the region of interest
- NDVI, SAVI, Brightness, Greenness, Wetness, and calculated and added to the data cube as bands
    - each time period has its own NDVI, SAVI, Brightness, Greenness, and Wetness bands
- The data cube is then mosaicked into a single image

### Fourier Transform Processing
- Time series processing and computation of Fourier Transform is done externally using the `time_series_tools` tool chain

### Terrain Analysis Processing
- Terrain analysis is done externally using the `terrain_tools` tool chain

### Sentinel 1 Processing
- Sentinel 1 input images are hand selected from the Sentinel 1 Image Collection
- The images are then filtered to the region of interest
- The images then have a 3 x 3 box car filer applied to them to reduce speckle
- The Ratio is then computed and added to the image
- The images are then mosaicked into a single image

### ALOS Processing
- ALOS input is computed from the ALOS Image Collection
- The images are then filtered to the region of interest
- The images then have a 3 x 3 box car filer applied to them to reduce speckle
- The Ratio is then computed and added to the image
- The images are then composited into a single image using the median value

## Classification
- Number of trees: 1000
- uses all bands from the input images as predictors
- The classification is done using the `ee.Classifier.smileRandomForest` classifier
- The classifier is trained using the training points
- The classifier is then used to classify the region of interest
- The classified image is then exported to the the users google drive