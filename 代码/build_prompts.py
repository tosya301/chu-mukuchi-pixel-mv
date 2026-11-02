"""提示词唯一来源：参考图说明 + 身份块 + 脸部规则 + 镜头块 + 画法块。
改提示词只改这里，再跑一次，同时重写 prompts/*.txt 和 docs/03-生成清单与提示词.md。

v2（11-01 晚，作者看第 1 批后）：「捧脸」那几个姿势不好看，改用原片的姿势 + 无口 + 轻微歪头。
所以凡是原片里有对应镜头的，都加一张原片那一帧的灰度图当姿势参考（只取姿势、取景，不取男生本人），取景改成原片那样的近景。
Chu 段两拍都用原片 7.4 s 那个姿势：A 拍镜像（人在左、朝右、无口），B 拍原向（人在右、朝左、chu 嘴）。

用法（在 chu-mukuchi-mv 目录）：../tools/mg-styles-15/.venv/bin/python -I tools/build_prompts.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REF_B = "refs/main_gpt_on_white.png"           # B：作者选定的人物图（透明底铺白）
REF_TILT = "refs/main_author_0124_on_white.png"   # 作者之前跑的歪头无口版，Chu 段的脸照它
REF_XT = "refs/xingtong_uniform_sheet.png"     # 星瞳校服三视图

def refs_main(has_pose):
    s = """Reference images:
- Image 1: the CHARACTER, her deadpan face and the ART STYLE. Keep her identity, her outfit and the exact pixel-art look of this image."""
    if has_pose:
        s += """
- Image 2: POSE and FRAMING reference only (a grey frame from another video). Copy only how the body and head are turned and tilted, where the hands are and how close the camera is. Do NOT copy the boy in image 2: not his black hair, his face, his smile, his blush lines, his black uniform or the grey colours."""
    return s

def refs_xt(has_pose):
    s = """Reference images:
- Image 1: a character sheet. Take ONLY the school uniform and the hair colour from it.
- Image 2: STYLE reference only. Draw in exactly the pixel-art technique of image 2, but do NOT copy the girl in image 2 (not her lavender hair, her wing ornaments, her flowers or her dress)."""
    if has_pose:
        s += """
- Image 3: POSE and FRAMING reference only (a grey frame from another video). Copy only how the body is turned, where the hands are and how close the camera is. Do NOT copy that girl's sailor uniform or the grey colours."""
    return s

ID_MAIN = """WHO SHE IS (left/right always mean the picture's left/right):
- Very long periwinkle-lavender hair with deep indigo-purple shadows, reaching past her waist; a few long thin strands drift out to both sides.
- A single strand of hair on top of her head loops into a heart shape (heart ahoge).
- One upright cream-white feathered wing ornament on each side of her head, each with a cream five-petal flower and small green leaf sprigs with tiny brown buds at its base.
- A soft peach-brown streak in her front bangs, running from the top of her head down across the forehead to the inner corner of the picture-RIGHT eye.
- Teal-blue eyes with a lighter lower half and a thick dark upper lash line, calm and half-lidded.
- Large rounded peach blush patches on both cheeks, a small peach dot for the nose, a tiny short flat peach line for the mouth.
- A lavender high choker collar with a white bow and a dark-green oval gem brooch; thin dark-red and white ribbons hang from the brooch over a white lace jabot; small white collar points on both sides; bare shoulders and upper arms.
- Small cream flower clusters in her hair at shoulder height on both sides."""

ID_XT = """WHO SHE IS (outfit only; left/right always mean the picture's left/right):
- Very long straight silver-white hair with a faint pale-blue sheen, reaching her thighs, falling behind her shoulders and down both sides of her body.
- White short-sleeved school shirt with a pointed collar and a chest pocket; each sleeve ends in a navy-blue band with a thin white stripe.
- A blue bow tie with diagonal white stripes at the collar.
- A black lanyard around her neck holding a small white ID card with a blue frame at mid-chest.
- A blue-and-white plaid pleated skirt.
- A fluffy pink scrunchie on her right wrist.
- HER FACE IS NEVER SHOWN: the top edge of the picture cuts across her neck just below the chin, so her mouth, glasses and eyes are all outside the picture."""

