#!/usr/bin/env python3
"""
QR Code Generator with Custom Colors, Logos, Borders, and Anti-aliasing.

Usage Examples:
    # Basic usage:
    python3 qr_generator.py "https://example.com" output.png

    # With colors, logo, and a rounded logo border:
    python3 qr_generator.py "https://example.com" custom_qr.png \
        --fg-color "#1a1a2e" \
        --bg-color "#f5f5f0" \
        --logo "my_logo.png" \
        --logo-border-color "#FF05FF" \
        --logo-border-width 4 \
        --logo-border-radius 12

    # As dots instead of squares (with a specific output size):
    python3 qr_generator.py "https://example.com" dotted_qr.png --dots --size 512
"""

import argparse
import base64
from io import BytesIO
from qrcodegen import QrCode
from PIL import Image, ImageDraw

def parse_color(color) -> tuple:
    """Accept a hex string ('#FF05FF') or an RGB/RGBA tuple, returns RGBA tuple."""
    if isinstance(color, str):
        color = color.lstrip("#")
        if len(color) == 6:
            r, g, b = int(color[0:2], 16), int(color[2:4], 16), int(color[4:6], 16)
            return (r, g, b, 255)
        elif len(color) == 8:
            r, g, b, a = (int(color[i:i+2], 16) for i in (0, 2, 4, 6))
            return (r, g, b, a)
        else:
            raise ValueError(f"Invalid hex color: #{color}")

    if len(color) == 3:
        return color + (255,)
    return tuple(color)

