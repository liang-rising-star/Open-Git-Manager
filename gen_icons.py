"""用 Pillow 生成 VS Code Seti 风格的文件类型图标"""
import os, math
from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "resource", "icon")
os.makedirs(OUT, exist_ok=True)

SIZE = 32
BG_TRANSPARENT = (0, 0, 0, 0)

# (名称, 背景色, 前景色, 图标类型)
# type: "circle"=圆形, "diamond"=菱形, "square"=方形, "rounded"=圆角方, "hex"=六边形
ICONS = [
    ("py",        (53,114,165,255),  (255,255,255,255), "circle",  "Py"),
    ("js",        (241,224,90,255),  (0,0,0,255),        "square",  "JS"),
    ("ts",        (49,120,198,255),  (255,255,255,255), "square",  "TS"),
    ("html",      (227,76,38,255),   (255,255,255,255), "diamond", "<>"),
    ("css",       (86,61,124,255),   (255,255,255,255), "diamond", "{}"),
    ("json",      (41,41,41,255),    (255,255,255,255), "rounded", "{}"),
    ("md",        (8,63,161,255),    (255,255,255,255), "circle",  "M↓"),
    ("txt",       (120,120,120,255), (255,255,255,255), "circle",  "Tx"),
    ("xml",       (0,96,172,255),    (255,255,255,255), "diamond", "</>"),
    ("yaml",      (203,23,30,255),   (255,255,255,255), "rounded", "Ym"),
    ("sh",        (137,224,81,255),  (0,0,0,255),        "rounded", "$$"),
    ("go",        (0,173,216,255),   (255,255,255,255), "circle",  "Go"),
    ("java",      (176,114,25,255),  (255,255,255,255), "circle",  "Jv"),
    ("c",         (85,85,85,255),    (255,255,255,255), "circle",  "C"),
    ("cpp",       (243,75,125,255),  (255,255,255,255), "circle",  "C+"),
    ("h",         (85,85,85,255),    (255,255,255,255), "circle",  "H"),
    ("rs",        (222,165,132,255), (0,0,0,255),        "circle",  "Rs"),
    ("rb",        (112,21,22,255),   (255,255,255,255), "circle",  "Rb"),
    ("php",       (79,93,149,255),   (255,255,255,255), "circle",  "Ph"),
    ("vue",       (65,184,131,255),  (255,255,255,255), "diamond", "Vw"),
    ("jsx",       (97,218,251,255),  (0,0,0,255),        "diamond", "Jx"),
    ("tsx",       (49,120,198,255),  (255,255,255,255), "diamond", "Tx"),
    ("sql",       (227,140,0,255),   (255,255,255,255), "circle",  "SQ"),
    ("toml",      (156,66,33,255),   (255,255,255,255), "rounded", "Tm"),
    ("ini",       (100,100,100,255), (255,255,255,255), "rounded", "In"),
    ("log",       (100,100,100,255), (255,255,255,255), "rounded", "Lg"),
    ("gitignore", (240,80,50,255),   (255,255,255,255), "hex",     "Gt"),
    ("docker",    (36,150,237,255),  (255,255,255,255), "square",  "Dk"),
    ("make",      (66,120,25,255),   (255,255,255,255), "rounded", "Mk"),
    ("default",   (102,102,102,255), (255,255,255,255), "circle",  "··"),
    ("folder",    (220,182,122,255), (255,255,255,255), "folder",  ""),
]


def find_font(size):
    for p in ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
              "C:/Windows/Fonts/consolab.ttf", "C:/Windows/Fonts/arial.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def draw_circle(draw, s, color):
    pad = 2
    draw.ellipse([pad, pad, s-pad-1, s-pad-1], fill=color)


def draw_rounded(draw, s, color, r=5):
    pad = 2
    draw.rounded_rectangle([pad, pad, s-pad-1, s-pad-1], radius=r, fill=color)


def draw_square(draw, s, color):
    pad = 3
    draw.rectangle([pad, pad, s-pad-1, s-pad-1], fill=color)


def draw_diamond(draw, s, color):
    cx, cy = s/2, s/2
    r = s/2 - 2
    pts = [(cx, cy-r), (cx+r, cy), (cx, cy+r), (cx-r, cy)]
    draw.polygon(pts, fill=color)


def draw_hex(draw, s, color):
    cx, cy = s/2, s/2
    r = s/2 - 2
    pts = []
    for i in range(6):
        angle = math.radians(60 * i - 30)
        pts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(pts, fill=color)


def draw_folder(draw, s, color):
    pad = 4
    # 文件夹主体
    draw.rounded_rectangle([pad, pad+4, s-pad, s-pad], radius=3, fill=color)
    # 文件夹标签
    draw.rounded_rectangle([pad, pad, s//2+2, pad+6], radius=2, fill=color)


def gen_icon(name, bg, fg, shape, label):
    img = Image.new("RGBA", (SIZE, SIZE), BG_TRANSPARENT)
    draw = ImageDraw.Draw(img)

    if shape == "circle":
        draw_circle(draw, SIZE, bg)
    elif shape == "square":
        draw_square(draw, SIZE, bg)
    elif shape == "diamond":
        draw_diamond(draw, SIZE, bg)
    elif shape == "rounded":
        draw_rounded(draw, SIZE, bg)
    elif shape == "hex":
        draw_hex(draw, SIZE, bg)
    elif shape == "folder":
        draw_folder(draw, SIZE, bg)

    if label and shape != "folder":
        font = find_font(8)
        bbox = draw.textbbox((0, 0), label, font=font)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        x = (SIZE - tw) / 2
        y = (SIZE - th) / 2 - 1
        draw.text((x, y), label, fill=fg, font=font)

    img.save(os.path.join(OUT, f"{name}.png"), "PNG")


if __name__ == "__main__":
    for name, bg, fg, shape, label in ICONS:
        gen_icon(name, bg, fg, shape, label)
        print(f"  ✓ {name}.png  [{shape}]")
    print(f"\n共 {len(ICONS)} 个图标 → {OUT}")
