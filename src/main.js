// Author: @patriciogv 2015
var bMousePressed = false;
var offset_target = [0, 0, 16];
var offset = [0,0];
var timer = 0;
var waitFor = 180;
var gui;

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
        init();
    });

    return map;
}());

function init() {
    layer.on('init', function() {    
        window.setInterval("update(getCurrentTime())", 100);
        // Create dat GUI
        initGUI();
    });
    layer.addTo(map);

    if (window.DeviceMotionEvent) {
        window.addEventListener("devicemotion", onMotionUpdate, false);
    }

    document.addEventListener('mousemove', onMouseUpdate, false);
    // document.body.ondrag
    map.on('mousedown', function () {
        bMousePressed = true;
        offset_target[0] = .5;
        offset_target[1] = 0;
    });

    map.on('mouseup', function () {
        bMousePressed = false;
    });
}

function initGUI () {
    gui = new dat.GUI({ autoPlace: true, hideable: false, width: 300 });

    gui.domElement.parentNode.style.zIndex = 500; // make sure GUI is on top of map
    window.gui = gui;
    
    gui.water_height = 0;
    var water_height = gui.add(gui, 'water_height', -20, 300).name("Water level");
    water_height.onChange(function(value) {
        scene.styles.water.shaders.uniforms.u_water_height = value;
        scene.styles.elevate_ply.shaders.uniforms.u_water_height = value;
        scene.styles.elevate_lns.shaders.uniforms.u_water_height = value;
        scene.styles.elevate_cls.shaders.uniforms.u_water_height = value;
    });

    scene.config.layers['earth'].visible = false;
    scene.config.layers['wireframe'].visible = false;
    scene.rebuildGeometry();

    var layer_controls = {};
    Object.keys(scene.config.layers).forEach(function(l) {
        layer_controls[l] = !(scene.config.layers[l].visible == false);
        gui.add(layer_controls, l).
            onChange(function(value) {
                scene.config.layers[l].visible = value;
                scene.rebuildGeometry();
            });
    });
}

function update(time) {   // time in seconds since Jan. 01, 1970 UTC
    var speed = .0125;

    if (bMousePressed) {
        speed = .1;
    }

    if (timer === 0) {
        var d = new Date();
        var t = d.getTime()/1000;
        offset_target[0] = .5+Math.abs(Math.sin(t*0.025));
        offset_target[1] = Math.abs(Math.cos(t*0.025));
        offset_target[2] = 18+Math.sin(Math.PI*.25+t*0.02)*2.5;
    } else if (!bMousePressed) {
        offset_target[2] = map.getZoom();
        timer--;
    }

    var target = [(1-offset_target[1])*Math.PI/2., offset_target[0]*Math.PI];

    if (target[0] !== offset[0] || target[1] !== offset[1]) {
        offset[0] += (target[0] - offset[0])*speed;
        offset[1] += (target[1] - offset[1])*speed;
        scene.styles.elevate_ply.shaders.uniforms.u_offset = offset;
        scene.styles.elevate_lns.shaders.uniforms.u_offset = offset;
        scene.styles.elevate_cls.shaders.uniforms.u_offset = offset;
        scene.styles.water.shaders.uniforms.u_offset = offset;
    }

    // map.setZoom( map.getZoom()+(offset_target[2]-map.getZoom())*speed*0.5 );
}

// ============================================= SET/GET
function getCurrentTime() {   // time in seconds since Jan. 01, 1970 UTC
  return Math.round(new Date().getTime()/1000);
}

// ============================================= EVENT
function onMouseUpdate (e) {
    if (!bMousePressed) {
        offset_target[0] = e.pageX/screen.width;
        offset_target[1] = 1-(e.pageY/screen.height);
    }
    timer = waitFor;
}

function onMotionUpdate (e) {
    var accX = Math.round(event.accelerationIncludingGravity.x*10)/10;  
    var accY = Math.round(event.accelerationIncludingGravity.y*10)/10;  
    var motion = [ -accX,-accY ];

    if (scene.styles && motion[0] && motion[1] ) {
        offset_target[1] = motion[0]/10 + motion[1]/10;
    }
}