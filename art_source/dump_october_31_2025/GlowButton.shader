
shader_type canvas_item;

uniform vec4 base_color : source_color = vec4(0.11, 0.15, 0.19, 1.0); // #1c2730
uniform vec4 edge_glow_color = vec4(0.12, 0.76, 0.70, 1.0);           // teal
uniform vec4 inner_gloss_color = vec4(1.0, 1.0, 1.0, 0.18);
uniform float corner = 0.18;       // 0..0.5 corner radius as fraction of min(width,height)
uniform float glow = 0.25;         // outer glow intensity
uniform float gloss_height = 0.35; // percent height for specular strip

// Rounded-rect distance field
float sdRoundRect(vec2 p, vec2 b, float r){
    vec2 q = abs(p) - b + vec2(r);
    return length(max(q, 0.0)) + min(max(q.x, q.y), 0.0) - r;
}

void fragment(){
    vec2 uv = UV;
    vec2 size = vec2(textureSize(TEXTURE, 0));
    vec2 px = (uv * size);
    vec2 half = size * 0.5;
    float radius = min(size.x, size.y) * corner;

    // Signed distance for rounded rect
    float d = sdRoundRect(px - half, half - vec2(1.0), radius);

    // Base fill
    vec4 col = base_color;

    // Bevel: top highlight, bottom shadow
    float ny = (px.y / size.y);
    col.rgb += smoothstep(0.0, 0.15, 1.0 - ny) * 0.06;
    col.rgb -= smoothstep(0.8, 1.0, ny) * 0.08;

    // Edge neon glow (outside)
    float edge = smoothstep(1.5, 0.0, d);
    vec3 glow_col = edge_glow_color.rgb * glow;
    col.rgb += glow_col * edge * 0.6;

    // Inner specular strip (under-glass)
    float gloss = smoothstep(0.0, gloss_height, ny) * smoothstep(gloss_height, gloss_height-0.08, ny);
    col.rgb = mix(col.rgb, inner_gloss_color.rgb, inner_gloss_color.a * gloss);

    // Clip outside rounded rect
    if (d > 0.5) discard;

    COLOR = col;
}
