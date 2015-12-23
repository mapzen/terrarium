function initUI() {
    var hud = document.getElementById("hud");

    if ( scene.config.styles['geometry-terrain'].shaders.uniforms['u_water_height'] !== undefined ) {
        hud.innerHTML += '  <div id="level">' +
                         '      <div id="level_display">0.0m</div>' +
                         '      <input id="level_range" type="range" min="0" max="32" step="1" value="0" oninput="levelChange(this.value)" onchange="levelChange(this.value)"/>' +
                         '  </div>';
    }
    
    addButton("orbit");
    addButton("manual");

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

// =================================================== BUTTON
function addButton(name) {
    var hud = document.getElementById("hud");
    var value = getControl(name);
    if (value) {
        value += ' checked';
    } else {
        value = '';
    }

    hud.innerHTML += '<div id="'+name+'" class="button"> <input type="checkbox" name="checkbox-option" id="button_'+name+'" class="hide-checkbox" value="'+name+'" '+value+'> <label onclick="onButtonClick(this)">'+name+'</label> </div>';
}

function setControl(name, value) {
    controls[name] = value;
    var button = document.getElementById("button_"+name);
    if (button !== undefined) {
        button.checked = controls[name];
    }
}

function getControl(name) {
    return controls[name];
}

function onButtonClick(button) {
    setControl(button.innerHTML,!getControl(button.innerHTML));

    if (button.innerHTML === "manual") {
        setControl("orbit",false);
    } else  if (button.innerHTML === "orbit") {
        setControl("manual",false);
    }
}