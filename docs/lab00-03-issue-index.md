# Lab 00–03 issue index

Audience: software engineers. Review date: 2026-10-03.
Scenes reviewed (there is no `scene_labxx_content.py`):

- `animations/scene_lab00_prep.py` — `Lab00PrepPrimer`
- `animations/scene_lab00_saturation.py` — `Lab00SaturationIntro`
- `animations/scene_lab01_multiplier.py` — `Lab01Multiplier`
- `animations/scene_lab02_mac_unit.py` — `Lab02MACUnit`
- `animations/scene_lab03_pe.py` — `Lab03ProcessingElement`

Paired guides: `labs/slides/lab00_prep_hardware_thinking_primer.md`, `lab00_adder_slides.md`, `lab01_multiplier_slides.md`, `lab02_mac_unit_slides.md`, `lab03_processing_element_slides.md`.
RTL checked: `rtl/adder.sv`, `rtl/multiplier_int8.sv`, `rtl/mac_unit.sv`, `rtl/pe.sv`.

`PROJECT.md` marks milestones M1–M4 as DONE and now points here. Do not treat a clean render as a content sign-off.

## Resolution, 2026-10-03

The rows below were fixed in the working tree and the five scenes rendered with `manim -ql` (exit 0).

Still open:

- `SYS-01`. Acts still hard-cut. `morph_to` and `focus_on` are still unused. Within an act, the numbers now move.
- `SYS-02`, partial. The banner shows only the lead sentence, so it no longer prints the punchline. Prep still swaps a line at a time. The other labs do not update the banner mid-act.
- `SYS-03`, partial. `voiceover()` no longer claims it prevents drift. Per-line WAV files are still not generated during the render. The prep script in `narrate_video.py` matches the new lines.
- `PREP-01`, partial. Act 0 and Act 1 both remain. Act 1 is now the program counter still walking after the chip already shows 5, 5, and 25.

Bar used: a 3Blue1Brown / Grant Sanderson scene, plus the same habit in channels that teach by transformation (Reducible, Primer, The Coding Train when it builds one object on screen). One idea per beat. A familiar object changes into the new object. The number lives on the picture and updates. Scale is honest, or the axis says it is not. The mechanism is visible before the slogan. The camera goes to the part that matters. Later labs reuse an earlier picture instead of restarting with a new card.

## How to fix one item

1. Pick an open ID below. Do not start a new scene until the factual blockers in that lab are closed.
2. Change the scene so the picture enacts the sentence. A correct caption next to a static card is not a fix.
3. If the claim is a number, put the derivation in the scene or delete the number. Do not leave a figure a viewer cannot recompute.
4. Render with `python animations/render_all.py --low <lab>` and watch the beat, not just the exit code.
5. Set the ID status to `fixed` and name the commit.

## Fix order

1. Factual blockers a software engineer can disprove in a REPL or a paper: `PREP-02`, `PREP-03`, `SAT-02`, `SAT-04`, `MUL-01`, `MUL-03`, `MAC-01`, `MAC-02`, `PE-02`, `PE-04`.
2. Geometry that draws the wrong circuit: `SYS-07`.
3. Rebuild each lab as one walked example (see "Target story" under each lab). Shared pipeline issues (`SYS-01` through `SYS-06`, `SYS-08`) get fixed once in `animations/components/kinematics.py` and `animations/theme.py`, then the scenes stop working around them.

---

## Shared pipeline

