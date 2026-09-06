import os
from PIL import Image, ImageDraw, ImageColor, ImageFilter

def render_canvas_in_room(artwork_path, room_filename, wall_color_hex, scale_factor=1.0):
    """
    Renders canvas painting resting on a wooden easel stand.
    """
    if not os.path.exists(artwork_path):
        artwork_path = os.path.join('static', 'images', 'paintings', 'faceless_couple.jpg')

    room_path = os.path.join('static', 'images', 'rooms', room_filename)
    if not os.path.exists(room_path):
        room_path = os.path.join('static', 'images', 'rooms', 'room_easel.jpg')

    # Load background with wooden easel stand
    room_img = Image.open(room_path).convert('RGB')
    rw, rh = room_img.size

    # Tint backdrop wall if requested
    if wall_color_hex and wall_color_hex != '#F0EEEA':
        try:
            target_rgb = ImageColor.getrgb(wall_color_hex)
            wall_mask = Image.new('L', (rw, rh), 0)
            w_draw = ImageDraw.Draw(wall_mask)
            w_draw.rectangle([0, 0, rw, 520], fill=255)
            
            wall_layer = Image.new('RGB', (rw, rh), target_rgb)
            room_img = Image.composite(wall_layer, room_img, wall_mask)
        except Exception as e:
            print(f"Backdrop tint warning: {e}")

    # Load and resize artwork
    art_img = Image.open(artwork_path).convert('RGB')
    
    base_width = int(320 * scale_factor)
    base_height = int(400 * scale_factor)
    art_resized = art_img.resize((base_width, base_height), Image.Resampling.LANCZOS)

    canvas_w = base_width
    canvas_h = base_height

    canvas_layer = Image.new('RGBA', (canvas_w, canvas_h), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(canvas_layer)

    # 3D canvas side edge depth (thick gallery wrap canvas)
    c_draw.rectangle([0, 0, canvas_w, canvas_h], fill=(255, 255, 255))
    canvas_layer.paste(art_resized, (0, 0))

    # Drop shadow behind easel canvas
    shadow = Image.new('RGBA', (rw, rh), (0, 0, 0, 0))
    s_draw = ImageDraw.Draw(shadow)
    
    center_x = rw // 2
    center_y = int(rh * 0.42)
    top_left_x = center_x - canvas_w // 2
    top_left_y = center_y - canvas_h // 2
    
    s_draw.rectangle(
        [top_left_x + 8, top_left_y + 12, top_left_x + canvas_w + 12, top_left_y + canvas_h + 16],
        fill=(0, 0, 0, 80)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(12))

    # Composite room + shadow + easel canvas
    room_rgba = room_img.convert('RGBA')
    room_shadowed = Image.alpha_composite(room_rgba, shadow)
    room_shadowed.paste(canvas_layer, (top_left_x, top_left_y), canvas_layer)

    preview_filename = f"preview_rendered.jpg"
    out_dir = os.path.join('static', 'images', 'temp')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, preview_filename)
    room_shadowed.convert('RGB').save(out_path, quality=90)

    return f"/static/images/temp/{preview_filename}"
