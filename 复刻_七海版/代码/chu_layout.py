"""Chu 段版式 + 动态样片（七海版，照 ../chu-mukuchi-mv/tools/chu_layout.py）：红底 + 白色大心 + 灰色 Chu♡ 底纹 + 黑色大字 Chu♡，人物 A（左）/ B（右）每拍互切。
版式数字从原片 7.0 s（A）和 7.4 s（B）两帧量出来（966×720 坐标，×K 放到 1440×1080）。
奶绿版是两种绿交替；七海版 作者 11-02 要「爱心换成红色」：R1 = 原片的红（第 219 帧底色实测平均），R2 = 同色相亮一档，A/B 交替。

用法（在 chu-mukuchi-nanami 目录）：
  ../tools/mg-styles-15/.venv/bin/python -I tools/chu_layout.py A.png B.png --out work/chu_preview [--scale-a 1.77 --scale-b 1.77]
出：两张静帧 + 原片 6.83–10.10 s 这一段的 30 fps 样片（带原音轨）。
"""
import argparse, subprocess
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT.parent / "fonts" / "google"
ROUND = FONTS / "mplusrounded1c" / "MPLUSRounded1c-Black.ttf"
SRC_VIDEO = ROOT / "原片.mp4"   # 原片（只用它的音轨和画面做测量）：换成你自己的文件路径
W, H, FPS = 1440, 1080, 30
K = W / 966
R1, R2 = (247, 57, 75), (249, 98, 118)
GRAY = (120, 120, 124)
# 原片 Chu 第一段切点（实测，和拍点误差 1 帧内）：A 先上，之后每个切点换一次
CUTS = [6.833, 7.167, 7.600, 8.000, 8.433, 8.833, 9.267, 9.667, 10.000]
SEG_END = 10.100

def cutout(path, tol=4, fringe=18, hole_px=400):
    """生成图是 ≈#E2E2E2 的平涂灰底。七海的卫衣是浅灰（≈217），奶绿版的抠法（底色 230、容差 22、去中性灰洞）会把卫衣一起抠掉，
    这里按图角实测底色、容差 4：去掉和画面边缘连通的那一片，再去掉被头发、手臂围住的大块底色（≥ hole_px，卫衣上贴近底色的只有零星抖动点），
    最后把贴着透明区、接近底色的 1 圈浅色毛边去掉（同 tools/key_base.py）。"""
    src = Image.open(path)
    if src.mode == "RGBA" and src.getextrema()[3][0] == 0:  # 本来就是透明底（基底图 main_nanami.png）：直接用它的透明度
        al = np.array(src)[..., 3]
        return Image.fromarray(np.dstack([np.array(src)[..., :3], np.where(al > 128, 255, 0).astype(np.uint8)]), "RGBA")
    a = np.array(src.convert("RGB")).astype(int)
    bg = np.median(a[5:60, 5:60].reshape(-1, 3), 0)
    near = np.abs(a - bg).max(-1) <= tol
    lab, n = ndimage.label(near)
    edge = np.unique(np.concatenate([lab[0], lab[-1], lab[:, 0], lab[:, -1]]))
    bgmask = np.isin(lab, edge[edge > 0])
    sizes = ndimage.sum(near, lab, range(1, n + 1))
    bgmask |= np.isin(lab, np.flatnonzero(sizes >= hole_px) + 1)
    ring = ndimage.binary_dilation(bgmask) & ~bgmask
    neutral = (a.max(-1) - a.min(-1)) <= 6
    bgmask |= ring & neutral & (np.abs(a - bg).max(-1) <= fringe)
    rgba = np.dstack([a.astype(np.uint8), np.where(bgmask, 0, 255).astype(np.uint8)])
    return Image.fromarray(rgba, "RGBA")

def sticker(im, white=16, line=3):
    alpha = im.split()[3]
    grow = lambda r: alpha.filter(ImageFilter.MaxFilter(2 * r + 1))
    out = Image.new("RGBA", im.size, (0, 0, 0, 0))
    out.paste((30, 30, 34, 255), mask=grow(white + line))
    out.paste((255, 255, 255, 255), mask=grow(white))
    out.alpha_composite(im)
    return out

def heart_mask(w, h, cell=5):
    cw, ch = w // cell, h // cell
    yy, xx = np.mgrid[0:ch, 0:cw]
    x = (xx + 0.5) / cw * 2.6 - 1.3
    y = 1.25 - (yy + 0.5) / ch * 2.5
    m = (x**2 + y**2 - 1) ** 3 - x**2 * y**3 <= 0
    return np.array(Image.fromarray((m * 255).astype(np.uint8)).resize((cw * cell, ch * cell), Image.NEAREST)) > 0

