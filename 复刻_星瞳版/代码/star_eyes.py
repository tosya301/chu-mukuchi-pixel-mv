"""BASE_2 抱着的星星玩偶，眼睛（两条黑色胶囊）里补三颗小白点，照 BASE_1（作者 11-02：「本地修改一下…就按 base1 的来」）。
BASE_1 实测：每只眼三颗白点，沿胶囊长轴排、间距 ≈ 8 px，中心比胶囊中心偏上 ≈ 1.5 px；两头的点 5×4 px，中间的 3×3 px，颜色 ≈ (243, 242, 242)。
这里按 BASE_2 两只胶囊各自的中心和长轴方向摆，点是和图一样横平竖直的像素块。

用法（在 chu-mukuchi-xingtong 目录）：../tools/mg-styles-15/.venv/bin/python -I tools/star_eyes.py
"""
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
SRC, DST = ROOT / "candidates/base/BASE_2.png", ROOT / "candidates/base/BASE_2_星星眼.png"
BOXES = [(375, 719, 431, 757), (497, 700, 560, 732)]   # BASE_2 两只星星眼的外框（暗像素连通块，自动量的）
DOTS = [(-8, 5, 4), (0, 3, 3), (8, 5, 4)]              # (沿长轴位置, 宽, 高)
PERP, WHITE = -1.5, (243, 242, 242)

def main():
    a = np.array(Image.open(SRC).convert("RGB"))
    dark = a.astype(int).max(-1) < 90
    for x0, y0, x1, y1 in BOXES:
        d = dark[y0:y1 + 1, x0:x1 + 1]
        ys, xs = np.nonzero(d)
        pts = np.stack([xs + x0, ys + y0], 1).astype(float); c = pts.mean(0)
        ax = np.linalg.svd(pts - c)[2][0]; ax = ax if ax[0] > 0 else -ax
        pe = np.array([-ax[1], ax[0]])
        for t, w, h in DOTS:
            cx, cy = c + t * ax + PERP * pe
            l, tp = int(round(cx - w / 2)), int(round(cy - h / 2))
            assert dark[tp:tp + h, l:l + w].all(), "白点要整个落在黑色胶囊里"
            a[tp:tp + h, l:l + w] = WHITE
    Image.fromarray(a).save(DST)
    print(DST)

if __name__ == "__main__":
    main()