FACE_RULE = """FACE RULE (deadpan, "mukuchi"): unless the SHOT names one change, her face is as calm as in image 1: half-lidded teal eyes looking at the viewer, eyebrows relaxed and level, the same blush patches, the mouth a tiny short flat line. No smile, no open mouth, no teeth, no tears, no sparkles or hearts in the eyes, no sweat drops, no blush hatching lines, no anime epsilon-shaped mouth, no motion lines."""

PIXELS = """Keep the pixel grid as coarse as in image 1: each pixel block is the same fraction of the whole picture as in image 1. Do not make the pixels finer because she is framed closer."""

STYLE_MAIN = """ART STYLE: exactly the pixel-art look of image 1: chunky square pixels, crisp pixel edges, a small limited palette (periwinkle lavender, deep indigo-purple, cream, peach, teal, olive green, dark red), flat colour fills with checkerboard dithering for the shading, dark indigo pixel outlines. """ + PIXELS + """ No gradients, no glow, no painterly texture, no 3D.
BACKGROUND: plain flat pale grey (#E6E6E6), nothing else in the picture: no floor, no shadow, no frame, no text, no watermark."""

STYLE_XT = """ART STYLE: exactly the pixel-art look of image 2: chunky square pixels of the SAME size as in image 2, crisp pixel edges, a small limited palette, flat colour fills with checkerboard dithering for the shading, dark pixel outlines. No gradients, no glow, no painterly texture, no 3D.
BACKGROUND: plain flat pale grey (#E6E6E6), nothing else in the picture: no floor, no shadow, no frame, no text, no watermark."""

HANDS = "Each hand has exactly four fingers and one thumb."
CLOSE = "Framing: a close-up as close as image 2, from the top of her head down to her upper chest, her face about a third of the picture width. The heart ahoge stays inside the picture; the tips of the wing ornaments may be cut off by the top edge."
# 自己设计的动作（不照原片男生）没有姿势参考图，取景写死成和第 2 批近景一样大
CLOSE_FREE = "Framing: a close-up from the top of her head down to her upper chest, her face about a third of the picture width, the same size as a waist-up shot cropped tight. The heart ahoge stays inside the picture; the tips of the wing ornaments may be cut off by the top edge."
NOFACE_TOP = "Framing: the top edge of the picture cuts straight across her neck just below the chin, so her face is NOT in the picture at all; the bottom edge is at her waist, with the olive-green sash just visible. Her long lavender hair falls down both sides of the picture."
BLUSH_UP = "her blush patches are a little larger and one shade deeper peach"

CHU_MOUTH = """The ONE change from the FACE RULE: her mouth is a small round pucker for a kiss ("chu"): a tiny rounded "o" about twice as tall as her usual flat line, drawn in dark red-brown pixels that are clearly darker than her peach nose dot, so it reads as a mouth and not as a second nose. The lips are NOT pushed forward, NOT epsilon- or 3-shaped, NOT duck lips. Eyes and eyebrows stay as calm as in image 1."""

