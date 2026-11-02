"""逐帧量原片歌词的包围盒和颜色（11-02）。每句歌词给一个搜索区域，只数「黑字」或「蓝字」像素。
输出 analysis/text_track.json：{元素: {帧号: [x0,y0,x1,y1,颜色]}}（原片 966×720 坐标），animatic.py 照它摆字。
用法：../tools/mg-styles-15/.venv/bin/python -I tools/measure_text.py
"""
import json
from pathlib import Path
import numpy as np
from PIL import Image
from scipy import ndimage

ROOT = Path(__file__).resolve().parent.parent
def F(f): return np.array(Image.open(ROOT / "work" / "orig_all" / f"{f + 1:04d}.png").convert("RGB")).astype(int)

def ink(a, kind):
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    if kind == "dark": return a.max(-1) < 70
    if kind == "blue": return (b > 150) & (r < 110) & (g < 140) & (b - r > 60)
    if kind == "red":  return (r > 190) & (g < 110) & (b < 130)
    raise KeyError(kind)

# 元素：(帧范围, 搜索区域 x0,y0,x1,y1, 颜色种类, 最小连通块像素)
ELEMS = {
    "S01_声を聴く": ((3, 100), (735, 0, 966, 700), ("dark",), 400),
    "S01_だけで":   ((63, 100), (470, 180, 735, 720), ("dark",), 400),
    "幸①_幸": ((103, 128), (0, 150, 300, 480), ("dark", "blue"), 600),
    "幸①_せ": ((103, 128), (660, 150, 966, 480), ("dark", "blue"), 600),
    "幸②_幸": ((130, 153), (60, 150, 420, 480), ("blue",), 600),
    "幸②_せ": ((130, 153), (560, 150, 900, 480), ("blue",), 600),
    "な_な": ((155, 165), (0, 0, 200, 180), ("dark",), 300),
    "なの_な": ((168, 178), (0, 0, 200, 200), ("dark",), 300),
    "なの_の": ((168, 178), (760, 0, 966, 200), ("dark",), 300),
    "なの!_な": ((180, 188), (0, 0, 120, 180), ("dark",), 300),
    "なの!_の": ((180, 188), (790, 0, 966, 200), ("dark",), 300),
    "なの!_!左": ((180, 188), (0, 180, 140, 640), ("red",), 300),
    "なの!_!右": ((180, 188), (820, 180, 966, 640), ("red",), 300),
    "なの!_で": ((180, 188), (0, 560, 130, 720), ("dark",), 300),
    "でも_で": ((193, 203), (0, 150, 290, 620), ("dark",), 600),
    "でも_♥": ((193, 203), (250, 150, 720, 620), ("red",), 600),
    "でも_も": ((193, 203), (700, 150, 966, 620), ("dark",), 600),
    "正面_左": ((303, 410), (0, 330, 300, 500), ("dark",), 200),
    "正面_右": ((303, 410), (700, 330, 966, 500), ("dark",), 200),
    "臆病_左": ((510, 615), (0, 330, 230, 520), ("dark",), 200),
    "臆病_右": ((510, 615), (640, 330, 966, 520), ("dark",), 200),
}

def main():
    out = {}
    for name, ((a, b), (x0, y0, x1, y1), kinds, minpx) in ELEMS.items():
        track = {}
        for f in range(a, b):
            img = F(f)[y0:y1, x0:x1]
            best = None
            for k in kinds:
                m = ink(img, k)
                lab, n = ndimage.label(ndimage.binary_closing(m, iterations=2))
                if n == 0: continue
                sizes = ndimage.sum(m, lab, range(1, n + 1))
                keep = np.isin(lab, np.flatnonzero(sizes >= minpx) + 1) & m
                if keep.sum() > (best[1] if best else 0):
                    best = (k, keep.sum(), keep)
            if best is None: continue
            ys, xs = np.nonzero(best[2])
            track[f] = [int(xs.min() + x0), int(ys.min() + y0), int(xs.max() + x0), int(ys.max() + y0), best[0]]
        out[name] = track
        # 只打印变化的帧
        last = None; line = []
        for f, v in track.items():
            if v != last: line.append(f"{f}:{v[:4]}{'' if v[4] == 'dark' else v[4]}"); last = v
        print(name, " ".join(line))
    (ROOT / "analysis" / "text_track.json").write_text(json.dumps(out))

if __name__ == "__main__":
    main()
