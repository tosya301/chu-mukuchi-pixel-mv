"""把 chu 嘴（S07_1 那个小圆 o）从橘红改成真实嘴里的粉红。作者 11-02：「张嘴的嘴巴的颜色可以自己修一下改成粉红色」。
只改颜色不改形状：嘴所在小框里，按每个像素有多暗，把原来「皮肤 → 浅橘红 → 深红棕」这条渐变换成「皮肤 → 粉红 → 深玫红」，
边上和皮肤混色的像素保持原来的混合比例，所以轮廓、明暗分布（左暗右亮）都不变。

用法（在 chu-mukuchi-mv 目录）：../tools/mg-styles-15/.venv/bin/python -I tools/recolor_mouth.py
"""
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "assets" / "chu_B_S07_1.png"
OUT = ROOT / "assets" / "chu_B_S07_1_pinkmouth.png"
BOX = (466, 444, 488, 462)          # 嘴的小框（x0, y0, x1, y1），鼻子在 y 404–423，不会碰到
SKIN = np.array([0xFE, 0xF3, 0xCD])
OLD_LIGHT = np.array([0xE4, 0x8A, 0x73])
# 第 2 版（作者 11-02：「下面颜色深，像舌头，上面颜色淡」）：颜色按上下位置走，不再按原图的明暗走
TOP, BOTTOM = np.array([0xF4, 0xA5, 0xB4]), np.array([0xB8, 0x3A, 0x58])
# 第 3 版（作者 11-02：中间那一层也改粉，最下面是红色就行）：嘴占第 447–459 行，第 451–455 行那条宽带也是粉，
# 只有最下面 456–459 行（右下那一小块）是红。分界放在嘴高的 72%，过渡 ±5%。
# 第 4 版（作者 11-02：「颜色过渡再自然一点」）：过渡拉到 ±22%，约第 453–457 行之间慢慢变深，458–459 是纯红，448–452 是纯粉。
SPLIT, SOFT = 0.70, 0.22
# 第 5 版（作者 11-02：「嘴巴还是全改成粉色吧，不要红了」）：上下同一个粉，渐变代码留着但不起作用。
# 第 6 版（作者 11-02：「粉色也不对，还是改成腮红一样的颜色吧」）：用这张图两颊腮红的中位色 #EEA984（鼻子是 #ECA581，几乎同色）。
TOP = BOTTOM = np.array([0xEE, 0xA9, 0x84])

def lum(c):
    return c[..., 0] * 0.299 + c[..., 1] * 0.587 + c[..., 2] * 0.114

def main():
    a = np.array(Image.open(SRC).convert("RGBA")).astype(float)
    x0, y0, x1, y1 = BOX
    reg = a[y0:y1, x0:x1, :3]
    touched = np.abs(reg - SKIN).max(-1) > 12               # 只动明显不是皮肤的像素
    ys = np.nonzero(touched.any(1))[0]
    top, bot = ys.min(), ys.max()
    v = ((np.arange(reg.shape[0]) - top) / max(bot - top, 1))[:, None, None]
    k = np.clip((v - (SPLIT - SOFT)) / (2 * SOFT), 0, 1)
    k = k * k * (3 - 2 * k)                                    # smoothstep
    color = TOP * (1 - k) + BOTTOM * k                         # 每一行的嘴色
    # 边上和皮肤混色的像素：按原图有多暗算「嘴占多少」，保持原来的混合比例
    cover = np.clip((lum(SKIN) - lum(reg)) / (lum(SKIN) - lum(OLD_LIGHT)), 0, 1)[..., None]
    pink = SKIN * (1 - cover) + color * cover
    touched = touched[..., None]
    out = np.where(touched, pink, reg)
    a[y0:y1, x0:x1, :3] = out
    Image.fromarray(np.clip(a, 0, 255).round().astype(np.uint8), "RGBA").save(OUT)
    print(OUT, "changed px:", int(touched.sum()))

if __name__ == "__main__":
    main()