| ID | Sev | Status | Where | Problem | Fix |
|---|---|---|---|---|---|
| SYS-01 | major | open | `kinematics.py` `StageContext.morph_to`, `SiliconCameraRig.focus_on`; all four scenes | Every act fades out and fades in a new poster. `morph_to` and `focus_on` are never called. The file headers claim a 3Blue1Brown standard the scenes do not use. | One lab, one object that transforms. Camera moves into the gate, the bit, or the PE. Hard cuts only when the world actually changes. |
| SYS-02 | major | partial | `theme.py` `narration_banner` (height 1.05); labs 00–03 `stage(..., narration=full paragraph)` | The banner prints the entire paragraph, including the punchline, then shrinks the type until it fits 1.05 units. The viewer reads the ending before the animation. | One sentence in the banner, swapped when that sentence becomes true on screen. Lab 00-Prep `_say` is the closer pattern. Do not scale a paragraph down to fit. |
| SYS-03 | major | partial | `kinematics.py` `voiceover`; `narrate_video.py` `SCRIPTS` | `voiceover()` does not synthesize or play audio. Duration is a 145 WPM guess plus punctuation. `narrate_video.py` only has scripts for `00_prep` and lab 04, and muxes with `apad`, so audio is not locked to acts. Labs 00–03 render silent, and a later mux will drift. | Generate per-line audio, wait on the real duration, and mux per scene. Until that exists, do not pretend the tracker prevents drift. |
| SYS-04 | major | fixed | clock HUD in every `construct` | `KineticClock` advances on slides where nothing is clocked. On the "no program counter" beat it implies the chip also took three cycles. | Show the clock only when a register samples. Combinational beats get no tick. |
| SYS-05 | minor | fixed | `StageContext.takeaway` | The callout is placed at `main_stage_center`, on top of the diagram that just made the point. | Leave the diagram up. Put one line under it, or cut to the line after a short hold. |
| SYS-06 | minor | fixed | `screen_shake` uses in prep, saturation, multiplier, MAC | The camera jumps (`frame.shift` plus `wait`, not `play`) instead of showing the bit, carry, or register that broke. | Delete the shake. Animate the failing bit. |
| SYS-07 | blocker | fixed | `scene_lab00_prep.py` Act 6; `scene_lab02_mac_unit.py` Act 0 and Act 4 | Arrows and wires are measured, then `HStack` / `fit_to_bounds` moves the boxes. The wires stay at the old coordinates. | Build wires after the final layout, or parent them to the same group that gets arranged and scaled. |
| SYS-08 | minor | fixed | `scene_lab00_saturation.py` `formula[0][2:7]`; `scene_lab02_mac_unit.py` `dot_eq[0][4:11]` | Coloring MathTex by character index breaks or paints the wrong glyphs across Manim versions. | Color named submobjects, or split the formula into separate `MathTex` parts. |
| SYS-09 | process | fixed | `PROJECT.md` milestones | M1–M4 are marked DONE, including "forensic audit CLEAN". That hides the items in this file. | Point the tracker at this index. Do not mark a lab done because `render_all.py --low` exited 0. |

---

## Lab 00-Prep — `scene_lab00_prep.py`

Target story: start from `def y(a, b, c, d)` with `a,b,c,d = 3,2,4,1`. The instruction pointer walks three lines and the CPU writes 5, then 5, then 25. The same function is then the circuit: both adders show 5 in the same beat, and the multiplier shows 25 with no program counter and no extra clock ticks. Later beats reuse that circuit (a register appears on the wire; `=` deletes a stage; `<=` keeps it). Do not open a new poster for each metaphor.

