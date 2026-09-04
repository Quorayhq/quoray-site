import math
import cairo
from PIL import Image, ImageDraw, ImageFont

# Same B1 "Verified Teal" mark geometry/colors as
# docs/brand_assets/ombrix_icon_b1_teal/render_assets.py (ombrix repo) and
# docs/store_listing/feature_graphics/render_feature_graphics.py. Kept in
# sync manually; mirror any change there here too.

def pt(cx, cy, r, phi_deg):
    a = math.radians(phi_deg)
    return cx + r * math.sin(a), cy - r * math.cos(a)

def tapered_band(cx, cy, r_out, r_in_start, r_in_end, start_deg, end_deg, n=64):
    outer_pts, inner_pts = [], []
    for i in range(n + 1):
        t = i / n
        ang = start_deg + t * (end_deg - start_deg)
        rin = r_in_start + t * (r_in_end - r_in_start)
        outer_pts.append(pt(cx, cy, r_out, ang))
        inner_pts.append(pt(cx, cy, rin, ang))
    return outer_pts + inner_pts[::-1]

BG = (0x15/255, 0x18/255, 0x1c/255)
THIN = (0x90/255, 0x96/255, 0x9f/255)
THICK = (0x14/255, 0x7d/255, 0x74/255)
INK_TEXT = (0xed, 0xef, 0xf1)
MUTED_TEXT = (0x9a, 0xa1, 0xab)

SEGOE_BOLD = r"C:\Windows\Fonts\segoeuib.ttf"
YU_GOTHIC_MEDIUM = r"C:\Windows\Fonts\YuGothM.ttc"

# Standard OGP/Twitter Card size (1.91:1)
W, H = 1200, 630
SAFE_MAX_WIDTH = 1020

TAGLINE = "これ、本当に元のまま？"

def draw_mark(ctx, cx, cy, scale):
    poly = tapered_band(cx, cy, 44*scale, 40*scale, 18*scale, 20, 320)
    g0 = pt(cx, cy, 44*scale, 20)
    g1 = pt(cx, cy, 44*scale, 320)
    grad = cairo.LinearGradient(g0[0], g0[1], g1[0], g1[1])
    grad.add_color_stop_rgb(0, *THIN)
    grad.add_color_stop_rgb(1, *THICK)
    ctx.move_to(*poly[0])
    for x, y in poly[1:]:
        ctx.line_to(x, y)
    ctx.close_path()
    ctx.set_source(grad)
    ctx.fill()

def fit_font(draw, text, font_path, start_size, min_size, max_width):
    size = start_size
    while size > min_size:
        font = ImageFont.truetype(font_path, size)
        bbox = draw.textbbox((0, 0), text, font=font, anchor="ls")
        if bbox[2] - bbox[0] <= max_width:
            return font
        size -= 1
    return ImageFont.truetype(font_path, min_size)

def render(path):
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H)
    ctx = cairo.Context(surface)
    ctx.set_source_rgb(*BG)
    ctx.rectangle(0, 0, W, H)
    ctx.fill()
    draw_mark(ctx, W / 2, 190, 2.2)
    surface.write_to_png(path)

    im = Image.open(path).convert("RGB")
    draw = ImageDraw.Draw(im)

    word_font = ImageFont.truetype(SEGOE_BOLD, 76)
    draw.text((W / 2, 390), "Ombrix", font=word_font, fill=INK_TEXT, anchor="ms")

    tag_font = fit_font(draw, TAGLINE, YU_GOTHIC_MEDIUM, start_size=40, min_size=22, max_width=SAFE_MAX_WIDTH)
    draw.text((W / 2, 460), TAGLINE, font=tag_font, fill=MUTED_TEXT, anchor="ms")

    im.save(path)
    print("wrote", path, W, H)

render("og-image.png")
