var UI;
var camera;
var slider;

function initUI() {
    var isSeaLevel = false;
    var height_total = 25;

    if (scene.config.styles['geometry-terrain'].shaders.uniforms['u_water_height'] !== undefined) {
        isSeaLevel = true;
        height_total = 220;
    }

    UI = new xgui({ width: 110, height: height_total, backgroundColor: "#dddddd", frontColor: "#444444", dimColor: "#dddddd" });

    var settingsDiv = document.getElementById('settings');
    settingsDiv.appendChild(UI.getDomElement());

    camera = new UI.DropDown( {x:5, y: 5, values: ["orbit","manual","fix"] } );
    camera.value.bind(cameraChange);

    if (isSeaLevel) {
        slider = new UI.VSlider( {x:30, y:30, width: 50, height: 180, value: controls.water_height, min:-10, max:100} );
        slider.value.bind(setSeaLevel);
    }
    

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
}