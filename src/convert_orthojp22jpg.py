from os.path import join, isfile
from os import listdir
import os
from multiprocessing import Pool
import argparse

argparser = argparse.ArgumentParser(description='Download orthophotos')
argparser.add_argument('-wd', '--working_dir', help='Output directory', default='../data/ortho')
args = argparser.parse_args()

working_dir = args.working_dir
years = ['16', '18', '20', '22']
boroughs = ['bronx', 'brooklyn', 'manhattan', 'queens', 'staten_island']

for year in years:
    for boro in boroughs:
        inp_dir = join(working_dir, 'boro_{}_sp{}'.format(boro, year))
        files = [tmp for tmp in listdir(inp_dir) if '.jp2' in tmp and 'jp2.' not in tmp]
        print('Processing {} files in {}'.format(len(files), inp_dir))
        # for file in files:
        def worker(file):
            if isfile(join(inp_dir, file).replace('.jp2', '.jpg')):
                return
            file = join(inp_dir, file)
            out_file = file.replace('.jp2', '.jpg')
            cmd = 'gdal_translate -of JPEG -b 1 -b 2 -b 3 {} {}'.format(file, out_file)
            print(cmd)
            os.system(cmd)
        with Pool(32) as p:
            p.map(worker, files)
    #     break
    # break