mamba create -n gsv_aerial_dl python=3.11 -y
mamba activate gsv_aerial_dl
pip install requests numpy fiona shapely matplotlib tqdm pillow scikit-learn earthengine-api wget rtree
mamba install -c conda-forge gdal=3.9.0 -y
mamba install -c conda-forge libgdal-jp2openjpeg -y

mkdir data