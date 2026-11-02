"""对照表：同一帧号，左奶绿版成片（../chu-mukuchi-mv/work/animatic_v6），右七海版，检查人物大小、位置、颜色有没有走样。

用法（在 chu-mukuchi-xingtong 目录）：../tools/mg-styles-15/.venv/bin/python -I tools/compare_sheet.py work/nanami_v1 5 80 104 106 ...
"""
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
NL = ROOT.parent / "chu-mukuchi-mv" / "work" / "animatic_v6" / "frames"
FONT = ImageFont.truetype("/System/Library/Fonts/Hiragino Sans GB.ttc", 22)

def main():
    out_dir, frames = ROOT / sys.argv[1], [int(x) for x in sys.argv[2:]]
    tw, th = 480, 360
    cols = 2   # 每行两对
    rows = (len(frames) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (2 * tw + 30), rows * (th + 34)), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    for k, f in enumerate(frames):
        x, y = (k % cols) * (2 * tw + 30), (k // cols) * (th + 34)
        d.text((x + 4, y + 4), f"帧 {f}（{f / 30:.2f} s）  左：奶绿 v6　右：星瞳", font=FONT, fill=(0, 0, 0))
        for j, p in enumerate((NL / f"{f:04d}.png", out_dir / "frames" / f"{f:04d}.png")):
            sheet.paste(Image.open(p).convert("RGB").resize((tw, th), Image.LANCZOS), (x + j * tw, y + 32))
    dst = out_dir / "对照表.jpg"
    sheet.save(dst, quality=88)
    print(dst, sheet.size)

if __name__ == "__main__":
    main()
