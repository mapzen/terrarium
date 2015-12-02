# Terrarium

## Process

### Plan A: One Image to rule them all 

Data Source:

* [Shuttle Radar Topography Mission](http://www2.jpl.nasa.gov/srtm/) fascilitaded by [this project](http://dwtkns.com/srtm30m/) of [Derek Watkins](https://twitter.com/dwtkns)

* [OpenStreetMap](http://www.openstreetmap.org/)

* [Mapzen’s vector tiles](https://mapzen.com/projects/vector-tiles)


### Plan B: a image per tile

Data Source:

* [Mapzen’s elevation data](https://mapzen.com/documentation/elevation/elevation-service/)

* [OpenStreetMap](http://www.openstreetmap.org/)

* [Mapzen’s vector tiles](https://mapzen.com/projects/vector-tiles)

## Requirements

- Install [Requests](http://docs.python-requests.org/en/latest/user/install/#install)

```bash
pip install requests
```

- Install Shapely:

```bash
pip install shapely 
```

## Terrain Tiles building process

```bash
cd src/
./makeTiles.py 111968 3-17
```
