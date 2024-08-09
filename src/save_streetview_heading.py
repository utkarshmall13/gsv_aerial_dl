### functions to read road networsk from osm data

import xml.etree.ElementTree as etree
import fiona
from shapely.geometry import shape, Point, Polygon, MultiPolygon
import numpy as np
from numpy.linalg import norm
import argparse
import numpy as np
from shapely.geometry import LineString, Point
from rtree import index

argparser = argparse.ArgumentParser(description='Download orthophotos')
argparser.add_argument('-if', '--input_file', help='Input file', default='sample_coordinates.csv')
argparser.add_argument('-of', '--output_file', help='Output file', default='sample_coordinates_with_heading.csv')
args = argparser.parse_args()
infile = args.input_file
outfile = args.output_file

def isroad(tags):
    if 'highway' in tags:
        if tags['highway'] in ['motorway','trunk','primary','secondary','tertiary', 'residential', 'motorway_link']:
            return True
    return False

def getpaths(filterfunc):
    segments = []
    segments_coords = []
    counter = 0
    ways=[]
    for event, elem in etree.iterparse(pathOSM, events=('start', 'end')):
        if event == 'start':
            pass
        else:
            counter+=1
            if elem.tag=='node':
                elem.clear()
            if elem.tag=='relation':
                elem.clear()

            if elem.tag=='way':
                tags = {}
                subnodes = []
                for child in elem:
                    if child.tag=='tag':
                        tags[child.get('k')] = child.get('v')
                    if child.tag=='nd':
                        subnodes.append(int(child.get('ref')))
                if filterfunc(tags):
                    segments.append(subnodes)
                elem.clear()
            if counter%1000000==0:
                print(len(segments), counter)
            pass
    for seg in segments:
        segments_coords.append([nodes[nodeid] for nodeid in seg])
    return segments_coords


print("Loading OSM data")
city, cityname = "nyc", "New York"

pathOSM = "../data/cities_osm/{}.osm".format(city)
nodes = {}
counter = 0
for event, elem in etree.iterparse(pathOSM, events=('start', 'end')):
    if event == 'start':
        pass
    else:
        counter+=1
        if elem.tag=='node':
            nodes[int(elem.get('id'))] = [float(elem.get('lat')), float(elem.get('lon'))]
        if counter%1000000==0:
            print(len(nodes), counter)
        elem.clear()
        pass


paths = getpaths(isroad)
print("Total roads:", len(paths))

pathsnp_start, pathsnp_end = [], []
for path in paths:
    for i in range(len(path)-1):
        pathsnp_start.append(path[i])
        pathsnp_end.append(path[i+1])
    # break
pathsnp_start, pathsnp_end = np.array(pathsnp_start), np.array(pathsnp_end)
print(pathsnp_start.shape, pathsnp_end.shape)

print("Loading city shapefile")
nyc = fiona.open("../sf/nyc_sf/geo_export_cf738421-b7e8-4297-bea9-f8521e74f2f5.shp")
polys = []
for x in nyc:
    poly = shape(x['geometry'])
    poly = poly.simplify(0.005)
    polys.append(poly)


new_polys = []
for nbr in polys:
    if nbr.geom_type == 'Polygon':
        coords = nbr.exterior.coords
        new_coords = [(x, y) for x, y in coords]
        nbr = Polygon(new_coords)
        new_polys.append(nbr)
    else:
        nps = []
        for polygon in nbr.geoms:
            coords = polygon.exterior.coords
            new_coords = [(x, y) for x, y in coords]
            polygon = Polygon(new_coords)
            nps.append(polygon)
        nps = MultiPolygon(nps)
        new_polys.append(nps)

inpathsnp_start, inpathsnp_end = [], []
for i in range(len(pathsnp_start)):
    outsideinds = []
    point_start = pathsnp_start[i]
    point_end = pathsnp_end[i]
    pt_start = Point(point_start[1], point_start[0])
    pt_end = Point(point_end[1], point_end[0])
    inside = False

    for poly in new_polys:
        if poly.contains(pt_start) and poly.contains(pt_end):
            inside = True
            break
    if inside:
        inpathsnp_start.append(point_start[:])
        inpathsnp_end.append(point_end[:])
inpathsnp_start, inpathsnp_end = np.array(inpathsnp_start), np.array(inpathsnp_end)
print(pathsnp_start.shape, pathsnp_end.shape)
print(inpathsnp_start.shape, inpathsnp_end.shape)

import csv
with open(infile) as ifd:
    coords = []
    reader = csv.reader(ifd)
    for row in reader:
        coords.append([float(row[0]), float(row[1])])
coords = np.array(coords)

coords = np.array(coords)
roads = np.array([inpathsnp_start, inpathsnp_end])
roads = np.transpose(roads, (1, 0, 2))
points = np.array(coords)

print("Setting up R-tree")

idx = index.Index()
road_segments = []

buffer_distance = 0.001
for i, road in enumerate(roads):
    line = LineString(road)
    road_segments.append(line)
    buffered_line = line.buffer(buffer_distance)
    idx.insert(i, buffered_line.bounds)

print(idx)
indices = []

coords_with_heading = []

for point in points:
    pt = Point(point)
    possible_matches = list(idx.intersection(pt.bounds))
    min_dist = float('inf')
    closest_segment_idx = None
    for i in possible_matches:
        segment = road_segments[i]
        distance = pt.distance(segment)
        if distance < min_dist:
            min_dist = distance
            closest_segment_idx = i    
    indices.append(closest_segment_idx)

for i, point in enumerate(points):
    closest_idx = indices[i]
    if closest_idx is not None:
        road = roads[closest_idx]
        heading = np.arctan2(road[1][1] - road[0][1], road[1][0] - road[0][0])
        heading = np.rad2deg(heading)
    else:
        heading = 0
    coords_with_heading.append([point[0], point[1], heading])

with open(outfile, "w") as ofd:
    writer = csv.writer(ofd)
    for row in coords_with_heading:
        writer.writerow(row)