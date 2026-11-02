"""整片灰模：20.5 s、30 fps、1440×1080，按原片逐帧切点拼所有镜头，配原音轨。
镜头表、转场帧、镜头内的动都是 11-02 从原片量出来的（帧号 = 原片 30 fps 的帧号，见 docs/02 第 30 条）。
Chu 两段直接用 chu_layout.py 的版式和实测动效。

还没做（灰模里先空着）：眨眼（闭眼图第 3 批）、呆毛弹跳 / 斜线腮红 / 汗滴（代码特效）、でもでも 字卡本身的动。

用法（在 chu-mukuchi-mv 目录）：
  ../tools/mg-styles-15/.venv/bin/python -I tools/animatic.py [--out work/animatic_v1] [--only 0-120]
"""
import argparse, subprocess, sys
from functools import lru_cache
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
import chu_layout as CL  # noqa: E402
import fx  # noqa: E402

W, H, FPS, N = 1440, 1080, 30, 615
K = W / 966
NP = 3.1 * K                      # 原片一个「大像素」在本片的宽度
SRC_VIDEO = ROOT / "原片.mp4"   # 原片（只用它的音轨和画面做测量）：换成你自己的文件路径
FONT = ROOT.parent / "fonts" / "google" / "notosansjp" / "NotoSansJP[wght].ttf"
G1, G2 = CL.G1, CL.G2
BLUE = (31, 82, 230)
A = ROOT / "assets"

# ---------- 镜头表（原片帧号，含头不含尾；wash_in = 开头几帧是「洗白」的入场帧） ----------
SHOTS = [
    # name,     start, end, wash_in, wash_out
    ("S01",       0,  100, 3, 0),
    ("koufuku1", 100, 128, 3, 0),
    ("koufuku2", 128, 153, 2, 0),
    ("na",       153, 165, 2, 0),
    ("nano",     165, 178, 3, 0),
    ("nano!",    178, 190, 2, 2),
    ("demodemo", 190, 203, 3, 0),
    ("chu1",     203, 303, 2, 3),
    ("front",    303, 410, 0, 0),
    ("chu2",     410, 510, 3, 2),
    ("okubyo",   510, 615, 0, 2),
]
CHU1 = [205, 215, 228, 240, 253, 265, 278, 290, 300]   # 拍点（原片实测），第一拍从 203 的洗白帧算起
CHU2 = [413, 423, 435, 448, 460, 473, 485, 498, 508]   # 原片实测；不是 CHU1 整体平移（v1 按 +208 算，3 个切点晚了 1 帧）
# 正面 / 臆病的人物大小（作者 11-02：两个画面人物放大 10%，呆毛被挡一点没关系）。以眼睛高度为准放大，脸不挪，顶上多裁一点。
FRONT_S, FRONT_EYE_Y = 1.415 * 1.10, 445          # B 原图（1282×1227）里眼睛的 y
OKUBYO_S, OKUBYO_EYE_Y = 1.406 * 1.10, 425        # S09B_2（1024²）里眼睛的 y
NANO_S, NANO_EYE_Y = 1.406 * 1.10, 478            # なの! S05A_2（同上，作者 11-02 也要放大 10%）

# 眨眼（11-02 用睁眼模板逐帧匹配原片量出来的闭眼帧；片尾 / 镜头尾的洗白帧不算）
BLINKS = {"front": [313, 314, 318, 319, 345, 346, 347, 368, 369, 385, 386, 387, 398, 399],
          "okubyo": [518, 519, 528, 529, 550, 551, 552, 575, 576, 577, 590, 591, 592, 603, 604]}
