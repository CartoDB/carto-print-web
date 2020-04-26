import geopandas as gpd
import networkx as nx
import osmnx as ox
from shapely.geometry import Point, LineString, Polygon
from geopandas import GeoSeries, GeoDataFrame

import os
import time

from cartoframes import to_carto
from cartoframes.auth import Credentials, set_default_credentials

from carto.auth import APIKeyAuthClient
from carto.maps import NamedMapManager
from carto.print import Printer

ox.config(log_console=True, use_cache=True)
ox.__version__

CARTO_BASE_URL = os.environ['CARTO_API_URL']
CARTO_API_KEY = os.environ['CARTO_API_KEY']
CARTO_USER_NAME = os.environ['CARTO_USER_NAME']
DPI = 72


def make_iso_polys(G, center_node, radius, distance, edge_buff=25, node_buff=50, infill=False):
    subgraph = nx.ego_graph(G, center_node, radius=radius, distance=distance)

    node_points = [Point((data['x'], data['y'])) for node, data in subgraph.nodes(data=True)]
    nodes_gdf = gpd.GeoDataFrame({'id': subgraph.nodes()}, geometry=node_points)
    nodes_gdf = nodes_gdf.set_index('id')

    edge_lines = []
    for n_fr, n_to in subgraph.edges():
        f = nodes_gdf.loc[n_fr].geometry
        t = nodes_gdf.loc[n_to].geometry
        edge_lines.append(LineString([f,t]))

    n = nodes_gdf.buffer(node_buff).geometry
    e = gpd.GeoSeries(edge_lines).buffer(edge_buff).geometry
    all_gs = list(n) + list(e)
    new_iso = gpd.GeoSeries(all_gs).unary_union

    # try to fill in surrounded areas so shapes will appear solid and blocks without white space inside them
    if infill:
        new_iso = Polygon(new_iso.exterior)
    return new_iso


def get_iso_distance(lat, lon, distance=1000, network_type='walk'):
    G = ox.graph_from_point((lat, lon), distance=distance, network_type=network_type)
    # find the centermost node and then project the graph to UTM
    center = ox.get_nearest_node(G, (lat, lon), method='euclidean', return_dist=True)
    G1 = ox.project_graph(G)
    center_node = center[0]

    iso = make_iso_polys(G1, center_node, distance, 'length', edge_buff=25, node_buff=0, infill=True)

    gdf = GeoDataFrame(geometry=GeoSeries(iso))
    gdf.crs = G1.graph['crs']
    gdf = gdf.to_crs("EPSG:4326")
    bounds = gdf.bounds

    return gdf, bounds


def create_named_map(auth_client, username, dataset_name, map_name, factor, lon, lat):
    template = {
      "version": "0.0.1",
      "name": map_name,
      "auth": {
        "method": "open"
      },
      "placeholders": {},
      "view": {},
      "layergroup": {
        "version": "1.0.1",
        "layers": [
          {
            "type": "http",
            "options": {
                "urlTemplate": "http://a.tile.stamen.com/toner/{z}/{x}/{y}.png"
                #"urlTemplate": "https://a.basemaps.cartocdn.com/rastertiles/voyager_labels_under/{z}/{x}/{y}.png"
            }
          },
          {
            "type": "cartodb",
            "options": {
              "cartocss_version": "2.1.1",
              "cartocss": '''#layer {
                              polygon-fill: #2a2a2a;
                              polygon-opacity: 0;
                            }
                            #layer::outline {
                              line-width: 6 * %d;
                              line-color: #4edce6;
                              line-opacity: 1;
                              line-dasharray: 10, 3, 2, 3;
                            }''' % (factor),
              "sql": '''SELECT 1 AS cartodb_id,
                               the_geom,
                               the_geom_webmercator
                        FROM {dataset}'''.format(dataset=dataset_name)
            }
          },
          {
            "type": "cartodb",
            "options": {
              "cartocss_version": "2.1.1",
              "cartocss": '''#layer {
                              marker-width: 40 * %d;
                              marker-fill: #EE4D5A;
                              marker-fill-opacity: 0.9;
                              marker-file: url('https://s3.amazonaws.com/com.cartodb.users-assets.production/maki-icons/cross-18.svg');
                              marker-allow-overlap: true;
                            }
                            ''' % (factor),
              "sql": '''SELECT 1 AS cartodb_id,
                               ST_SetSRID( ST_Point( {lon}, {lat}), 4326) as the_geom,
                               ST_Transform(ST_SetSRID( ST_Point( {lon}, {lat}), 4326), 3857) as the_geom_webmercator
                     '''.format(lon=lon, lat=lat)
            }
          }
        ]
      }
    }

    named_map_manager = NamedMapManager(auth_client)

    try:
        named_map = named_map_manager.get(map_name)
        if named_map is not None:
            named_map.client = auth_client
            named_map.delete()
    except Exception as e:
        #ignore
        print(e)

    return named_map_manager.create(template=template)


def create_map(iso, lon, lat):
    creds = Credentials(username=CARTO_USER_NAME, api_key=CARTO_API_KEY)
    set_default_credentials(creds)
    dataset_name = 'onekmiso'
    dataset_name = dataset_name + str(int(round(time.time() * 1000)))

    to_carto(iso, dataset_name, if_exists='replace', log_enabled=True)

    auth_client = APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY)
    FACTOR = DPI / 72.0
    map_name = 'tpl_' + dataset_name
    create_named_map(auth_client, CARTO_USER_NAME, dataset_name, map_name, FACTOR, lon, lat)
    return map_name


def export_map(map_name, bounds):
    map = {
        'username': CARTO_USER_NAME,
        'map_id': map_name,
        'width': 29.7,
        'height': 21,
        'dpi': DPI,
        'zoom': 1,
        'bounds': f"{bounds['minx'][0]},{bounds['miny'][0]},{bounds['maxx'][0]},{bounds['maxy'][0]}",
        'api_key': CARTO_API_KEY
    }

    p = Printer(map['username'], map['map_id'], map['api_key'], map['width'], map['height'], map['zoom'], map['bounds'], map['dpi'], 'RGBA')
    return p.export('/tmp')


def delete_map(map_name):
    auth_client = APIKeyAuthClient(CARTO_BASE_URL, CARTO_API_KEY)
    named_map_manager = NamedMapManager(auth_client)

    try:
        named_map = named_map_manager.get(map_name)
        if named_map is not None:
            named_map.client = auth_client
            named_map.delete()
    except Exception as e:
        #ignore
        print(e)