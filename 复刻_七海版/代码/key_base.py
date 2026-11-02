"""基底图抠透明底：七海的卫衣是浅灰（≈217），灰底只有 ≈226，奶绿版 cutout()（底色 230、容差 22、去中性灰洞）会把卫衣一起抠掉。
这里按实测底色、容差 4，只去和画面边缘连通的那一片；再把贴着透明区、接近底色的 1 圈浅色毛边去掉。

用法（在 chu-mukuchi-nanami 目录）：../tools/mg-styles-15/.venv/bin/python -I tools/key_base.py candidates/base/BASE_3.png
输出 refs/main_nanami.png（透明底）、refs/main_nanami_on_white.png（铺白，当出图参考的图 1）
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent

def key(path, tol=4, fringe=18):
    a = np.array(Image.open(path).convert("RGB")).astype(int)
    bg = np.median(a[5:60, 5:60].reshape(-1, 3), 0)
    near = np.abs(a - bg).max(-1) <= tol
    lab, _ = ndimage.label(near)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    m = np.isin(lab, edge[edge > 0])
    ring = ndimage.binary_dilation(m) & ~m
    neutral = (a.max(-1) - a.min(-1)) <= 6
    m |= ring & neutral & (np.abs(a - bg).max(-1) <= fringe)
    return Image.fromarray(np.dstack([a.astype(np.uint8), np.where(m, 0, 255).astype(np.uint8)]), "RGBA"), bg

def main():
    im, bg = key(sys.argv[1])
    im.save(ROOT / "refs" / "main_nanami.png")
    white = Image.new("RGBA", im.size, (255, 255, 255, 255)); white.alpha_composite(im)
    white.convert("RGB").save(ROOT / "refs" / "main_nanami_on_white.png")
    print("底色", bg, "透明占比 %.3f" % (np.array(im)[..., 3] == 0).mean())

if __name__ == "__main__":
    main()
