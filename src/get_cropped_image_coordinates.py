import json
from tqdm import tqdm
import numpy as np
from sklearn.neighbors import NearestNeighbors
import csv
import argparse

argparser = argparse.ArgumentParser(description='Download orthophotos')
argparser.add_argument('-if', '--input_file', help='Input files', default='sample_coordinates.csv')
args = argparser.parse_args()
input_file = args.input_file

satellite_centers = []
satellite_dates = []
with open(input_file, 'r') as f:
    reader = csv.reader(f)
    for row in reader:
        satellite_centers.append([float(row[0]), float(row[1])])
        if len(row) > 2:
            satellite_dates.append(row[2])

if len(satellite_dates) == 0:
    satellite_dates = ['2022-01-01']*len(satellite_centers)

assert len(satellite_centers) == len(satellite_dates)

bounds_by_year = {}
with open('bounds.json') as f:
    bounds = json.load(f)
    for key in bounds:
        year = key.split('/')[0].split('sp')[1]
        if year in bounds_by_year:
            bounds_by_year[year][key] = bounds[key]
        else:
            bounds_by_year[year] = {key: bounds[key]}

nbrss = {} 
fnamess = {}
for key in bounds_by_year:
    coords = []
    fnames = []
    for key2 in sorted(bounds_by_year[key]):
        coords.append([bounds_by_year[key][key2][0][0], bounds_by_year[key][key2][0][1]])
        fnames.append(key2)
    coords = np.array(coords)
    fnames = np.array(fnames)
    nbrs = NearestNeighbors(n_neighbors=4).fit(coords)
    nbrss[key] = nbrs
    fnamess[key] = fnames

dates = ["2016-01-01", "2018-01-01", "2020-01-01", "2022-01-01"]
years = ["16", "18", "20", "22"]
dates = np.array([np.datetime64(date) for date in dates])

# dates = []

data = {}
counter = 0
for i in tqdm(range(len(satellite_centers))):
    date = np.datetime64(satellite_dates[i])
    key = years[np.argmin(np.abs(dates - date))]
    distances, indices = nbrss[key].kneighbors(np.array([satellite_centers[i]]))
    for index in indices[0]:
        fname = fnamess[key][index]
        polybounds = bounds_by_year[key][fname]
        if satellite_centers[i][0] > polybounds[1][0] and satellite_centers[i][0] < polybounds[0][0] and satellite_centers[i][1] > polybounds[0][1] and satellite_centers[i][1] < polybounds[2][1]:
            tl = polybounds[0]
            bl = polybounds[1]
            tr = polybounds[2]
            br = polybounds[3]
            pixelyl = (satellite_centers[i][0]-bl[0])/(tl[0]-bl[0])
            pixelyr = (satellite_centers[i][0]-br[0])/(tr[0]-br[0])

            pixelxt = (satellite_centers[i][1]-tl[1])/(tr[1]-tl[1])
            pixelxb = (satellite_centers[i][1]-bl[1])/(br[1]-bl[1])

            pixelx = pixelxt*(1-(pixelyl+pixelyl)/2) + pixelxb*(pixelyl+pixelyl)/2
            pixely = pixelyl*(1-(pixelxt+pixelxb)/2) + pixelyr*(pixelxt+pixelxb)/2

            if fname in data:
                data[fname].append([i, pixelx, pixely, satellite_centers[i][0], satellite_centers[i][1]])
            else:
                data[fname] = [[i, pixelx, pixely, satellite_centers[i][0], satellite_centers[i][1]]]
            counter += 1
            break

    

# json dump
print(counter)
with open('coordinates.json', 'w') as f:
    json.dump(data, f, indent=4)