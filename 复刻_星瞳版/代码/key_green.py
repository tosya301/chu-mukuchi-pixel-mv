"""抠薄荷绿底（星瞳版出图都用 #4CC870 一类的平涂绿）：她身上没有绿色，按颜色直接抠，不用管连不连通（耳朵和头之间、胳膊和身体之间围住的绿也一起去掉）。
贴着背景的 1–2 圈像素混了绿（溢色）：偏绿很多的去掉，偏绿一点的把绿通道压回到红蓝的较大值（去溢色），描边留着。

用法（在 chu-mukuchi-xingtong 目录）：../tools/mg-styles-15/.venv/bin/python -I tools/key_green.py candidates/base/BASE_2_星星眼.png
输出 refs/main_xingtong.png（透明）、refs/main_xingtong_on_white.png（铺白，当出图参考的图 1）
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent

def key(path, hard=40, drop=25, ring_px=2):
    a = np.array(Image.open(path).convert("RGB")).astype(int)
    g_over = a[..., 1] - np.maximum(a[..., 0], a[..., 2])
    bg = g_over > hard
    ring = ndimage.binary_dilation(bg, iterations=ring_px) & ~bg
    bg |= ring & (g_over > drop)
    spill = ring & ~bg & (g_over > 0)
    a[spill, 1] = np.maximum(a[spill, 0], a[spill, 2])
    return Image.fromarray(np.dstack([a.astype(np.uint8), np.where(bg, 0, 255).astype(np.uint8)]), "RGBA")

def main():
    im = key(sys.argv[1])
    im.save(ROOT / "refs" / "main_xingtong.png")
    white = Image.new("RGBA", im.size, (255, 255, 255, 255)); white.alpha_composite(im)
    white.convert("RGB").save(ROOT / "refs" / "main_xingtong_on_white.png")
    print("透明占比 %.3f" % (np.array(im)[..., 3] == 0).mean())

if __name__ == "__main__":
    main()
