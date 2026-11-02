"""星瞳版（兔子帽形象）提示词：照奶绿版 `../chu-mukuchi-mv/tools/build_prompts.py` 进片的那几个镜头，句子不动，只换人物。
换掉的：人物描述（ID_MAIN）、脸部规则里的眼睛颜色、画风调色板、取景里的心形呆毛和翅膀、不露脸镜头里的长发和腰带、背景（薄荷绿，见 README）。
和七海版学到的：Chu A / B 用奶绿版那两张当角度参考（原片灰度帧当参考，七海版三张都转反了）；颗粒写硬数字。
按星瞳改的：S05A 长发挡嘴 → 兔耳朵挡嘴（作者 11-02 点名）；S01 耳塞线从兔子帽下面出来；S02H 呆毛照奶绿版（她帽子顶上也有一根）。
基底图里她抱着星星，其他镜头手要空出来做动作，都写明星星不在画面里。

用法（在 chu-mukuchi-xingtong 目录）：python3 tools/build_prompts.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REF_X = "refs/main_xingtong_on_white.png"   # 基底图：作者 11-02 选的 BASE_2（星星眼补了白点），抠底铺白
REF_NL_A = "refs/naiLv_chuA_on_white.png"   # 奶绿版 Chu A（作者的 01_24）：S06 的角度参考
REF_NL_B = "refs/naiLv_chuB.png"            # 奶绿版 Chu B（S07_1，改嘴色之前）：S07 的角度参考

def refs_main(has_pose):
    s = """Reference images:
- Image 1: the CHARACTER, her deadpan face and the ART STYLE. Keep her identity, her outfit and the exact pixel-art look of this image."""
    if has_pose:
        s += """
