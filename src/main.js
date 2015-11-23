// Author: @patriciogv 2015

// ============================================= INIT 
// Prepair leafleat and tangram
map = (function () {
    'use strict';

    var map_start_location = [0, 0, 3];
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
        scrollWheelZoom: 'center'
    });

    // Tangram Layer
    var layer = Tangram.leafletLayer({
        scene: 'scene.yaml',
        attribution: '<a href="https://twitter.com/patriciogv" target="_blank">@patriciogv</a> | <a href="https://mapzen.com/tangram" target="_blank">Tangram</a> | &copy; OSM contributors | <a href="https://mapzen.com/" target="_blank">Mapzen</a>'
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

