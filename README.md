# Terrarium

![](imgs/terrarium.jpg)

## Process

### Approach A: One big image to rule them all 

#### Data Sources

* [Shuttle Radar Topography Mission](http://www2.jpl.nasa.gov/srtm/) through [Derek Watkins’s](https://twitter.com/dwtkns) [tool](http://dwtkns.com/srtm30m/)

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

The creation of the necessary tiles could be done running the script followed by the USGS ID (default: `N37W123`) and zoom levels (default: `3-17`)

```bash
cd data
python makeATiles.py [USGS_ID] [ZOOM_RANGE]
```

Once the tiles are done and you watch the map in higher zoom levels could be appreciated a new problem. 

![buildings error](imgs/01-buildings.png)

The top of the buildings have been extrude according to the heightmap but in a incongruent way. To fix this issue a new approach had to be develop


### Approach B: an image per tile

#### Data Sources

* [Mapzen’s elevation data](https://mapzen.com/documentation/elevation/elevation-service/)

* [OpenStreetMap](http://www.openstreetmap.org/)

* [Mapzen’s vector tiles](https://mapzen.com/projects/vector-tiles)

#### Log

In order to solve the incongruence on building extrusion I thought will be beneficial to have control over the heightmap. For that a new set of tiles need to be develop. Each tile will have a double format of GeoJSON and PNG Images. The first will store the geometries explained on the previous log plus the addition of building vertices, together with that a PNG image will be compose to store the elevation data in useful way to make coherent. For that I will fetch the elevation for just the present vertices using [Mapzen’s elevation service](https://mapzen.com/documentation/elevation/elevation-service/) and construct voronoi tiled images from them.

![voronoi](imgs/02-voronoi.png) ![voronoi-zoom](imgs/02-voronoi-zoom.png)

The idea behind this approach is that vertices will fill ‘cells’ with a similar elevation. On the case of the buildings, all vertices should have the same height, and each cell of each corner will have the same value. This will work as a leveled “platform” for the building to rest with out distorting the roof elevation from the original.

![skyline](imgs/02-v-buildings.png)

Because I’m composing the elevation images for each tile we have way more control and curation on the data. This will allow to increase the resolution of the tile conform we zoom in. But still he have another to resolve first. Right now the elevation information is pass as a grayscale value, an the elevation range have to be hardcoded (look for ```ZMIN``` and ```ZMAX``` in the above code). If we are going to build tiles for the hole world we need a consistent way to pass this information rather than a 1 bit.

Checking with Kevin in charge of the Mapzen’s elevation service, the elevation data have a precession of 2 bit. A quick check on [wikipedia](https://en.wikipedia.org/wiki/Elevation), revel the highest and lower points on earth.

![](imgs/03-EarthHypso.png)

With an approximated range between 9000 to -12000 meters using to color channels (GB = 255*255 = 65025) will be enough to accommodate this range. This on the python script in charge of making the raster elevation tiles look like this:

```python
	elev_unsigned = 12000+elevation
	GREEN = math.floor(elev_unsigned/255)%255
	BLUE = math.floor(elev_unsigned%255)
``` 

This produce a image that looks like this:

![](imgs/03-colored_elevation.png)

On the vertex shader we will need to “decode” this value by doing:

```glsl
	vec3 elev_color = texture2D(u_terrain, st).rgb;
	float height = -12000.0+elev_color.g*65025.+elev_color.b*255.;

```

Finally and all together each tile is hable to compose something that looks like this:

![](imgs/03-landscape.png)

The creation of the necessary tiles could be done running the script followed by the OSM ID (default: `111968`) and ZOOM RANGE (default: `3-17`)

```bash
cd data
python makeATiles.py [OSM_ID] [ZOOM_RANGE]
```

## Building your own set of terrarium tiles

### Requirements

You should install the following Python modules:

- [SciPy](http://www.scipy.org/install.html)

- PIL

```bash
pip install pil
```

- [Requests](http://docs.python-requests.org/en/latest/user/install/#install)

```bash
pip install requests
```

- Shapely:

```bash
apt-get install libgeos++
pip install shapely 
```

If you are going to make A tiles (first approach described above) you should also install [GDAL](https://www.mapbox.com/tilemill/docs/guides/gdal/).

## Making terrarium tiles

```bash
cd ~
git clone —depth 1 https://github.com/patriciogonzalezvivo/terrarium.git
cd terrarium/data
python makeTiles.py 111968 3-17
```
