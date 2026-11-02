"""候选对比板（星瞳版，照七海版改）：每个镜头一行，最左是奶绿版进片的那张（同一条提示词），右边 3 张星瞳候选。
星瞳的候选是薄荷绿底，板上先按 tools/key_green.py 抠掉、铺浅灰，顺便检查抠图。
闭眼局部改（E 开头）只放眼睛那一块的放大，不然 3 张看起来一样。

用法（在 chu-mukuchi-xingtong 目录）：
  ../tools/mg-styles-15/.venv/bin/python -I tools/review_board.py batch-1 第1批A S01 S03B S04P S05A
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).resolve().parent))
from key_green import key  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
MV = ROOT.parent / "chu-mukuchi-mv" / "assets"
FONT = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", 24)
NAILV = {"S01": "listen_S01_3.png", "S03B": "heart_S03B_3.png", "S04P": "poke_S04P_3.png", "S05A": "nano_S05A_2.png",
         "S06": "chu_A_author0124.png", "S02H": "ahoge_S02H_2.png", "S07": "chu_B_S07_1_pinkmouth.png", "S09B": "okubyo_S09B_2.png",
         "E08b": "front_closed_E08b_2.png", "E09b": "okubyo_closed_E09b_1.png"}
LABEL = {"S01": "声を聴くだけで（捏耳塞线）", "S03B": "幸せ（比心）", "S04P": "なの（戳手指）", "S05A": "なの!（兔耳挡嘴）",
         "S06": "Chu A 拍", "S07": "Chu B 拍（chu 嘴）", "S09B": "臆病だっけ?（食指抵下巴）", "E08b": "正面闭眼（局部改）",
         "S02H": "幸せ①（呆毛竖起来）", "E09b": "臆病闭眼（局部改）"}
REC = {"S01": 3, "S02H": 2, "S03B": 2, "S04P": 1, "S05A": 3, "S06": 3, "S07": 3, "S09B": 2, "E08b": 2}   # 第 1 批我的推荐，绿框标出
REC_1B = {}
EYE_BOX = {"E08b": (360, 320, 680, 440)}   # 闭眼行只看这一块（底图坐标）
EYE_BASE = {"E08b": "refs/main_xingtong_on_white.png", "E09b": "assets/okubyo_S09B.png"}
TH = 360

def on_grey(path):
    im = Image.open(path)
    if "candidates" in str(path):   # 星瞳候选是绿底：抠掉再铺灰
        im = key(path)
    if im.mode == "RGBA":
        bg = Image.new("RGBA", im.size, (230, 230, 230, 255)); bg.alpha_composite(im); im = bg
    return im.convert("RGB")

def fit(im, h):
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)

def main():
    batch, title, ids = sys.argv[1], sys.argv[2], sys.argv[3:]
    rows = []
    rec_map = REC_1B if batch == "batch-1b" else REC
    for sid in ids:
        cands = [ROOT / "candidates" / batch / f"{sid}_{i}.png" for i in (1, 2, 3)]
        tiles = [("奶绿版", on_grey(MV / NAILV[sid]))] + [(f"{sid}_{i}", on_grey(p)) for i, p in enumerate(cands, 1)]
        if sid in EYE_BOX:
            box = EYE_BOX[sid]
            src = on_grey(ROOT / EYE_BASE[sid])
            tiles = [("底图（睁眼）", src.crop(box))] + [(n, im.crop(box)) for n, im in tiles[1:]]
            tiles = [(n, im.resize((im.width * 2, im.height * 2), Image.NEAREST)) for n, im in tiles]
        else:
            tiles = [(n, fit(im, TH)) for n, im in tiles]
        h = max(im.height for _, im in tiles)
        w = sum(im.width for _, im in tiles) + 20 * (len(tiles) + 1)
        r = Image.new("RGB", (w, h + 84), (250, 250, 250))
        d = ImageDraw.Draw(r)
        d.text((20, 8), f"{sid}　{LABEL[sid]}", font=FONT, fill=(20, 20, 20))
        x = 20
        for name, im in tiles:
            rec = name == f"{sid}_{rec_map.get(sid)}"
            d.text((x, 44), name + ("（推荐）" if rec else ""), font=FONT, fill=(40, 150, 60) if rec else (110, 110, 110))
            r.paste(im, (x, 80))
            if rec:
                d.rectangle([x - 6, 74, x + im.width + 5, 80 + im.height + 5], outline=(40, 170, 70), width=6)
            x += im.width + 20
        rows.append(r)
    W = max(r.width for r in rows)
    out = Image.new("RGB", (W, sum(r.height for r in rows) + 10 * len(rows)), (250, 250, 250))
    y = 0
    for r in rows:
        out.paste(r, (0, y)); y += r.height + 10
    dst = ROOT / "candidates" / f"{title}对比板.jpg"
    out.save(dst, quality=90)
    print(dst, out.size)

if __name__ == "__main__":
    main()
