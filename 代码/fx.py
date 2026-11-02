"""代码特效（11-02）：贴在人物原图上的像素小贴图，和呆毛弹跳。都在人物原图（1024² 或 B 的 1282×1227）坐标里画，
之后跟人物一起按最近邻放大，所以像素格和人物一致。

- sweat_drop：原片的汗滴（深色描边、白底、一点浅蓝高光），静止不动（原片也不动）。
- blush_hatch：原片的腮红是桃色椭圆里几道竖短线「|||」，不是斜线。
- deepen_blush：把腮红色整体加深一档（只换色，不改形状）。
- stretch_ahoge：呆毛那一块以根部为支点竖向拉伸（弹跳用）。
- tiny_heart：冒出来的小心心。
"""
import numpy as np
from PIL import Image
from scipy import ndimage

OUTLINE = (60, 47, 90)
WHITE = (255, 255, 255)
ICE = (190, 226, 242)
HATCH = (214, 84, 88)
BLUSH = np.array([0xEE, 0xA9, 0x84])
BLUSH_DEEP = (0xE5, 0x8A, 0x6E)

def _sprite(rows, palette, cell):
    h, w = len(rows), len(rows[0])
    a = np.zeros((h, w, 4), np.uint8)
    for y, r in enumerate(rows):
        for x, ch in enumerate(r):
            if ch in palette:
                a[y, x] = palette[ch] + (255,)
    return Image.fromarray(a).resize((w * cell, h * cell), Image.NEAREST)

def sweat_drop(cell):
    rows = ["..o..",
            ".oWo.",
            ".oWo.",
            "oWWIo",
            "oWWIo",
            "oWIIo",
            ".ooo."]
    return _sprite(rows, {"o": OUTLINE, "W": WHITE, "I": ICE}, cell)

def blush_hatch(cell, n=4):
    """n 道竖短线，每道 1 格宽 3 格高，间隔 1 格；上下错开一点像手画。"""
    w, h = 2 * n - 1, 4
    rows = [["."] * w for _ in range(h)]
    for i in range(n):
        x, y0 = 2 * i, (i % 2)
        for y in range(y0, y0 + 3):
            rows[y][x] = "h"
    return _sprite(["".join(r) for r in rows], {"h": HATCH}, cell)

def tiny_heart(cell, color):
    rows = [".oo.oo.",
            "oGGoGGo",
            "oGGGGGo",
            ".oGGGo.",
            "..oGo..",
            "...o..."]
    return _sprite(rows, {"o": WHITE, "G": color}, cell)

def blush_blobs(img, box=None, tol=26, min_px=300):
    """找腮红：颜色接近 #EEA984 的两大块（box 限定在脸附近），返回 [(x0,y0,x1,y1)]，按 x 排序。"""
    a = np.array(img.convert("RGB")).astype(int)
    m = np.abs(a - BLUSH).max(-1) <= tol
    if box:
        x0, y0, x1, y1 = box
        z = np.zeros_like(m); z[y0:y1, x0:x1] = m[y0:y1, x0:x1]; m = z
    lab, n = ndimage.label(ndimage.binary_closing(m, iterations=2))
    sizes = ndimage.sum(m, lab, range(1, n + 1))
    out = []
    for i in np.argsort(sizes)[::-1][:2]:
        if sizes[i] < min_px:
            continue
        ys, xs = np.nonzero(lab == i + 1)
        out.append((xs.min(), ys.min(), xs.max(), ys.max()))
    return sorted(out)

def deepen_blush(img, blobs, tol=30):
    """腮红块里接近腮红色的像素换深一档。"""
    a = np.array(img.convert("RGBA"))
    for x0, y0, x1, y1 in blobs:
        reg = a[y0:y1 + 1, x0:x1 + 1]
        m = np.abs(reg[..., :3].astype(int) - BLUSH).max(-1) <= tol
        reg[m, :3] = BLUSH_DEEP
    return Image.fromarray(a, "RGBA")

def stamp(img, sprite, xy):
    out = img.convert("RGBA").copy()
    out.alpha_composite(sprite, (int(xy[0]), int(xy[1])))
    return out

def stretch_ahoge(img, box, base_y, s):
    """box=(x0,x1) 横向范围，base_y 呆毛根部那一行；把 [0,base_y) 这一块以 base_y 为支点竖向拉到 s 倍。"""
    if s == 1.0:
        return img
    x0, x1 = box
    a = img.convert("RGBA")
    block = a.crop((x0, 0, x1, base_y))
    nh = round(base_y * s)
    block = block.resize((x1 - x0, nh), Image.NEAREST)
    out = a.copy()
    bg = Image.new("RGBA", (x1 - x0, base_y), (230, 230, 230, 255))   # 先用底色盖掉原呆毛
    out.paste(bg, (x0, 0))
    top = base_y - nh
    if top < 0:
        block = block.crop((0, -top, x1 - x0, nh)); top = 0
    out.paste(block, (x0, top))
    return out
