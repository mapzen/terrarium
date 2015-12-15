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

After downloading and unzipping the tile from [Shuttle Radar Topography Mission](http://www2.jpl.nasa.gov/srtm/), I converted it to a PNG using [gdal](https://www.mapbox.com/tilemill/docs/guides/gdal/):

```bash
wget http://e4ftl01.cr.usgs.gov/SRTM/SRTMGL1.003/2000.02.11/N37W123.SRTMGL1.hgt.zip
tar xzvf N37W123.SRTMGL1.hgt.zip
gdal_translate -ot Int16 -of PNG N37W123.hgt N37W123.png
```

Downloading and inspecting the [JSON file with the bounding boxes](http://dwtkns.com/srtm30m/srtm30m_bounding_boxes.json) from [Derek Watkins’s](https://twitter.com/dwtkns) [tool](http://dwtkns.com/srtm30m/), I determine the boundaries of that tile. Which then I export to webmercator:

```
[-13692328.289900804, -13580946.954451224, 4439068.068371599, 4579465.0539420955]
```

Later I feed this values into a vertex shader on [Mapzen’s Map Engine](https://github.com/tangrams/tangram) together with a ```MINZ``` and ```MAXZ``` for the elevation range:

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

In the code above you can see how I’m checking if the vertex is inside the zone for where I have elevation data. If that’s true it extrudes the vertices.

![just earth](imgs/00-earth-orig.png)

Sometimes the polygons that form the ```earth``` layer on OSM don’t have enough subdivisions and the vertices are extruded in a way that hides important features like roads and buildings, as seen in the image below.

![errors](imgs/00-earth.png)

To fix this I generate a custom set of plane tiles with subdivisions on important corners (coming from polygons and lines from OSM ```earth```, ```roads``` and ```landuse``` layers)

![subdivitions](imgs/00-subdivision.png)

By breaking the tiles into small fragments, the extrusion of the terrain doesn’t hide the geometry.

![terrain](imgs/00-terrain.png)

Running this script using the USGS ID (default: `N37W123`) and zoom levels (default: `3-17`) will create the necessary tiles:

```bash
cd data
python makeATiles.py [USGS_ID] [ZOOM_RANGE]
```

Once the tiles are done and you look at the map in higher zoom levels, a new problem might emerge: 

![buildings error](imgs/01-buildings.png)

The top of the buildings have been extruded according to the heightmap, but in a incongruent way. To fix this issue we developed a new approach.


### Approach B: an image per tile

#### Data Sources

* [Mapzen’s elevation data](https://mapzen.com/documentation/elevation/elevation-service/)

* [OpenStreetMap](http://www.openstreetmap.org/)

* [Mapzen’s vector tiles](https://mapzen.com/projects/vector-tiles)

#### Log

In order to solve the incongruence on building extrusion I thought it would be beneficial to have control over the heightmap. For that, we need to develop a new set of tiles. Each tile will have a double format of both GeoJSON and PNG images. The first will store the geometries explained on the previous section, plus the addition of building vertices, together with a PNG image that stores the elevation data in a useful and coherent way. For that I will fetch the elevation for just the present vertices using [Mapzen’s elevation service](https://mapzen.com/documentation/elevation/elevation-service/) and construct Voronoi tiled images from them.

![voronoi](imgs/02-voronoi.png) ![voronoi-zoom](imgs/02-voronoi-zoom.png)

The idea behind this approach is that vertices will fill ‘cells’ with a similar elevation. In the case of the buildings, all vertices should have the same height, and each cell of each corner will have the same value. This will work as a leveled “platform” for the building to rest upon, with out distorting the original roof elevation.

![skyline](imgs/02-v-buildings.png)

Because I’m composing the elevation images for each tile, we have way more control and curation of the data. This will allow us to increase the resolution and precision of the tile as we zoom in. But we still have another issue to resolve: Right now the elevation information is passed as a grayscale value, but the elevation range has to be hardcoded (look for ```ZMIN``` and ```ZMAX``` in the above code). If we are going to build tiles for the whole world we need a consistent way to pass this information rather than as a 1 bit value.

Checking with [Kevin](https://twitter.com/kevinkreiser) who is in charge of Mapzen’s elevation service, the elevation data have a precision of 2 bits. A quick check on [wikipedia](https://en.wikipedia.org/wiki/Elevation) reveals the highest and lowest points on earth.

![](imgs/03-EarthHypso.png)

With an approximate range of 9000 to -12000 meters, color channels (GB = 255*255 = 65025) can accommodate this data range. The python script in charge of making the raster elevation tiles now looks like this...

```python
	elev_unsigned = 12000+elevation
	GREEN = math.floor(elev_unsigned/255)%255
	BLUE = math.floor(elev_unsigned%255)
``` 

which produces a image that looks like this:

![](imgs/03-colored-elevation.png) ![](imgs/03-colored-elevation-zoom.png)

On the vertex shader we will need to “decode” this value:

```glsl
	vec3 elev_color = texture2D(u_terrain, st).rgb;
	float height = -12000.0+elev_color.g*65025.+elev_color.b*255.;

```

Putting it all together, each tile is rendered into something that looks like this!

![](imgs/03-landscape.png)

The necessary tiles can be created by running the script with the OSM ID (default: `111968`) and ZOOM RANGE (default: `3-17`)

```bash
cd data
python makeATiles.py [OSM_ID] [ZOOM_RANGE]
```

### Parallel explorations

#### Normalmap

![](imgs/04-normalmap.png)

It is possible to illuminate the surface of the terrain by adding "normal" information to [Tangram](https://github.com/tangrams/tangram)’s light engine. (The [normal](https://mapzen.com/documentation/tangram/Materials-Overview/#normals) of a polygon is a three-dimensional vector describing the direction that it is considered to be facing, which affects the color and shininess of the polygon.)


We can make the NormalMap using the HeightMap we got from the [Shuttle Radar Topography Mission](http://www2.jpl.nasa.gov/srtm/) using GIMP or the Tangram shader [here](https://github.com/patriciogonzalezvivo/terrarium/blob/master/data/normal.frag) using [glslViewer](https://github.com/patriciogonzalezvivo/glslViewer) like this:

```bash
cd data/
glslViewer normal.frag A/N37W123.png -o A/N37W123-normal.png
```

On the fragment shader we can use the following function to retrieve the normal values for each point...

```glsl
vec3 getNormal(vec2 position) {
	vec2 worldPos = u_map_position.xy + position.xy;
	if (inZone(worldPos)) {
		vec2 st = vec2(0.0);
		st.x = (worldPos.x-XMIN)/(XMAX-XMIN);
		st.y = (worldPos.y-YMIN)/(YMAX-YMIN);
		return texture2D(u_normalmap, st).rgb*2.-1.;
	} else {
		return vec3(0.,0.,1.);
	}
}
```

and then use it on the YAML scene to modify the normals on the fragment shader:

```yaml
	normal: |
		normal.gb = getNormal(v_orig_pos.xy);
```

Once the terrain is "lit", the terrain looks like this:

![enlighten terrain](imgs/04-terrain-normals.png)

#### Under water

Using the bounding box of the image we downloaded from Shuttle Radar Topography Mission](http://www2.jpl.nasa.gov/srtm/), I can construct a big rectangular polygon in which to draw the water level.

I use a [Spherical Environmental Map](http://www.ozone3d.net/tutorials/glsl_texturing_p04.php) on it together with some fragment shader code to disturb the normals using a regular simplex noise function to make it look more "natural".

![SEM](imgs/sem-sky-0001.jpg)

The code for this ```water``` is the following:

```yaml
    water:
        base: polygons
        animated: true
        mix: [geometry-matrices, filter-grain]
        blend: inlay
        material:
            ambient: .7
            diffuse:
                texture: ../imgs/sem-sky-0001.jpg
                mapping: sphere map
        shaders:
            uniforms:
                u_offset: [0, 0]
                u_water_height: 0.
            blocks:
                position: |
                    position.z += u_water_height;
                    position.xyz = rotateX3D(abs(cos(u_offset.x))*1.3) * rotateZ3D(cos(u_offset.y)*1.57075) * position.xyz;
                normal: |
                    normal += snoise(vec3(worldPosition().xy*0.08,u_time*.5))*0.02;
                filter: |
                    color.a *= .9;
```

Then on the rest of the geometry I apply the following [caustic filter](https://en.wikipedia.org/wiki/Caustic_(optics)) to everything that above the water level. 

```yaml

        shaders:
            defines:
                TAU: 6.28318530718
                MAX_ITER: 3
            blocks:
                global: |
                    // Caustic effect from https://www.shadertoy.com/view/4ljXWh
                    vec3 caustic (vec2 uv) {
                        vec2 p = mod(uv*TAU, TAU)-250.0;
                        float time = u_time * .5+23.0;
                        vec2 i = vec2(p);
                        float c = 1.0;
                        float intent = .005;
                        for (int n = 0; n < int(MAX_ITER); n++) {
                            float t = time * (1.0 - (3.5 / float(n+1)));
                            i = p + vec2(cos(t - i.x) + sin(t + i.y), sin(t - i.y) + cos(t + i.x));
                            c += 1.0/length(vec2(p.x / (sin(i.x+t)/inten),p.y / (cos(i.y+t)/inten)));
                        }
                        c /= float(MAX_ITER);
                        c = 1.17-pow(c, 1.4);
                        vec3 color = vec3(pow(abs(c), 8.0));
                        color = clamp(color + vec3(0.0, 0.35, 0.5), 0.0, 1.0);
                        color = mix(color, vec3(1.0,1.0,1.0),0.3);
                        return color;
                    }
                     
                filter: |
										vec2 wordPos = u_map_position.xy + v_orig_pos.xy;
                    if (inZone(wordPos) && ZMIN+height*(ZMAX-ZMIN)+worldPosition().z < u_water_height) {
                        color.gb += caustic(worldPosition().xy*0.005)*0.2;
                    }
```

All of this makes the water looks like this:

![under water](imgs/05-underwater.png)

This together with a slider updating the position of the uniform ```u_water_height``` allows a nice interactive animation of  the sea levels rising:

![flood](imgs/05-flood.gif)


### DONE’s

- Faster voronoi algorithm: right now each B Tile takes almost a minute to calculate! Kevin offered to make a C program to do that. https://github.com/mapzen/terrarium/pull/2

### TODO’s

- Implement a texture per tile method on Tangram

- Add more vertices to compute on the GeoJson geometry tiles using contours lines, so we are sure there is enough information to cover non urban areas.

- Under zoom level 12, geoJSON tiles are too big (~10mb in the worst scenario). These zoom levels may not need so much definition for the terrain geometry. Simplifing data coming from elevation contours and heightmap/normalmap may be enough. Contour/roads data is enough until between 1-14 as the buildings are too small to be visible. Or maybe just heightmap/normalmap is enough as users don’t really see the terrain under 12.
 
## Building your own set of terrarium tiles

### Requirements

You should install the following Python modules:

- [SciPy](http://www.scipy.org/install.html)

- PIL

```bash
sudo pip install pil
```

- [Requests](http://docs.python-requests.org/en/latest/user/install/#install)

```bash
sudo pip install requests
```

- NumPy:

```bash
sudo pip install numpy
```

- OpenCV for python:

```bash
sudo apt-get install python-opencv
```

- Shapely:

```bash
sudo apt-get install libgeos++
sudo pip install shapely 
```

If you are going to make A tiles (the first approach, described at the top of this post) you should also install [GDAL](https://www.mapbox.com/tilemill/docs/guides/gdal/).

## Making terrarium tiles

```bash
cd ~
git clone —depth 1 https://github.com/patriciogonzalezvivo/terrarium.git
cd terrarium/data
python makeTiles.py 111968 3-17
```

## How work on this?

- [Patricio Gonzalez Vivo](https://twitter.com/patriciogv): Came up with the first round of A and B tiles ideas

- [Kevin Kreiser](https://twitter.com/kevinkreiser): improve the voronoi algorithm to rasterize B tiles faster

- [Rob Marianski](https://twitter.com/rmarianski): help us with his python tiling magic
 
