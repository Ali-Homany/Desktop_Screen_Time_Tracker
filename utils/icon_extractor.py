import os
from icoextract import IconExtractor
from PIL import Image
import svgwrite


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
