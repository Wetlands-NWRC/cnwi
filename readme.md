# create conda environment
```bash
conda create -n cnwi python=3.11
```
# install dependencies
```bash
conda install -c conda-forge earthengine-api geopandas -y
```

# install cnwi package
```bash
pip install -e .
```