| ID | Sev | Status | Problem | Fix |
|---|---|---|---|---|
| PREP-01 | major | partial | Act 0 and Act 1 are the same lesson: Python steps versus two adders and a multiplier. | Keep one of them. Act 1 should be the moment the program counter is shown to have nothing to point at. |
| PREP-02 | blocker | fixed | Narration says both adds happen in the same moment of physics. The scene then advances `CLK` three times, moves tokens on tick 2, and reveals `y = 25` on tick 3. The partial sums 5 and 5 are never drawn. The HUD says the chip also took three cycles. | Light both adders together, label them 5 and 5, and show 25 in that same beat. Reserve clock ticks for Act 3 and Act 4, where a register actually samples. |
| PREP-03 | blocker | fixed | MAC bar width 0.15 versus DRAM bar width 4.8 is about 32×, while the claim is 1,000× (0.2 pJ vs 200 pJ). The caption also says `C_pcb` is 10,000× local capacitance. `P = α C V² f` cannot support both ratios unless the missing factors are shown. | Draw an honest scale (or label a log axis). Use one ratio. If both C and energy are kept, show the arithmetic that connects them. |
| PREP-04 | major | fixed | Blocking `b = a; c = b` is drawn as "B and C both become 10" and, in the same beat, as "B dissolves into a bypass wire". Those are different synthesis outcomes. | Pick one and animate it. Best version: values sit in the registers, the clock edge hits, and the viewer watches B and C both take 10 while the non-blocking side becomes 10 then 20. The tuple-unpack analogy (`b, c = a, b`) is the right software hook; keep it. |
| PREP-05 | major | fixed | Act 5 names a ring buffer, MMIO doorbell, PCIe Gen5, DMA, and ping-pong SRAM without moving one tensor. The spark at the doorbell is faded without traveling. Swapping the bank groups moves the silicon; the role labels ride along, so it is a translation, not a role swap. | Follow four numbers from host memory, across the bus, into bank B, while bank A is consumed in place. Then swap the role labels, not the rectangles. |
| PREP-06 | major | fixed | Act 6 awaits `RisingEdge` before a combinational adder shows `sum = 30`, so addition looks clocked. Wires are built before `fit_to_bounds` (`SYS-07`). "100% HARDWARE ASSERTION PASSED" overclaims one assert. The checkmark glyph depends on the font. | Drive `a` and `b`, show the sum update with no clock if the adder is combinational, and say one assert passed. |

---

## Lab 00 — saturation — `scene_lab00_saturation.py`

Target story: open a REPL frame, `np.int8(100) + np.int8(50)` equals `-106`. Then those exact bits fall through eight full adders. The sign bit flips. The wrap dial is the same number. The mux clamps using the operand sign, the bit `rtl/adder.sv` actually uses, and the output becomes `+127`.

Checked arithmetic: `100 = 0b01100100`, `50 = 0b00110010`, raw sum `0b10010110` = 150 unsigned = `-106` signed. Carry into bit 7 is 1, carry out of bit 7 is 0, so `V = cin[7] XOR cout[7]` is 1. That part of Act 2's narration is right. The ripple widget does not show these bits.

| ID | Sev | Status | Problem | Fix |
|---|---|---|---|---|
| SAT-01 | major | fixed | The lab never shows the one-liner a software engineer can run. It opens on a place-value formula. | First frame: the numpy expression and the result `-106`. Then open the bits. |
| SAT-02 | blocker | fixed | The attention sidebar is on screen before the sum is written. `e^(+150)` is not a representable FP32 softmax input (`exp` overflows near 88). The scene also does not say where an int8 add sits inside attention. Lab 06 already teaches the max-subtraction fix, and this scene contradicts it. | Drop `e^(+150)`. If the lab connects to attention, show a small logit that wraps, then point forward to Lab 06. Reveal the disaster after the bits flip, not beside them. |
| SAT-03 | major | fixed | `RippleCarryChain.animate_ripple` is a generic sweep. It does not add 100 and 50, so the overflow identity is a caption. | Each cell shows that column's bits and carry. Bit 7 is the only place cin and cout disagree. |
| SAT-04 | blocker | fixed | On-screen select is `sel = {overflow, sign_bit}`. It does not say whose sign. The sum's sign in this example is 1, and using it would clamp to `-128`. `rtl/adder.sv` clamps with the operand sign `a[MSB]`, which is 0 here, so the result is `+127`. The picture shows `+127` while the formula is ambiguous. | Label the bit `a[7]`, matching the RTL. Show the wrong choice (result sign → `-128`) and the right choice (operand sign → `+127`) on the same mux. |

---

## Lab 01 — multiplier — `scene_lab01_multiplier.py`

Target story: `1 × 1` is an AND. Then a tiny multiply, for example `0b0110 × 0b0101`, fills only the partial products that are actually 1. The viewer adds those shifted rows and sees the width grow. Only then does 8×8 become "64 ANDs, and `(-128)×(-128) = 16384` needs a 16th bit". Booth recoding regroups those same rows. The Wallace tree is those rows collapsing, not a sentence.

