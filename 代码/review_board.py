"""候选对比板：每个镜头一行，左边是原片对应那一帧（没有就放 B 原图），右边是 3 张候选。

用法（在 chu-mukuchi-mv 目录）：
  ../tools/mg-styles-15/.venv/bin/python -I tools/review_board.py batch-2 S01 S03B S04 S05 S09
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FONT = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", 24)
REF = {  # 镜头 → 原片参考帧（work/ 里截好的）
    "S01": "work/orig_1.0.png", "S04": "work/orig_5.7.png", "S05": "work/orig_6.1.png",
    "S09": "work/orig_18.0.png", "S02": "analysis/frames/t_3.8.png",
    "S02H": "analysis/frames/t_3.8.png", "S04P": "work/orig_5.7.png",
}
LABEL = {"S01": "声を聴くだけで", "S03B": "幸せ（比心）", "S04": "なの（星瞳）", "S05": "なの!（捏领口）", "S09": "臆病だっけ?（竖食指）", "S05A": "なの!（长发挡嘴）", "S09B": "臆病だっけ?（食指抵下巴）", "S02H": "幸せ①（呆毛竖起来）", "S04P": "なの（戳手指）"}
REC = {"S01": 3, "S03B": 3, "S04": 2, "S05": 2, "S09": 2, "S05A": 2, "S09B": 2, "S02H": 2, "S04P": 3}   # 我的推荐 / 作者已选，绿框标出
TH = 420

def fit(im, h):
    im = im.convert("RGB")
    return im.resize((round(im.width * h / im.height), h), Image.LANCZOS)

def main():
    batch, ids = sys.argv[1], sys.argv[2:]
    rows = []
    for sid in ids:
        ref = Image.open(ROOT / REF.get(sid, "refs/main_gpt_on_white.png"))
        tiles = [(fit(ref, TH), "原片" if sid in REF else "B 原图")]
        for i in (1, 2, 3):
            p = ROOT / "candidates" / batch / f"{sid}_{i}.png"
            if p.exists():
                tiles.append((fit(Image.open(p), TH), f"{sid}_{i}"))
        w = sum(t.width for t, _ in tiles) + 12 * (len(tiles) - 1)
        row = Image.new("RGB", (w, TH + 40), (255, 255, 255))
        d = ImageDraw.Draw(row)
        x = 0
        for t, lab in tiles:
            row.paste(t, (x, 40))
            rec = lab == f"{sid}_{REC.get(sid)}"
            text = lab + (f"　{LABEL.get(sid, '')}" if lab.startswith("原") or lab.startswith("B") else "") + ("　推荐" if rec else "")
            d.text((x + 6, 6), text, font=FONT, fill=(30, 140, 60) if rec else (20, 20, 24))
            if rec:
                d.rectangle((x, 40, x + t.width - 1, 40 + TH - 1), outline=(30, 170, 70), width=6)
            x += t.width + 12
        rows.append(row)
    W = max(r.width for r in rows)
    board = Image.new("RGB", (W, sum(r.height for r in rows) + 20 * (len(rows) - 1)), (236, 234, 230))
    y = 0
    for r in rows:
        board.paste(r, (0, y)); y += r.height + 20
    out = ROOT / "candidates" / batch / "候选对比板.jpg"
    board.save(out, quality=88)
    print(out, board.size)

if __name__ == "__main__":
    main()
