"""逐帧测原片 Chu 段人物的动：对每一帧，用 ECC 仿射对齐到同一姿势的参考帧，拆出缩放、旋转、位移。
用法：../tools/imagegen/.venv/bin/python -I tools/measure_motion.py
"""
from pathlib import Path
import numpy as np, cv2, json

ROOT = Path(__file__).resolve().parent.parent
FR = ROOT / "work" / "orig_chu_frames"
T0, FPS = 6.70, 30
CUTS = [6.833, 7.167, 7.600, 8.000, 8.433, 8.833, 9.267, 9.667, 10.000]
MASK = {"A": (20, 80, 440, 700), "B": (520, 40, 940, 700)}   # 人物所在区域（966×720 坐标）
REF_T = {"A": 7.80, "B": 7.40}

def load(i):
    return cv2.imread(str(FR / f"{i:04d}.png"), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255

def idx(t):
    return int(round((t - T0) * FPS)) + 1

def main():
    rows = []
    refs = {s: load(idx(t)) for s, t in REF_T.items()}
    prev = None
    for i in range(1, len(list(FR.glob("*.png"))) + 1):
        t = T0 + (i - 1) / FPS
        img = load(i)
        diff = float(np.abs(img - prev).mean() * 255) if prev is not None else 0.0
        prev = img
        if t < CUTS[0] - 1e-3 or t >= CUTS[-1] - 1e-3:
            rows.append(dict(i=i, t=round(t, 3), diff=round(diff, 2))); continue
        k = max(j for j, c in enumerate(CUTS) if c <= t + 1e-3)
        side = "A" if k % 2 == 0 else "B"
        x0, y0, x1, y1 = MASK[side]
        mask = np.zeros(img.shape, np.uint8); mask[y0:y1, x0:x1] = 255
        warp = np.eye(2, 3, dtype=np.float32)
        try:
            cc, warp = cv2.findTransformECC(refs[side], img, warp, cv2.MOTION_AFFINE,
                                            (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6), mask, 5)
        except cv2.error:
            cc = float("nan")
        a, b, tx, c, d, ty = warp.flatten()
        scale = float(np.sqrt(a * a + c * c)); rot = float(np.degrees(np.arctan2(c, a)))
        rows.append(dict(i=i, t=round(t, 3), beat=k, side=side, frame_in_beat=int(round((t - CUTS[k]) * FPS)),
                         scale=round(scale, 4), rot=round(rot, 2), tx=round(float(tx), 1), ty=round(float(ty), 1),
                         cc=round(float(cc), 3), diff=round(diff, 2)))
    (ROOT / "work" / "motion_orig.json").write_text(json.dumps(rows, indent=0))
    for r in rows:
        if "side" in r:
            print(f"{r['t']:6.3f} b{r['beat']} {r['side']} f{r['frame_in_beat']:2d}  s={r['scale']:.4f} r={r['rot']:+5.2f} tx={r['tx']:+6.1f} ty={r['ty']:+6.1f} cc={r['cc']:.3f} diff={r['diff']:.1f}")

if __name__ == "__main__":
    main()
