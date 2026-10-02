import re

with open('slides/generate_pptx_slides.py', 'r') as f:
    content = f.read()

# 1. Add build_module_slide function
module_slide_func = """
def build_module_slide(prs, module_num, title, description, color):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide)
    
    # Large colored block
    block = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.5), Inches(1.5), Inches(10.333), Inches(4.5))
    block.fill.solid()
    block.fill.fore_color.rgb = color
    block.line.fill.background()
    
    tb_mod = slide.shapes.add_textbox(Inches(2.0), Inches(2.0), Inches(9.333), Inches(0.8))
    p_mod = tb_mod.text_frame.paragraphs[0]
    p_mod.text = f"MODULE {module_num}"
    p_mod.font.name = FONT_HEAD
    p_mod.font.size = Pt(24)
    p_mod.font.bold = True
    p_mod.font.color.rgb = COLOR_BG
    
    tb_title = slide.shapes.add_textbox(Inches(2.0), Inches(2.8), Inches(9.333), Inches(1.2))
    p_title = tb_title.text_frame.paragraphs[0]
    p_title.text = title
    p_title.font.name = FONT_HEAD
    p_title.font.size = Pt(48)
    p_title.font.bold = True
    p_title.font.color.rgb = COLOR_TEXT_MAIN
    
    tb_desc = slide.shapes.add_textbox(Inches(2.0), Inches(4.2), Inches(9.333), Inches(1.0))
    p_desc = tb_desc.text_frame.paragraphs[0]
    p_desc.text = description
    p_desc.font.name = FONT_BODY
    p_desc.font.size = Pt(18)
    p_desc.font.color.rgb = COLOR_BG

"""

content = content.replace("def build_title_slide(prs):", module_slide_func + "def build_title_slide(prs):")

# 2. Modify generate_all_decks to include modules
old_master = """    build_roadmap_slide(master_prs)
    build_lab00_slides(master_prs)
    build_lab01_slides(master_prs)
    build_lab02_slides(master_prs)
    build_lab03_slides(master_prs)
    build_lab04_slides(master_prs)
    build_lab05_slides(master_prs)
    build_lab06_slides(master_prs)
    build_lab07_slides(master_prs)
    build_lab08_slides(master_prs)
    build_summary_slide(master_prs)"""

new_master = """    build_roadmap_slide(master_prs)
    
    build_module_slide(master_prs, 1, "Hardware AI Basics", "Beginner Introduction to functional AI Math (A*B, A+B).", COLOR_CYAN)
    build_lab00_slides(master_prs)
    build_lab01_slides(master_prs)
    
    build_module_slide(master_prs, 2, "Deep Dive: Silicon Arithmetic", "Under the hood of logic gates, Booth encoding, and Multiply-Accumulate.", COLOR_ROSE)
    build_lab02_slides(master_prs)
    
    build_module_slide(master_prs, 3, "Matrix Engines & 2D Arrays", "Weight-Stationary PEs and 2D Systolic Array Scheduling.", COLOR_EMERALD)
    build_lab03_slides(master_prs)
    build_lab04_slides(master_prs)
    
    build_module_slide(master_prs, 4, "Transformer SFUs", "Special Function Units for Attention, Softmax, and Non-Linearities.", COLOR_PURPLE)
    build_lab05_slides(master_prs)
    build_lab06_slides(master_prs)
    build_lab07_slides(master_prs)
    build_lab08_slides(master_prs)
    
    build_summary_slide(master_prs)"""

content = content.replace(old_master, new_master)

# 3. Simplify Lab 01 to abstract beginner stuff instead of gate complexity
old_lab01_hook = """    add_stat_card(slide1, 0.8, 1.5, 2.7, 1.2, "O(N²)", "Gate Area Complexity", COLOR_CYAN)
    add_stat_card(slide1, 3.7, 1.5, 2.7, 1.2, "16 Bits", "Required INT8×INT8 Width", COLOR_EMERALD)
    add_stat_card(slide1, 6.6, 1.5, 2.7, 1.2, "1 DSP", "FPGA Resource Mapping", COLOR_AMBER)
    add_stat_card(slide1, 9.5, 1.5, 3.0, 1.2, "[-16.2k, +16.3k]", "Full Product Range", COLOR_PURPLE)

    tf_left = add_bento_card(slide1, 0.8, 2.9, 5.7, 3.8, "🪝 The Hook: Why Multipliers Dominate Silicon", COLOR_ROSE)
    add_bullet(tf_left, "The Matrix Engine:", "99% of LLM compute is matrix multiplications (Y = W · X).")
    add_bullet(tf_left, "Quadratic Growth:", "While adders scale O(N), multipliers scale O(N²) in gate area (~456 gates for 8-bit).")
    add_bullet(tf_left, "Bit-Growth Rule:", "Multiplying two 8-bit numbers strictly requires 16 bits (8 + 8) to avoid losing precision.")

    tf_right = add_bento_card(slide1, 6.8, 2.9, 5.7, 3.8, "💡 Hardware Intuition & Sign Extension", COLOR_CYAN)
    add_bullet(tf_right, "Range:", "[-128 × +127 = -16256] to [-128 × -128 = +16384].")
    add_bullet(tf_right, "Sign Extension:", "Must treat inputs as signed two's complement, preventing -1 from converting to 255.")
    add_bullet(tf_right, "Timing / Cycles:", "Combinational (0 clock cycles) or mapped to DSP slices.")"""