CLOSED_B = ROOT / "assets" / "front_closed_E08b_2.png"               # 第 3 批 E08b_2 贴回后（作者 11-02 选定）
CLOSED_OKUBYO = ROOT / "assets" / "okubyo_closed_E09b_1.png"           # 第 3 批 E09b_1 贴回后（作者 11-02 选定）
# 正面 / 臆病：每拍人物往下沉 2 大像素，停一次更新（2–3 帧）
DIPS = {"front": [(318, 2), (333, 2), (345, 3), (358, 2), (370, 3), (383, 2), (395, 3)],
        "okubyo": [(525, 3), (538, 2), (550, 3), (563, 2), (575, 3), (588, 2), (600, 3)]}
# 正面 / 臆病的背景心：不是滚动，是 15 帧一循环、6 个纵向位置来回跳（原片 px）
HEART_JITTER = [(0, 0), (3, -35), (5, 35), (8, -19), (10, -53), (13, 54)]
JITTER_ANCHOR = {"front": 328, "okubyo": 513}
# 入场第一下比后面大一圈（原片：正面 1.165、臆病 1.18、其他约 1.06），停一次更新
POP = {"koufuku1": (1.057, 2), "front": (1.165, 2), "okubyo": (1.18, 3)}   # 只有这三个镜头有（v1 给所有镜头都加了，なの/なの! 多出两次跳）

