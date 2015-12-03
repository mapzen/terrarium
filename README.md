# Terrarium

## Process

### A Approach: One big image to rule them all 

My first approach was to download a heightmap from the [Shuttle Radar Topography Mission](http://www2.jpl.nasa.gov/srtm/) through [Derek Watkins’s](https://twitter.com/dwtkns) [tool](http://dwtkns.com/srtm30m/) and simply project the vertices on the vertex shader.

![Tile N37W123](imgs/00-heighmap.png)

Once I download the tile from [Derek Watkins’s](https://twitter.com/dwtkns) [tool](http://dwtkns.com/srtm30m/) I transforme it to:

```
wget http://e4ftl01.cr.usgs.gov/SRTM/SRTMGL1.003/2000.02.11/N37W123.SRTMGL1.hgt.zip

gdal_translate -ot Int16 -of PNG infile.hgt outfile.png
```

The first approach was to 

Data Source:

* 
* [OpenStreetMap](http://www.openstreetmap.org/)

* [Mapzen’s vector tiles](https://mapzen.com/projects/vector-tiles)


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
