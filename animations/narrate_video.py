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

# Voiceover for Lab 00-Prep — keep in lockstep with scene_lab00_prep.py banners
LAB00_PREP_SCRIPT = [
    # Title
    ("You think in time: one line, then the next. A chip thinks in space: the circuit is always there.", 0.6),

    # Act 0
    ("In Python, a function is a recipe: the CPU fetches one instruction, does it, then fetches the next.", 0.5),
    ("A chip is not a recipe. The adders and the multiplier are physical objects sitting on the die at the same time.", 0.5),
    ("Same math. Two machines. One walks a list. The other is the list, wired in metal.", 0.7),

    # Act 1
    ("To compute y equals (a plus b) times (c plus d), a CPU can point its program counter at only one line.", 0.5),
    ("The chip has no program counter. With a=3, b=2, c=4, d=1, both adders show 5, and the multiplier already holds 25.", 0.5),
    ("This is not threading. You placed two adder objects on the die. They exist together, so they finish while the CPU is still walking.", 0.7),

    # Act 2
    ("In Python, a times b and arr of i look equally cheap. In silicon they are not even the same sport.", 0.5),
    ("An eight-bit multiply-accumulate is about zero point two picojoules. Fetching that byte from off-chip DRAM is about two hundred picojoules — a thousand times more.", 0.5),
    ("The ratio is one thousand. A linear bar would hide the multiply. Longer wires hold more charge, so the fetch costs more than the math.", 0.7),

    # Act 3
    ("A combinational gate is an Excel formula: change an input, the output updates immediately. It has no memory.", 0.5),
    ("A D flip-flop is a snapshot. On the rising clock edge it samples D and freezes it at Q until the next tick.", 0.5),
    ("Data must be stable just before the edge, and stay stable just after. If it is still changing, you capture garbage — like reading a dict while another thread writes it.", 0.7),

    # Act 4
    ("The number one RTL bug for software people: blocking equals versus non-blocking less-than-equals.", 0.5),
    ("Blocking assignment is ordinary Python: b equals a, then c equals b. C sees the new B. A two-stage pipeline collapses into a wire.", 0.5),
    ("Non-blocking is tuple unpack: b, c equals a, b. Both right-hand sides are the old values. The pipeline survives the clock tick.", 0.7),

    # Act 5
    ("When you call torch.matmul, the CPU is not doing the multiply. It writes a small descriptor, then rings one memory-mapped register: a doorbell.", 0.5),
    ("That write wakes a DMA engine. Tensors stream over PCIe into on-chip SRAM while Python keeps running.", 0.5),
    ("Double buffering is the hardware version of ping-pong queues: one SRAM bank feeds the array while the other fills from the bus.", 0.7),

    # Act 6
    ("You cannot git revert a chip. A tape-out is tens of millions of dollars. So we test the design as software first.", 0.5),
    ("Cocotb drives the pins from Python. This adder is combinational, so the sum updates with no clock edge.", 0.5),
    ("Carry three rules into every lab: the circuit is a live graph, clocked state uses less-than-equals, and moving data costs more than math.", 0.8),
]

