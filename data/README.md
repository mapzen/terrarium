
 
## Building your own set of terrarium tiles

### Install

```bash
cd ~
git clone —depth 1 https://github.com/mapzen/terrarium.git
cd terrarium
./install.sh
```

### Making tiles

```makeBTiles.py``` require a OSM ID of the place you want to make tiles for it. To get this id go to [openStreetMap](http://www.openstreetmap.org/) and type the name of a city, and search for the number between ```(``` ```)```.

![](imgs/10-OSM.png)

Then pass this number as the first argument of the script, while the third argument is the range of zoom you are interested

```bash
cd data
python makeBTiles.py 111968 3-17
```

#### List of places and OSM_ID

[20 Cities With The Most To Lose From Rising Seas:](http://www.weather.com/science/environment/news/20-cities-most-lose-rising-sea-levels-20130822)

* Nagoya: 4576938
* Xiamen: 244082165
* Bangkok: 92277
* Boston: 2315704
* Saint Petersburg: 421007
* Zhenjiang: 244083006
* Surat: 1952514
* Chennai: 3233393892
* Abidjan: 3377982
* Jakarta: 29939632
* New Orleans: 131885
* Ho Chi Minh City: 1973756
* New York City: 175905
* Tianjin: 912999
* Miami: 1216769
* Guayaquil: 3652281
* Kolkata: 1971802
* Mumbai: 16173235
* Guangzhou City: 3287346


Others:

* Cape Town: 32675806
* Bangladesh: 184640
* Marshall Islands: 571771
* Japan: 382313
* Lima: 1944670
* San Francisco: 111968
* Rio de Janeiro: 2697338
* Seoul: 2297418
* Cairo: 5466227
* Paris: 7444
* Istanbul: 1882099475
* Buenos Aires: 1224652
* London: 65606
* Barcelona: 347950
* Los Angeles: 207359
