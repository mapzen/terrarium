
uniform sampler2D u_tex0;
uniform vec2 u_tex0Resolution;

uniform vec2 u_mouse;
uniform vec2 u_resolution;
uniform float u_time;

void main(){
    vec2 st = gl_FragCoord.xy/u_resolution.xy;
    vec2 pixel = 1./u_tex0Resolution;

    float center     = texture2D(u_tex0, st).r;
    float topLeft    = texture2D(u_tex0, st + vec2(-pixel.x, -pixel.y) ).r;
    float left       = texture2D(u_tex0, st + vec2(-pixel.x, 0.0) ).r;
    float bottomLeft = texture2D(u_tex0, st + vec2(-pixel.x, pixel.y) ).r;
    float top        = texture2D(u_tex0, st + vec2(0.0, -pixel.y) ).r;
    float bottom     = texture2D(u_tex0, st + vec2(0.0, pixel.y) ).r;
    float topRight   = texture2D(u_tex0, st + vec2(pixel.x, -pixel.y) ).r;
    float right      = texture2D(u_tex0, st + vec2(pixel.x, 0.0) ).r;
    float bottomRight= texture2D(u_tex0, st + vec2(pixel.x, pixel.y) ).r;
    
    float dX = topRight + 2.0 * right + bottomRight - topLeft - 2.0 * left - bottomLeft;
    float dY = bottomLeft + 2.0 * bottom + bottomRight - topLeft - 2.0 * top - topRight;
    
    vec3 N = normalize( vec3( dX, dY, 0.01) );
    
    N *= 0.5;
    N += 0.5;

	gl_FragColor.rgb = N;
	gl_FragColor.a = 1.;
}