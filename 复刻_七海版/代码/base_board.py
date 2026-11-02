"""基底图对比板：上排三张参考（七海不带帽 / 带帽 / 奶绿主图 B 画风），中排 3 张候选，
下排把脸按两眼间距缩到一样大，用最近邻放大比像素颗粒。

用法（在 chu-mukuchi-nanami 目录）：../tools/mg-styles-15/.venv/bin/python -I tools/base_board.py
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", 26)
BG = (250, 250, 250)
# 两眼中心（原图坐标，目测后量过）：脸部特写按眼距对齐
EYES = {"refs/naiLv_B_on_white.png": ((548, 462), (727, 462)),
        "candidates/base/BASE_1.png": ((432, 356), (575, 356)),
        "candidates/base/BASE_2.png": ((440, 347), (586, 347)),
        "candidates/base/BASE_3.png": ((436, 355), (580, 355))}

def fit(im, h):
    im = im.convert("RGB")
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)

def face(path, w=400):
    (x0, y0), (x1, y1) = EYES[path]
    d = x1 - x0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    box = (round(cx - 1.4 * d), round(cy - 1.0 * d), round(cx + 1.4 * d), round(cy + 1.4 * d))
    im = Image.open(ROOT / path).convert("RGB").crop(box)
    return im.resize((w, round(w * im.height / im.width)), Image.NEAREST)

def row(ims, labels, pad=24):
    h = max(i.height for i in ims) + 44
    w = sum(i.width for i in ims) + pad * (len(ims) + 1)
    r = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(r)
    x = pad
    for im, lab in zip(ims, labels):
        d.text((x, 6), lab, font=FONT, fill=(40, 40, 40))
        r.paste(im, (x, 44))
        x += im.width + pad
    return r

def main():
    refs = ["refs/nanami_nohat.png", "refs/nanami_hat.png", "refs/naiLv_B_on_white.png"]
    cands = [f"candidates/base/BASE_{i}.png" for i in (1, 2, 3)]
    r1 = row([fit(Image.open(ROOT / p), 420) for p in refs], ["参考1 不带帽（主）", "参考2 带帽（眼色、卫衣）", "参考3 奶绿 B（画风）"])
    r2 = row([fit(Image.open(ROOT / p), 560) for p in cands], ["BASE_1", "BASE_2", "BASE_3"])
    r3 = row([face(p, 330) for p in ["refs/naiLv_B_on_white.png"] + cands], ["奶绿 B 脸部", "1 脸部", "2 脸部", "3 脸部"])
    W = max(r.width for r in (r1, r2, r3))
    out = Image.new("RGB", (W, r1.height + r2.height + r3.height + 40), BG)
    y = 10
    for r in (r1, r2, r3):
        out.paste(r, ((W - r.width) // 2, y)); y += r.height + 10
    dst = ROOT / "candidates" / "base" / "基底图对比板.jpg"
    out.save(dst, quality=92)
    print(dst, out.size)

if __name__ == "__main__":
    main()