# (编号, 镜头/歌词, 中文想法, 谁, 尺寸, [参考图], 镜头块)
SHOTS = [
    ("S06", "Chu A 拍｜6.8–10.1 / 13.6–17.0 s（不再生成：作者定用自己的 01_24，已入库 assets/chu_A_author0124.png）", "原片 7.4 s 的姿势左右镜像：近景、身体和脸朝画面右侧、一只手蜷在领口、轻微歪头，完全无口。成片里放在画面左半边、G1 绿底。",
     "main", "1024x1024", [REF_TILT, "refs/pose_chuA_mirror_gray.png"],
     CLOSE + """
SHOT: her body and face are turned three-quarters toward the picture-RIGHT, exactly like the figure in image 2, while her eyes look at the viewer. Copy the slight head tilt of image 2. One hand is raised to her collar just under the brooch, fingers loosely curled inward, the backs of the fingers toward the viewer, in the same place as the hand in image 2.
FACE RULE with no change: completely deadpan, the mouth a tiny flat line. """ + HANDS),
    ("S07", "Chu B 拍｜同上，和 A 每拍互切（不再生成：作者定用第 1 批 S07_1，已入库 assets/chu_B_S07_1.png）", "原片 7.4 s 的姿势原向：近景、身体和脸朝画面左侧、手蜷在领口、轻微歪头，chu 嘴（比鼻子深的小圆 o）。成片里放在画面右半边、G2 绿底。",
     "main", "1024x1024", [REF_TILT, "refs/pose_chuB_orig_gray.png"],
     CLOSE + """
SHOT: her body and face are turned three-quarters toward the picture-LEFT, exactly like the figure in image 2, while her eyes look at the viewer. Copy the slight head tilt of image 2. One hand is raised to her collar just under the brooch, fingers loosely curled inward, the backs of the fingers toward the viewer, in the same place as the hand in image 2.
""" + CHU_MOUTH + " " + HANDS),
    ("S02", "幸せ｜3.3–4.3 s（作废：作者 11-02 决定星瞳完全不用）", "星瞳不露脸，双手交握在裙前。", "xt", "1024x1536", [REF_XT, REF_B],
     """SHOT: front view, standing straight. The top edge of the picture cuts across her neck just below the chin; the bottom edge is at mid-thigh. Both arms hang down in front of her body and her hands are loosely clasped together in front of the skirt at hip height, fingers interlaced, the pink scrunchie visible on her right wrist (picture-LEFT). Shoulders relaxed, the ID card hanging straight at mid-chest, the silver hair falling down both sides. """ + HANDS),
    ("S01", "声を聴くだけで｜0.0–3.3 s", "原片 1.0 s 的姿势：近景、一手捏住耳机、头往一侧偏，眼皮比平时再垂一点，像在专心听。",
     "main", "1024x1024", [REF_B, "refs/pose_S01_orig_gray.png"],
     CLOSE + """
SHOT: copy the body angle and the head tilt of image 2. She wears small white wired earbuds; a thin white cable runs from each ear down to her chest. Her left hand (on the picture-RIGHT) is raised to her ear exactly like the hand in image 2, thumb and index finger lightly pinching the earbud, the other fingers loosely curled.
The ONE change from the FACE RULE: her eyelids are lowered a little more than in image 1, as if she is listening closely; no smile. """ + HANDS),
    ("S03B", "幸せ｜4.3–5.1 s（推荐）", "她本人在胸前双手比心，脸完全淡定（原片这里没有她的镜头，不给姿势参考）。",
     "main", "1024x1024", [REF_B],
     """Framing: a close-up from the top of her head down to her chest, her face about a third of the picture width; the heart ahoge stays inside the picture.
SHOT: front view, head tilted very slightly toward the picture-LEFT. Both hands are raised in front of her chest, just below her chin, and form one big heart: the curled index fingers meet at the top, the thumbs touch at the bottom point; the heart shape is clearly readable and its inside is empty. FACE RULE with no change: completely deadpan, as if making a heart is nothing special. """ + HANDS),
    ("S03A", "幸せ｜4.3–5.1 s（作废：框住的是星瞳，星瞳不用了）", "第一人称视角：她的双手从下方伸进画面比心，叠在星瞳那张上框住她。",
     "main", "1536x1024", [REF_B],
     """SHOT: point of view. Two large hands (the viewer's own hands) enter from the bottom corners of the picture and form one big heart in the middle: the curled index fingers meet at the top, the thumbs meet at the bottom point. The hands have the pale cream skin of image 1, and each wrist wears a puffy cream flower-petal cuff. The inside of the heart is empty background. Nothing else in the picture: no face, no body. """ + HANDS),
    ("S04", "なの｜5.5–5.9 s（作废：作者 11-02 先选了 S04_1，随后决定星瞳完全不用）", "原片 5.7 s 的姿势：星瞳不露脸，侧身，一只手捏着领结。",
     "xt", "1024x1536", [REF_XT, REF_B, "refs/pose_S04_orig_gray.png"],
     """SHOT: copy the body angle, the framing and the hand position of image 3. The top edge of the picture cuts across her neck just below the chin. Her right hand (the one with the pink scrunchie) is raised to her collar and gently pinches one tail of the blue striped bow tie between thumb and index finger; the other arm hangs relaxed at her side. """ + HANDS),
    ("S05", "なの!｜5.9–6.3 s（作废：作者 11-02「奶绿是女性，捏领口太奇怪」，改用 S05A/B/C）", "原片 6.05 s 的姿势（我之前看错了，不是捂嘴）：双手捏住领口往上提到下巴，像想躲到领子后面；脸一点没变，只有腮红大一圈、深一档。斜线腮红和汗滴之后用代码叠。",
     "main", "1024x1024", [REF_B, "refs/pose_S05_orig_gray.png"],
     CLOSE + """
SHOT: front view; copy the hand positions of image 2. Both hands pinch the front edges of her lace jabot and collar and pull them up toward her chin, as if trying to hide behind her collar; the fingertips reach just under her chin and the mouth stays visible.
The ONE change from the FACE RULE: her blush patches are a little larger and one shade deeper peach. Everything else on her face is as calm as in image 1: half-lidded eyes looking straight at the viewer, level eyebrows, the tiny flat mouth. She is flustered, but her face refuses to show it. """ + HANDS),
    ("S09", "こんなに臆病だっけ?｜17.0–20.5 s（方案 A：照原片竖食指，第 2 批已出）", "原片 18.0 s 的姿势：正面近景，画面左下竖起食指；嘴角往下压 1 格，有点不服气。",
     "main", "1024x1024", [REF_B, "refs/pose_S09_orig_gray.png"],
     CLOSE + """
SHOT: front view; copy the framing and the raised hand of image 2. Her right hand (on the picture-LEFT) is raised at the lower left of the picture beside her chin, index finger pointing straight up, the other fingers curled, palm facing the viewer.
The ONE change from the FACE RULE: the corners of her tiny mouth turn down by one pixel, a small sulky line. Eyes and eyebrows as calm as in image 1. """ + HANDS),
    # —— 11-02 重新设计（作者：不要完全照原片男生的动作，和歌词搭点边就行，要适合无口的女生）——
    ("S05A", "なの!｜5.9–6.3 s（方案 A，推荐）", "长发挡嘴：双手各捏一缕自己的长发拉到嘴前，像面纱一样挡住嘴和下巴，只露眼睛；眼神不变。嘴上说「就是幸福啦」，却把嘴藏起来。腮红加深、斜线腮红、汗滴出图后用代码加。",
     "main", "1024x1024", [REF_B],
     CLOSE_FREE + """
SHOT: front view, head tilted very slightly down, eyes looking up at the viewer. With both hands she lifts one long lock of her own lavender hair from each side of her face and draws the two locks across in front of her face like a veil, so they cover her mouth and chin; the locks cross just below her nose. Her hands stay beside her cheeks, holding the locks loosely between thumb and fingers. Her eyes, eyebrows and blush patches stay fully visible above the hair.
The ONE change from the FACE RULE: """ + BLUSH_UP + """. Everything visible above the hair is as calm as in image 1: half-lidded eyes looking at the viewer, level eyebrows. She is flustered, but her face refuses to show it. """ + HANDS),
    ("S05B", "なの!｜5.9–6.3 s（方案 B）", "移开视线：头微微侧开，眼睛瞟向画面外不看镜头，一只手的食指卷着一缕头发；腮红加深。害羞但嘴硬。",
     "main", "1024x1024", [REF_B],
     CLOSE_FREE + """
SHOT: her head turned about 20 degrees toward the picture-RIGHT. Her left hand (on the picture-RIGHT) is raised to cheek height and twirls a thin lock of her hair around the index finger.
The changes from the FACE RULE: her eyes glance sideways toward the picture-RIGHT edge, away from the viewer, with the same half-lidded lids; and """ + BLUSH_UP + """. Eyebrows level, the mouth the same tiny flat line. """ + HANDS),
    ("S05C", "なの!｜5.9–6.3 s（方案 C）", "胸前小拳头「ぐっ」：双手在下巴下面握成小拳头，像在用力强调「なの!」，脸却完全没跟上，一点表情都没有。",
     "main", "1024x1024", [REF_B],
     CLOSE_FREE + """
SHOT: front view. Both hands are raised in front of her chest just below her chin, each clenched into a small soft fist with the knuckles toward the viewer, elbows tucked in to her sides: a tiny determined "I mean it!" gesture.
FACE RULE with no change: completely deadpan, as if the gesture had nothing to do with her face. """ + HANDS),
    ("S09B", "こんなに臆病だっけ?｜17.0–20.5 s（方案 B，推荐）", "食指抵下巴 + 歪头 + 眼睛往上瞟：在自问「我有这么胆小吗?」，嘴角往下压 1 格，有点不服气。",
     "main", "1024x1024", [REF_B],
     CLOSE_FREE + """
SHOT: front view, head tilted about 15 degrees toward the picture-RIGHT shoulder. Her right hand (on the picture-LEFT) is raised and the tip of her index finger rests on her chin just below the corner of her mouth, the other fingers loosely curled.
The changes from the FACE RULE: her eyes look up and toward the picture-RIGHT, as if wondering about something, with the same half-lidded lids; and the corners of her tiny mouth turn down by one pixel, a small sulky line. Eyebrows level. """ + HANDS),
    # —— 11-02 星瞳撤出，两个空位换成奶绿自己的镜头 ——
    ("S02H", "幸せ（第一个）｜3.3–4.3 s（方案 A，推荐）", "呆毛特写：脸完全不变，头顶的心形呆毛「啵」地竖起来——嘴不说，呆毛出卖了她。出一张呆毛竖着的图，弹跳用代码做（把呆毛那一块抠出来按拍子弹一下，再冒两颗像素小心心）。",
     "main", "1024x1024", [REF_B],
     """Framing: a close-up from just above the tip of the heart ahoge down to her chin, her face about half the picture width, centred; the wing ornaments are cut off by the picture's sides.
SHOT: front view. Her heart-shaped ahoge stands straight up from the top of her head, perky and slightly larger than in image 1, a clean closed heart outline with plain background inside it, clearly separated from the rest of her hair.
FACE RULE with no change: completely deadpan, half-lidded eyes looking at the viewer, as if she has no idea what her hair is doing."""),
    ("S02C", "幸せ（第一个）｜3.3–4.3 s（方案 B）", "不露脸：双手交叠轻轻按在胸口的绿宝石胸针上，像把刚听到的声音收在心口。保留原片这里「只拍身体」的节奏。",
     "main_noface", "1024x1024", [REF_B],
     NOFACE_TOP + """
SHOT: front view, standing straight. Both hands are pressed gently one over the other on her chest, over the dark-green oval brooch, fingers relaxed and slightly curved, as if holding something precious close to her heart. The red-and-white ribbons hang below her hands. """ + HANDS),
    ("S04P", "なの｜5.5–5.9 s（方案 A，推荐）", "不露脸：两根食指在胸前对戳（👉👈），害羞的小动作；下一拍「なの!」再露出她用头发挡嘴的脸。",
     "main_noface", "1024x1024", [REF_B],
     NOFACE_TOP + """
SHOT: front view. Both hands are raised in front of her chest just below the brooch; the tips of her two index fingers touch each other, pointing inward, in a shy fidgeting "finger poke" gesture; the other fingers are loosely curled and the thumbs relaxed, elbows close to her sides. """ + HANDS),
    ("S04R", "なの｜5.5–5.9 s（方案 B）", "不露脸：手指捏着胸针下垂的红丝带一端，轻轻绕着玩。",
     "main_noface", "1024x1024", [REF_B],
     NOFACE_TOP + """
SHOT: three-quarter view, her body turned slightly toward the picture-LEFT. Her right hand (on the picture-LEFT) is raised to her chest and pinches the end of one of the dark-red ribbons hanging from the brooch between thumb and index finger, twisting it slightly; the other arm hangs relaxed at her side. """ + HANDS),
]