def heart_outline(size, cell, stroke=2):
    """大字后面那个空心心形：在小格子上画，描边 stroke 格。"""
    m = heart_mask(size, size, 1)
    small = Image.fromarray((m * 255).astype(np.uint8)).resize((size // cell, size // cell), Image.NEAREST)
    s = np.array(small) > 0
    inner = ndimage.binary_erosion(s, iterations=stroke)
    ring = Image.fromarray(((s & ~inner) * 255).astype(np.uint8)).resize((s.shape[1] * cell, s.shape[0] * cell), Image.NEAREST)
    return ring

def pixel_word(text, size, cell):
    f = ImageFont.truetype(str(ROUND), size)
    l, t, r, b = f.getbbox(text)
    small = Image.new("L", (r - l + 2, b - t + 2), 0)
    d = ImageDraw.Draw(small)
    d.fontmode = "1"
    d.text((1 - l, 1 - t), text, font=f, fill=255)
    return small.resize((small.width * cell, small.height * cell), Image.NEAREST)

def pattern_row(n=4, size=22, cell=5):  # 原片底纹字高约 75 px（966 坐标）≈ 本片 112 px
    """灰色底纹的一行「Chu♡Chu♡…」。"""
    word = pixel_word("Chu", size, cell)
    hrt = heart_outline(word.height, cell, stroke=1)
    gap = cell * 2
    row = Image.new("L", ((word.width + hrt.width + 2 * gap) * n, max(word.height, hrt.height)), 0)
    x = 0
    for _ in range(n):
        row.paste(word, (x, 0)); x += word.width + gap
        row.paste(hrt, (x, 0)); x += hrt.width + gap
    return row

# 心跳（11-02 量原片：每拍切点那 2–3 帧白色大心大一圈，人物走第一步时缩回原大小，只有大/原两档；
# 里面的灰色底纹不动，只有心的轮廓变）。原片外侧边缘移 15–16 px、心尖移 10 px（966 坐标），
# 换到我们的心形上，绕心的包围盒中心放大 1.03 倍最接近（边缘 25 px、心尖 12 px，本片坐标）。
PULSE = 1.03

def background(side, pulse=1.0):
    """side='A'：大心在右；side='B'：大心在左。pulse>1 时大心绕自己中心放大（心跳）。"""
    bg = np.zeros((H, W, 3), np.uint8)
    bg[:] = R1 if side == "A" else R2
    base = int(660 * K)
    m0 = heart_mask(base, base)
    r0 = np.nonzero(m0.any(1))[0]
    cx = (700 if side == "A" else 290) * K
    cy = -30 * K + (r0.min() + r0.max()) / 2            # 心形包围盒中心（放大的支点）
    hw = hh = int(base * pulse)
    m = heart_mask(hw, hh)
    r1 = np.nonzero(m.any(1))[0]
    x0, y0 = int(cx - hw / 2), int(cy - (r1.min() + r1.max()) / 2)
    pattern_x0 = int(cx - base / 2)                      # 底纹按原大小的心定位，心跳时不跟着动
    full = np.zeros((H, W), bool)
    ys, xs = slice(max(y0, 0), min(y0 + m.shape[0], H)), slice(max(x0, 0), min(x0 + m.shape[1], W))
    full[ys, xs] = m[ys.start - y0: ys.stop - y0, xs.start - x0: xs.stop - x0]
    bg[full] = 255
    # 灰色 Chu♡ 底纹：每行错开半个词，只留在大心里面，和白色 1:1 棋盘格抖动
    yy, xx = np.mgrid[0:H, 0:W]
    checker = ((xx // 3 + yy // 3) % 2) == 0
    row = np.array(pattern_row()) > 0
    for i, ry in enumerate((40, 155, 270, 385, 500)):
        y = int(ry * K)
        x = int(pattern_x0 - (i % 2) * row.shape[1] / 8)
        tgt = np.zeros((H, W), bool)
        h2 = min(row.shape[0], H - y)
        xa, xb = max(x, 0), min(x + row.shape[1], W)
        tgt[y:y + h2, xa:xb] = row[:h2, xa - x: xb - x]
        bg[tgt & full & checker] = GRAY
    return Image.fromarray(bg).convert("RGBA")

def big_chu(cell=6):
    word = pixel_word("Chu", 40, cell)
    hrt = heart_outline(int(word.height * 0.95), cell, stroke=3)
    m = Image.new("L", (word.width + hrt.width + cell * 3, max(word.height, hrt.height) + 4 * cell), 0)
    m.paste(word, (cell * 2, cell * 2))
    m.paste(hrt, (word.width + cell * 3, cell * 2 + (word.height - hrt.height) // 2))
    halo = m.filter(ImageFilter.MaxFilter(2 * cell + 1))
    out = Image.new("RGBA", m.size, (0, 0, 0, 0))
    out.paste((255, 255, 255, 255), mask=halo)
    out.paste((22, 22, 24, 255), mask=m)
    return out

# 镜头内的动（tools/measure_motion.py 用 ECC + 模板匹配逐帧量原片 6.83–10.10 s 得出，11-02）：
# - 没有缩放、没有旋转，只有平移；底纹和白色大心不动。
# - 原片是约 311×232 的像素画放大 3.1 倍，所有位移都是整「大像素」（原片 3.1 px，本片 3.1×K ≈ 4.62 px）。
# - 位置约每 2.5 帧（≈ 12 fps）更新一次，A 拍在第 0/2/5/7/10 帧、B 拍在第 0/3/5/8/10 帧。
# - 人物：先斜着往上「跳」4 格，在顶上停一会儿，再往同一侧落回原高度（一拍一个小跳）；
#   大字：往画面外侧滑 12–13 格，先快后慢。人物和字移动的距离不同，看起来像有前后层次的横摇。
NP = 3.1 * K
MOTION = {
    "A": {"steps": [0, 2, 5, 7, 10], "char": [(0, 0), (4, -4), (4, -4), (5, -3), (8, 0)], "text": [0, 4, 10, 12, 13]},
    "B": {"steps": [0, 3, 5, 8, 10], "char": [(0, 0), (-3, -3), (-3, -3), (-4, -2), (-6, 0)], "text": [0, -8, -9, -10, -12]},
}

def motion_at(side, f):
    """拍内第 f 帧时的位置（取最近一个已经到达的台阶，不在台阶之间插值——原片就是这样一格一格走的）。"""
    m = MOTION[side]
    s = max(j for j, st in enumerate(m["steps"]) if st <= f)
    (cx, cy), tx = m["char"][s], m["text"][s]
    return s, (round(cx * NP), round(cy * NP)), round(tx * NP)

# 人物顶边（本片 px）：七海 B 图头顶被图边切掉，只能贴着画面顶；A 按眼睛和 B 一样高往上提（animatic.py 里算，见 CHU_TOP）
TOP = {"A": 4, "B": 4}

def frame(char, side, face_cx, char_off=(0, 0), text_dx=0, pulse=1.0, top=None):
    canvas = background(side, pulse)
    target_cx = (280 if side == "A" else 720) * K
    top = TOP[side] if top is None else top
    # alpha_composite 不接受负坐标（A 的顶边在画面上方）：先贴到同尺寸透明层上
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(char, (int(target_cx - face_cx) + char_off[0], top + char_off[1]), char)
    canvas.alpha_composite(layer)
    chu = big_chu()
    right = (960 if side == "A" else 480) * K
    x, y = int(right - chu.width) + text_dx, int(290 * K - 2 * 6)
    # alpha_composite 不接受负坐标：先贴到同尺寸透明层上再合成，超出画面的部分自然被裁掉
    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    layer.paste(chu, (x, y), chu)
    canvas.alpha_composite(layer)
    return canvas.convert("RGB")

def prep(path, scale):
    im = cutout(path)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.NEAREST)
    box = im.getbbox()
    face_cx = (box[0] + box[2]) / 2
    return sticker(im), face_cx + 19  # sticker 外扩了 white+line 像素

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("a"); ap.add_argument("b")
    ap.add_argument("--out", default="work/chu_preview")
    ap.add_argument("--scale-a", type=float, default=1.77)
    ap.add_argument("--scale-b", type=float, default=1.77)
    args = ap.parse_args()
    out = ROOT / args.out
    (out / "frames").mkdir(parents=True, exist_ok=True)
    A, acx = prep(args.a, args.scale_a)
    B, bcx = prep(args.b, args.scale_b)
    frame(A, "A", acx).save(out / "still_A.png")
    frame(B, "B", bcx).save(out / "still_B.png")
    t0 = CUTS[0]
    n = round((SEG_END - t0) * FPS)
    cut_frames = [round((c - t0) * FPS) for c in CUTS]       # 用整数帧号比，浮点累加会让切点晚 1 帧
    cache = {}
    log = []
    for i in range(n):
        t = t0 + i / FPS
        k = max(j for j, cf in enumerate(cut_frames) if cf <= i)
        side = "A" if k % 2 == 0 else "B"
        since_frames = i - cut_frames[k]
        if k == 0:                                           # 原片第一拍从 6.77 的转场后接上，相当于从拍内第 2 帧开始
            since_frames += 2
        step, coff, tdx = motion_at(side, since_frames)
        key = (side, step)
        if key not in cache:
            # 第 0 档（切点到人物走第一步之前）大心放大，之后回原大小
            cache[key] = frame(A if side == "A" else B, side, acx if side == "A" else bcx, coff, tdx,
                               PULSE if step == 0 else 1.0)
        f = cache[key]
        if i >= cut_frames[-1]:                              # 10.0 s 起淡到白（原片转场）
            w = min(1.0, (i - cut_frames[-1] + 1) / (n - cut_frames[-1]))
            f = Image.blend(f, Image.new("RGB", f.size, (255, 255, 255)), 0.85 * w)
        f.save(out / "frames" / f"{i:04d}.png")
        log.append(f"{i:03d} {t:6.3f} {side} f{since_frames:02d} step{step} char{coff} text{tdx:+d}")
    (out / "frame_log.txt").write_text("\n".join(log) + "\n")
    mp4 = out / "chu_preview.mp4"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-framerate", str(FPS), "-i", str(out / "frames" / "%04d.png"),
                    "-ss", f"{t0:.3f}", "-t", f"{SEG_END - t0:.3f}", "-i", str(SRC_VIDEO),
                    "-map", "0:v", "-map", "1:a", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "16",
                    "-c:a", "aac", "-b:a", "192k", "-shortest", str(mp4)], check=True)
    print(mp4)

if __name__ == "__main__":
    main()
