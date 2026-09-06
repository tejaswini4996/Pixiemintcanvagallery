import os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

def create_directories():
    os.makedirs('static/images/paintings', exist_ok=True)
    os.makedirs('static/images/rooms', exist_ok=True)

def generate_artwork(filename, title, color_palette, art_type='faceless'):
    width, height = 800, 1000
    img = Image.new('RGB', (width, height), color=color_palette[0])
    draw = ImageDraw.Draw(img)
    
    if art_type == 'faceless':
        for i in range(height):
            r = int(color_palette[0][0] + (color_palette[1][0] - color_palette[0][0]) * (i / height))
            g = int(color_palette[0][1] + (color_palette[1][1] - color_palette[0][1]) * (i / height))
            b = int(color_palette[0][2] + (color_palette[1][2] - color_palette[0][2]) * (i / height))
            draw.line([(0, i), (width, i)], fill=(r, g, b))
            
        draw.ellipse([260, 220, 420, 420], fill=(45, 42, 38))
        draw.ellipse([280, 270, 400, 440], fill=(235, 195, 160))
        draw.polygon([(220, 440), (460, 440), (500, 850), (180, 850)], fill=color_palette[2])
        
        draw.ellipse([420, 260, 560, 440], fill=(30, 28, 25))
        draw.ellipse([440, 300, 540, 450], fill=(225, 185, 150))
        draw.polygon([(390, 450), (590, 450), (620, 880), (360, 880)], fill=color_palette[3])
        
    elif art_type == 'haldi':
        for i in range(height):
            r = int(255 - i * 0.05)
            g = int(190 + (i % 50))
            b = int(40 + (i % 20))
            draw.line([(0, i), (width, i)], fill=(min(255, r), min(255, g), min(255, b)))
            
        center_x, center_y = 400, 450
        for radius in range(300, 50, -30):
            col = (255, 215, 0) if radius % 60 == 0 else (218, 165, 32)
            draw.ellipse([center_x - radius, center_y - radius, center_x + radius, center_y + radius], outline=col, width=6)
            
        draw.ellipse([300, 380, 500, 580], fill=(255, 140, 0, 180))

    elif art_type == 'wedding':
        # Rich royal maroon & gold wedding portrait aesthetic
        for i in range(height):
            r = int(120 - i * 0.06)
            g = int(20 + (i % 30))
            b = int(35 + (i % 20))
            draw.line([(0, i), (width, i)], fill=(max(0, r), g, b))
            
        # Royal mandala & golden wedding portrait embellishments
        center_x, center_y = 400, 450
        for radius in range(320, 40, -40):
            draw.ellipse([center_x - radius, center_y - radius, center_x + radius, center_y + radius], outline=(244, 208, 63), width=5)
            
        # Groom & Bride ceremonial silhouette
        draw.ellipse([320, 260, 480, 440], fill=(244, 208, 63))
        draw.polygon([(260, 440), (540, 440), (580, 850), (220, 850)], fill=(180, 30, 50))

    # Canvas texture overlay
    texture = Image.new('RGBA', (width, height), (0,0,0,0))
    t_draw = ImageDraw.Draw(texture)
    for y in range(0, height, 4):
        t_draw.line([(0, y), (width, y)], fill=(255, 255, 255, 15))
    for x in range(0, width, 4):
        t_draw.line([(x, 0), (x, height)], fill=(0, 0, 0, 12))
        
    img = Image.alpha_composite(img.convert('RGBA'), texture).convert('RGB')
    img.save(f'static/images/paintings/{filename}', quality=95)
    print(f"Generated artwork: {filename}")

def generate_easel_rooms():
    rooms = [
        ('room_easel.jpg', (240, 238, 233), "Natural Pine Wooden Easel Stand"),
        ('room_table.jpg', (225, 228, 230), "Tabletop Display Easel"),
    ]
    for filename, bg_color, label in rooms:
        img = Image.new('RGB', (1200, 800), color=bg_color)
        draw = ImageDraw.Draw(img)
        
        table_y = 520
        draw.rectangle([0, table_y, 1200, 800], fill=(140, 100, 70))
        draw.line([(0, table_y), (1200, table_y)], fill=(100, 70, 45), width=6)
        
        draw.line([(600, 180), (420, 750)], fill=(160, 120, 80), width=18)
        draw.line([(600, 180), (780, 750)], fill=(160, 120, 80), width=18)
        draw.line([(600, 180), (600, 750)], fill=(110, 80, 50), width=14)
        draw.rectangle([380, 510, 820, 532], fill=(180, 135, 90))
        draw.rectangle([380, 510, 820, 516], fill=(130, 95, 60))
        
        img.save(f'static/images/rooms/{filename}', quality=95)

if __name__ == '__main__':
    create_directories()
    generate_artwork('faceless_couple.jpg', 'Faceless Illustration', [(245, 240, 235), (220, 205, 195), (160, 110, 90), (90, 120, 110)], 'faceless')
    generate_artwork('haldi_blessing.jpg', 'Magic Haldi Paintings', [(255, 220, 100), (255, 170, 0), (218, 165, 32), (184, 134, 11)], 'haldi')
    generate_artwork('wedding_portrait.jpg', 'Wedding Magic Portraits', [(120, 20, 35), (244, 208, 63), (180, 30, 50), (255, 230, 150)], 'wedding')
    generate_easel_rooms()
