# Terrarium

## Process

### A Approach: One big image to rule them all 

#### Data Sources

* 
* [OpenStreetMap](http://www.openstreetmap.org/)

* [Mapzen’s vector tiles](https://mapzen.com/projects/vector-tiles)

#### Log

My first approach was to download a heightmap from the [Shuttle Radar Topography Mission](http://www2.jpl.nasa.gov/srtm/) through [Derek Watkins’s](https://twitter.com/dwtkns) [tool](http://dwtkns.com/srtm30m/) and simply project the vertices on the vertex shader.

![Tile N37W123](imgs/00-heighmap.png)

Once I download and unzip the tile from [Shuttle Radar Topography Mission](http://www2.jpl.nasa.gov/srtm/). I convert it to a PNG using [gdal](https://www.mapbox.com/tilemill/docs/guides/gdal/):

```bash
wget http://e4ftl01.cr.usgs.gov/SRTM/SRTMGL1.003/2000.02.11/N37W123.SRTMGL1.hgt.zip
tar xzvf N37W123.SRTMGL1.hgt.zip
gdal_translate -ot Int16 -of PNG N37W123.hgt N37W123.png
```

Downloading and inspecting the [JSON file with the bounding boxes](http://dwtkns.com/srtm30m/srtm30m_bounding_boxes.json) from [Derek Watkins’s](https://twitter.com/dwtkns) [tool](http://dwtkns.com/srtm30m/), I determine the boundaries of that tile. Which then I export to webmercator:

```
[-13692328.289900804, -13580946.954451224, 4439068.068371599, 4579465.0539420955]
```

Later I feed this values into a vertex shader on [Mapzen’s Map Engine](https://github.com/tangrams/tangram) together with a ```MINZ``` and ```MAXZ``` for the elevation range

```yams
geometry-terrain:
        animated: true
        mix: [generative-caustic, geometry-matrices, functions-map, filter-grain]
        shaders:
            uniforms:
                u_terrain: data/A/N37W123.png
                u_water_height: 0.
            defines:
                XMIN: -13692328.289900804
                XMAX: -13580946.954451224
                YMIN: 4439068.068371599
                YMAX: 4579465.0539420955
                ZMIN: -10.0
                ZMAX: 800.0
            blocks:
                global: |
                    bool inZone(vec2 _worldPos) {
                        return  _worldPos.x > XMIN && _worldPos.x < XMAX &&
                                _worldPos.y > YMIN && _worldPos.y < YMAX;
                    }

                    float getNormalHeight(vec2 position) {
                        vec2 worldPos = u_map_position.xy + position.xy;
                        if (inZone(worldPos)) {
                            vec2 st = vec2(0.0);
                            st.x = (worldPos.x-XMIN)/(XMAX-XMIN);
                            st.y = (worldPos.y-YMIN)/(YMAX-YMIN);
                            return texture2D(u_terrain, st).r;
                        } else {
                            return 1.1;
                        }
                    }

                    void extrudeTerrain(inout vec4 position) {
                        vec2 pos = position.xy;
                        float height = getNormalHeight(pos.xy);
                        if (height <= 1.0) {
                            position.z += ZMIN+height*(ZMAX-ZMIN);
                        }
                    }
```

In the above code you can see how I’m checking if the vertex is inside the zone for what I have elevation data. If that’s true it perform the extrusion of the vertices.

![just earth](imgs/00-earth-orig.png)

As can be notice the Polygons form the ```earth``` layer on OSM don’t have enough subdivisions and the vertices are extruded in a way that hide important features like roads and buildings (notice the errors generated on the image bellow).

![errors](imgs/00-earth.png)

To fix this I start making a custom set of plane tiles with subdivisions on important corners ( coming from polygons and lines from OSM ```earth```, ```roads``` and ```landuse``` layers)

![subdivitions](imgs/00-subdivision.png)

In this way by breaking the tiles into small fragments the extortion of the terrain don’t hide geometry.

![terrain](imgs/00-terrain.png)

The creation of the necessary tiles could be done running the script

```bash
cd data
./makeATiles.py
```



### Plan B: a image per tile

Data Source:

* [Mapzen’s elevation data](https://mapzen.com/documentation/elevation/elevation-service/)

* [OpenStreetMap](http://www.openstreetmap.org/)

* [Mapzen’s vector tiles](https://mapzen.com/projects/vector-tiles)

## Requirements

- Install PyProj

```bash
pip install pyproj
```

- Install [Requests](http://docs.python-requests.org/en/latest/user/install/#install)

```bash
pip install requests
```

- Install Shapely:

```bash
pip install shapely 
```

- Install [TileStache](https://github.com/TileStache/TileStache)

```bash
pip install TileStache 
```

## Terrain Tiles building process

```bash
cd src/
./makeTiles.py 111968 3-17
```