def rounded_rect_mask(width: int, height: int, radius: int) -> Image.Image:
    """Return an 'L'-mode mask with a filled rounded rectangle."""
    mask = Image.new("L", (width, height), 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle((0, 0, width - 1, height - 1), radius=radius, fill=255)
    return mask

def is_finder_pattern_module(row: int, col: int, module_count: int) -> bool:
    """True for modules inside one of the three 8x8 corner finder-pattern
    blocks (the position markers scanners lock onto first). These must stay
    solid squares even in dotted mode -- stylizing them breaks detection."""
    in_top = row < 8
    in_bottom = row >= module_count - 8
    in_left = col < 8
    in_right = col >= module_count - 8
    return (in_top and in_left) or (in_top and in_right) or (in_bottom and in_left)

def generate_custom_qr(
    data: str,
    filename: str = None,
    scale: int = 10,
    output_size: int = None,
    border: int = 4,
    fg_color="#000000",
    bg_color="#ffffff",
    logo_path: str = None,
    logo_border_width: int = 0,
    logo_border_color="#ffffff",
    logo_border_radius: int = 0,
    dots: bool = False,
) -> Image.Image:

    fg_rgba = parse_color(fg_color)
    bg_rgba = parse_color(bg_color)
    border_rgba = parse_color(logo_border_color)

    qr = QrCode.encode_text(data, QrCode.Ecc.HIGH)
    module_count = qr.get_size()

    # Calculate actual scale if a target output pixel size is requested
    if output_size:
        # Ensures the scale is at least 1 so it doesn't break on massive strings with small targets
        scale = max(1, output_size // (module_count + border * 2))

    clear_modules = 0
    min_clear, max_clear = -1, -1

    if logo_path:
        clear_modules = int(module_count * 0.35)
        center_idx = module_count // 2
        min_clear = center_idx - (clear_modules // 2)
        max_clear = center_idx + (clear_modules // 2)

    img_size = (module_count + border * 2) * scale

    # ----- SUPERSAMPLING LOGIC FOR RASTER ANTI-ALIASING -----
    # We draw at a much larger size (4x) and shrink it down so curves look perfectly smooth.
    ss_factor = 4 if dots else 1
    ss_scale = scale * ss_factor
    ss_img_size = img_size * ss_factor
    
    ss_img = Image.new("RGBA", (ss_img_size, ss_img_size), bg_rgba)
    draw = ImageDraw.Draw(ss_img)
    ss_dot_gap = ss_scale * 0.1

    for row in range(module_count):
        for col in range(module_count):
            if logo_path and (min_clear <= row <= max_clear) and (min_clear <= col <= max_clear):
                continue

            if qr.get_module(col, row):
                x0 = (col + border) * ss_scale
                y0 = (row + border) * ss_scale
                x1 = x0 + ss_scale
                y1 = y0 + ss_scale

                if dots and not is_finder_pattern_module(row, col, module_count):
                    draw.ellipse(
                        [x0 + ss_dot_gap, y0 + ss_dot_gap, x1 - ss_dot_gap, y1 - ss_dot_gap],
                        fill=fg_rgba,
                    )
                else:
                    draw.rectangle([x0, y0, x1 - 1, y1 - 1], fill=fg_rgba)

    # Downscale the supersampled image back to the target size for crisp edges
    if ss_factor > 1:
        img = ss_img.resize((img_size, img_size), Image.Resampling.LANCZOS)
    else:
        img = ss_img
    # ---------------------------------------------------------

    logo_svg_tag = None
    if logo_path:
        try:
            cleared_pixel_size = ((max_clear - min_clear) + 1) * scale
            logo = Image.open(logo_path).convert("RGBA")
            max_logo_size = cleared_pixel_size - (logo_border_width * 2)
            logo.thumbnail((max_logo_size, max_logo_size), Image.Resampling.LANCZOS)

            logo_frame = Image.new("RGBA", (cleared_pixel_size, cleared_pixel_size), (0, 0, 0, 0))

            if logo_border_width > 0:
                border_bg = Image.new("RGBA", (cleared_pixel_size, cleared_pixel_size), border_rgba)
                if logo_border_radius > 0:
                    mask = rounded_rect_mask(cleared_pixel_size, cleared_pixel_size, logo_border_radius)
                    border_bg.putalpha(mask)
                logo_frame.paste(border_bg, (0, 0), border_bg)

            logo_w, logo_h = logo.size
            logo_x = (cleared_pixel_size - logo_w) // 2
            logo_y = (cleared_pixel_size - logo_h) // 2
            logo_frame.paste(logo, (logo_x, logo_y), logo)

            pos_x = (min_clear + border) * scale
            pos_y = (min_clear + border) * scale

            img.paste(logo_frame, (pos_x, pos_y), logo_frame)

            # Generate base64 tag for SVG embedding
            buffered = BytesIO()
            logo_frame.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            logo_svg_tag = f'<image href="data:image/png;base64,{img_str}" x="{pos_x}" y="{pos_y}" width="{cleared_pixel_size}" height="{cleared_pixel_size}"/>'

        except Exception as e:
            print(f"Warning: Could not process logo. Generating base QR code. Error: {e}")

    # --- MULTI-FORMAT SAVING LOGIC (skipped when filename is None, e.g. GUI previews) ---
    if not filename:
        return img

    ext = filename.lower().split('.')[-1]

    if ext in ['jpg', 'jpeg']:
        # Convert RGBA to RGB for JPEG compatibility using the background color
        rgb_img = Image.new("RGB", img.size, bg_rgba[:3])
        rgb_img.paste(img, mask=img.split()[3])
        rgb_img.save(filename)

    elif ext == 'svg':
        # Construct Raw SVG XML (Vector scaling ensures dots are perfectly round regardless of supersampling)
        svg_parts = [
            '<?xml version="1.0" encoding="UTF-8"?>',
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {img_size} {img_size}" version="1.1">'
        ]

        bg_hex = f"#{bg_rgba[0]:02x}{bg_rgba[1]:02x}{bg_rgba[2]:02x}"
        fg_hex = f"#{fg_rgba[0]:02x}{fg_rgba[1]:02x}{fg_rgba[2]:02x}"

        # Add background rect
        svg_parts.append(f'  <rect width="100%" height="100%" fill="{bg_hex}"/>')

        # Recalculate original gap for accurate SVG mapping
        dot_gap = scale * 0.1

        if dots:
            radius = (scale - 2 * dot_gap) / 2
            path_d = []
            for row in range(module_count):
                for col in range(module_count):
                    if logo_path and (min_clear <= row <= max_clear) and (min_clear <= col <= max_clear):
                        continue
                    if not qr.get_module(col, row):
                        continue
                    if is_finder_pattern_module(row, col, module_count):
                        x = (col + border) * scale
                        y = (row + border) * scale
                        path_d.append(f"M{x},{y}h{scale}v{scale}h-{scale}z")
                    else:
                        cx = (col + border) * scale + scale / 2
                        cy = (row + border) * scale + scale / 2
                        svg_parts.append(f'  <circle cx="{cx}" cy="{cy}" r="{radius}" fill="{fg_hex}"/>')

            if path_d:
                svg_parts.append(f'  <path d="{" ".join(path_d)}" fill="{fg_hex}"/>')
        else:
            path_d = []
            for row in range(module_count):
                for col in range(module_count):
                    if logo_path and (min_clear <= row <= max_clear) and (min_clear <= col <= max_clear):
                        continue
                    if qr.get_module(col, row):
                        x = (col + border) * scale
                        y = (row + border) * scale
                        path_d.append(f"M{x},{y}h{scale}v{scale}h-{scale}z")

            if path_d:
                svg_parts.append(f'  <path d="{" ".join(path_d)}" fill="{fg_hex}"/>')

        if logo_svg_tag:
            svg_parts.append(f'  {logo_svg_tag}')

        svg_parts.append('</svg>')

        with open(filename, "w", encoding="utf-8") as f:
            f.write("\n".join(svg_parts))

    else:
        # PNG natively handles the beautifully smoothed RGBA dots we generated
        img.save(filename)

    print(f"Saved: {filename}")
    return img


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a highly customizable QR code.")
    parser.add_argument("text", help="Text or URL to encode into the QR code")
    parser.add_argument("output", help="Output PNG/JPG/SVG filename (e.g., qrcode.png)")
    parser.add_argument("--scale", type=int, default=10, help="Pixels per QR module")
    parser.add_argument("--size", type=int, default=None, help="Target output size in pixels (overrides --scale)")
    parser.add_argument("--border", type=int, default=4, help="Outer margin width in modules")
    parser.add_argument("--fg-color", type=str, default="#000000", help="Foreground color (Hex)")
    parser.add_argument("--bg-color", type=str, default="#ffffff", help="Background color (Hex)")
    parser.add_argument("--logo", type=str, default=None, help="Path to an image to overlay in the center")
    parser.add_argument("--logo-border-width", type=int, default=0, help="Thickness of the border around the logo")
    parser.add_argument("--logo-border-color", type=str, default="#ffffff", help="Color of the logo border (Hex)")
    parser.add_argument("--logo-border-radius", type=int, default=0, help="Border corner radius (0 for square)")
    parser.add_argument("--dots", action="store_true", help="Render modules as dots/pips instead of squares")
    args = parser.parse_args()

    generate_custom_qr(
        data=args.text, filename=args.output, scale=args.scale, output_size=args.size, border=args.border,
        fg_color=args.fg_color, bg_color=args.bg_color, logo_path=args.logo,
        logo_border_width=args.logo_border_width, logo_border_color=args.logo_border_color,
        logo_border_radius=args.logo_border_radius, dots=args.dots,
    )