Checked: `(-128)×(-128) = 16384 = 2^14`. In 15-bit two's complement, bit 14 is the sign, so that pattern reads as `-16384`. The 16-bit claim is right. `mma.sync` `m16n8k32` is 16×8×32 = 4096 MACs per warp instruction. That count can stay. The reason given for it cannot.

| ID | Sev | Status | Problem | Fix |
|---|---|---|---|---|
| MUL-01 | blocker | fixed | Die rectangles are 3.0, 4.0, and 5.0 wide for 42, 456, and 7000 gates. The picture says FP32 is slightly wider. The narration turns 7000/456 into "16× more engines" and then into a Tensor Core fact. Area ratio is not the same claim as warp MMA throughput. | Scale the dies to the gate counts, or remove the picture. Keep 4096 MACs only with the instruction shape (`m16n8k32`), not as a consequence of the 16× slogan. |
| MUL-02 | major | fixed | The 8×8 grid is 64 identical dots. No partial product is computed. | Animate one small multiply. Dots that are zero stay dim. The viewer can add the rows by hand. |
| MUL-03 | blocker | fixed | The Booth window slides across `011010100` while the probe cycles through canned strings (`+2×M`, `-1×M`, `-2×M`) that are not a function of the bits inside the window. | Compute the radix-4 digit from the triplet under the window, and show the row that digit selects. If the teaching RTL is just `a * b`, say that in one line and spend the time on the partial products the RTL's behavior still has. |
| MUL-04 | major | fixed | The Wallace tree is the line "4 Booth Rows → 3:2 CSA → 2 vectors → CPA". The logarithmic-depth claim has no picture. | Show four rows become two. A caption can name the compressor after the rows have collapsed. |

---

## Lab 02 — MAC — `scene_lab02_mac_unit.py`

Target story: the int8 product `(-128)×(-128) = 16384` lands in an int16 accumulator. The second add produces mathematical `32768`, and the register shows `-32768` — the same sign flip as Lab 00. Widening to 32 bits is the fix. Sign-extending `-5` (`0xFFFB` → `0xFFFFFFFFFFFB` stays `-5`; zero-fill becomes `65531`) is the trap, shown as bits copying upward. The pipeline beat uses the real period, including the register delay already drawn on the flop.

Verified, do not "fix": zero-extending 16-bit `-5` (`0xFFFB`) to 32 bits is `0x0000FFFB = 65531`. The on-screen `65,531` is that number. `K_max = floor((2^31-1)/16384) = 131071` is the right positive worst-case count. `PROJECT.md` says `K ≤ 131072`, which is the off-by-one: `131072 × 16384 = 2^31`, not representable as a positive int32.

| ID | Sev | Status | Problem | Fix |
|---|---|---|---|---|
| MAC-01 | blocker | fixed | Term 2 is labeled `+32,768 (OVERFLOW!)` and the tank shakes. Signed 16-bit storage of 32768 is `-32768`. The lab never shows that bit pattern, so it drops the lesson Lab 00 exists to teach. | After the second add, show `0x8000` and the value `-32768`. The tank can crack only after the bits have wrapped. |
| MAC-02 | blocker | fixed | "3 guard bits" for LLaMA `d_model = 8192` is wrong. `8192 × 16384 = 2^27`. Signed 32-bit magnitude is 31 bits, so the spare is 4 bits. The takeaway "one pipeline register nearly doubles the clock" is also wrong: `4.0 ns → 2.8 ns` is 250 MHz → about 357 MHz, roughly 1.4×, because the multiplier stage still dominates. The drawn `t_cq ≈ 0.2 ns` is omitted from `max(2.8, 1.2)`. | Say 4 guard bits. State 250 MHz and ~350 MHz, and say why it is not 500 MHz. Add `t_cq + t_setup` or stop printing `t_cq`. |
| MAC-03 | major | fixed | The tile "16 product + 16 headroom" does not produce 131,071. That bound exists because the extreme product is `2^14`, not a full 16-bit magnitude. | One formula, one picture. Drop the slogan or derive it. |
| MAC-04 | major | fixed | Act 0 creates `dot_m` and `dot_a` and never plays them. The MAC "heartbeat" is a stroke flash. Act 0 and Act 4 arrows are built before `HStack` (`SYS-07`). | Move a labeled product into the accumulator. Rebuild the pipeline wires after layout. |

