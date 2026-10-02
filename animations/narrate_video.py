#!/usr/bin/env python3
"""
Automated Voiceover & Audio Narration Generator for Hardware AI Video Suite.

Uses macOS high-clarity speech synthesis ('say' with 'Samantha' or 'Daniel')
to generate synchronized, professional voiceover narration, then muxes it
directly into Manim MP4 videos using FFmpeg.

Usage:
    python animations/narrate_video.py --scene 04
    python animations/narrate_video.py --voice Samantha
"""

import sys
import os
import subprocess
import json
from pathlib import Path

ANIMATIONS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = ANIMATIONS_DIR.parent
VIDEOS_DIR = PROJECT_ROOT / "media" / "videos"

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


def generate_audio_track(output_wav, voice="Samantha"):
    """Generate audio speech files and concatenate them with exact pauses."""
    temp_dir = ANIMATIONS_DIR / "temp_audio"
    temp_dir.mkdir(exist_ok=True)

    file_list = []
    print(f"🎙 Generating voiceover using macOS voice '{voice}'...")

    for idx, (sentence, pause_sec) in enumerate(LAB04_SCRIPT):
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
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(output_mp4)
    ]
    subprocess.run(cmd, check=True)
    print(f"🎉 Production video ready: {output_mp4}")


def main():
    target_video = VIDEOS_DIR / "scene_lab04_systolic_array" / "720p30" / "Lab04SystolicArray.mp4"
    if not target_video.exists():
        print(f"❌ Video not found at {target_video}. Please render it first!")
        sys.exit(1)

    master_audio = ANIMATIONS_DIR / "temp_audio" / "lab04_master_voiceover.wav"
    output_video = VIDEOS_DIR / "scene_lab04_systolic_array" / "720p30" / "Lab04SystolicArray_narrated.mp4"

    generate_audio_track(master_audio, voice="Samantha")
    mux_video_and_audio(target_video, master_audio, output_video)


if __name__ == "__main__":
    main()
