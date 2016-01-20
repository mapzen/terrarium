var UI;
var camera;
var uniforms = {};

function initUI() {
    const ui_height = 18;

    for (var style in scene.styles) {
        if (scene.styles[style].shaders.uniforms) {
            for (var uniform in scene.styles[style].shaders.uniforms) {
                var u = scene.styles[style].shaders.uniforms[uniform];
                if (uniform === 'u_offset') {
                    continue;
                }

                if ( u instanceof Array) {
                    uniforms[uniform] = { d: u.length, value: u};
                } else if ( typeof u === 'number') {
                    uniforms[uniform] = { d: 1, value: u };
                }
            }
        }
    }

    var height_total = 20;
    for (var uniform in uniforms) {
        height_total += ui_height + ui_height*uniforms[uniform].d;
    }
    height_total += ui_height;
    UI = new xgui({ width: 110, height: height_total, backgroundColor: "#dddddd", frontColor: "#444444", dimColor: "#dddddd" });

    var settingsDiv = document.getElementById('settings');
    settingsDiv.appendChild(UI.getDomElement());

    // adding camera
    var height = 5;
    var label = new UI.Label( {x: 5, y: height, text: "Camera:"} );
    height += ui_height;
    camera = new UI.DropDown( {x:5, y: height, values: ["orbit","manual","fix"] } );
    camera.value.bind(cameraChange);

    // Adding rest of the UI
    for (var uniform in uniforms) {
        height += ui_height;
        uniforms[uniform].label = new UI.Label( {x: 5, y: height, text: uniform + ":"} );
        if (uniforms[uniform].d === 1) {
            height += ui_height;
            uniforms[uniform].ui = new UI.HSlider( {x:5, y:height, value: uniforms[uniform].value, min:0, max:1} );
            uniforms[uniform].ui.value.bind(uniforms[uniform], "value");
            uniforms[uniform].ui.value.bind(updateUI);
        } else {
            uniforms[uniform].ui = [];
            for (var i = 0; i < uniforms[uniform].d; i++) {
                height += ui_height;
                uniforms[uniform].ui.push(new UI.HSlider( {x:5, y:height, value: uniforms[uniform].value[i], min:0, max:1} ));
                uniforms[uniform].ui[i].value.bind(uniforms[uniform].value, i);
                uniforms[uniform].ui[i].value.bind(updateUI);
            }
        }
    }
 }

function cameraChange(v) {
    controls.camera = v;
}

function updateUI(value) {
    for (var style in scene.styles) {
        if (scene.styles[style].shaders.uniforms) {
            for (var uniform in scene.styles[style].shaders.uniforms) {
                var variable = uniforms[uniform];
                if (variable) {
                    scene.styles[style].shaders.uniforms[uniform] = variable.value;
                }
            }
        }
    }
}