# Complete Voiceover Script for Lab 04 Masterclass (Timed to match scene acts)
LAB04_SCRIPT = [
    # Act 1: The Software Paradox & The LLM Scaling Crisis
    ("Welcome to Hardware AI Acceleration. Today, we bridge the fundamental gap between software code in PyTorch and physical silicon gates on a chip.", 0.5),
    ("As software engineers, we write matrix multiplications as clean single-line abstractions, like Q times K transpose in self-attention.", 0.5),
    ("Under the hood, a standard sequential CPU translates this into three nested loops, running with O of N cubed time complexity.", 0.5),
    ("In modern Large Language Models with one-million-token context windows, a single attention head requires over one trillion arithmetic operations.", 0.5),
    ("On standard CPUs, this causes catastrophic cache thrashing. The processor spends ninety percent of its clock cycles and power simply waiting for memory from DRAM.", 0.5),
    ("How do Google TPUs and NVIDIA Tensor Cores solve this? The answer lies in Spatial Hardware Computing.", 0.8),

    # Act 2: The Physical Silicon Limits & The 1,000x Memory Energy Wall
    ("In computer science, we analyze algorithmic Big-O complexity. But in silicon physics, wire distance and energy dissipation dictate everything.", 0.5),
    ("Look at the physical numbers: performing an eight-bit multiply-accumulate operation takes just zero-point-two picojoules of energy.", 0.5),
    ("Accessing an on-chip SRAM cache takes five picojoules. But fetching that same number from external DRAM takes two hundred picojoules!", 0.5),
    ("That is a one-thousand-times energy penalty just to move a number across circuit board traces!", 0.5),
    ("A CPU moves numbers back and forth over a shared bus on every iteration. To achieve massive AI throughput, we must never re-read weights from memory.", 0.5),
    ("This fundamental insight gave birth to the Weight-Stationary Systolic Array.", 0.8),

    # Act 3: Inside the Weight-Stationary Processing Element (PE)
    ("Let us zoom into the silicon floorplan and inspect a single Processing Element, or P-E.", 0.5),
    ("Each Processing Element contains a dedicated weight register, an eight-bit MAC engine, an activation forwarding register, and a partial sum forwarding register.", 0.5),
    ("Weights are pre-loaded once before matrix multiplication begins, and remain locked stationary in local flip-flops.", 0.5),
    ("Activations stream horizontally from West to East. Partial sums accumulate vertically from North to South.", 0.5),
    ("There are zero shared memory buses. Every Processing Element communicates only with its immediate physical neighbors.", 0.5),
    ("Because wire lengths are microscopic, parasitic resistance is near zero, allowing modern tensor engines to clock at gigahertz speeds.", 0.8),

    # Act 4: The 2D Systolic Wavefront & Activation Skewing
    ("Now, connect these Processing Elements into a two-dimensional spatial grid. Here we encounter the central architectural puzzle: Activation Skewing.", 0.5),
    ("In software, line one and line two execute whenever called. But in physical hardware, flip-flop registers introduce a one-clock-cycle propagation delay.", 0.5),
    ("PE zero-zero produces its partial sum at Clock One. That sum takes one full clock cycle to travel South to PE one-zero.", 0.5),
    ("If Row One activations entered at Clock One, PE one-zero would have no partial sum yet! It would compute corrupted garbage.", 0.5),
    ("The architectural solution is input skewing. Row k is delayed by exactly k clock cycles using hardware D flip-flop shift registers.", 0.5),
    ("Let us trace the wavefront clock by clock with real numbers: input vector A equals one, two; weight matrix W equals five, six, seven, eight.", 0.5),
    ("At Clock One, activation one enters PE zero-zero. One times five equals five. The partial sum five latches into the South register.", 0.5),
    ("At Clock Two, activation one hops East to PE zero-one. Skewed activation two enters PE one-zero. Five plus two times seven equals nineteen! Column zero is complete!", 0.5),
    ("At Clock Three, activation two hops East to PE one-one. Partial sum six flows South. Six plus two times eight equals twenty-two! Column one is complete!", 0.5),
    ("At Clock Four, the final result vector C equals nineteen, twenty-two streams out of the chip's bottom pins.", 0.5),
    ("Checking our software math: one times five plus two times seven is nineteen, and one times six plus two times eight is twenty-two. The physical silicon executed the exact dot product!", 0.8),

    # Act 5: Architectural Checkpoint & Challenge
    ("Pause and think: Why is this called a Systolic Array? Like the medical systole of a human heart pumping blood, data pulses through the silicon grid on every rising clock edge.", 0.5),
    ("Try this test: for input vector three, four and weight matrix one, two, three, four, the result vector is fifteen, twenty-two.", 0.8),

    # Act 6: Pre-Silicon Verification & Career Roadmap
    ("In production, Google TPUs scale this exact architecture to massive one-hundred-twenty-eight by one-hundred-twenty-eight systolic arrays, performing over sixteen thousand operations every clock cycle.", 0.5),
    ("Because chip tape-outs cost fifty to one hundred million dollars, hardware teams verify everything pre-silicon using Python Cocotb testbenches driving synthesizable SystemVerilog.", 0.5),
    ("The tech industry faces a massive shortage of engineers who understand both software frameworks and hardware architecture. Bridging this gap places you in the highest-compensation tier of AI engineering.", 0.5),
    ("Your next step: open rtl slash systolic array dot sv, run the Cocotb testbench, and launch the interactive visualizer to see the wavefront live.", 0.5),
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
