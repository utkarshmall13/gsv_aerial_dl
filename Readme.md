## Step-0: Setup

See `setup.sh` for mamba/conda environment.

After setup run `mkdir data` to create a data directory where outputs will be stored.

## Step-1: Downloading ortho imagery

### Get raw ortho imagery

Use `download_ortho.py` to download the raw ortho iamgery from New York's GIS data website. 

### Processing ortho imagery

The ortho imagery are in format not suitable for deep learning applications. So we first convert it into computer vision format.

run the following three scripts:

> python3 convert_orthojp22jpg.py

This converts jp2 images to jpeg images. Then to get geocoordinate bounds of these images run `get_ortho_bounds.py`

> python3 get_ortho_bounds.py

After getting bounds for ortho images, use `get_cropped_image_coordinates.py` to get cropped image bounds for the corresponding ground images. 

> python3 get_cropped_image_coordinates.py

Finally, run

> python3 get_cropped_images.py

to obtain the cropeed images corresponding to ground images. You can also change dimensions etc of these images to increase the span.

## Step-2 Download streetview images.
For street locations, Openstreetmap extracts are also needed along with the shapefile. The NYC shapefile is already in the repo.

[bbbike](https://extract.bbbike.org/) is the best source for this. 

* Just select your area of interest either using bounding box aor polygon tool. (Select the 5 boroughs of NYC.)
* Remember to download in *OSM XML gzip'd* format.
* After clicking extract it redirects you to download page. Once the download is ready move it to the 'data/cities_osm' directory.
* Extract the osm.gz file.

> gunzip -k ../data/cities_osm/nyc.osm.gz 

Once the osm is downloaded first run `save_streetview_heading.py` to save the heading direction for each location.
This saves the direction in which GSV car is heading and results in consitent views.

Obtain google cloud api key:

* Follow the instructions on the [google api page](https://developers.google.com/maps/documentation/streetview/overview) to see instrutions on obtaining the api key.
* Put the api key in the `streetview_downloader.py`, `google_key` variable.

