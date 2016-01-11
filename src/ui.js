var UI;

function initUI() {
    var callback = function(v){ debug.innerHTML = v; }

    UI = new UIL.Gui('top:5px; right:10px;', 300, true);

    if (scene.config.styles['geometry-terrain'].shaders.uniforms['u_water_height'] !== undefined) {
        UI.add('slide',  { name:'sea level (m)', callback:setSeaLevel, min:-10, max:100, value:0, precision:0 });
    }
    
    UI.add('list', { name:'camera', callback:cameraChange, list:["orbit","manual","fix"]});

    if ( JSON.stringify(scene.background.color) === "[1,1,1,1]") {
        console.log('Load Light theme');
        loadCSS('css/light.css');
    }
 }

function loadCSS(filename) {
    var fileref = document.createElement("link")
    fileref.setAttribute("rel", "stylesheet")
    fileref.setAttribute("type", "text/css")
    fileref.setAttribute("href", filename)
    document.getElementsByTagName("head")[0].appendChild(fileref)
}

function cameraChange(v) {
    controls.camera = v;
    for (var ui of UI.uis) {
        if (ui.txt && ui.txt === "camera") {
            console.log("Force",v);
            ui.value = v;
        }
    }   
}

function setSeaLevel(value) {
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