new_lab01_hook = """    add_stat_card(slide1, 0.8, 1.5, 2.7, 1.2, "Y = W × X", "The Core Operation", COLOR_CYAN)
    add_stat_card(slide1, 3.7, 1.5, 2.7, 1.2, "16 Bits", "Required INT8×INT8 Width", COLOR_EMERALD)
    add_stat_card(slide1, 6.6, 1.5, 2.7, 1.2, "Beginner", "Functional Abstraction", COLOR_AMBER)
    add_stat_card(slide1, 9.5, 1.5, 3.0, 1.2, "[-16.2k, +16.3k]", "Full Product Range", COLOR_PURPLE)

    tf_left = add_bento_card(slide1, 0.8, 2.9, 5.7, 3.8, "🪝 The Hook: AI is just A * B", COLOR_ROSE)
    add_bullet(tf_left, "The Matrix Engine:", "99% of LLM compute is matrix multiplications (Y = W · X).")
    add_bullet(tf_left, "Simple Concept:", "For now, treat the hardware multiplier as a simple 'a * b' block. We'll deep dive into what happens inside the silicon later!")
    add_bullet(tf_left, "Bit-Growth Rule:", "Multiplying two 8-bit numbers strictly requires 16 bits (8 + 8) to avoid losing precision.")

    tf_right = add_bento_card(slide1, 6.8, 2.9, 5.7, 3.8, "💡 Beginner Hardware Intuition", COLOR_CYAN)
    add_bullet(tf_right, "Focus on the Inputs/Outputs:", "We input two INT8 numbers, and we get one INT16 product out.")
    add_bullet(tf_right, "Sign Extension:", "Must treat inputs as signed two's complement, preventing -1 from converting to 255.")
    add_bullet(tf_right, "Deep Dive Later:", "How Booth Encoding and Partial Products actually build this math at the gate level will be covered in Module 2.")"""

content = content.replace(old_lab01_hook, new_lab01_hook)

# Add a "Deep Dive Slide" function to add more variety to the templates.
deep_dive_slide_func = """
def build_deep_dive_slide(prs, title, content_bullets, image_path=None):
    slide = prs.slides.add_slide(prs.slide_layouts[6])
    apply_background(slide)
    add_header(slide, "DEEP DIVE", title, "Looking under the hood at the gate level")
    
    tf = add_bento_card(slide, 0.8, 1.5, 5.7 if image_path else 11.7, 5.2, "🔬 Under the Hood Details", COLOR_ROSE, bg_color=RGBColor(20, 15, 25))
    for bullet in content_bullets:
        add_bullet(tf, "", bullet, font_size=12, text_color=COLOR_TEXT_MAIN)
        
    if image_path:
        add_schematic_card(slide, 6.8, 1.5, 5.7, 5.2, "Gate Level Visualization", image_path)

"""

content = content.replace("def build_title_slide(prs):", deep_dive_slide_func + "def build_title_slide(prs):")

# Modify Lab02 to include a deep dive slide since it's the start of Module 2
lab02_mod = """    build_title_slide(prs)
    build_fn(prs)"""
new_lab02_mod = """    build_title_slide(prs)
    if filename == "Lab02_MAC_Unit.pptx":
        build_deep_dive_slide(prs, "Deep Dive: How Multipliers Actually Work (Booth & Wallace)", [
            "At the functional level, a*b is simple. At the gate level, it's complex.",
            "Partial Products: Every bit of 'A' AND'ed with every bit of 'B' creates O(N²) partial products.",
            "Wallace Tree: A fast way to add all partial products together in O(log N) delay using full adders.",
            "Booth Encoding: Reduces the number of partial products by half by looking at 3-bit sliding windows.",
            "This quadratic O(N²) gate area growth is why multipliers are the most expensive standard resource in AI chips!"
        ], "schematics/multiplier_int8.png")
    build_fn(prs)"""

content = content.replace(lab02_mod, new_lab02_mod)

with open('slides/generate_pptx_slides.py', 'w') as f:
    f.write(content)