# ---------- 小工具 ----------
@lru_cache(maxsize=None)
def pixel_text(text, size, cell=6, color=(20, 20, 22), vertical=False, gap=0):
    f = ImageFont.truetype(str(FONT), size)
    f.set_variation_by_axes([900])
    chars = list(text) if vertical else [text]
    blocks = []
    for ch in chars:
        l, t, r, b = f.getbbox(ch)
        small = Image.new("L", (r - l + 4, b - t + 4), 0)
        d = ImageDraw.Draw(small); d.fontmode = "1"
        d.text((2 - l, 2 - t), ch, font=f, fill=255)
        blocks.append(small)
    if vertical:
        wmax = max(b.width for b in blocks)
        m = Image.new("L", (wmax, sum(b.height for b in blocks) + gap * (len(blocks) - 1)), 0)
        y = 0
        for b in blocks:
            m.paste(b, ((wmax - b.width) // 2, y)); y += b.height + gap
    else:
        m = blocks[0]
    big = m.resize((m.width * cell, m.height * cell), Image.NEAREST)
    pad = cell * 2
    mm = Image.new("L", (big.width + 2 * pad, big.height + 2 * pad), 0); mm.paste(big, (pad, pad))
    halo = mm.filter(ImageFilter.MaxFilter(2 * cell + 1))
    out = Image.new("RGBA", mm.size, (0, 0, 0, 0))
    out.paste((255, 255, 255, 255), mask=halo)
    out.paste(color + (255,), mask=mm)
    return out

def at(x, y):  # 原片坐标 → 本片
    return int(x * K), int(y * K)

def paste(canvas, im, xy):
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    layer.paste(im, xy, im)
    canvas.alpha_composite(layer)

def strip(canvas, where):
    m = strip_image(where)
    paste(canvas, m, (0, H - m.height) if where == "bottom" else (0, 0))

@lru_cache(maxsize=None)
def strip_image(where):
    """原片的红色爱心花边条，改 G1 绿：一排半圆鼓包，每个里面一颗白心。"""
    cell = 5
    w, h = W // cell, int(58 * K) // cell
    m = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(m)
    step = int(70 * K) // cell
    d.rectangle((0, 0, w, h * 0.45), fill=G1 + (255,))
    for i in range(-1, w // step + 2):
        cx = i * step + step // 2
        d.ellipse((cx - step * 0.56, -h * 0.25, cx + step * 0.56, h * 0.98), fill=G1 + (255,))
        hm = CL.heart_mask(int(step * 0.55) * cell, int(step * 0.45) * cell, cell)
        hi = Image.fromarray((hm * 255).astype(np.uint8)).resize((hm.shape[1] // cell, hm.shape[0] // cell), Image.NEAREST)
        m.paste((255, 255, 255, 255), (cx - hi.width // 2, int(h * 0.3)), hi)
    m = m.resize((w * cell, h * cell), Image.NEAREST)
    return m.transpose(Image.FLIP_TOP_BOTTOM) if where == "bottom" else m

YY, XX = np.mgrid[0:H, 0:W]
WASH_CELLS = ((XX / NP).astype(int) + (YY / NP).astype(int)) % 2 == 0

def tiled_hearts(canvas, dy_orig):
    return hearts_base(dy_orig).copy()

@lru_cache(maxsize=None)
def hearts_base(dy_orig):
    canvas = white()
    """正面 / 臆病背景：两列 G1/G2 交替的抖动心（同正面风格帧），整体按 dy 跳。"""
    bg = np.array(canvas)
    hw, hh = int(215 * K), int(170 * K)
    m = CL.heart_mask(hw, hh)
    checker = ((XX // 2 + YY // 2) % 2) == 0
    period = 182.5
    for ci, cx in enumerate((107, 860)):
        for ri in range(-2, 7):
            cy = -87 + ri * period + dy_orig
            ink = (G1, G2)[(ci + ri) % 2]
            x0, y0 = int(cx * K - hw / 2), int(cy * K - hh / 2)
            xs, ys = slice(max(x0, 0), min(x0 + hw, W)), slice(max(y0, 0), min(y0 + m.shape[0], H))
            if xs.stop <= xs.start or ys.stop <= ys.start:
                continue
            sub = m[ys.start - y0: ys.stop - y0, xs.start - x0: xs.stop - x0]
            region = bg[ys, xs]
            region[sub & checker[ys, xs]] = ink + (255,)
            bg[ys, xs] = region
    return Image.fromarray(bg)

def wash(img, strength=0.3):
    """原片转场帧：整体往白推一点，再把每隔一个大像素换成白（棋盘格），看上去发白发虚。"""
    a = np.array(img.convert("RGB")).astype(float)
    a = a + (255 - a) * strength
    a[WASH_CELLS] = 255
    return Image.fromarray(a.astype(np.uint8))

def scaled(im, s, center):
    """以 center 为中心整体缩放一帧（入场「大一圈」）。"""
    if s == 1.0:
        return im
    cx, cy = center
    big = im.resize((round(W * s), round(H * s)), Image.NEAREST)
    x0, y0 = round(cx * s - cx), round(cy * s - cy)
    return big.crop((x0, y0, x0 + W, y0 + H))

# ---------- 素材 ----------
# ---------- 特效（11-02，tools/fx.py）：先贴在人物原图上，再跟人物一起放大 ----------
FX_DIR = ROOT / "work" / "fx"
AHOGE_BOX, AHOGE_BASE = (405, 645), 190          # 呆毛图 ahoge_S02H_2：呆毛横向范围、根部那一行（逐行量的）
AHOGE_BEATS = [105, 118]                         # 这个镜头里的两个拍点（librosa 3.529 / 3.947 s，落到 12 fps 网格）
AHOGE_STRETCH = [1.15, 0.94, 1.05, 1.0]          # 拍点后每个网格帧的拉伸：弹上去 → 回弹压一下 → 小回 → 停

def decorated(name, variant=None):
    """返回加了特效的原图路径（写在 work/fx/）；没有特效的图直接返回原路径。"""
    FX_DIR.mkdir(parents=True, exist_ok=True)
    src = A / name
    out = FX_DIR / (name if variant is None else f"{Path(name).stem}_{variant}.png")
    if name == "nano_S05A_2.png":        # なの!：腮红深一档 + 竖线腮红 + 一滴汗
        im = Image.open(src).convert("RGBA")
        blobs = fx.blush_blobs(im, (300, 450, 760, 620))
        im = fx.deepen_blush(im, blobs)
        hatch = fx.blush_hatch(5)
        for x0, y0, x1, y1 in blobs:
            im = fx.stamp(im, hatch, ((x0 + x1 - hatch.width) // 2, (y0 + y1 - hatch.height) // 2))
        # 汗滴 11-02 作者说多余，删掉（「那个泪和汗珠有点多余了 删掉 根本不需要」）
    elif name == "okubyo_S09B_2.png" and variant == "blink":
        return CLOSED_OKUBYO
    elif name == "ahoge_S02H_2.png" and variant is not None:
        im = fx.stretch_ahoge(Image.open(src), AHOGE_BOX, AHOGE_BASE, float(variant))
    else:
        return src
    im.save(out)
    return out

def b_with_drops(path, eye_shot=False):
    """B（正面 / 眼睛特写）。原来在这里加汗滴，11-02 作者说汗和泪都多余、删掉；函数留着方便以后加别的。"""
    return Image.open(path)

class Assets:
    def __init__(self):
        self.cache = {}

    def char(self, name, scale, variant=None):
        key = (name, scale, variant)
        if key not in self.cache:
            im = CL.cutout(decorated(name, variant))
            im = im.resize((round(im.width * scale), round(im.height * scale)), Image.NEAREST)
            self.cache[key] = CL.sticker(im)
        return self.cache[key]

# ---------- 每个镜头画一帧 ----------
def white():
    return Image.new("RGBA", (W, H), (255, 255, 255, 255))

FIT_H = H / 1024   # 1024² 图整张放进画面高度

def closeup(AS, name, scale=1.406, top=0):
    """1024² 近景图：居中、贴顶。scale=1.406 横向铺满（下边裁掉），FIT_H 整张放下。"""
    c = AS.char(name, scale)
    return c, ((W - c.width) // 2, top)

# ---------- 歌词：按原片逐帧量出来的框摆（analysis/text_track.json，tools/measure_text.py） ----------
import json  # noqa: E402
TRACK = {k: {int(f): v for f, v in d.items()} for k, d in json.loads((ROOT / "analysis" / "text_track.json").read_text()).items()}
BLACK = (20, 20, 22)

def box_at(elem, f):
    """这一帧这句歌词在原片里的框（原片坐标）；洗白入场帧用第一帧的框。"""
    tr = TRACK[elem]
    ks = [k for k in tr if k <= f]
    return tr[max(ks)] if ks else tr[min(tr)]

def block(lines, size, color=BLACK, align="l", vertical=False, gap=0):
    """多行字：lines 是每行文字；align 是每行对齐（'l' / 'r'，可以给一个字符串逐行指定）。"""
    if vertical:
        return pixel_text(lines[0], size, color=color, vertical=True, gap=gap)
    parts = [pixel_text(t, size, color=color) for t in lines]
    w = max(p.width for p in parts); h = sum(p.height for p in parts) - 2 * 6 * 2 * (len(parts) - 1)
    out = Image.new("RGBA", (w, h), (0, 0, 0, 0)); y = 0
    for p, al in zip(parts, (align * len(parts))[:len(parts)]):
        out.alpha_composite(p, (w - p.width if al == "r" else 0, y)); y += p.height - 2 * 6 * 2
    return out

def fit_to_box(cv, blk, box, ink):
    """把字块里「墨色」那部分的外框，缩放到原片量出来的框（原片坐标 → 本片），白描边跟着一起缩。"""
    a = np.array(blk)
    m = (a[..., 3] > 0) & (np.abs(a[..., :3].astype(int) - np.array(ink)).max(-1) <= 8)
    ys, xs = np.nonzero(m)
    ix0, iy0, ix1, iy1 = xs.min(), ys.min(), xs.max() + 1, ys.max() + 1
    bx0, by0, bx1, by1 = box[0] * K, box[1] * K, (box[2] + 1) * K, (box[3] + 1) * K
    sx, sy = (bx1 - bx0) / (ix1 - ix0), (by1 - by0) / (iy1 - iy0)
    r = blk.resize((max(1, round(blk.width * sx)), max(1, round(blk.height * sy))), Image.NEAREST)
    paste(cv, r, (round(bx0 - ix0 * sx), round(by0 - iy0 * sy)))

def lyric(cv, elem, f, blk, ink=BLACK):
    fit_to_box(cv, blk, box_at(elem, f), ink)

def heart_shape(color, cell=8):
    hm = CL.heart_mask(400, 340, cell)
    h = Image.new("RGBA", (hm.shape[1], hm.shape[0]), (0, 0, 0, 0))
    h.paste(color + (255,), (0, 0), Image.fromarray((hm * 255).astype(np.uint8)))
    return h

def popped(c, s):
    """入场「大一圈」：只放大人物（原片的歌词不跟着变），返回 (图, 中心偏移)。"""
    if s == 1.0:
        return c, (0, 0)
    r = c.resize((round(c.width * s), round(c.height * s)), Image.NEAREST)
    return r, ((c.width - r.width) // 2, (c.height - r.height) // 2)

def pop_scale(name, f):
    s_pop, n_pop = POP.get(name, (1.0, 0))
    first = [s for n, s, e, wi, wo in SHOTS if n == name][0] + [wi for n, s, e, wi, wo in SHOTS if n == name][0]
    return s_pop if n_pop and first <= f < first + n_pop else 1.0

def shot_S01(AS, f):
    cv = white()
    strip(cv, "top"); strip(cv, "bottom")
    c = AS.char("listen_S01_3.png", 1.6)
    # 原片整张图每次更新往下滑 12.6 px（≈ 每 2.5 帧一次，150 px/s），从第 3 帧滑到第 99 帧
    step = max(0, int((f - 3) / 2.5))
    y = -558 - round(0.10 * H) + round(step * 12.6 * K)   # 作者 11-02：起始位置太靠下，整条下滑轨迹上移画面高度的 10%（108 px）
    paste(cv, c, ((W - c.width) // 2, y))
    fit_to_box(cv, block(["声を聴く"], 38, vertical=True), TRACK["S01_声を聴く"][3], BLACK)   # 后面几帧框被头发撑大，用第 3 帧
    if f >= 63:
        lyric(cv, "S01_だけで", f, block(["だけで"], 38, vertical=True))
    return cv

def grid_ticks(start, f):
    """start 之后（含 start）到 f 为止经过了几个 12 fps 网格帧（帧号 mod 5 ∈ {0,3}），start 本身算第 0 个。"""
    return sum(1 for g in range(start, f + 1) if g % 5 in (0, 3)) - 1

def shot_koufuku1(AS, f):
    cv = white(); strip(cv, "top"); strip(cv, "bottom")
    beat = max([b for b in AHOGE_BEATS if b <= f], default=None)
    tick = grid_ticks(beat, f) if beat is not None else None
    s = AHOGE_STRETCH[min(tick, len(AHOGE_STRETCH) - 1)] if tick is not None else 1.0
    c = AS.char("ahoge_S02H_2.png", FIT_H, None if s == 1.0 else f"{s:.2f}")
    c, (ox, oy) = popped(c, pop_scale("koufuku1", f))
    paste(cv, c, ((W - c.width) // 2, 30 + oy))      # 往下挪 30 px，给呆毛拉长留空间
    if tick is not None and tick <= 4:             # 每拍冒两颗小心心，往外上方飘 4 个网格帧
        h = fx.tiny_heart(6, G1)
        cx, top = W // 2 + round((524 - 512) * FIT_H), 30 + 19
        for side in (-1, 1):
            paste(cv, h, (cx + side * (70 + 10 * tick) - h.width // 2, top + 40 - 22 * tick))
    # 原片：第 125 帧起「幸せ」由黑变蓝（切到下一镜之前 3 帧），下一镜继续蓝、往里靠
    col = BLUE if f >= 125 else BLACK
    lyric(cv, "幸①_幸", f, block(["幸"], 44, color=col), col)
    lyric(cv, "幸①_せ", f, block(["せ"], 44, color=col), col)
    return cv

def shot_koufuku2(AS, f):
    cv = white(); strip(cv, "top"); strip(cv, "bottom")
    c, xy = closeup(AS, "heart_S03B_3.png", FIT_H)
    paste(cv, c, xy)
    lyric(cv, "幸②_幸", f, block(["幸"], 44, color=BLUE), BLUE)
    lyric(cv, "幸②_せ", f, block(["せ"], 44, color=BLUE), BLUE)
    return cv

def shot_na(AS, f):
    b = b_with_drops(ROOT / "refs" / "main_gpt_on_white.png", eye_shot=True).convert("RGB")
    eye = b.crop((430, 300, 850, 615)).resize((W, H), Image.NEAREST).convert("RGBA")
    lyric(eye, "な_な", f, block(["な"], 34))
    return eye

def shot_nano(AS, f):
    cv = white()
    c, xy = closeup(AS, "poke_S04P_3.png")
    paste(cv, c, xy)
    lyric(cv, "なの_な", f, block(["な"], 34)); lyric(cv, "なの_の", f, block(["の"], 34))
    return cv

def bang(color=G1):
    """原片的「!」：竖杠下面那个点换成了一颗心（原片红色，改绿）。只留竖杠，点去掉（11-02 v2 点和心都留了，作者指出）。"""
    from scipy import ndimage
    t = pixel_text("!", 62, color=color)
    a = np.array(t)
    ink = (a[..., 3] > 0) & (np.abs(a[..., :3].astype(int) - np.array(color)).max(-1) <= 8)
    lab, n = ndimage.label(ink)
    sizes = ndimage.sum(ink, lab, range(1, n + 1))
    dot = np.isin(lab, [i + 1 for i in range(n) if i != int(np.argmax(sizes))])   # 除了最大的竖杠，其余（点）都去掉
    halo = np.array(Image.fromarray((dot * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * 6 * 2 + 1))) > 0
    bar_halo = np.array(Image.fromarray(((lab == int(np.argmax(sizes)) + 1) * 255).astype(np.uint8)).filter(ImageFilter.MaxFilter(2 * 6 * 2 + 1))) > 0
    a[halo & ~bar_halo] = 0                                                       # 点和它的白描边一起擦掉
    ys = np.nonzero(a[..., 3].any(1))[0]
    t = Image.fromarray(a).crop((0, 0, a.shape[1], ys.max() + 1))
    hm = CL.heart_mask(int(80 * K), int(66 * K), 5)
    h = Image.new("RGBA", (hm.shape[1], hm.shape[0]), (0, 0, 0, 0))
    h.paste(color + (255,), (0, 0), Image.fromarray((hm * 255).astype(np.uint8)))
    out = Image.new("RGBA", (max(t.width, h.width), t.height + h.height + 6), (0, 0, 0, 0))
    out.alpha_composite(t, ((out.width - t.width) // 2, 0)); out.alpha_composite(h, ((out.width - h.width) // 2, t.height + 6))
    return out

def shot_nano_bang(AS, f):
    cv = white(); strip(cv, "top")
    c = AS.char("nano_S05A_2.png", NANO_S)
    paste(cv, c, ((W - c.width) // 2, round(NANO_EYE_Y * 1.406) - round(NANO_EYE_Y * NANO_S)))
    lyric(cv, "なの!_な", f, block(["な"], 34)); lyric(cv, "なの!_の", f, block(["の"], 34))
    b = bang()
    lyric(cv, "なの!_!左", f, b, G1); lyric(cv, "なの!_!右", f, b, G1)   # 原片「!」入场先拉长再落回
    lyric(cv, "なの!_で", f, block(["で"], 34))
    return cv

def shot_demodemo(AS, f):
    """原片：入场字竖向拉长 1.4 倍，三步落回；最后 3 帧字往里收、心大一圈。全按逐帧量的框摆。"""
    cv = white()
    lyric(cv, "でも_♥", f, heart_shape(G1), G1)
    lyric(cv, "でも_で", f, block(["で"], 62)); lyric(cv, "でも_も", f, block(["も"], 62))
    return cv

def shot_chu(AS, f, cuts):
    # 注意别用 dict.setdefault(key, CL.prep(...))：参数每次都会先算，v1 每个 Chu 帧都重做一次抠图+贴纸描边（约 12 s/帧）
    if "chuA" not in AS.cache:
        AS.cache["chuA"] = CL.prep(A / "chu_A_author0124.png", 1.415)
        AS.cache["chuB"] = CL.prep(A / "chu_B_S07_1_pinkmouth.png", 1.70)
    A_, acx = AS.cache["chuA"]
    B_, bcx = AS.cache["chuB"]
    beats = cuts[:-1]
    k = max([j for j, c in enumerate(beats) if c <= f], default=0)
    k = min(k, len(beats) - 1)
    side = "A" if k % 2 == 0 else "B"
    # 原片整片按同一个 12 fps 网格更新：帧号 mod 5 ∈ {0, 3} 的帧才换画面。拍内第几步 = 拍点之后过了几个网格帧。
    # （v1 按「拍点后第几帧」算，Chu① 刚好对上，Chu② 每拍里的小步差 1 帧）
    start = beats[k] if k else beats[0] - 2              # 第一拍从洗白入场帧算起（同 chu_layout）
    ticks = sum(1 for g in range(start + 1, f + 1) if g % 5 in (0, 3))
    step = min(ticks, len(CL.MOTION[side]["steps"]) - 1)
    m = CL.MOTION[side]
    coff = (round(m["char"][step][0] * CL.NP), round(m["char"][step][1] * CL.NP))
    tdx = round(m["text"][step] * CL.NP)
    key = ("chu", side, step)
    if key not in AS.cache:
        AS.cache[key] = CL.frame(A_ if side == "A" else B_, side, acx if side == "A" else bcx, coff, tdx,
                                 CL.PULSE if step == 0 else 1.0).convert("RGBA")
    return AS.cache[key]

def shot_front(AS, f, name="front"):
    phase = (f - JITTER_ANCHOR[name]) % 15
    dy = [d for st, d in HEART_JITTER if st <= phase][-1]
    dip = any(s <= f < s + n for s, n in DIPS[name])
    ps = pop_scale(name, f)
    blink = f in BLINKS[name]
    key = (name, dy, dip, ps, blink)
    if key not in AS.cache:
        AS.cache[key] = _front(AS, name, dy, dip, ps, f, blink)
    return AS.cache[key]

def _front(AS, name, dy, dip, ps, f, blink=False):
    cv = tiled_hearts(white(), dy)
    sink = round(2 * NP) if dip else 0
    if name == "front":
        bkey = "B_closed" if blink else "B"
        if bkey not in AS.cache:
            src = Image.open(CLOSED_B if blink else ROOT / "refs" / "main_gpt.png").convert("RGBA")
            s = FRONT_S
            im = src.resize((round(src.width * s), round(src.height * s)), Image.NEAREST)
            a = np.array(im); a[..., 3] = np.where(a[..., 3] > 128, 255, 0)
            AS.cache[bkey] = (CL.sticker(Image.fromarray(a)), round(640 * s) + 19)
        c, fcx = AS.cache[bkey]
        c, (ox, oy) = popped(c, ps)
        top = 6 + round(FRONT_EYE_Y * 1.415) - round(FRONT_EYE_Y * FRONT_S)   # 眼睛留在原来的高度
        paste(cv, c, (W // 2 - fcx + ox, top + oy + sink))
        lyric(cv, "正面_左", f, block(["知らない", "感情で"], 18, align="lr"))
        lyric(cv, "正面_右", f, block(["埋もれ", "そう"], 18, align="lr"))
    else:
        c = AS.char("okubyo_S09B_2.png", OKUBYO_S, "blink" if blink else None)
        xy = ((W - c.width) // 2, round(OKUBYO_EYE_Y * 1.406) - round(OKUBYO_EYE_Y * OKUBYO_S))
        c, (ox, oy) = popped(c, ps)
        paste(cv, c, (xy[0] + ox, xy[1] + oy + sink))
        lyric(cv, "臆病_左", f, block(["こん", "なに"], 18, align="lr"))
        lyric(cv, "臆病_右", f, block(["臆病", "だっけ?"], 18, align="ll"))
    return cv

def render_shot(AS, name, f):
    if name == "S01":
        step = (max(0, int((f - 3) / 2.5)), f >= 63)
        if step not in S01_CACHE:
            S01_CACHE[step] = shot_S01(AS, f)
        return S01_CACHE[step]
    if name == "koufuku1": return shot_koufuku1(AS, f)
    if name == "koufuku2": return shot_koufuku2(AS, f)
    if name == "na": return shot_na(AS, f)
    if name == "nano": return shot_nano(AS, f)
    if name == "nano!": return shot_nano_bang(AS, f)
    if name == "demodemo": return shot_demodemo(AS, f)
    if name == "chu1": return shot_chu(AS, f, CHU1)
    if name == "chu2": return shot_chu(AS, f, CHU2)
    if name == "front": return shot_front(AS, f, "front")
    if name == "okubyo": return shot_front(AS, f, "okubyo")
    raise KeyError(name)

S01_CACHE = {}
STATIC = {"na", "nano"}   # 歌词完全不动的镜头才能整镜头缓存（幸せ②、なの! 的字有动作）
KOUFUKU1_CACHE = {}

def frame_at(AS, f):
    for name, s, e, wi, wo in SHOTS:
        if s <= f < e:
            break
    first_solid = s + wi
    # 洗白帧：入场用这个镜头自己的样子；出场（wash_out）用离场前最后一帧的样子
    src_f = f
    if wo and f >= e - wo:
        src_f = e - wo - 1
    key = ("shot", name, src_f if name not in STATIC else 0)
    img = AS.cache.get(key) if name in STATIC else None
    if img is None:
        img = render_shot(AS, name, src_f).convert("RGB")
        if name in STATIC:
            AS.cache[key] = img
    # 入场「大一圈」在各镜头函数里只放大人物（pop_scale）
    if f < first_solid:
        img = wash(img, 0.85 if name == "demodemo" else 0.3)
    elif wo and f >= e - wo:
        img = wash(img, 0.3)
    return img, name

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="work/animatic_v1")
    ap.add_argument("--only", default=None, help="只重渲这些帧号，如 0-100,165-190（其余帧沿用上次的），渲完照样合成视频")
    args = ap.parse_args()
    out = ROOT / args.out
    (out / "frames").mkdir(parents=True, exist_ok=True)
    if args.only:
        todo = [f for part in args.only.split(",") for f in range(int(part.split("-")[0]), int(part.split("-")[1]))]
    else:
        todo = list(range(N))
    AS = Assets()
    log = []
    for f in todo:
        img, name = frame_at(AS, f)
        img.save(out / "frames" / f"{f:04d}.png", compress_level=1)
        log.append(f"{f:03d} {f / FPS:6.3f} {name}")
    if not args.only:
        (out / "frame_log.txt").write_text("\n".join(log) + "\n")
    mp4 = out / "animatic.mp4"
    # 音频直接拷贝原片的 AAC（原片峰值已到 −0.1 dBFS，重新编码会顶到 0）
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(out / "frames" / "%04d.png"),
                    "-i", str(SRC_VIDEO), "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-pix_fmt", "yuv420p",
                    "-crf", "16", "-c:a", "copy", "-shortest", str(mp4)], check=True)
    print(mp4)

if __name__ == "__main__":
    main()