# 局部改图（localedit.py：只在双眼椭圆里改，seam 贴回）
EDITS = [
    ("E08b", "眨眼帧｜10.1–13.6 s", "在 B 原图上只把双眼改成闭眼。", REF_B),
    ("E09b", "眨眼帧｜17.0–20.5 s", "在选定的 S09B_2 上只把双眼改成闭眼。", "assets/okubyo_S09B_2.png"),
]
EDIT_PROMPT = """Change ONLY the eyes; this is a pixel-art image and the pixel size must stay exactly the same. Both eyes are now closed: each eye becomes a short, gently downward-curved line of dark indigo pixels lying where the upper lash line was, about as wide as the open eye was. No iris, no white, no lashes sticking out, no tears. The bangs crossing the eyes, the blush patches, the face outline and everything outside the eyes stay exactly as they are."""

BATCHES = [
    ("第 2 批：其余镜头（已跑）", ["S01", "S03B", "S04", "S05", "S09"]),
    ("第 2b 批：重新设计（作者选了 S05A + S09B，已跑）", ["S05A", "S09B"]),
    ("第 2c 批：星瞳撤出后的两个空位，作者选方案后再跑", ["S02H", "S02C", "S04P", "S04R"]),
    ("第 3 批：闭眼局部改", ["E08b", "E09b"]),
]

