import argparse
from os import makedirs
from os.path import join, exists, isdir
import wget
from multiprocessing import Pool
from zipfile import ZipFile

argparser = argparse.ArgumentParser(description='Download orthophotos')
argparser.add_argument('-od', '--output_dir', help='Output directory', default='../data/ortho')

args = argparser.parse_args()

if not isdir(args.output_dir):
    makedirs(args.output_dir)

# Download orthophotos
url = 'https://gisdata.ny.gov/ortho/nysdop{}/new_york_city/spcs/zips/boro_{}_sp{}.zip'
years = ['16', '18', '20', '22']
iterations = ['8', '9', '10', '11']
boroughs = ['bronx', 'brooklyn', 'manhattan', 'queens', 'staten_island']

def downloader(borough):
    for iteration, year in zip(iterations, years):
        urlform = url.format(iteration, borough, year)
        filename = urlform.split('/')[-1]
        if not exists(join(args.output_dir, filename)):
            print(f'Downloading {filename}')
            wget.download(urlform, out=args.output_dir)
        else:
            print(f'{filename} already exists')
        if not isdir(join(args.output_dir, filename.split('.')[0])):
            print(f'Unzipping {filename}')
            ZipFile(join(args.output_dir, filename)).extractall(join(args.output_dir, filename.split('.')[0]))
        else:
            print(f'{filename} already unzipped')

with Pool(5) as p:
    p.map(downloader, boroughs)