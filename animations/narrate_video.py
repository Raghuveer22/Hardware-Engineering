#!/usr/bin/env python3
"""
Automated Voiceover & Audio Narration Generator for Hardware AI Video Suite.

Uses macOS high-clarity speech synthesis ('say' with 'Samantha' or 'Daniel')
to generate synchronized, professional voiceover narration, then muxes it
directly into Manim MP4 videos using FFmpeg.

Usage:
    python animations/narrate_video.py --scene 00_prep
    python animations/narrate_video.py --scene 04
    python animations/narrate_video.py --voice Samantha
"""

import sys
import os
import subprocess
import json
import argparse
import shutil
from pathlib import Path

ANIMATIONS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ANIMATIONS_DIR.parent
VIDEOS_DIR = PROJECT_ROOT / "media" / "videos"

# Voiceover for Lab 00-Prep — keep in lockstep with scene_lab00_prep.py.
# Pauses cover on-screen questions and names, which are not spoken.
LAB00_PREP_SCRIPT = [
    ("You already know this. a is 3, b is 2, c is 4, and d is 1. Add on the left, add on the right, then multiply those two results. Nothing here is new arithmetic. What changes is who does each step, and when that result is allowed to move.", 0.3),
    ("A CPU runs one line, then the next, then the one after that. Right now the only live line is t1 equals a plus b. The second add and the multiply are still waiting. Until this line finishes, those other two lines do not run.", 1.6),
    ("Watch only the left adder. The inputs on it are 3 and 2. Add them yourself before the 5 appears: 3 plus 2. The right adder is still empty, and the multiply has nothing to read. The CPU is still pointing at that first line.", 0.3),
    ("Now the right adder. Its inputs are 4 and 1. Add those before its 5 appears: 4 plus 1. Both adders will hold the same number, and neither result has traveled yet. The multiply is still waiting on the two wires beneath it.", 0.3),
    ("Both fives leave the adders and ride the short wires into the multiply. Do not wait for the CPU. Multiply them yourself, 5 times 5, and say that product out loud. It stays hidden until you have had a moment to answer.", 0.4),
    ("There is the product, 25, already fixed by the two fives. Look back at the CPU. It is still on t1 equals a plus b. The other two lines never became the current line. The graph held 5, 5, and 25 while that first line stayed put.", 1.6),
    ("The multiply is already finished. A byte from memory is still charging the long wire, and that trip is not free. The short wire costs about two tenths of a picojoule. The long wire costs about two hundred. The arithmetic was the cheap part.", 1.6),
    ("The pair on the left is only a wire. Change the input from 0 to 1 and the output moves with it, in the same moment, with nothing stored between them. There is no tick. If the input falls back to 0, the output falls back too.", 0.3),
    ("The box on the right waits. Its input changes to 1, and its output stays the old 0. On the timeline the data edge sits well to the left of the tick, so the new bit has been quiet. When the tick arrives, the output copies that settled 1.", 0.3),
    ("Look at the shaded gap between that data edge and the tick. The bit arrived early, sat still, and the tick took a clean picture of it. The output became 1 because the change and the tick were far apart. Keep your eye on the edge.", 0.3),
    ("The same edge now slides right, into the tick itself. The bit is still changing while the picture is taken, so there is no settled value to copy. The output does not become 1. It comes back as X, which means the box stored garbage.", 1.6),
    ("C is supposed to receive what B holds. B holds 20, and A holds 10. Watch the ordered write. B is updated to 10 first, and the 20 leaves the box. C then reads B and receives 10. The 20 that C needed never arrives.", 0.3),
    ("Put 20 back into B, and clear C. This time both right-hand sides are read before either write. The 10 from A and the 20 from B are held still, then the writes land together. B receives 10, and C still receives 20.", 1.6),
    ("New numbers, same two writes. A now holds 4, and B now holds 7. C is empty again. Use the rule you just watched. If the writes go in order, B changes before C reads. If the right-hand sides freeze, C reads the value B holds now.", 1.6),
    ("The frozen pair lands. B receives 4, the value A held. C receives 7, the value B held before either write. Check the ordered alternative in your head: that path would have handed C a 4. The cells show 7, so the old value moved.", 0.3),
    ("The CPU writes a single 1 into this register. That 1 is the whole message. As soon as the write finishes, the CPU dims and steps away. It does not stay to push the remaining bytes. The register holds the 1 so the other side can notice.", 1.6),
    ("Count the bytes into the left bank: 1, then 2, then 3, then 4. Those four arrive from the bus after the CPU has already left. The right bank is not waiting on them. It is already working the previous batch, so the banks are on different jobs.", 1.6),
    ("Same adder, driven the way a Python check drives it. First stimulus: 3 plus 2. You already know this pair from the expression above. The sum is 5. The circle does not remember the expression. It only adds the two numbers placed on it.", 0.3),
    ("Second check, smaller on purpose. 1 plus 1. Add it before you trust the circle: the only honest answer is 2. If the adder had kept the previous 5, this check would fail. The old sum leaves, and 2 replaces it.", 0.3),
    ("Third check: 8 plus negative 1. The bits of 8 are 1000, and the signed nibble for negative 1 is 1111. Add the columns yourself. The low four bits are 0111, and that pattern is 7. Eight plus negative one is 7.", 0.3),
    ("The expression above never left. The two adds and the multiply were already live while the CPU sat on the first line. A register kept an old value that an ordered write would have destroyed. Moving a byte on the long wire cost more than the multiply.", 0.4),
]