def build(shot):
    sid, _, _, who, _, refs, body = shot
    has_pose = any("pose_" in r for r in refs)
    if who == "main":
        return "\n\n".join([refs_main(has_pose), ID_MAIN, FACE_RULE, body, STYLE_MAIN])
    if who == "main_noface":  # 只拍身体的镜头，脸在画面外，不需要脸部规则
        return "\n\n".join([refs_main(has_pose), ID_MAIN, body, STYLE_MAIN])
    return "\n\n".join([refs_xt(has_pose), ID_XT, body, STYLE_XT])

def main():
    pdir = ROOT / "prompts"
    pdir.mkdir(exist_ok=True)
    for s in SHOTS:
        (pdir / f"{s[0]}.txt").write_text(build(s) + "\n")
    for e in EDITS:
        (pdir / f"{e[0]}.txt").write_text(EDIT_PROMPT + "\n")

    lines = ["# 生成清单与提示词 v2（待 作者看过再生成）", "",
             "由 `tools/build_prompts.py` 生成，改提示词请改那个文件。每个提示词出 3 张候选，放 `candidates/`，作者点头的才进 `assets/`。", "",
             "模型 gpt-image-2.5-sunburst，quality high，走 `../tools/imagegen/gen.py`。图 8（正面平静脸）直接用 B 原图，眼睛大特写从 B 裁，都不用生成。", "",
             "v2 改动（作者 11-01 看第 1 批：捧脸姿势不好看，用原片姿势 + 无口 + 轻微歪头）：原片里有对应镜头的都加原片那一帧的灰度图当姿势参考（`refs/pose_*_gray.png`），取景改成原片的近景；Chu 段的脸照 作者的歪头图 `refs/main_author_0124.png`。第 1 批的 S06/S07（v1）不用，v1 提示词留在 `candidates/batch-1/*.json`。", "",
             "## 分批", ""]
    for name, ids in BATCHES:
        lines.append(f"- **{name}**：{'、'.join(ids)}（{len(ids)} 个提示词 × 3 张 = {len(ids) * 3} 张）")
    lines += ["", "Chu 段 A/B 已定（作者 11-01：「这两张可以了不用重跑了」），S06/S07 的 v2 提示词留作记录不跑。S02 第 1 批已出 3 张，等 作者挑。11-02 星瞳完全撤出：S02、S04、S03A 作废，空位换成 S02H/S02C 二选一、S04P/S04R 二选一。S05 定 S05A，S09 定 S09B。S03A / S03B 二选一（推荐 B：比心时那张脸面无表情，正好是反差的地方）。", "",
              "## 每张图", ""]
    for s in SHOTS:
        sid, when, idea, who, size, refs, _ = s
        lines += [f"### {sid}　{when}", "", f"- 想法：{idea}",
                  f"- 参考图（按顺序 = image 1, 2, 3）：{'、'.join(refs)}　尺寸：{size}", "", "```text", build(s), "```", ""]
    lines += ["## 闭眼局部改", ""]
    for eid, when, idea, base in EDITS:
        lines += [f"### {eid}　{when}", "", f"- 想法：{idea}", f"- 底图：{base}；遮罩：双眼两个椭圆（含睫毛线，不含刘海以外的头发）", ""]
    lines += ["```text", EDIT_PROMPT, "```", ""]
    (ROOT / "docs" / "03-生成清单与提示词.md").write_text("\n".join(lines))
    print("wrote", len(SHOTS) + len(EDITS), "prompts + docs/03")

if __name__ == "__main__":
    main()
