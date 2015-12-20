// Author: @patriciogv 2015
var bMousePressed = false;
var gui;
var controls = {offset: [0.5,0], offset_target: [0.5, 0, 16], orbit: true, water_height: 0}


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
        scrollWheelZoom: 'center'
    });

    var style_file = 'styles/scene.yaml';
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
        scene: style_file,
        attribution: '<a href="https://mapzen.com/tangram" target="_blank">Tangram</a> | &copy; OSM contributors | <a href="https://mapzen.com/" target="_blank">Mapzen</a>'
    });

    window.layer = layer;
    var scene = layer.scene;
    window.scene = scene;

    map.setView(map_start_location.slice(0, 2), map_start_location[2]);
    var hash = new L.Hash(map);

    /***** Render loop *****/
    window.addEventListener('load', function () {
        init();
    });

    return map;
}());

function init() {
    layer.on('init', function() {    
        window.setInterval("update(getCurrentTime())", 100);
    });
    layer.addTo(map);

    if (window.DeviceMotionEvent) {
        window.addEventListener("devicemotion", onMotionUpdate, false);
    }

    document.addEventListener('mousemove', onMouseUpdate, false);
    // document.body.ondrag
    map.on('mousedown', function () {
        bMousePressed = true;
        orbitUpdate(false);
        controls.offset_target[0] = .5;
        controls.offset_target[1] = 0;
    });

    map.on('mouseup', function () {
        bMousePressed = false;
    });
}

function levelChange(value) {
    value *= 2.;
    for (var style in scene.styles) {
        if (scene.styles[style] &&
            scene.styles[style].shaders &&
            scene.styles[style].shaders.uniforms &&
            scene.styles[style].shaders.uniforms.u_water_height !== undefined) {
            scene.styles[style].shaders.uniforms.u_water_height = value;
        }
    }
    var displ = document.getElementById("level_display");
    displ.innerHTML = value.toFixed(1) + "m";
}

function orbitChange() {
    orbitUpdate(!controls.orbit);
}

function orbitUpdate(value) {
    controls.orbit = value;
    var button = document.getElementById("orbit_button");
    button.checked = controls.orbit;
}

function update(time) {   // time in seconds since Jan. 01, 1970 UTC
    var speed = .01;

    if (bMousePressed) {
        speed = .3;
    }

    if (controls.orbit) {
        var d = new Date();
        var t = d.getTime()/1000;
        controls.offset_target[0] = .5+Math.abs(Math.sin(t*0.025));
        controls.offset_target[1] = Math.abs(Math.cos(t*0.025));
        controls.offset_target[2] = 18+Math.sin(Math.PI*.25+t*0.02)*2.5;
    }

    var target = [(Math.PI/2.-controls.offset_target[1]*Math.PI/4.), controls.offset_target[0]*Math.PI];
    if (target[0] !== controls.offset[0] || target[1] !== controls.offset[1]) {
        controls.offset[0] += (target[0] - controls.offset[0])*speed;
        controls.offset[1] += (target[1] - controls.offset[1])*speed;      
        for (var style in scene.styles) {
            if (scene.styles[style] &&
                scene.styles[style].shaders &&
                scene.styles[style].shaders.uniforms &&
                scene.styles[style].shaders.uniforms.u_offset) {
                scene.styles[style].shaders.uniforms.u_offset = controls.offset;
            }
        }
    }

    // map.setZoom( map.getZoom()+(offset_target[2]-map.getZoom())*speed*0.5 );
}

// ============================================= SET/GET
function getCurrentTime() {   // time in seconds since Jan. 01, 1970 UTC
  return Math.round(new Date().getTime()/1000);
}

// ============================================= EVENT
function onMouseUpdate (e) {
    // if (!bMousePressed) {
    //     controls.offset_target[0] = 0.;//e.pageX/screen.width;
    //     controls.offset_target[1] = 1.;//(e.pageY/screen.height);
    // }
}

function onMotionUpdate (e) {
    var accX = Math.round(event.accelerationIncludingGravity.x*10)/10;  
    var accY = Math.round(event.accelerationIncludingGravity.y*10)/10;  
    var motion = [ -accX,-accY ];

    if (scene.styles && motion[0] && motion[1] ) {
        controls.offset_target[1] = motion[0]/10 + motion[1]/10;
    }
}