---

## Lab 03 — processing element — `scene_lab03_pe.py`

Target story: the triple loop is on screen, then `i` and `j` become a grid and `k` becomes a tick. One cell, weight 7, activation 6, partial 100, computes `100 + 42 = 142` and passes 6 east and 142 south. Only after that number has moved do you say what stayed still (the weight). Taxonomy and energy are consequences of that picture, with the assumptions written down.

Checked traffic arithmetic for the slide's model (`M = K = N = 128`, every MAC fetches A and W from DRAM, no cache): `2 × 128³ = 4,194,304` bytes ≈ 4.19 MB, weight-stationary fetches `2 × 128² = 32,768` bytes ≈ 32.8 KB, ratio 128. That arithmetic is fine. The energy unit is not.

`838,860,800 pJ = 0.83886 mJ`, not `839.28 mJ`. The weight-stationary side is `7,392,460 pJ = 0.00739 mJ`, not `7.39 mJ`. Both sides are 1,000× high (divided by 10^6 instead of 10^9). The ratio `839.28 / 7.39 ≈ 113.5` survives the unit error. `113×` is not `128×` because MAC energy does not shrink; the animation never says that.

Eyeriss (Chen, Emer, Sze, ISCA 2016) is row-stationary. It is not output-stationary, and it is not an input-stationary variant. The animation and `labs/slides/lab03_processing_element_slides.md` disagree with each other, and both are wrong. ShiDianNao is the closer output-stationary citation. TPU v1 is the clean weight-stationary citation; "v1–v5" overclaims.

| ID | Sev | Status | Problem | Fix |
|---|---|---|---|---|
| PE-01 | major | fixed | The primer and Act 1 both show the same triple loop. Act 1's payoff is a statistics panel, not the loops becoming cells. | Morph the `for` lines into a grid. `k` is the clock. |
| PE-02 | blocker | fixed | Slides and the scene call the energy `839 mJ` and `7.39 mJ`. Those quantities are `0.839 mJ` and `0.00739 mJ`. The scene also prints 128× and 113.5× with no reason they differ. | Fix the unit in the slides and the scene. Show the leftover MAC energy as the reason the energy ratio is smaller than the traffic ratio. |
| PE-03 | major | fixed | The 128× model assumes no cache and omits output writeback (`128 × 128 × 4 = 64 KB` of int32 stores). A software engineer running a 128³ GEMM will not see 4 MB of DRAM traffic. | Put the assumptions on screen: array holds all of N, cold DRAM, reads only. Or compare against a cached baseline so the claim survives contact with numpy. |
| PE-04 | blocker | fixed | Scene Act 2: "Output-stationary, like Stanford's Eyeriss." Slides put Eyeriss on the input-stationary row as a "row-stationary variant." | Eyeriss is row-stationary, its own column. Output-stationary gets a real example (ShiDianNao). Weight-stationary gets TPU v1, not v1–v5, unless the later TPUs are actually described. |
| PE-05 | major | fixed | Act 3's comment says `100 + 6×7 = 142`. The west and north probes already show `+6` and `100` before the weight is loaded, and the result probes appear with the answer. No multiply is drawn. Act 4 repeats the "48 DFF" card and adds Apple ANE clock-gating, which is not in `rtl/pe.sv` and is not marked as a concept the way Lab 01 and Lab 02 mark Booth and pipelining. | Play the MAC inside the cell. Badge anything that is not in the RTL. |

48 flip-flops (`8 + 8 + 32`) matches the register budget in the slides. Leave that count alone.

---

## Labs 04–08

Not reviewed in this pass. The same failure mode is already visible in the pipeline they share: full-paragraph banners, a clock HUD on static beats, unused `morph_to`, and `PROJECT.md` marking them done. Review them against this index before rewriting them.
