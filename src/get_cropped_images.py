from os.path import join, isdir
from os import listdir, mkdir
import json
from PIL import Image
from tqdm import tqdm
import argparse

argparser = argparse.ArgumentParser(description='Download orthophotos')
argparser.add_argument('-id', '--input_dir', help='Input directory', default='../data/ortho')
argparser.add_argument('-od', '--output_dir', help='Output directory', default='../data/satelliteimages')
argparser.add_argument('-d', '--dimensions', help='Dimensions of the image', default=336)


args = argparser.parse_args()

idir = args.input_dir
coordfile = 'coordinates.json'
odir = args.output_dir
dim = int(args.dimensions)

if not isdir(odir):
    mkdir(odir)

with open(coordfile, 'r') as f:
    coords = json.load(f)

for key in tqdm(coords.keys()):
    # print(coords[key])
    im = Image.open(join(idir, key+'.jpg')) 
    h, w = im.size
    for row in coords[key]:
        center = [int(row[1]*w), int((1-row[2])*h)]
        # print(row, center)
        left = max(0, center[0]-dim//2)
        right = min(w, center[0]+dim//2)
        top = max(0, center[1]-dim//2)
        bottom = min(h, center[1]+dim//2)
        if left==0:
            right = dim
        if right==w:
            left = w-dim
        if top==0:
            bottom = dim
        if bottom==h:
            top = h-dim
        assert right-left==dim and bottom-top==dim
        im1 = im.crop((left, top, right, bottom))
        im1.save(join(odir, str(row[0]).zfill(8)+'_'+str(int(row[3]*1e8))+'_'+str(int(row[4]*1e8)) +'.jpg'))
        # break
    # break
    # break