# Lab 04 — keep in lockstep with scene_lab04_systolic_array.py.
# Pauses cover the on-screen question and the names, which are not spoken.
LAB04_SCRIPT = [
    ("Two rows want to enter on the same tick. The top cells hold weights five and six, and the bottom cells hold seven and eight. Activation one is still at the top door. Activation two is already waiting on the weight seven cell, which is too soon.", 0.3),
    ("The partial sum from the cell above has not arrived. The weight seven cell multiplies anyway, and the center fills with an X. That X is garbage. A product written while the partial is missing is not a number anyone can pass downward.", 1.6),
    ("Hold the two for one tick, outside the cell, in the small box on the left. The top row is allowed to go first. The two waits there until a real partial exists above it. We will not feed the lower cell early a second time.", 0.3),
    ("Tick zero is only the hold. Every center is still empty, and the two is outside the grid. On the next tick the top left cell is the only one allowed to multiply. Be ready to take one times five as soon as that activation steps inside.", 0.3),
    ("Tick one. Activation one steps into the top left cell, and the weight waiting there is five. One times five. Do that multiply before the center of the cell prints a number. The two is still sitting in the hold box, unused.", 0.3),
    ("Five now sits in the top left cell, and a copy of it travels down into the gap. The held two finally enters the weight seven cell. Two times seven, then add that product to the five from above. Finish the whole sum before the lower cell prints it.", 0.3),
    ("Nineteen is correct. The two waited one tick, so it met the five instead of an empty partial from above. The little box on the left is what kept the lower cell patient. The top left cell did its multiply alone, on the earlier tick.", 1.6),
    ("Next tick, the other column starts. Activation one has passed to the right, into the cell whose parked weight is six. One times six. Work that product before the center of the top right cell changes. The lower right cell is still empty.", 0.3),
    ("Six is the partial above the bottom right cell, and the two passes across into the weight eight cell. Two times eight, then add that product to the six. Finish the sum before the bottom right cell prints it. The center has not printed yet.", 0.3),
    ("Twenty two just landed in the bottom right cell. Column zero finished at nineteen, and column one finished at twenty two. Each lower cell waited for a partial from above and an activation from the left. The whole grid kept the same beat.", 1.6),
    ("Same grid, new weights. The top row is now one and two. The bottom row is now three and four. The centers are clear again. If the lower activation waits one tick, the way the two just waited, you can call both columns before either total prints.", 0.3),
    ("First, try the wrong timing on purpose. Activation three is at the top door and activation four is already at the weight three cell. The partial from above is missing again. The lower left cell should not know a real sum yet. Let the early four step in.", 0.3),
    ("The lower cell wrote garbage again. Four arrived before the top cell could multiply three by one and hand a partial down. Clear that X out of the center. We will hold four for one tick and let the top left cell go first.", 0.3),
    ("Four steps back into the hold box and waits there. Three enters the top left cell, whose weight is now one. Three times one. Do that small product before the center prints anything. The held four still has not touched the lower cell.", 0.3),
    ("Three is now the partial sitting above. Four leaves the hold box and meets the cell whose weight is three. Four times three, then add that product to the three coming down. That sum is the whole first column. Call it before the cell shows you.", 1.6),
    ("Fifteen just landed in column zero. That was three times one, plus four times three. The hold gave the top cell a tick to build the partial, and the lower cell added the second product. The right hand column has not run yet.", 0.3),
    ("Activation three passes to the right, into the cell whose parked weight is two. Three times two. Work that product before the top right center changes. Four is still moving across, toward the bottom cell whose weight is four.", 0.3),
    ("Six travels down as the partial from the top right cell. Four arrives beside the weight four. Four times four, then add that product onto the six. This is the whole second column. Finish the add before the number prints in the cell.", 0.3),
    ("Twenty two landed again, on the new weights. Column zero was fifteen, and column one is twenty two. The lower activation waited one tick, the partial from above was real, and the early row did not get to write garbage this time.", 0.4),
]

