import numpy as np
import requests
from os.path import join, isfile, isdir
from os import mkdir
import csv
from tqdm import tqdm
from PIL import Image
import argparse

argparser = argparse.ArgumentParser(description='Download orthophotos')
argparser.add_argument('-if', '--input_file', help='Input file', default='sample_coordinates_with_heading.csv')
argparser.add_argument('-od', '--output_dir', help='Output directory', default='../data/streetviewimages')
argparser.add_argument('-gk', '--google_key', help='Google API key', default='YOUR_API_KEY')
args = argparser.parse_args()

output_dir = args.output_dir
if not isdir(output_dir):
    mkdir(output_dir)
infile = args.input_file
google_key = args.google_key

with open(infile, 'r') as f:
    reader = csv.reader(f)
    locs = []
    for row in reader:
        locs.append([float(row[0]), float(row[1]), float(row[2])])
    print(len(locs))

    for i in tqdm(range(len(locs))) :
        loc = locs[i]
        for j in range(4):
            fname = join(output_dir, str(i).zfill(8)+'_'+str(int(float(row[0])*1e8))+'_'+str(int(float(row[1])*1e8))+'_'+str(j)+'.jpg')
            if isfile(fname):
                continue
            url = "https://maps.googleapis.com/maps/api/streetview?size=640x480&location={},{}&fov=90&heading={}&pitch=15&key={}".format(loc[0], loc[1], loc[2]+(90*j), google_key)
            # print(url)
            try:
                im = Image.open(requests.get(url, stream=True).raw)
                im.save(fname)
            except Exception as e:
                print(e, url)
                pass
    # if i==10:
    #     break