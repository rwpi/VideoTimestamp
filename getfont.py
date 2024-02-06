import matplotlib.font_manager
import os

def get_system_config():
    # Get a list of all system fonts
    system_fonts = matplotlib.font_manager.findSystemFonts(fontpaths=None, fontext='ttf')
    # Try to find Arial among the system fonts
    arial_font = next((font for font in system_fonts if 'arial' in os.path.basename(font).lower()), None)
    # If Arial is not found, try to find DejaVu Sans
    if not arial_font:
        arial_font = next((font for font in system_fonts if 'dejavusans' in os.path.basename(font).lower()), None)
    # If DejaVu Sans is not found, try to find Liberation Sans
    if not arial_font:
        arial_font = next((font for font in system_fonts if 'liberationsans' in os.path.basename(font).lower()), None)
    # If Liberation Sans is not found, try to find Times New Roman
    if not arial_font:
        arial_font = next((font for font in system_fonts if 'times' in os.path.basename(font).lower()), None)
    # If Times New Roman is not found, try to find the first available font with "serif" in the name
    if not arial_font:
        arial_font = next((font for font in system_fonts if 'serif' in os.path.basename(font).lower()), None)
    # If no serif font is found, use the first available system font
    font_path = arial_font if arial_font else system_fonts[0]
    return font_path