SCRIPTS = {
    "00_prep": (
        LAB00_PREP_SCRIPT,
        "scene_lab00_prep",
        "Lab00PrepPrimer",
        "lab00_prep_master_voiceover.wav"
    ),
    "04": (
        LAB04_SCRIPT,
        "scene_lab04_systolic_array",
        "Lab04SystolicArray",
        "lab04_master_voiceover.wav"
    ),
}


def generate_audio_track(script, output_wav, voice="Samantha"):
    """Generate audio speech files and concatenate them with exact pauses."""
    if sys.platform != "darwin" or not shutil.which("say"):
        print("❌ Error: Speech synthesis via 'say' is only available natively on macOS.")
        print("   On Windows/Linux, you can provide an external WAV voiceover or run on macOS.")
        sys.exit(1)

    if not shutil.which("ffmpeg"):
        print("❌ Error: 'ffmpeg' executable not found in PATH!")
        print("   macOS: brew install ffmpeg")
        print("   Windows: winget install Gyan.FFmpeg")
        sys.exit(1)

    temp_dir = ANIMATIONS_DIR / "temp_audio"
    temp_dir.mkdir(exist_ok=True)

    file_list = []
    print(f"🎙 Generating voiceover using macOS voice '{voice}'...")

    for idx, (sentence, pause_sec) in enumerate(script):
        aiff_path = temp_dir / f"line_{idx:03d}.aiff"
        wav_path = temp_dir / f"line_{idx:03d}.wav"

        # Generate speech
        subprocess.run(["say", "-v", voice, "-o", str(aiff_path), sentence], check=True)
        # Convert to WAV
        subprocess.run([
            "ffmpeg", "-y", "-i", str(aiff_path),
            "-ar", "44100", "-ac", "1", str(wav_path)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        file_list.append(str(wav_path))

        # Add pause silence
        if pause_sec > 0:
            silence_path = temp_dir / f"silence_{idx:03d}.wav"
            subprocess.run([
                "ffmpeg", "-y", "-f", "lavfi", "-i",
                f"anullsrc=r=44100:cl=mono", "-t", str(pause_sec),
                str(silence_path)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            file_list.append(str(silence_path))

    # Concat file list
    concat_txt = temp_dir / "concat.txt"
    with open(concat_txt, "w") as f:
        for fpath in file_list:
            f.write(f"file '{fpath}'\n")

    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0",
        "-i", str(concat_txt), "-c", "copy", str(output_wav)
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    print(f"✅ Generated master audio track: {output_wav}")


def mux_video_and_audio(input_mp4, input_wav, output_mp4):
    """Mux video and audio into final production video, looping/padding audio as needed."""
    print(f"🎬 Muxing video and audio into {output_mp4}...")
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_mp4),
        "-i", str(input_wav),
        "-filter_complex", "[1:a]apad[aout]",
        "-map", "0:v",
        "-map", "[aout]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_mp4)
    ]
    subprocess.run(cmd, check=True)
    print(f"🎉 Production video ready: {output_mp4}")


def main():
    parser = argparse.ArgumentParser(description="Voiceover Narration Generator")
    parser.add_argument("--scene", default="00_prep", choices=["00_prep", "04", "prep", "00"], help="Scene key to narrate")
    parser.add_argument("--voice", default="Samantha", help="macOS TTS voice (Samantha, Daniel, etc.)")
    parser.add_argument("--quality", default="720p30", choices=["480p15", "720p30", "1080p60"], help="Video quality directory")
    args = parser.parse_args()

    key = "00_prep" if args.scene in ["00_prep", "prep", "00"] else "04"
    script, folder, scene_name, wav_name = SCRIPTS[key]

    target_video = VIDEOS_DIR / folder / args.quality / f"{scene_name}.mp4"
    if not target_video.exists():
        # Fallback to any existing quality folder
        for q in ["480p15", "720p30", "1080p60"]:
            alt = VIDEOS_DIR / folder / q / f"{scene_name}.mp4"
            if alt.exists():
                target_video = alt
                break

    if not target_video.exists():
        print(f"❌ Video not found at {target_video}. Please render it first!")
        sys.exit(1)

    master_audio = ANIMATIONS_DIR / "temp_audio" / wav_name
    output_video = target_video.parent / f"{scene_name}_narrated.mp4"

    generate_audio_track(script, master_audio, voice=args.voice)
    mux_video_and_audio(target_video, master_audio, output_video)


if __name__ == "__main__":
    main()
