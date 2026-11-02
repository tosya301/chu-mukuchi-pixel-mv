"""按 build_prompts.py 里的镜头表跑一批生图：参考图、尺寸都从镜头表取，几个镜头并行，每个出 3 张。
已经存在的输出会跳过（--force 才覆盖）。

用法（在 chu-mukuchi-mv 目录）：
  python3 tools/run_batch.py batch-2 S01 S03B S04 S05 S09 [--dry-run] [--force]
"""
import subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from build_prompts import SHOTS  # noqa: E402

GEN = ROOT.parent / "tools" / "imagegen" / "gen.py"

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    dry, force = "--dry-run" in sys.argv, "--force" in sys.argv
    batch, ids = args[0], args[1:]
    shots = {s[0]: s for s in SHOTS}
    out_dir = ROOT / "candidates" / batch
    out_dir.mkdir(parents=True, exist_ok=True)
    (ROOT / "work" / "logs").mkdir(parents=True, exist_ok=True)
    procs = []
    for sid in ids:
        _, _, _, _, size, refs, _ = shots[sid]
        out = out_dir / f"{sid}.png"
        if (out_dir / f"{sid}_1.png").exists() and not force:
            print("skip (exists):", sid); continue
        cmd = ["python3", str(GEN), "--prompt-file", str(ROOT / "prompts" / f"{sid}.txt"),
               "--ref", *[str(ROOT / r) for r in refs], "--out", str(out),
               "--size", size, "--quality", "high", "--n", "3"]
        print(sid, size, "refs:", ", ".join(refs))
        if not dry:
            log = open(ROOT / "work" / "logs" / f"{batch}_{sid}.log", "w")
            procs.append((sid, subprocess.Popen(cmd, stdout=log, stderr=subprocess.STDOUT)))
    for sid, p in procs:
        print(sid, "exit", p.wait())

if __name__ == "__main__":
    main()
