from osgeo import ogr, osr
from os.path import join, isfile
from os import listdir
import json
import argparse
from tqdm import tqdm

target_srs = osr.SpatialReference()
target_srs.ImportFromEPSG(4326)  # EPSG code for WGS84

argparser = argparse.ArgumentParser(description='Getting orthophotos bounds')
argparser.add_argument('-wd', '--working_dir', help='Working directory', default='../data/ortho')
args = argparser.parse_args()

idir = args.working_dir
years = ['16', '18', '20', '22']
borough = ['bronx', 'brooklyn', 'manhattan', 'queens', 'staten_island']



bounds = {}
for year in years:
    for boro in borough:
        inp_dir = join(idir, 'boro_{}_sp{}'.format(boro, year))
        files2 = [tmp for tmp in listdir(inp_dir) if '.jp2' in tmp and 'jp2.' not in tmp]
        files = [tmp.replace('jp2', 'tab') for tmp in files2 if isfile(join(inp_dir, tmp.replace('jp2', 'tab')))]
        print(year, boro, len(files), len(files2))
        if len(files) != len(files2):
            print('Mismatch')
            continue
          
        for file in tqdm(files, desc='Processing files'):
            fileoext = file.replace('.tab', '')
            file = join(inp_dir, file)
            # print(file)
            with open(file, 'r') as f:
                lines = f.readlines()
            # print(lines)
            # print()
            rows = []
            for row in lines:
                if '"SW"' in row or '"NW"' in row or '"NE"' in row or '"SE"' in row:
                    rows.append(row)
            for row in lines:
                if row.startswith('  CoordSys Earth Projection 3'):
                    rows.append(row)
                    break
            if not rows[-1].startswith('  CoordSys Earth Projection 3'):
                continue
            # print(file)
            # print(rows)
            system = [float(tmp) for tmp in rows[-1].strip().split(', ')[3:]]
            system[-2] = system[-2]*0.3048006096012192
            system[-1] = system[-1]*0.3048006096012192
            coords = [tmp.split('(')[1].split(')')[0] for tmp in rows[:4]]
            vertices = [[float(tmp2) for tmp2 in tmp.split(', ')] for tmp in coords]
            # print(vertices)
            src_srs = osr.SpatialReference()
            src_srs.ImportFromProj4("+proj=lcc +lon_0={} +lat_0={} +lat_1={} +lat_2={} +x_0={} +y_0={} +to_meter=0.3048006096012192 +ellps=GRS80".format(*system))
            transform = osr.CoordinateTransformation(src_srs, target_srs)

            newv = []
            for vertex in vertices:
                point = ogr.Geometry(ogr.wkbPoint)
                point.AddPoint(*vertex)
                point.Transform(transform)
                newv.append([point.GetX(), point.GetY()])
            bounds[join('boro_{}_sp{}'.format(boro, year), fileoext)] = newv
        # pool
        # break
    # break
with open('bounds.json', 'w') as f:
    json.dump(bounds, f, indent=4)

        