- Image 2: POSE and FRAMING reference only (a grey frame from another video). Copy only how the body and head are turned and tilted, where the hands are and how close the camera is. Do NOT copy the boy in image 2: not his black hair, his face, his smile, his blush lines, his black uniform or the grey colours."""
    return s

ID_MAIN = """WHO SHE IS (left/right always mean the picture's left/right):
- Short silver-white bob hair with pale blue-grey shading, straight blunt bangs, ending around her jaw.
- A soft white bunny hood: the hood has its own little face on the front above her bangs (two small black dot eyes and two pink blush ovals), a single small grey ahoge curl pokes out of the top of the hood, and two long floppy white bunny ears with pink insides hang down on both sides of her head to below her shoulders.
- Bright blue eyes with a lighter lower half and a thick dark upper lash line, calm and half-lidded.
- Rounded soft peach blush patches on both cheeks, a small peach dot for the nose, a tiny short flat line for the mouth.
- A thin white layered choker necklace; her shoulders are bare.
- An oversized off-shoulder white-grey hoodie with tiny white star prints and big puffy sleeves, a pink ribbon bow tied around each upper arm; two white fluffy pom-poms on strings hang at both sides of her neck.
- A pink bow with a tiny white bunny charm at her chest on the picture-RIGHT side."""

NO_STAR = "The yellow star plush from image 1 is NOT in this picture; her hands are free."

FACE_RULE = """FACE RULE (deadpan, "mukuchi"): unless the SHOT names one change, her face is as calm as in image 1: half-lidded blue eyes looking at the viewer, eyebrows relaxed and level, the same blush patches, the mouth a tiny short flat line. No smile, no open mouth, no teeth, no tears, no sparkles or hearts in the eyes, no sweat drops, no blush hatching lines, no anime epsilon-shaped mouth, no motion lines."""

PIXELS = """Keep the pixel grid as coarse as in image 1: each pixel block is the same size as in image 1, about 4 pixels of this 1024-pixel picture. Do not make the pixels finer because she is framed closer."""

STYLE_MAIN = """ART STYLE: exactly the pixel-art look of image 1: chunky square pixels, crisp pixel edges, a small limited palette (silver white, pale blue-grey, grey, pink, blue, peach), flat colour fills with checkerboard dithering for the shading, dark grey-navy pixel outlines. """ + PIXELS + """ No gradients, no glow, no painterly texture, no 3D.
BACKGROUND: plain flat mint green (#4CC870), nothing else in the picture: no floor, no shadow, no frame, no text, no watermark. Do not let the green tint her hair, her hood, her clothes or her skin."""

HANDS = "Each hand has exactly four fingers and one thumb."
CLOSE = "Framing: a close-up as close as image 2, from the top of the bunny hood down to her upper chest, her face about a third of the picture width. The top of the hood stays inside the picture; the bunny ears may be cut off by the picture's sides."
# 自己设计的动作没有姿势参考图，取景写死成近景
CLOSE_FREE = "Framing: a close-up from the top of the bunny hood down to her upper chest, her face about a third of the picture width, the same size as a waist-up shot cropped tight. The top of the hood stays inside the picture; the bunny ears may be cut off by the picture's sides."
NOFACE_TOP = "Framing: the top edge of the picture cuts straight across her neck just below the chin, so her face is NOT in the picture at all; the bottom edge is at her waist. Her choker sits just below the top edge; the two pom-poms and the ends of the bunny ears hang down at both sides."
BLUSH_UP = "her blush patches are a little larger and one shade deeper peach"

CHU_MOUTH = """The ONE change from the FACE RULE: her mouth is a small round pucker for a kiss ("chu"): a tiny rounded "o" about twice as tall as her usual flat line, drawn in dark red-brown pixels that are clearly darker than her peach nose dot, so it reads as a mouth and not as a second nose. The lips are NOT pushed forward, NOT epsilon- or 3-shaped, NOT duck lips. Eyes and eyebrows stay as calm as in image 1."""

# (编号, 镜头/歌词, 中文想法, 谁, 尺寸, [参考图], 镜头块)
SHOTS = [
    ("S01", "声を聴くだけで｜0.0–3.3 s", "原片 1.0 s 的姿势：近景、一手捏着耳塞线、头往一侧偏，眼皮比平时再垂一点，像在专心听。耳朵在兔子帽里，耳塞线从帽子下面出来。",
     "main", "1024x1024", [REF_X, "refs/pose_S01_orig_gray.png"],
     CLOSE + """
SHOT: copy the body angle and the head tilt of image 2. She wears small white wired earbuds; her ears are hidden under the hood, so a thin white cable comes out from under each side of the hood and runs down to her chest. Her left hand (on the picture-RIGHT) is raised to the side of her head exactly like the hand in image 2, thumb and index finger lightly pinching the earbud cable just where it comes out from under the hood, the other fingers loosely curled.
The ONE change from the FACE RULE: her eyelids are lowered a little more than in image 1, as if she is listening closely; no smile. """ + NO_STAR + " " + HANDS),
    ("S02H", "幸せ（第一个）｜3.3–4.3 s", "呆毛特写：脸完全不变，兔子帽顶上那根小呆毛「啵」地竖起来——嘴不说，呆毛出卖了她。弹跳用代码做（同奶绿版）。",
     "main", "1024x1024", [REF_X],
     """Framing: a close-up from just above the tip of the ahoge down to her chin, her face about half the picture width, centred; the bunny ears are cut off by the picture's sides.
SHOT: front view. The small grey ahoge curl on top of her bunny hood stands straight up, perky and a little larger than in image 1, clearly separated from the hood with plain background around it.
FACE RULE with no change: completely deadpan, half-lidded eyes looking at the viewer, as if she has no idea what her hair is doing. """ + NO_STAR),
    ("S03B", "幸せ｜4.3–5.1 s", "她在胸前双手比心，脸完全淡定。",
     "main", "1024x1024", [REF_X],
     """Framing: a close-up from the top of the bunny hood down to her chest, her face about a third of the picture width; the top of the hood stays inside the picture.
SHOT: front view, head tilted very slightly toward the picture-LEFT. Both hands are raised in front of her chest, just below her chin, and form one big heart: the curled index fingers meet at the top, the thumbs touch at the bottom point; the heart shape is clearly readable and its inside is empty. FACE RULE with no change: completely deadpan, as if making a heart is nothing special. """ + NO_STAR + " " + HANDS),
    ("S04P", "なの｜5.5–5.9 s", "不露脸：两根食指在胸前对戳，害羞的小动作；下一拍「なの!」再露出她用兔耳朵挡嘴的脸。",
     "main_noface", "1024x1024", [REF_X],
     NOFACE_TOP + """
SHOT: front view. Both hands are raised in front of her chest just below the choker; the tips of her two index fingers touch each other, pointing inward, in a shy fidgeting "finger poke" gesture; the other fingers are loosely curled and the thumbs relaxed, elbows close to her sides. """ + NO_STAR + " " + HANDS),
    ("S05A", "なの!｜5.9–6.3 s", "兔耳朵挡嘴（作者 11-02 点名，像奶绿用头发那样）：双手把兔子帽的两只长耳朵往前拉，在嘴前交叉，挡住嘴和下巴，只露眼睛；眼神不变。腮红加深。",
     "main", "1024x1024", [REF_X],
     CLOSE_FREE + """
SHOT: front view, head tilted very slightly down, eyes looking up at the viewer. With both hands she pulls the two long floppy bunny ears of her hood forward and down, and crosses them in front of her face like a veil, so they cover her mouth and chin; the ears cross just below her nose. Her hands stay beside her cheeks, holding the ears loosely between thumb and fingers. Her eyes, eyebrows and blush patches stay fully visible above the ears.
The ONE change from the FACE RULE: """ + BLUSH_UP + """. Everything visible above the ears is as calm as in image 1: half-lidded eyes looking at the viewer, level eyebrows. She is flustered, but her face refuses to show it. """ + NO_STAR + " " + HANDS),
    ("S06", "Chu A 拍｜6.8–10.1 / 13.6–17.0 s", "身体和脸朝画面右侧、一只手蜷在锁骨前、轻微歪头，完全无口。角度参考用奶绿版 Chu A。",
     "main_nlpose", "1024x1024", [REF_X, REF_NL_A],
     CLOSE_FREE + """
SHOT: her body and face are turned three-quarters toward the picture-RIGHT, exactly like the girl in image 2: her nose points toward the picture-RIGHT edge, the near cheek (on the picture-LEFT) looks wider and the far cheek (on the picture-RIGHT) narrower, while her eyes look at the viewer. Copy the slight head tilt of image 2. One hand is raised to her collarbone just under her choker, fingers loosely curled inward, the backs of the fingers toward the viewer, in the same place as the hand in image 2.
FACE RULE with no change: completely deadpan, the mouth a tiny flat line. """ + NO_STAR + " " + HANDS),
    ("S07", "Chu B 拍｜同上，和 A 每拍互切", "身体和脸朝画面左侧、手蜷在锁骨前、轻微歪头，chu 嘴（比鼻子深的小圆 o）。角度参考用奶绿版 Chu B。",
     "main_nlpose", "1024x1024", [REF_X, REF_NL_B],
     CLOSE_FREE + """
SHOT: her body and face are turned three-quarters toward the picture-LEFT, exactly like the girl in image 2: her nose points toward the picture-LEFT edge, the near cheek (on the picture-RIGHT) looks wider and the far cheek (on the picture-LEFT) narrower, while her eyes look at the viewer. Copy the slight head tilt of image 2. One hand is raised to her collarbone just under her choker, fingers loosely curled inward, the backs of the fingers toward the viewer, in the same place as the hand in image 2.
""" + CHU_MOUTH + " " + NO_STAR + " " + HANDS),
    ("S09B", "こんなに臆病だっけ?｜17.0–20.5 s", "食指抵下巴 + 歪头 + 眼睛往上瞟：在自问「我有这么胆小吗?」，嘴角往下压 1 格，有点不服气。",
     "main", "1024x1024", [REF_X],
     CLOSE_FREE + """
SHOT: front view, head tilted about 15 degrees toward the picture-RIGHT shoulder. Her right hand (on the picture-LEFT) is raised and the tip of her index finger rests on her chin just below the corner of her mouth, the other fingers loosely curled.
The changes from the FACE RULE: her eyes look up and toward the picture-RIGHT, as if wondering about something, with the same half-lidded lids; and the corners of her tiny mouth turn down by one pixel, a small sulky line. Eyebrows level. """ + NO_STAR + " " + HANDS),
]

# 局部改图（../tools/imagegen/localedit.py：只在双眼椭圆里改，seam 贴回；seam 的 inner 要盖满遮罩，七海版的教训）
EDIT_PROMPT = """Change ONLY the eyes; this is a pixel-art image and the pixel size must stay exactly the same. Both eyes are now closed: each eye becomes a short, gently downward-curved line of dark grey-navy pixels lying where the upper lash line was, about as wide as the open eye was. No iris, no white, no lashes sticking out, no tears. The bangs crossing the eyes, the blush patches, the face outline and everything outside the eyes stay exactly as they are."""

# (编号, 镜头, 想法, 底图, 提示词)
EDITS = [
    ("E08b", "眨眼帧｜10.1–13.6 s", "在基底图上只把双眼改成闭眼。", REF_X, EDIT_PROMPT),
    ("E09b", "眨眼帧｜17.0–20.5 s", "在选定的 S09B 上只把双眼改成闭眼（S09B 挑定后再跑）。", "assets/okubyo_S09B.png", EDIT_PROMPT),
]

BATCHES = [
    ("第 1 批：照奶绿版换人的镜头", ["S01", "S02H", "S03B", "S04P", "S05A", "S06", "S07", "S09B"]),
    ("第 1 批：基底图闭眼局部改", ["E08b"]),
    ("S09B 挑定后：闭眼局部改", ["E09b"]),
]

def build(shot):
    sid, _, _, who, _, refs, body = shot
    has_pose = any("pose_" in r for r in refs)
    if who == "main":
        return "\n\n".join([refs_main(has_pose), ID_MAIN, FACE_RULE, body, STYLE_MAIN])
    if who == "main_nlpose":  # 图 2 是奶绿版同一镜头，只取角度、手和歪头
        refs = refs_main(False) + """
- Image 2: POSE and ANGLE reference only: a different girl drawn in pixel art. Copy only which way her body and head are turned, how her head is tilted and where her hand is. Do NOT copy the girl in image 2: not her lavender hair, her heart-shaped ahoge, her wing ornaments, her flowers, her choker, her dress or her teal eyes. The framing may differ from image 2 (see Framing)."""
        return "\n\n".join([refs, ID_MAIN, FACE_RULE, body, STYLE_MAIN])
    # main_noface：只拍身体的镜头，脸在画面外，不需要脸部规则
    return "\n\n".join([refs_main(has_pose), ID_MAIN, body, STYLE_MAIN])

def main():
    pdir = ROOT / "prompts"
    pdir.mkdir(exist_ok=True)
    for s in SHOTS:
        (pdir / f"{s[0]}.txt").write_text(build(s) + "\n")
    for e in EDITS:
        (pdir / f"{e[0]}.txt").write_text(e[4] + "\n")

    lines = ["# 星瞳版（兔子帽）生成清单与提示词", "",
             "由 `tools/build_prompts.py` 生成，改提示词请改那个文件。每个提示词出 3 张候选，放 `candidates/`，作者点头的才进 `assets/`。", "",
             "模型 gpt-image-2.5-sunburst，quality high，走 `../tools/imagegen/gen.py`。正面平静脸直接用基底图（抱星星），眼睛大特写从基底图裁，都不用生成。", "",
             "## 分批", ""]
    for name, ids in BATCHES:
        lines.append(f"- **{name}**：{'、'.join(ids)}")
    lines += ["", "## 每张图", ""]
    for s in SHOTS:
        sid, when, idea, who, size, refs, _ = s
        lines += [f"### {sid}　{when}", "", f"- 想法：{idea}",
                  f"- 参考图（按顺序 = image 1, 2）：{'、'.join(refs)}　尺寸：{size}", "", "```text", build(s), "```", ""]
    lines += ["## 局部改（闭眼）", ""]
    for eid, when, idea, base, prompt in EDITS:
        lines += [f"### {eid}　{when}", "", f"- 想法：{idea}", f"- 底图：{base}；遮罩只盖两只眼睛", "", "```text", prompt, "```", ""]
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "03-生成清单与提示词.md").write_text("\n".join(lines))
    print("wrote", len(SHOTS) + len(EDITS), "prompts + docs/03")

if __name__ == "__main__":
    main()
