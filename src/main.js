// ============================================= INIT 
// Prepair leafleat and tangram
map = (function () {
    'use strict';

    var map_start_location = [37.7938, -122.3490, 14];
    /*** URL parsing ***/
    var url_hash = window.location.hash.slice(1).split('/');
    if (url_hash.length == 3) {
        map_start_location = [url_hash[1],url_hash[2], url_hash[0]];
        map_start_location = map_start_location.map(Number);
    }
    
    // Leaflet Map
    var map = L.map('map',{
        trackResize: true,
        keyboard: false,
        maxZoom: 18,
        scrollWheelZoom: 'center'
    });

    var style_file = 'default.yaml';
    var url_search = window.location.search.slice(1);
    if (url_search.length > 0) {
        var ext = url_search.substr(url_search.lastIndexOf('.') + 1);
        if (ext == "yaml" || ext == "yaml/") {
            style_file = url_search;
            console.log('LOADING' + url_search + ' STYLE');
        } else {
            style_file = url_search+'.yaml';
            console.log('LOADING' + url_search + ' STYLE');
        }
    }

    // Tangram Layer
    var layer = Tangram.leafletLayer({
        scene: "styles/"+style_file,
        attribution: '<a href="https://twitter.com/patriciogv" target="_blank">@patriciogv</a> | <a href="https://mapzen.com/tangram" target="_blank">Tangram</a> | <a href="https://mapzen.com/" target="_blank">Mapzen</a> | &copy; OSM contributors'
    });

    window.layer = layer;
    var scene = layer.scene;
    window.scene = scene;

    map.setView(map_start_location.slice(0, 2), map_start_location[2]);
    var hash = new L.Hash(map);

    /***** Render loop *****/
    window.addEventListener('load', function () {
        layer.addTo(map);
    });

    return map;
}());