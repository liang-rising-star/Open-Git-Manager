"""用 Pillow 近似绘制 GitHub octocat"""
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(__file__), "resource", "icon")
SIZE = 32

def gen_github():
    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    s = SIZE / 16

    # 身体主体 - 大圆
    draw.ellipse([3*s, 2*s, 13*s, 12*s], fill=(255,255,255,255))

    # 左耳三角
    draw.polygon([(3*s,6*s), (5.5*s,0.5*s), (7.5*s,5*s)], fill=(255,255,255,255))
    # 右耳三角
    draw.polygon([(8.5*s,5*s), (10.5*s,0.5*s), (13*s,6*s)], fill=(255,255,255,255))

    # 身体下部
    draw.ellipse([5*s,9*s,11*s,15*s], fill=(255,255,255,255))

    # 左手
    draw.ellipse([0.5*s,10*s,5*s,14*s], fill=(255,255,255,255))
    # 右手
    draw.ellipse([11*s,10*s,15.5*s,14*s], fill=(255,255,255,255))

    # 左脚
    draw.ellipse([3.5*s,13.5*s,7*s,16*s], fill=(255,255,255,255))
    # 右脚
    draw.ellipse([9*s,13.5*s,12.5*s,16*s], fill=(255,255,255,255))

    # 左眼
    draw.ellipse([6*s,5.5*s,8*s,7.5*s], fill=(36,41,46,255))
    # 右眼
    draw.ellipse([8*s,5.5*s,10*s,7.5*s], fill=(36,41,46,255))

    img.save(os.path.join(OUT, "github.png"), "PNG")
    print("✓ github.png")

if __name__ == "__main__":
    gen_github()
