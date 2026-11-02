"""七海版提示词：照奶绿版 `../chu-mukuchi-mv/tools/build_prompts.py` 进片的那几个镜头，句子不动，只换人物。
换掉的：人物描述（ID_MAIN）、脸部规则里的眼睛颜色、画风调色板、取景里的心形呆毛和翅膀、不露脸镜头里的长发和腰带。
道具不同的镜头按七海自己的东西改：S01 耳塞 → 她的红耳机，S05A 长发挡嘴 → 袖子挡嘴（她是短发），S02H 呆毛 → 鲨鱼帽弹上来（等 作者看过再跑）。

用法（在 chu-mukuchi-nanami 目录）：python3 tools/build_prompts.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REF_N = "refs/main_nanami_on_white.png"   # 基底图：作者 11-02 选的 BASE_3，抠底铺白
REF_HAT = "refs/nanami_hat.png"           # 七海带帽原图，只在鲨鱼帽镜头里给帽子样子
REF_NL_A = "refs/naiLv_chuA_on_white.png"  # 奶绿版 Chu A（作者的 01_24，铺白）：S06 v2 的角度参考（作者 11-02：S06 第 1 批三张角度都错了）

def refs_main(has_pose):
    s = """Reference images:
- Image 1: the CHARACTER, her deadpan face and the ART STYLE. Keep her identity, her outfit and the exact pixel-art look of this image."""
    if has_pose:
        s += """
