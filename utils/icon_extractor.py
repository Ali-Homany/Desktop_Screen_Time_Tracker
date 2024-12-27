import os
import io
from icoextract import IconExtractor
from PIL import Image
import svgwrite
import requests


def extract_icon(app_name: str, exe_path: str, output_path: str) -> str:
    output_path = os.path.join(output_path, f'{app_name}.ico')
    extractor = IconExtractor(exe_path)
    icon = extractor.get_icon()
    
    with open(output_path, 'wb') as icon_file:
        icon_file.write(icon.getvalue())
    print(f'Extracted Icon: {output_path}')
    return output_path

def ico_to_png(ico_file_path: str):
    """Convert ICO file to PNG."""
    with Image.open(ico_file_path) as img:
        png_path = ico_file_path.replace('.ico', '.png')
        img.save(png_path, format='PNG')
    return png_path

def png_to_svg(png_file_path: str, svg_file_path: str):
    """Convert PNG to SVG (simple representation, not vectorization)."""
    dwg = svgwrite.Drawing(svg_file_path)
    dwg.add(dwg.image(png_file_path, insert=(0, 0)))
    dwg.save()
    print(f'Saved SVG: {svg_file_path}')

def extract_website_icon(website_url: str, website_name: str, output_path: str) -> str:
    print(f'Extracting icon for {website_url}')
    base_icon_url = 'https://www.google.com/s2/favicons?domain='
    icon_url = base_icon_url + website_url
    response = requests.get(icon_url)
    if response.status_code == 200:
        image = Image.open(io.BytesIO(response.content))
        icon_path = os.path.join(output_path, f'{website_name}.ico')
        with open(icon_path, 'wb') as f:
            image.save(f, format='ICO')
        print(f'Extracted Icon: {icon_path}')
        return icon_path
    else:
        return 'Unknown'