- Image 2: POSE and FRAMING reference only (a grey frame from another video). Copy only how the body and head are turned and tilted, where the hands are and how close the camera is. Do NOT copy the boy in image 2: not his black hair, his face, his smile, his blush lines, his black uniform or the grey colours."""
    return s

ID_MAIN = """WHO SHE IS (left/right always mean the picture's left/right):
- Straight warm chestnut-brown hair cut in a bob that reaches just past her chin to the top of her shoulders, with full blunt bangs over her eyebrows and a few longer strands framing both cheeks.
- A round yellow smiley-face hair clip on a silver hair pin, clipped in her bangs on the picture-RIGHT side.
- Warm amber-brown eyes with a thick dark-brown upper lash line, calm and half-lidded.
- Rounded soft peach blush patches on both cheeks, a small peach dot for the nose, a tiny short flat line for the mouth.
- Big red over-ear headphones resting around her neck, each ear cup red with white and black stripes and a black rim; a thin black cable hangs from the picture-right cup down the front of her hoodie.
- A white collared shirt with a small red bow tie at the collar.
- A loose light-grey pullover hoodie; the shark hood lies down behind her neck, its rim lined in red with a row of white triangular shark teeth; each sleeve has a black band with a white stripe running down from the shoulder; two white drawstrings hang down the front.
- Small round pin badges on the picture-right side of her chest: one red tartan, one yellow, one light blue."""

FACE_RULE = """FACE RULE (deadpan, "mukuchi"): unless the SHOT names one change, her face is as calm as in image 1: half-lidded amber-brown eyes looking at the viewer, eyebrows relaxed and level, the same blush patches, the mouth a tiny short flat line. No smile, no open mouth, no teeth, no tears, no sparkles or hearts in the eyes, no sweat drops, no blush hatching lines, no anime epsilon-shaped mouth, no motion lines."""

PIXELS = """Keep the pixel grid as coarse as in image 1: each pixel block is the same fraction of the whole picture as in image 1. Do not make the pixels finer because she is framed closer."""

STYLE_MAIN = """ART STYLE: exactly the pixel-art look of image 1: chunky square pixels, crisp pixel edges, a small limited palette (chestnut brown, light grey, black, white, red, amber, peach), flat colour fills with checkerboard dithering for the shading, dark brown-grey pixel outlines. """ + PIXELS + """ No gradients, no glow, no painterly texture, no 3D.
BACKGROUND: plain flat pale grey (#E6E6E6), nothing else in the picture: no floor, no shadow, no frame, no text, no watermark."""

HANDS = "Each hand has exactly four fingers and one thumb."
CLOSE = "Framing: a close-up as close as image 2, from the top of her head down to her upper chest, her face about a third of the picture width. The top of her head stays inside the picture."
# 自己设计的动作没有姿势参考图，取景写死成近景
CLOSE_FREE = "Framing: a close-up from the top of her head down to her upper chest, her face about a third of the picture width, the same size as a waist-up shot cropped tight. The top of her head stays inside the picture."
NOFACE_TOP = "Framing: the top edge of the picture cuts straight across her neck just below the chin, so her face is NOT in the picture at all; the bottom edge is at her waist. The red headphones around her neck sit at the top edge of the picture, and the ends of her brown hair may just show at the top corners."
BLUSH_UP = "her blush patches are a little larger and one shade deeper peach"

CHU_MOUTH = """The ONE change from the FACE RULE: her mouth is a small round pucker for a kiss ("chu"): a tiny rounded "o" about twice as tall as her usual flat line, drawn in dark red-brown pixels that are clearly darker than her peach nose dot, so it reads as a mouth and not as a second nose. The lips are NOT pushed forward, NOT epsilon- or 3-shaped, NOT duck lips. Eyes and eyebrows stay as calm as in image 1."""

# (编号, 镜头/歌词, 中文想法, 谁, 尺寸, [参考图], 镜头块)
SHOTS = [
    ("S01", "声を聴くだけで｜0.0–3.3 s", "原片 1.0 s 的姿势：近景、一手按住耳机、头往一侧偏，眼皮比平时再垂一点，像在专心听。奶绿版是白耳塞，七海换成她自己的红耳机戴在头上。",
     "main", "1024x1024", [REF_N, "refs/pose_S01_orig_gray.png"],
     CLOSE + """
SHOT: copy the body angle and the head tilt of image 2. For this shot she wears her red headphones on her head instead of around her neck: the headband goes over the top of her head and an ear cup covers each ear; the black cable hangs down. Her left hand (on the picture-RIGHT) is raised to her ear exactly like the hand in image 2, the fingertips gently pressing the picture-right ear cup against her ear, the other fingers loosely curled.
The ONE change from the FACE RULE: her eyelids are lowered a little more than in image 1, as if she is listening closely; no smile. """ + HANDS),
    ("S03B", "幸せ｜4.3–5.1 s", "她在胸前双手比心，脸完全淡定。",
     "main", "1024x1024", [REF_N],
     """Framing: a close-up from the top of her head down to her chest, her face about a third of the picture width; the top of her head stays inside the picture.
SHOT: front view, head tilted very slightly toward the picture-LEFT. Both hands are raised in front of her chest, just below her chin, and form one big heart: the curled index fingers meet at the top, the thumbs touch at the bottom point; the heart shape is clearly readable and its inside is empty. FACE RULE with no change: completely deadpan, as if making a heart is nothing special. """ + HANDS),
    ("S04P", "なの｜5.5–5.9 s", "不露脸：两根食指在胸前对戳，害羞的小动作；下一拍「なの!」再露出她挡嘴的脸。",
     "main_noface", "1024x1024", [REF_N],
     NOFACE_TOP + """
SHOT: front view. Both hands are raised in front of her chest just below the headphones; the tips of her two index fingers touch each other, pointing inward, in a shy fidgeting "finger poke" gesture; the other fingers are loosely curled and the thumbs relaxed, elbows close to her sides. """ + HANDS),
    ("S05A", "なの!｜5.9–6.3 s", "袖子挡嘴：卫衣袖子盖住手（萌え袖），两只袖口并在一起挡住嘴和下巴，只露眼睛；眼神不变。奶绿版是用长发挡，七海是短发，换成袖子。腮红加深。",
     "main", "1024x1024", [REF_N],
     CLOSE_FREE + """
SHOT: front view, head tilted very slightly down, eyes looking up at the viewer. Her hoodie sleeves are long and cover her hands up to the fingertips ("sleeve paws"). She holds both sleeve-covered hands together in front of her mouth and chin, so her mouth and chin are hidden behind the grey sleeves with their black-and-white stripes; only a few fingertips peek out of the cuffs. Her eyes, eyebrows and blush patches stay fully visible above the sleeves.
The ONE change from the FACE RULE: """ + BLUSH_UP + """. Everything visible above the sleeves is as calm as in image 1: half-lidded eyes looking at the viewer, level eyebrows. She is flustered, but her face refuses to show it."""),
    ("S06", "Chu A 拍｜6.8–10.1 / 13.6–17.0 s（v2）", "身体和脸朝画面右侧、一只手蜷在领口、轻微歪头，完全无口。v1 用原片灰度帧当姿势参考，三张都转成了朝左（作者 11-02 指出）；v2 按 作者说的换成奶绿版 Chu A 那张当角度参考。",
     "main_nlpose", "1024x1024", [REF_N, REF_NL_A],
     CLOSE_FREE + """
SHOT: her body and face are turned three-quarters toward the picture-RIGHT, exactly like the girl in image 2: her nose points toward the picture-RIGHT edge, the near cheek (on the picture-LEFT) looks wider and the far cheek (on the picture-RIGHT) narrower, while her eyes look at the viewer. Copy the slight head tilt of image 2. One hand is raised to her collar just under the red bow tie, fingers loosely curled inward, the backs of the fingers toward the viewer, in the same place as the hand in image 2.
FACE RULE with no change: completely deadpan, the mouth a tiny flat line. """ + HANDS),
    ("S07", "Chu B 拍｜同上，和 A 每拍互切", "原片 7.4 s 的姿势原向：近景、身体和脸朝画面左侧、手蜷在领口、轻微歪头，chu 嘴（比鼻子深的小圆 o）。",
     "main", "1024x1024", [REF_N, "refs/pose_chuB_orig_gray.png"],
     CLOSE + """
SHOT: her body and face are turned three-quarters toward the picture-LEFT, exactly like the figure in image 2, while her eyes look at the viewer. Copy the slight head tilt of image 2. One hand is raised to her collar just under the red bow tie, fingers loosely curled inward, the backs of the fingers toward the viewer, in the same place as the hand in image 2.
""" + CHU_MOUTH + " " + HANDS),
    ("S09B", "こんなに臆病だっけ?｜17.0–20.5 s", "食指抵下巴 + 歪头 + 眼睛往上瞟：在自问「我有这么胆小吗?」，嘴角往下压 1 格，有点不服气。",
     "main", "1024x1024", [REF_N],
     CLOSE_FREE + """
SHOT: front view, head tilted about 15 degrees toward the picture-RIGHT shoulder. Her right hand (on the picture-LEFT) is raised and the tip of her index finger rests on her chin just below the corner of her mouth, the other fingers loosely curled.
The changes from the FACE RULE: her eyes look up and toward the picture-RIGHT, as if wondering about something, with the same half-lidded lids; and the corners of her tiny mouth turn down by one pixel, a small sulky line. Eyebrows level. """ + HANDS),
    # —— 奶绿版这里是心形呆毛竖起来，七海没有呆毛：改成鲨鱼帽自己弹上来扣在头上。作者看过提示词再跑 ——
    ("S02H", "幸せ（第一个）｜3.3–4.3 s（待 作者看）", "鲨鱼帽特写：脸完全不变，背后的鲨鱼帽「啪」地弹上来扣在头上，鲨鱼牙一圈框住脸——嘴不说，帽子出卖了她。弹跳用代码做。",
     "main_hood", "1024x1024", [REF_N, REF_HAT],
     """Framing: a close-up from just above the top of the shark hood down to her chin, her face about half the picture width, centred.
SHOT: front view. Her shark hood has just flipped up onto her head by itself and sits over her hair, shaped like the hood in image 2: dark grey on top with two small round black shark eyes, light grey around the face, and a row of white triangular shark teeth along the rim framing her face like an open shark mouth. Her brown bangs and the smiley-face hair clip are still visible inside the hood.
FACE RULE with no change: completely deadpan, half-lidded eyes looking at the viewer, as if she has no idea what her hood is doing."""),
]

# 局部改图（../tools/imagegen/localedit.py：只在双眼椭圆里改，seam 贴回）
EDIT_PROMPT = """Change ONLY the eyes; this is a pixel-art image and the pixel size must stay exactly the same. Both eyes are now closed: each eye becomes a short, gently downward-curved line of dark brown pixels lying where the upper lash line was, about as wide as the open eye was. No iris, no white, no lashes sticking out, no tears. The bangs crossing the eyes, the blush patches, the face outline and everything outside the eyes stay exactly as they are."""

# (编号, 镜头, 想法, 底图, 提示词)
EDITS = [
    ("E08b", "眨眼帧｜10.1–13.6 s", "在基底图上只把双眼改成闭眼。", REF_N, EDIT_PROMPT),
    ("E09b", "眨眼帧｜17.0–20.5 s", "在选定的 S09B 上只把双眼改成闭眼（S09B 挑定后再跑）。", "assets/okubyo_S09B.png", EDIT_PROMPT),
]

BATCHES = [
    ("第 1 批：照奶绿版换人的镜头", ["S01", "S03B", "S04P", "S05A", "S06", "S07", "S09B"]),
    ("第 1 批：基底图闭眼局部改", ["E08b"]),
    ("待 作者看提示词：鲨鱼帽镜头", ["S02H"]),
    ("S09B 挑定后：闭眼局部改", ["E09b"]),
    ("第 1b 批（作者 11-02）：S06 换奶绿 Chu A 当角度参考重跑（S06_3 直接当 Chu B，不改嘴）", ["S06"]),
]

def build(shot):
    sid, _, _, who, _, refs, body = shot
    has_pose = any("pose_" in r for r in refs)
    if who == "main":
        return "\n\n".join([refs_main(has_pose), ID_MAIN, FACE_RULE, body, STYLE_MAIN])
    if who == "main_nlpose":  # 图 2 是奶绿版同一镜头，只取角度、手和歪头
        refs = refs_main(False) + """
- Image 2: POSE and ANGLE reference only: a different girl drawn in pixel art. Copy only which way her body and head are turned, how her head is tilted and where her hand is. Do NOT copy the girl in image 2: not her lavender hair, her heart-shaped ahoge, her wing ornaments, her flowers, her choker, her dress or her teal eyes. The framing is closer than image 2 (see Framing)."""
        return "\n\n".join([refs, ID_MAIN, FACE_RULE, body, STYLE_MAIN])
    if who == "main_noface":  # 只拍身体的镜头，脸在画面外，不需要脸部规则
        return "\n\n".join([refs_main(has_pose), ID_MAIN, body, STYLE_MAIN])
    # main_hood：图 2 是七海带帽原图，只取帽子样子
    refs_hood = refs_main(False) + """
- Image 2: the SAME character drawn in a different, non-pixel style with her shark hood up. Take ONLY the shape and colours of the shark hood from it; draw everything in the pixel-art style of image 1."""
    return "\n\n".join([refs_hood, ID_MAIN, FACE_RULE, body, STYLE_MAIN])

def main():
    pdir = ROOT / "prompts"
    pdir.mkdir(exist_ok=True)
    for s in SHOTS:
        (pdir / f"{s[0]}.txt").write_text(build(s) + "\n")
    for e in EDITS:
        (pdir / f"{e[0]}.txt").write_text(e[4] + "\n")

    lines = ["# 七海版 生成清单与提示词", "",
             "由 `tools/build_prompts.py` 生成，改提示词请改那个文件。每个提示词出 3 张候选，放 `candidates/`，作者点头的才进 `assets/`。", "",
             "模型 gpt-image-2.5-sunburst，quality high，走 `../tools/imagegen/gen.py`。正面平静脸直接用基底图，眼睛大特写从基底图裁，都不用生成。", "",
             "## 分批", ""]
    for name, ids in BATCHES:
        lines.append(f"- **{name}**：{'、'.join(ids)}")
    lines += ["", "## 每张图", ""]
    for s in SHOTS:
        sid, when, idea, who, size, refs, _ = s
        lines += [f"### {sid}　{when}", "", f"- 想法：{idea}",
                  f"- 参考图（按顺序 = image 1, 2）：{'、'.join(refs)}　尺寸：{size}", "", "```text", build(s), "```", ""]
    lines += ["## 局部改（闭眼、chu 嘴）", ""]
    for eid, when, idea, base, prompt in EDITS:
        lines += [f"### {eid}　{when}", "", f"- 想法：{idea}", f"- 底图：{base}；遮罩只盖要改的地方", "", "```text", prompt, "```", ""]
    (ROOT / "docs").mkdir(exist_ok=True)
    (ROOT / "docs" / "03-生成清单与提示词.md").write_text("\n".join(lines))
    print("wrote", len(SHOTS) + len(EDITS), "prompts + docs/03")

if __name__ == "__main__":
    main()
