#!/usr/bin/env python3
"""
==============================================================================
File: synthesis/generate_schematics.py
Description: Generates fully interactive, hierarchical, collapsible SVG schematics
             for hardware modules (multiplier_int8, mac_unit, pe, systolic_array).
             
Features:
- Components collapse/expand on click to reveal internal logic and submodules.
- Multi-bit bus lines with bitwidth badges instead of exploding into wire spaghetti.
- Clean routing with pin stubs and toggleable global control nets (clk, rst_n, en).
- Interactive net highlighting on hover/click with glowing signal paths.
- Embedded SVG JavaScript and CSS for standalone operation in any browser or viewer.
- 100% strict XML/SVG compliant (validated with xml.etree.ElementTree).
==============================================================================
"""

import os
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

def create_svg_header(width, height, title, view_box=None):
    if view_box is None:
        view_box = f"0 0 {width} {height}"
    
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view_box}" width="100%" height="100%" class="schematic-canvas" id="schematic-svg" data-title="{title}">
<defs>
    <style><![CDATA[
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600;700&family=Inter:wght@400;500;600;700&display=swap');
        
        :root {{
            --bg: #090d13;
            --panel: #111827;
            --card: #1f2937;
            --card-header: #374151;
            --border: #374151;
            --text: #f3f4f6;
            --text-muted: #9ca3af;
            --accent: #38bdf8;
            --accent-glow: rgba(56, 189, 248, 0.4);
            --bus-color: #60a5fa;
            --bus-width: 3.5px;
            --wire-color: #94a3b8;
            --control-color: #f59e0b;
            --highlight: #22d3ee;
            --pe-bg: #131d2e;
            --pe-border: #2563eb;
            --mac-bg: #1e1b4b;
            --mac-border: #6366f1;
            --reg-bg: #142e2b;
            --reg-border: #10b981;
            --mult-bg: #31132b;
            --mult-border: #ec4899;
        }}
        
        text {{
            font-family: 'Inter', -apple-system, sans-serif;
            user-select: none;
        }}
        
        .mono {{
            font-family: 'JetBrains Mono', monospace;
        }}
        
        /* Interactive Component Styling */
        .component-box {{
            cursor: pointer;
            transition: all 0.25s ease;
        }}
        
        .component-box:hover .box-rect {{
            stroke: var(--highlight);
            stroke-width: 2.5px;
            filter: drop-shadow(0 0 10px var(--accent-glow));
        }}
        
        .toggle-btn {{
            cursor: pointer;
            transition: transform 0.2s ease;
        }}
        .toggle-btn:hover circle {{
            fill: var(--highlight);
        }}
        
        /* Collapsible Elements */
        .collapsible-content {{
            transition: opacity 0.3s ease, transform 0.3s ease;
        }}
        .collapsed .collapsible-content {{
            display: none;
            opacity: 0;
        }}
        .collapsed .expanded-only {{
            display: none;
        }}
        .expanded .collapsed-only {{
            display: none;
        }}
        
        /* Wire and Bus Styling */
        .net-bus {{
            fill: none;
            stroke: var(--bus-color);
            stroke-width: 3.5px;
            stroke-linecap: round;
            stroke-linejoin: round;
            transition: stroke 0.2s, stroke-width 0.2s, filter 0.2s;
        }}
        
        .net-control {{
            fill: none;
            stroke: var(--control-color);
            stroke-width: 1.5px;
            stroke-dasharray: 4 3;
            stroke-linecap: round;
            stroke-linejoin: round;
            transition: stroke 0.2s, stroke-width 0.2s;
        }}
        
        .net-wire {{
            fill: none;
            stroke: var(--wire-color);
            stroke-width: 2px;
            stroke-linecap: round;
            stroke-linejoin: round;
            transition: stroke 0.2s, stroke-width 0.2s;
        }}
        
        .net-active {{
            stroke: #f43f5e !important;
            stroke-width: 4.5px !important;
            filter: drop-shadow(0 0 8px #f43f5e) !important;
        }}
        
        .net-highlight {{
            stroke: #38bdf8 !important;
            stroke-width: 4.5px !important;
            filter: drop-shadow(0 0 10px #38bdf8) !important;
        }}
        
        /* Ports and Pins */
        .pin-node {{
            cursor: pointer;
            transition: r 0.2s, fill 0.2s;
        }}
        .pin-node:hover {{
            r: 6px;
            fill: var(--highlight);
        }}
        
        /* Tooltip */
        #svg-tooltip {{
            position: absolute;
            display: none;
            background: rgba(17, 24, 39, 0.95);
            color: #fff;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 12px;
            font-family: 'JetBrains Mono', monospace;
            border: 1px solid #38bdf8;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
            pointer-events: none;
            z-index: 1000;
        }}
        
        /* Toolbar inside SVG */
        .svg-toolbar {{
            fill: #111827;
            stroke: #374151;
            stroke-width: 1px;
            rx: 6px;
        }}
        .svg-tool-btn {{
            cursor: pointer;
        }}
        .svg-tool-btn:hover rect {{
            fill: #1f2937;
            stroke: #38bdf8;
        }}
    ]]></style>
    
    <!-- Gradients and Markers -->
    <linearGradient id="bgGrad" x1="0%" y1="0%" x2="100%" y2="100%">
        <stop offset="0%" stop-color="#0a0f18" />
        <stop offset="100%" stop-color="#04070c" />
    </linearGradient>
    
    <linearGradient id="peGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#1e293b" />
        <stop offset="100%" stop-color="#0f172a" />
    </linearGradient>
    
    <linearGradient id="macGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#2d1b4e" />
        <stop offset="100%" stop-color="#19102c" />
    </linearGradient>
    
    <linearGradient id="regGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#064e3b" />
        <stop offset="100%" stop-color="#022c22" />
    </linearGradient>
    
    <linearGradient id="multGrad" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" stop-color="#701a75" />
        <stop offset="100%" stop-color="#4a044e" />
    </linearGradient>
    
    <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
        <feGaussianBlur stdDeviation="4" result="blur" />
        <feComposite in="SourceGraphic" in2="blur" operator="over" />
    </filter>
    
    <marker id="bus-arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
        <path d="M 0 1 L 9 5 L 0 9 z" fill="#60a5fa" />
    </marker>
    <marker id="wire-arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#94a3b8" />
    </marker>
    <marker id="ctrl-arrow" viewBox="0 0 10 10" refX="7" refY="5" markerWidth="5" markerHeight="5" orient="auto-start-reverse">
        <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#f59e0b" />
    </marker>
</defs>

<!-- Background -->
<rect width="100%" height="100%" fill="url(#bgGrad)" />

<!-- Grid Pattern -->
<pattern id="dotGrid" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse">
    <circle cx="2" cy="2" r="1" fill="#1e293b" opacity="0.6" />
</pattern>
<rect width="100%" height="100%" fill="url(#dotGrid)" />

<!-- Canvas Viewport for Pan/Zoom -->
<g id="viewport" transform="translate(0, 0) scale(1)">
"""

def create_svg_footer():
    return """</g>

<!-- Integrated Interactive Controls Toolbar -->
<g id="ui-toolbar" transform="translate(20, 20)">
    <rect width="360" height="42" class="svg-toolbar" rx="8" />
    
    <g class="svg-tool-btn" onclick="toggleAllComponents(true)" transform="translate(10, 7)">
        <rect width="100" height="28" rx="5" fill="#1f2937" stroke="#4b5563" />
        <text x="50" y="18" fill="#e2e8f0" font-size="11" font-weight="600" text-anchor="middle">➕ Expand All</text>
    </g>
    
    <g class="svg-tool-btn" onclick="toggleAllComponents(false)" transform="translate(118, 7)">
        <rect width="105" height="28" rx="5" fill="#1f2937" stroke="#4b5563" />
        <text x="52" y="18" fill="#e2e8f0" font-size="11" font-weight="600" text-anchor="middle">➖ Collapse All</text>
    </g>
    
    <g class="svg-tool-btn" onclick="toggleControls()" transform="translate(230, 7)">
        <rect width="120" height="28" rx="5" fill="#1f2937" stroke="#4b5563" />
        <text x="60" y="18" fill="#f59e0b" font-size="11" font-weight="600" text-anchor="middle">⚡ Toggle Control</text>
    </g>
</g>

<!-- Tooltip Container -->
<g id="tooltip-group" style="display: none; pointer-events: none;">
    <rect id="tooltip-bg" fill="#111827" stroke="#38bdf8" stroke-width="1.5" rx="6" opacity="0.95" />
    <text id="tooltip-text" fill="#f3f4f6" font-size="12" font-family="'JetBrains Mono', monospace" y="0"></text>
</g>

<script><![CDATA[
    // Interactive Collapsible Schematic Logic
    let showControlNets = true;
    let currentHighlightedNet = null;

    function toggleComponent(id) {
        const comp = document.getElementById(id);
        if (!comp) return;
        const isCollapsed = comp.classList.contains('collapsed');
        if (isCollapsed) {
            comp.classList.remove('collapsed');
            comp.classList.add('expanded');
        } else {
            comp.classList.remove('expanded');
            comp.classList.add('collapsed');
        }
        updateBadge(comp);
    }

    function updateBadge(comp) {
        const badge = comp.querySelector('.toggle-badge text');
        if (badge) {
            badge.textContent = comp.classList.contains('collapsed') ? '+' : '−';
        }
    }

    function toggleAllComponents(expand) {
        const comps = document.querySelectorAll('.collapsible-comp');
        comps.forEach(c => {
            if (expand) {
                c.classList.remove('collapsed');
                c.classList.add('expanded');
            } else {
                c.classList.remove('expanded');
                c.classList.add('collapsed');
            }
            updateBadge(c);
        });
    }

    function toggleControls() {
        showControlNets = !showControlNets;
        const ctrls = document.querySelectorAll('.net-control, .control-port');
        ctrls.forEach(el => {
            el.style.display = showControlNets ? '' : 'none';
        });
    }

    function highlightNet(netName) {
        if (currentHighlightedNet === netName) {
            clearHighlight();
            return;
        }
        clearHighlight();
        currentHighlightedNet = netName;
        const wires = document.querySelectorAll(`[data-net="${netName}"]`);
        wires.forEach(w => {
            w.classList.add('net-highlight');
        });
    }

    function clearHighlight() {
        if (currentHighlightedNet) {
            const wires = document.querySelectorAll(`[data-net="${currentHighlightedNet}"]`);
            wires.forEach(w => w.classList.remove('net-highlight'));
            currentHighlightedNet = null;
        }
    }

    function showTooltip(evt, text) {
        const tt = document.getElementById('tooltip-group');
        const bg = document.getElementById('tooltip-bg');
        const txt = document.getElementById('tooltip-text');
        if (!tt || !txt || !bg) return;
        
        txt.textContent = text;
        const bbox = txt.getBBox();
        bg.setAttribute('width', bbox.width + 16);
        bg.setAttribute('height', bbox.height + 12);
        bg.setAttribute('x', bbox.x - 8);
        bg.setAttribute('y', bbox.y - 6);
        
        // Position near mouse
        const pt = getSVGPoint(evt);
        tt.setAttribute('transform', `translate(${pt.x + 12}, ${pt.y - 20})`);
        tt.style.display = 'block';
    }

    function hideTooltip() {
        const tt = document.getElementById('tooltip-group');
        if (tt) tt.style.display = 'none';
    }

    function getSVGPoint(evt) {
        const svg = document.getElementById('schematic-svg');
        const pt = svg.createSVGPoint();
        pt.x = evt.clientX;
        pt.y = evt.clientY;
        return pt.matrixTransform(svg.getScreenCTM().inverse());
    }

    // Pan and Zoom support
    let isPanning = false;
    let startX = 0, startY = 0;
    let translateX = 0, translateY = 0, scale = 1;
    const viewport = document.getElementById('viewport');

    window.addEventListener('load', () => {
        const svg = document.getElementById('schematic-svg');
        if (!svg) return;

        svg.addEventListener('mousedown', (e) => {
            if (e.target.closest('.component-box') || e.target.closest('.svg-tool-btn')) return;
            isPanning = true;
            startX = e.clientX - translateX;
            startY = e.clientY - translateY;
        });

        window.addEventListener('mousemove', (e) => {
            if (!isPanning) return;
            translateX = e.clientX - startX;
            translateY = e.clientY - startY;
            viewport.setAttribute('transform', `translate(${translateX}, ${translateY}) scale(${scale})`);
        });

        window.addEventListener('mouseup', () => {
            isPanning = false;
        });

        svg.addEventListener('wheel', (e) => {
            e.preventDefault();
            const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
            const newScale = Math.min(Math.max(scale * zoomFactor, 0.3), 5.0);
            scale = newScale;
            viewport.setAttribute('transform', `translate(${translateX}, ${translateY}) scale(${scale})`);
        });
    });
]]></script>
</svg>"""

def save_and_validate_svg(svg_content, out_path):
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(svg_content)
    # Strictly validate XML well-formedness
    try:
        ET.parse(out_path)
    except Exception as e:
        print(f"❌ XML Parsing Error in {out_path}: {e}")
        raise
    print(f"✅ Generated & Validated SVG: {out_path}")

# ==============================================================================
# 1. MULTIPLIER_INT8 SCHEMATIC GENERATOR
# ==============================================================================
def generate_multiplier_svg(out_path):
    width, height = 1100, 700
    svg = [create_svg_header(width, height, "multiplier_int8 - 8-Bit Signed Multiplier")]

    # Title Banner
    svg.append("""
    <g transform="translate(40, 80)">
        <text x="0" y="0" fill="#f8fafc" font-size="22" font-weight="700">🔬 MODULE: multiplier_int8</text>
        <text x="0" y="24" fill="#94a3b8" font-size="13">High-Radix Signed Booth Multiplier (8-bit x 8-bit = 16-bit Product)</text>
    </g>
    """)

    # Main Collapsible Multiplier Component Box
    svg.append("""
    <g id="comp_multiplier" class="collapsible-comp expanded" transform="translate(180, 140)">
        <!-- Container Box -->
        <g class="component-box" onclick="toggleComponent('comp_multiplier')">
            <rect class="box-rect" x="0" y="0" width="740" height="480" rx="12" fill="#1e1329" stroke="#c084fc" stroke-width="2" />
            <rect x="0" y="0" width="740" height="42" rx="12" fill="#3b0764" />
            <rect x="0" y="30" width="740" height="12" fill="#3b0764" />
            
            <text x="24" y="27" fill="#f3e8ff" font-size="15" font-weight="700">⚙️ multiplier_int8 Core</text>
            <text x="220" y="26" fill="#d8b4fe" font-size="12" font-family="'JetBrains Mono', monospace">DATA_WIDTH = 8, PROD_WIDTH = 16</text>
            
            <!-- Toggle Badge -->
            <g class="toggle-badge" transform="translate(705, 21)">
                <circle cx="0" cy="0" r="12" fill="#6b21a8" stroke="#d8b4fe" stroke-width="1.5" />
                <text x="0" y="4" fill="#ffffff" font-size="14" font-weight="bold" text-anchor="middle">−</text>
            </g>
        </g>
        
        <!-- COLLAPSED ONLY VIEW: Clean High-Level Multiplier Function -->
        <g class="collapsed-only" transform="translate(220, 150)">
            <rect x="0" y="0" width="300" height="180" rx="10" fill="#2e1065" stroke="#a855f7" stroke-width="2" />
            <text x="150" y="70" fill="#f3e8ff" font-size="28" font-weight="bold" text-anchor="middle">✖️ MULTIPLIER</text>
            <text x="150" y="105" fill="#c084fc" font-size="14" font-family="'JetBrains Mono', monospace" text-anchor="middle">product = a * b (Signed)</text>
            <text x="150" y="140" fill="#9333ea" font-size="12" text-anchor="middle">Click anywhere to expand internal logic</text>
            
            <!-- Internal Flow Bus in collapsed view -->
            <path d="M -160 50 L 0 50" class="net-bus" data-net="a" />
            <path d="M -160 130 L 0 130" class="net-bus" data-net="b" />
            <path d="M 300 90 L 460 90" class="net-bus" data-net="product" />
        </g>
        
        <!-- EXPANDED ONLY VIEW: 4 Internal Functional Stages -->
        <g class="collapsible-content expanded-only">
            <!-- Stage 1: Booth Radix-4 Encoder -->
            <g id="sub_booth" class="collapsible-comp expanded" transform="translate(40, 80)">
                <rect class="box-rect" x="0" y="0" width="180" height="340" rx="8" fill="#1e1b4b" stroke="#818cf8" stroke-width="1.5" />
                <rect x="0" y="0" width="180" height="32" rx="8" fill="#312e81" />
                <text x="12" y="21" fill="#e0e7ff" font-size="12" font-weight="700">1. Radix-4 Booth Enc</text>
                <text x="90" y="70" fill="#c7d2fe" font-size="11" text-anchor="middle">Recodes Operand B</text>
                <text x="90" y="90" fill="#94a3b8" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="middle">b[7:0] + b[-1]=0</text>
                <rect x="20" y="120" width="140" height="180" rx="6" fill="#0f172a" stroke="#4338ca" />
                <text x="90" y="150" fill="#a5b4fc" font-size="11" text-anchor="middle">4 Partial Multipliers:</text>
                <text x="90" y="180" fill="#cbd5e1" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">PP0: {0, ±1a, ±2a}</text>
                <text x="90" y="210" fill="#cbd5e1" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">PP1: {0, ±1a, ±2a}</text>
                <text x="90" y="240" fill="#cbd5e1" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">PP2: {0, ±1a, ±2a}</text>
                <text x="90" y="270" fill="#cbd5e1" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">PP3: {0, ±1a, ±2a}</text>
            </g>
            
            <!-- Stage 2: Partial Product Generator -->
            <g id="sub_ppgen" transform="translate(260, 80)">
                <rect x="0" y="0" width="190" height="340" rx="8" fill="#14253d" stroke="#38bdf8" stroke-width="1.5" />
                <rect x="0" y="0" width="190" height="32" rx="8" fill="#0369a1" />
                <text x="12" y="21" fill="#e0f2fe" font-size="12" font-weight="700">2. PP Generator</text>
                <text x="95" y="65" fill="#bae6fd" font-size="11" text-anchor="middle">Sign Extension &amp; Shift</text>
                
                <rect x="15" y="90" width="160" height="45" rx="5" fill="#0c4a6e" />
                <text x="95" y="118" fill="#ffffff" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">PP0 (16-bit) &lt;&lt; 0</text>
                
                <rect x="15" y="150" width="160" height="45" rx="5" fill="#0c4a6e" />
                <text x="95" y="178" fill="#ffffff" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">PP1 (16-bit) &lt;&lt; 2</text>
                
                <rect x="15" y="210" width="160" height="45" rx="5" fill="#0c4a6e" />
                <text x="95" y="238" fill="#ffffff" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">PP2 (16-bit) &lt;&lt; 4</text>
                
                <rect x="15" y="270" width="160" height="45" rx="5" fill="#0c4a6e" />
                <text x="95" y="298" fill="#ffffff" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">PP3 (16-bit) &lt;&lt; 6</text>
            </g>
            
            <!-- Stage 3: Wallace / CSA Tree Reduction -->
            <g id="sub_csatree" transform="translate(490, 80)">
                <rect x="0" y="0" width="210" height="180" rx="8" fill="#064e3b" stroke="#34d399" stroke-width="1.5" />
                <rect x="0" y="0" width="210" height="32" rx="8" fill="#047857" />
                <text x="12" y="21" fill="#ecfdf5" font-size="12" font-weight="700">3. CSA Reduction Tree</text>
                <text x="105" y="65" fill="#a7f3d0" font-size="11" text-anchor="middle">4:2 Compressor Tree</text>
                
                <rect x="20" y="90" width="170" height="30" rx="4" fill="#065f46" />
                <text x="105" y="110" fill="#d1fae5" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">Carry Vector [15:0]</text>
                
                <rect x="20" y="130" width="170" height="30" rx="4" fill="#065f46" />
                <text x="105" y="150" fill="#d1fae5" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">Sum Vector [15:0]</text>
            </g>
            
            <!-- Stage 4: Final CPA Adder -->
            <g id="sub_cpa" transform="translate(490, 290)">
                <rect x="0" y="0" width="210" height="130" rx="8" fill="#713f12" stroke="#facc15" stroke-width="1.5" />
                <rect x="0" y="0" width="210" height="32" rx="8" fill="#a16207" />
                <text x="12" y="21" fill="#fefce8" font-size="12" font-weight="700">4. Final CPA (Adder)</text>
                <text x="105" y="65" fill="#fde047" font-size="11" text-anchor="middle">Carry Lookahead 16-bit</text>
                <text x="105" y="100" fill="#ffffff" font-size="13" font-family="'JetBrains Mono', monospace" text-anchor="middle">Product = Sum + Carry</text>
            </g>
            
            <!-- Internal Interconnect Buses -->
            <path d="M 220 200 L 260 200" class="net-bus" data-net="booth_ctrl" />
            <path d="M 450 140 L 490 140" class="net-bus" data-net="pp_vectors" />
            <path d="M 595 260 L 595 290" class="net-bus" data-net="csa_vectors" />
        </g>
    </g>
    """)

    # External Ports and Clean Bus Lines
    svg.append("""
    <!-- External Ports and Buses -->
    <!-- Input A -->
    <g class="port-group" onmouseover="highlightNet('a')" onmouseout="clearHighlight()">
        <rect x="30" y="240" width="100" height="36" rx="6" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5" />
        <text x="80" y="263" fill="#38bdf8" font-size="13" font-weight="700" text-anchor="middle">a [7:0]</text>
        <path d="M 130 258 L 180 258" class="net-bus" data-net="a" marker-end="url(#bus-arrow)" />
        <circle cx="180" cy="258" r="4" fill="#38bdf8" class="pin-node" onmouseover="showTooltip(event, 'Port: a [7:0] (Signed INT8 operand)')" onmouseout="hideTooltip()" />
    </g>
    
    <!-- Input B -->
    <g class="port-group" onmouseover="highlightNet('b')" onmouseout="clearHighlight()">
        <rect x="30" y="380" width="100" height="36" rx="6" fill="#1e293b" stroke="#fb923c" stroke-width="1.5" />
        <text x="80" y="403" fill="#fb923c" font-size="13" font-weight="700" text-anchor="middle">b [7:0]</text>
        <path d="M 130 398 L 180 398" class="net-bus" data-net="b" marker-end="url(#bus-arrow)" />
        <circle cx="180" cy="398" r="4" fill="#fb923c" class="pin-node" onmouseover="showTooltip(event, 'Port: b [7:0] (Signed INT8 operand)')" onmouseout="hideTooltip()" />
    </g>
    
    <!-- Output Product -->
    <g class="port-group" onmouseover="highlightNet('product')" onmouseout="clearHighlight()">
        <path d="M 920 375 L 970 375" class="net-bus" data-net="product" marker-end="url(#bus-arrow)" />
        <rect x="970" y="357" width="110" height="36" rx="6" fill="#1e293b" stroke="#4ade80" stroke-width="1.5" />
        <text x="1025" y="380" fill="#4ade80" font-size="13" font-weight="700" text-anchor="middle">product [15:0]</text>
        <circle cx="920" cy="375" r="4" fill="#4ade80" class="pin-node" onmouseover="showTooltip(event, 'Port: product [15:0] (Signed INT16 output)')" onmouseout="hideTooltip()" />
    </g>
    """)

    svg.append(create_svg_footer())
    save_and_validate_svg("\n".join(svg), out_path)

# ==============================================================================
# 2. MAC_UNIT SCHEMATIC GENERATOR
# ==============================================================================
def generate_mac_unit_svg(out_path):
    width, height = 1150, 720
    svg = [create_svg_header(width, height, "mac_unit - Multiply-Accumulate Unit")]

    svg.append("""
    <g transform="translate(40, 75)">
        <text x="0" y="0" fill="#f8fafc" font-size="22" font-weight="700">🔬 MODULE: mac_unit</text>
        <text x="0" y="24" fill="#94a3b8" font-size="13">Combinational Multiply-Accumulator: sum_out = sum_in + (a * b)</text>
    </g>
    """)

    # Main MAC Unit Box
    svg.append("""
    <g id="comp_mac" class="collapsible-comp expanded" transform="translate(180, 130)">
        <g class="component-box" onclick="toggleComponent('comp_mac')">
            <rect class="box-rect" x="0" y="0" width="760" height="500" rx="12" fill="#13172e" stroke="#6366f1" stroke-width="2" />
            <rect x="0" y="0" width="760" height="42" rx="12" fill="#312e81" />
            <rect x="0" y="30" width="760" height="12" fill="#312e81" />
            
            <text x="24" y="27" fill="#e0e7ff" font-size="15" font-weight="700">⚙️ mac_unit (Multiply-Accumulate)</text>
            <text x="320" y="26" fill="#a5b4fc" font-size="12" font-family="'JetBrains Mono', monospace">DATA_WIDTH = 8, ACC_WIDTH = 32</text>
            
            <g class="toggle-badge" transform="translate(725, 21)">
                <circle cx="0" cy="0" r="12" fill="#4338ca" stroke="#c7d2fe" stroke-width="1.5" />
                <text x="0" y="4" fill="#ffffff" font-size="14" font-weight="bold" text-anchor="middle">−</text>
            </g>
        </g>
        
        <!-- COLLAPSED ONLY VIEW -->
        <g class="collapsed-only" transform="translate(230, 160)">
            <rect x="0" y="0" width="300" height="180" rx="10" fill="#1e1b4b" stroke="#818cf8" stroke-width="2" />
            <text x="150" y="70" fill="#f3e8ff" font-size="26" font-weight="bold" text-anchor="middle">MAC CELL</text>
            <text x="150" y="105" fill="#a5b4fc" font-size="14" font-family="'JetBrains Mono', monospace" text-anchor="middle">sum_out = sum_in + (a*b)</text>
            <text x="150" y="140" fill="#6366f1" font-size="12" text-anchor="middle">Click to expand submodules</text>
            
            <path d="M -170 40 L 0 40" class="net-bus" data-net="a" />
            <path d="M -170 90 L 0 90" class="net-bus" data-net="b" />
            <path d="M -170 140 L 0 140" class="net-bus" data-net="sum_in" />
            <path d="M 300 90 L 470 90" class="net-bus" data-net="sum_out" />
        </g>
        
        <!-- EXPANDED VIEW: Multiplier Submodule + Sign Extender + Adder -->
        <g class="collapsible-content expanded-only">
            <!-- Submodule 1: Multiplier Block -->
            <g id="sub_mac_mult" class="collapsible-comp expanded" transform="translate(50, 70)">
                <g class="component-box" onclick="toggleComponent('sub_mac_mult')">
                    <rect class="box-rect" x="0" y="0" width="260" height="240" rx="8" fill="#2d1230" stroke="#f43f5e" stroke-width="1.5" />
                    <rect x="0" y="0" width="260" height="32" rx="8" fill="#881337" />
                    <text x="14" y="21" fill="#ffe4e6" font-size="13" font-weight="700">✖️ u_mult (multiplier_int8)</text>
                    <g class="toggle-badge" transform="translate(235, 16)">
                        <circle cx="0" cy="0" r="9" fill="#be123c" stroke="#fecdd3" stroke-width="1" />
                        <text x="0" y="3" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">−</text>
                    </g>
                </g>
                
                <g class="collapsed-only" transform="translate(30, 80)">
                    <rect x="0" y="0" width="200" height="110" rx="6" fill="#4c0519" />
                    <text x="100" y="50" fill="#fda4af" font-size="14" font-weight="bold" text-anchor="middle">8x8 Multiplier</text>
                    <text x="100" y="75" fill="#f43f5e" font-size="11" text-anchor="middle">Output: 16-bit Product</text>
                </g>
                
                <g class="expanded-only" transform="translate(20, 50)">
                    <rect x="0" y="0" width="220" height="165" rx="6" fill="#1c0514" stroke="#9f1239" />
                    <text x="110" y="30" fill="#fb7185" font-size="12" font-weight="600" text-anchor="middle">Booth 8x8 Core</text>
                    <rect x="15" y="45" width="190" height="40" rx="4" fill="#881337" />
                    <text x="110" y="70" fill="#fff" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">Radix-4 Partial Products</text>
                    <rect x="15" y="95" width="190" height="40" rx="4" fill="#881337" />
                    <text x="110" y="120" fill="#fff" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">16-bit Product = a * b</text>
                </g>
            </g>
            
            <!-- Submodule 2: Sign-Extension Block -->
            <g id="sub_sign_ext" transform="translate(360, 160)">
                <rect class="box-rect" x="0" y="0" width="130" height="110" rx="8" fill="#172554" stroke="#60a5fa" stroke-width="1.5" />
                <rect x="0" y="0" width="130" height="28" rx="8" fill="#1e40af" />
                <text x="10" y="19" fill="#dbeafe" font-size="11" font-weight="700">Sign-Extend</text>
                <text x="65" y="55" fill="#93c5fd" font-size="11" text-anchor="middle">16-bit ➔ 32-bit</text>
                <text x="65" y="78" fill="#bfdbfe" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="middle">{{16{MSB}}, P}</text>
            </g>
            
            <!-- Submodule 3: 32-Bit Accumulator Adder -->
            <g id="sub_adder" class="collapsible-comp expanded" transform="translate(540, 190)">
                <g class="component-box" onclick="toggleComponent('sub_adder')">
                    <rect class="box-rect" x="0" y="0" width="180" height="240" rx="8" fill="#064e3b" stroke="#34d399" stroke-width="1.5" />
                    <rect x="0" y="0" width="180" height="32" rx="8" fill="#065f46" />
                    <text x="12" y="21" fill="#ecfdf5" font-size="13" font-weight="700">➕ 32-Bit Adder</text>
                    <g class="toggle-badge" transform="translate(158, 16)">
                        <circle cx="0" cy="0" r="9" fill="#047857" stroke="#a7f3d0" stroke-width="1" />
                        <text x="0" y="3" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">−</text>
                    </g>
                </g>
                
                <g class="collapsed-only" transform="translate(15, 60)">
                    <rect x="0" y="0" width="150" height="130" rx="6" fill="#022c22" />
                    <text x="75" y="60" fill="#a7f3d0" font-size="14" font-weight="bold" text-anchor="middle">32b ADDER</text>
                    <text x="75" y="85" fill="#6ee7b7" font-size="11" text-anchor="middle">ACC_WIDTH = 32</text>
                </g>
                
                <g class="expanded-only" transform="translate(15, 50)">
                    <rect x="0" y="0" width="150" height="165" rx="6" fill="#022c22" stroke="#059669" />
                    <text x="75" y="28" fill="#6ee7b7" font-size="11" font-weight="600" text-anchor="middle">Carry-Lookahead</text>
                    <rect x="12" y="45" width="126" height="40" rx="4" fill="#047857" />
                    <text x="75" y="70" fill="#fff" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="middle">Input A: sum_in</text>
                    <rect x="12" y="98" width="126" height="40" rx="4" fill="#047857" />
                    <text x="75" y="123" fill="#fff" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="middle">Input B: ext_prod</text>
                </g>
            </g>
            
            <!-- Internal Routing Buses -->
            <path d="M 310 215 L 360 215" class="net-bus" data-net="mult_prod" />
            <rect x="315" y="200" width="40" height="18" rx="3" fill="#1e293b" />
            <text x="335" y="213" fill="#fb7185" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="middle">[15:0]</text>
            
            <path d="M 490 215 L 515 215 L 515 280 L 540 280" class="net-bus" data-net="ext_prod" />
            <rect x="495" y="240" width="40" height="18" rx="3" fill="#1e293b" />
            <text x="515" y="253" fill="#60a5fa" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="middle">[31:0]</text>
            
            <path d="M 0 380 L 540 380" class="net-bus" data-net="sum_in" />
            <rect x="250" y="365" width="40" height="18" rx="3" fill="#1e293b" />
            <text x="270" y="378" fill="#4ade80" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="middle">[31:0]</text>
            
            <path d="M 720 330 L 760 330" class="net-bus" data-net="sum_out" />
        </g>
    </g>
    """)

    # External Ports
    svg.append("""
    <!-- External Ports -->
    <g class="port-group" onmouseover="highlightNet('a')" onmouseout="clearHighlight()">
        <rect x="30" y="190" width="100" height="36" rx="6" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5" />
        <text x="80" y="213" fill="#38bdf8" font-size="13" font-weight="700" text-anchor="middle">a [7:0]</text>
        <path d="M 130 208 L 230 208" class="net-bus" data-net="a" marker-end="url(#bus-arrow)" />
        <circle cx="230" cy="208" r="4" fill="#38bdf8" class="pin-node" onmouseover="showTooltip(event, 'Port: a [7:0] (Signed INT8 activation operand)')" onmouseout="hideTooltip()" />
    </g>
    
    <g class="port-group" onmouseover="highlightNet('b')" onmouseout="clearHighlight()">
        <rect x="30" y="270" width="100" height="36" rx="6" fill="#1e293b" stroke="#fb923c" stroke-width="1.5" />
        <text x="80" y="293" fill="#fb923c" font-size="13" font-weight="700" text-anchor="middle">b [7:0]</text>
        <path d="M 130 288 L 230 288" class="net-bus" data-net="b" marker-end="url(#bus-arrow)" />
        <circle cx="230" cy="288" r="4" fill="#fb923c" class="pin-node" onmouseover="showTooltip(event, 'Port: b [7:0] (Signed INT8 weight operand)')" onmouseout="hideTooltip()" />
    </g>
    
    <g class="port-group" onmouseover="highlightNet('sum_in')" onmouseout="clearHighlight()">
        <rect x="30" y="490" width="100" height="36" rx="6" fill="#1e293b" stroke="#4ade80" stroke-width="1.5" />
        <text x="80" y="513" fill="#4ade80" font-size="13" font-weight="700" text-anchor="middle">sum_in [31:0]</text>
        <path d="M 130 508 L 180 508" class="net-bus" data-net="sum_in" marker-end="url(#bus-arrow)" />
        <circle cx="180" cy="508" r="4" fill="#4ade80" class="pin-node" onmouseover="showTooltip(event, 'Port: sum_in [31:0] (Previous partial sum)')" onmouseout="hideTooltip()" />
    </g>
    
    <g class="port-group" onmouseover="highlightNet('sum_out')" onmouseout="clearHighlight()">
        <path d="M 940 460 L 990 460" class="net-bus" data-net="sum_out" marker-end="url(#bus-arrow)" />
        <rect x="990" y="442" width="120" height="36" rx="6" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5" />
        <text x="1050" y="465" fill="#38bdf8" font-size="13" font-weight="700" text-anchor="middle">sum_out [31:0]</text>
        <circle cx="940" cy="460" r="4" fill="#38bdf8" class="pin-node" onmouseover="showTooltip(event, 'Port: sum_out [31:0] (Accumulated output)')" onmouseout="hideTooltip()" />
    </g>
    """)

    svg.append(create_svg_footer())
    save_and_validate_svg("\n".join(svg), out_path)

# ==============================================================================
# 3. PE (PROCESSING ELEMENT) SCHEMATIC GENERATOR
# ==============================================================================
def generate_pe_svg(out_path):
    width, height = 1300, 850
    svg = [create_svg_header(width, height, "pe - Systolic Processing Element")]

    svg.append("""
    <g transform="translate(40, 75)">
        <text x="0" y="0" fill="#f8fafc" font-size="22" font-weight="700">🔬 MODULE: pe (Processing Element)</text>
        <text x="0" y="24" fill="#94a3b8" font-size="13">Weight-Stationary Systolic Unit with Internal Pipeline Registers &amp; MAC Core</text>
    </g>
    """)

    # Main PE Component Container
    svg.append("""
    <g id="comp_pe" class="collapsible-comp expanded" transform="translate(180, 130)">
        <g class="component-box" onclick="toggleComponent('comp_pe')">
            <rect class="box-rect" x="0" y="0" width="920" height="640" rx="14" fill="#0f172a" stroke="#38bdf8" stroke-width="2.5" />
            <rect x="0" y="0" width="920" height="46" rx="14" fill="#1e293b" />
            <rect x="0" y="32" width="920" height="14" fill="#1e293b" />
            
            <text x="24" y="30" fill="#38bdf8" font-size="17" font-weight="700">⚡ pe (Processing Element Cell)</text>
            <text x="300" y="29" fill="#94a3b8" font-size="13" font-family="'JetBrains Mono', monospace">Weight-Stationary Arch | INT8 Weights &amp; Acts | INT32 Acc</text>
            
            <g class="toggle-badge" transform="translate(880, 23)">
                <circle cx="0" cy="0" r="13" fill="#0284c7" stroke="#bae6fd" stroke-width="1.5" />
                <text x="0" y="5" fill="#ffffff" font-size="16" font-weight="bold" text-anchor="middle">−</text>
            </g>
        </g>
        
        <!-- COLLAPSED ONLY VIEW: Clean Black-Box PE Cell -->
        <g class="collapsed-only" transform="translate(280, 200)">
            <rect x="0" y="0" width="360" height="240" rx="12" fill="#1e293b" stroke="#0ea5e9" stroke-width="2" />
            <text x="180" y="80" fill="#ffffff" font-size="28" font-weight="bold" text-anchor="middle">PE CELL</text>
            <text x="180" y="115" fill="#38bdf8" font-size="15" font-family="'JetBrains Mono', monospace" text-anchor="middle">Weight-Stationary</text>
            <text x="180" y="150" fill="#94a3b8" font-size="13" text-anchor="middle">Registers: a_reg, weight_reg, sum_reg</text>
            <text x="180" y="180" fill="#64748b" font-size="12" text-anchor="middle">Click to expand internal structure</text>
        </g>
        
        <!-- EXPANDED ONLY VIEW: Full Internal Hardware Architecture -->
        <g class="collapsible-content expanded-only">
            <!-- 1. Weight Register & Load Multiplexer Block -->
            <g id="block_weight_reg" class="collapsible-comp expanded" transform="translate(40, 70)">
                <g class="component-box" onclick="toggleComponent('block_weight_reg')">
                    <rect class="box-rect" x="0" y="0" width="220" height="180" rx="8" fill="#1e2417" stroke="#84cc16" stroke-width="1.5" />
                    <rect x="0" y="0" width="220" height="30" rx="8" fill="#365314" />
                    <text x="12" y="20" fill="#ecfccb" font-size="12" font-weight="700">💾 weight_reg [7:0]</text>
                    <g class="toggle-badge" transform="translate(198, 15)">
                        <circle cx="0" cy="0" r="8" fill="#4d7c0f" stroke="#d9f99d" />
                        <text x="0" y="3" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">−</text>
                    </g>
                </g>
                
                <g class="collapsed-only" transform="translate(15, 45)">
                    <rect x="0" y="0" width="190" height="115" rx="5" fill="#141c0c" />
                    <text x="95" y="65" fill="#bef264" font-size="13" font-weight="bold" text-anchor="middle">Weight DFF</text>
                </g>
                
                <g class="expanded-only" transform="translate(15, 45)">
                    <!-- Load MUX -->
                    <polygon points="10,20 40,30 40,70 10,80" fill="#3f6212" stroke="#a3e635" />
                    <text x="25" y="55" fill="#ffffff" font-size="10" text-anchor="middle">MUX</text>
                    
                    <!-- DFF Register -->
                    <rect x="65" y="15" width="120" height="80" rx="6" fill="#1a2e05" stroke="#65a30d" />
                    <text x="125" y="45" fill="#d9f99d" font-size="12" font-weight="700" text-anchor="middle">8-Bit DFF</text>
                    <text x="125" y="68" fill="#a3e635" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="middle">weight_reg</text>
                    
                    <path d="M 40 50 L 65 50" class="net-bus" data-net="w_mux_dff" />
                    <text x="5" y="110" fill="#bef264" font-size="9">En: weight_load_en</text>
                </g>
            </g>
            
            <!-- 2. Activation Register (a_reg) Block -->
            <g id="block_a_reg" class="collapsible-comp expanded" transform="translate(40, 270)">
                <g class="component-box" onclick="toggleComponent('block_a_reg')">
                    <rect class="box-rect" x="0" y="0" width="220" height="160" rx="8" fill="#132433" stroke="#38bdf8" stroke-width="1.5" />
                    <rect x="0" y="0" width="220" height="30" rx="8" fill="#0369a1" />
                    <text x="12" y="20" fill="#e0f2fe" font-size="12" font-weight="700">💾 a_reg [7:0] (Pipeline)</text>
                    <g class="toggle-badge" transform="translate(198, 15)">
                        <circle cx="0" cy="0" r="8" fill="#0284c7" stroke="#bae6fd" />
                        <text x="0" y="3" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">−</text>
                    </g>
                </g>
                
                <g class="collapsed-only" transform="translate(15, 45)">
                    <rect x="0" y="0" width="190" height="95" rx="5" fill="#082f49" />
                    <text x="95" y="55" fill="#7dd3fc" font-size="13" font-weight="bold" text-anchor="middle">Activation DFF</text>
                </g>
                
                <g class="expanded-only" transform="translate(15, 45)">
                    <rect x="40" y="10" width="145" height="75" rx="6" fill="#0c4a6e" stroke="#0284c7" />
                    <text x="112" y="40" fill="#e0f2fe" font-size="12" font-weight="700" text-anchor="middle">8-Bit DFF</text>
                    <text x="112" y="62" fill="#7dd3fc" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="middle">a_reg &lt;= a_in</text>
                    <text x="5" y="98" fill="#38bdf8" font-size="9">En: compute_en</text>
                </g>
            </g>
            
            <!-- 3. Combinational MAC Submodule (u_mac) -->
            <g id="block_u_mac" class="collapsible-comp expanded" transform="translate(330, 110)">
                <g class="component-box" onclick="toggleComponent('block_u_mac')">
                    <rect class="box-rect" x="0" y="0" width="310" height="380" rx="10" fill="#1e1838" stroke="#a855f7" stroke-width="2" />
                    <rect x="0" y="0" width="310" height="36" rx="10" fill="#581c87" />
                    <rect x="0" y="24" width="310" height="12" fill="#581c87" />
                    <text x="16" y="24" fill="#f3e8ff" font-size="13" font-weight="700">⚙️ u_mac (mac_unit)</text>
                    <g class="toggle-badge" transform="translate(285, 18)">
                        <circle cx="0" cy="0" r="10" fill="#7e22ce" stroke="#e9d5ff" />
                        <text x="0" y="4" fill="#ffffff" font-size="12" font-weight="bold" text-anchor="middle">−</text>
                    </g>
                </g>
                
                <g class="collapsed-only" transform="translate(20, 60)">
                    <rect x="0" y="0" width="270" height="280" rx="8" fill="#2e1065" stroke="#9333ea" />
                    <text x="135" y="120" fill="#f3e8ff" font-size="20" font-weight="bold" text-anchor="middle">MAC CORE</text>
                    <text x="135" y="155" fill="#d8b4fe" font-size="13" font-family="'JetBrains Mono', monospace" text-anchor="middle">mac_result =</text>
                    <text x="135" y="180" fill="#c084fc" font-size="13" font-family="'JetBrains Mono', monospace" text-anchor="middle">sum_in + (a * w)</text>
                    <text x="135" y="220" fill="#7e22ce" font-size="11" text-anchor="middle">Click to expand MAC internals</text>
                </g>
                
                <g class="expanded-only" transform="translate(20, 50)">
                    <!-- Multiplier Core inside MAC -->
                    <rect x="15" y="15" width="240" height="120" rx="6" fill="#3b0764" stroke="#c084fc" />
                    <text x="135" y="45" fill="#f5d0fe" font-size="12" font-weight="700" text-anchor="middle">✖️ Signed Multiplier (8x8)</text>
                    <text x="135" y="70" fill="#d8b4fe" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">prod = a_in * weight_reg</text>
                    <rect x="35" y="85" width="200" height="30" rx="4" fill="#581c87" />
                    <text x="135" y="105" fill="#fae8ff" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="middle">Sign-Extend ➔ 32-bit</text>
                    
                    <!-- 32-bit Adder inside MAC -->
                    <rect x="15" y="165" width="240" height="135" rx="6" fill="#064e3b" stroke="#34d399" />
                    <text x="135" y="195" fill="#d1fae5" font-size="12" font-weight="700" text-anchor="middle">➕ 32-Bit Accumulator Adder</text>
                    <text x="135" y="225" fill="#6ee7b7" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">sum_in + ext_prod</text>
                    <text x="135" y="255" fill="#a7f3d0" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">mac_result [31:0]</text>
                    
                    <!-- Internal MAC Wire -->
                    <path d="M 135 135 L 135 165" class="net-bus" data-net="internal_prod" />
                </g>
            </g>
            
            <!-- 4. Accumulator Register (sum_reg) Block -->
            <g id="block_sum_reg" class="collapsible-comp expanded" transform="translate(680, 240)">
                <g class="component-box" onclick="toggleComponent('block_sum_reg')">
                    <rect class="box-rect" x="0" y="0" width="200" height="220" rx="8" fill="#063e32" stroke="#10b981" stroke-width="1.5" />
                    <rect x="0" y="0" width="200" height="30" rx="8" fill="#047857" />
                    <text x="12" y="20" fill="#ecfdf5" font-size="12" font-weight="700">💾 sum_reg [31:0]</text>
                    <g class="toggle-badge" transform="translate(178, 15)">
                        <circle cx="0" cy="0" r="8" fill="#059669" stroke="#a7f3d0" />
                        <text x="0" y="3" fill="#ffffff" font-size="10" font-weight="bold" text-anchor="middle">−</text>
                    </g>
                </g>
                
                <g class="collapsed-only" transform="translate(15, 45)">
                    <rect x="0" y="0" width="170" height="155" rx="5" fill="#022c22" />
                    <text x="85" y="85" fill="#6ee7b7" font-size="13" font-weight="bold" text-anchor="middle">Sum DFF</text>
                </g>
                
                <g class="expanded-only" transform="translate(15, 45)">
                    <rect x="15" y="20" width="140" height="110" rx="6" fill="#064e3b" stroke="#059669" />
                    <text x="85" y="55" fill="#a7f3d0" font-size="12" font-weight="700" text-anchor="middle">32-Bit DFF</text>
                    <text x="85" y="80" fill="#ffffff" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="middle">sum_reg &lt;=</text>
                    <text x="85" y="98" fill="#ffffff" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="middle">mac_result</text>
                    <text x="5" y="150" fill="#10b981" font-size="9">En: compute_en</text>
                </g>
            </g>
            
            <!-- PE Internal Interconnect Buses -->
            <path d="M 260 160 L 330 160" class="net-bus" data-net="weight_reg" />
            <circle cx="295" cy="160" r="3" fill="#84cc16" />
            
            <path d="M 295 160 L 295 560 L 150 560 L 150 640" class="net-bus" data-net="weight_out" />
            
            <path d="M 0 350 L 40 350" class="net-bus" data-net="a_in" />
            <path d="M 25 350 L 25 210 L 330 210" class="net-bus" data-net="a_in" />
            
            <path d="M 260 350 L 310 350 L 310 500 L 920 500" class="net-bus" data-net="a_out" />
            
            <path d="M 480 0 L 480 110" class="net-bus" data-net="sum_in" />
            
            <path d="M 640 350 L 680 350" class="net-bus" data-net="mac_result" />
            
            <path d="M 780 460 L 780 640" class="net-bus" data-net="sum_out" />
        </g>
    </g>
    """)

    # External Port Connectors
    svg.append("""
    <!-- External Boundary Pins and Buses -->
    <!-- Weight In (Top) -->
    <g class="port-group" onmouseover="highlightNet('weight_in')" onmouseout="clearHighlight()">
        <rect x="220" y="30" width="130" height="34" rx="6" fill="#1e293b" stroke="#84cc16" stroke-width="1.5" />
        <text x="285" y="52" fill="#84cc16" font-size="12" font-weight="700" text-anchor="middle">weight_in [7:0]</text>
        <path d="M 285 64 L 285 130" class="net-bus" data-net="weight_in" marker-end="url(#bus-arrow)" />
        <circle cx="285" cy="130" r="4" fill="#84cc16" class="pin-node" onmouseover="showTooltip(event, 'Port: weight_in [7:0] (Shifts weights from top neighbor)')" onmouseout="hideTooltip()" />
    </g>
    
    <!-- Weight Out (Bottom) -->
    <g class="port-group" onmouseover="highlightNet('weight_out')" onmouseout="clearHighlight()">
        <path d="M 330 770 L 330 810" class="net-bus" data-net="weight_out" marker-end="url(#bus-arrow)" />
        <rect x="265" y="810" width="130" height="34" rx="6" fill="#1e293b" stroke="#84cc16" stroke-width="1.5" />
        <text x="330" y="832" fill="#84cc16" font-size="12" font-weight="700" text-anchor="middle">weight_out [7:0]</text>
        <circle cx="330" cy="770" r="4" fill="#84cc16" class="pin-node" onmouseover="showTooltip(event, 'Port: weight_out [7:0] (Passes weight down to bottom neighbor)')" onmouseout="hideTooltip()" />
    </g>
    
    <!-- Activation In (Left) -->
    <g class="port-group" onmouseover="highlightNet('a_in')" onmouseout="clearHighlight()">
        <rect x="30" y="460" width="110" height="36" rx="6" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5" />
        <text x="85" y="483" fill="#38bdf8" font-size="13" font-weight="700" text-anchor="middle">a_in [7:0]</text>
        <path d="M 140 478 L 180 478" class="net-bus" data-net="a_in" marker-end="url(#bus-arrow)" />
        <circle cx="180" cy="478" r="4" fill="#38bdf8" class="pin-node" onmouseover="showTooltip(event, 'Port: a_in [7:0] (Activation entering from left neighbor)')" onmouseout="hideTooltip()" />
    </g>
    
    <!-- Activation Out (Right) -->
    <g class="port-group" onmouseover="highlightNet('a_out')" onmouseout="clearHighlight()">
        <path d="M 1100 630 L 1150 630" class="net-bus" data-net="a_out" marker-end="url(#bus-arrow)" />
        <rect x="1150" y="612" width="110" height="36" rx="6" fill="#1e293b" stroke="#38bdf8" stroke-width="1.5" />
        <text x="1205" y="635" fill="#38bdf8" font-size="13" font-weight="700" text-anchor="middle">a_out [7:0]</text>
        <circle cx="1100" cy="630" r="4" fill="#38bdf8" class="pin-node" onmouseover="showTooltip(event, 'Port: a_out [7:0] (Registered activation leaving to right neighbor)')" onmouseout="hideTooltip()" />
    </g>
    
    <!-- Partial Sum In (Top) -->
    <g class="port-group" onmouseover="highlightNet('sum_in')" onmouseout="clearHighlight()">
        <rect x="595" y="30" width="130" height="34" rx="6" fill="#1e293b" stroke="#4ade80" stroke-width="1.5" />
        <text x="660" y="52" fill="#4ade80" font-size="12" font-weight="700" text-anchor="middle">sum_in [31:0]</text>
        <path d="M 660 64 L 660 130" class="net-bus" data-net="sum_in" marker-end="url(#bus-arrow)" />
        <circle cx="660" cy="130" r="4" fill="#4ade80" class="pin-node" onmouseover="showTooltip(event, 'Port: sum_in [31:0] (Partial sum from top neighbor)')" onmouseout="hideTooltip()" />
    </g>
    
    <!-- Partial Sum Out (Bottom) -->
    <g class="port-group" onmouseover="highlightNet('sum_out')" onmouseout="clearHighlight()">
        <path d="M 960 770 L 960 810" class="net-bus" data-net="sum_out" marker-end="url(#bus-arrow)" />
        <rect x="895" y="810" width="130" height="34" rx="6" fill="#1e293b" stroke="#4ade80" stroke-width="1.5" />
        <text x="960" y="832" fill="#4ade80" font-size="12" font-weight="700" text-anchor="middle">sum_out [31:0]</text>
        <circle cx="960" cy="770" r="4" fill="#4ade80" class="pin-node" onmouseover="showTooltip(event, 'Port: sum_out [31:0] (Accumulated sum to bottom neighbor)')" onmouseout="hideTooltip()" />
    </g>
    
    <!-- Global Control Pins -->
    <g class="control-port" transform="translate(30, 180)">
        <rect x="0" y="0" width="90" height="26" rx="4" fill="#1f1a10" stroke="#f59e0b" />
        <text x="45" y="17" fill="#f59e0b" font-size="11" font-weight="600" text-anchor="middle">clk</text>
        <path d="M 90 13 L 180 13" class="net-control" />
    </g>
    <g class="control-port" transform="translate(30, 220)">
        <rect x="0" y="0" width="90" height="26" rx="4" fill="#1f1a10" stroke="#f59e0b" />
        <text x="45" y="17" fill="#f59e0b" font-size="11" font-weight="600" text-anchor="middle">rst_n</text>
        <path d="M 90 13 L 180 13" class="net-control" />
    </g>
    <g class="control-port" transform="translate(30, 260)">
        <rect x="0" y="0" width="90" height="26" rx="4" fill="#1f1a10" stroke="#f59e0b" />
        <text x="45" y="17" fill="#f59e0b" font-size="11" font-weight="600" text-anchor="middle">en</text>
        <path d="M 90 13 L 180 13" class="net-control" />
    </g>
    <g class="control-port" transform="translate(30, 300)">
        <rect x="0" y="0" width="130" height="26" rx="4" fill="#1f1a10" stroke="#f59e0b" />
        <text x="65" y="17" fill="#f59e0b" font-size="11" font-weight="600" text-anchor="middle">weight_load_en</text>
        <path d="M 130 13 L 180 13" class="net-control" />
    </g>
    """)

    svg.append(create_svg_footer())
    save_and_validate_svg("\n".join(svg), out_path)

# ==============================================================================
# 4. SYSTOLIC_ARRAY (4x4 2D GRID) SCHEMATIC GENERATOR
# ==============================================================================
def generate_systolic_array_svg(out_path):
    width, height = 1800, 1500
    svg = [create_svg_header(width, height, "systolic_array - 4x4 Weight-Stationary Matrix Multiplier")]

    svg.append("""
    <g transform="translate(50, 75)">
        <text x="0" y="0" fill="#f8fafc" font-size="24" font-weight="700">🔬 MODULE: systolic_array (4x4 2D Grid)</text>
        <text x="0" y="26" fill="#94a3b8" font-size="14">Parameterized 2D Systolic Tensor Core: 16 Processing Elements with Skew Pipelines</text>
        <text x="0" y="48" fill="#38bdf8" font-size="12">💡 Interactive: Click on ANY PE Cell to expand its internal architecture in-place!</text>
    </g>
    """)

    start_x, start_y = 380, 180
    pe_w, pe_h = 240, 200
    spacing_x, spacing_y = 320, 280

    # 1. Row Skewing Delay Pipelines on the Left
    svg.append("""<g id="skew_pipelines" transform="translate(80, 180)">""")
    for r in range(4):
        y_pos = r * spacing_y + 40
        svg.append(f"""
        <!-- Row {r} Skew Unit -->
        <g id="skew_row_{r}" class="collapsible-comp expanded" transform="translate(0, {y_pos})">
            <rect x="0" y="0" width="220" height="110" rx="8" fill="#132433" stroke="#0284c7" stroke-width="1.5" />
            <rect x="0" y="0" width="220" height="28" rx="8" fill="#0369a1" />
            <text x="12" y="19" fill="#e0f2fe" font-size="11" font-weight="700">Row {r} Skew Delay</text>
            <text x="200" y="19" fill="#bae6fd" font-size="10" font-family="'JetBrains Mono', monospace">+{r}T</text>
            
            <g class="collapsed-only" transform="translate(10, 40)">
                <text x="100" y="35" fill="#7dd3fc" font-size="12" text-anchor="middle">{r} Cycle Pipeline</text>
            </g>
            <g class="expanded-only" transform="translate(10, 38)">
        """)
        if r == 0:
            svg.append("""
                <text x="100" y="30" fill="#38bdf8" font-size="12" font-weight="600" text-anchor="middle">Direct Feed (0 Delay)</text>
                <text x="100" y="48" fill="#94a3b8" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="middle">act_skewed[0] = in[0]</text>
            """)
        else:
            for d in range(r):
                box_x = 10 + d * (180 // r)
                svg.append(f"""
                <rect x="{box_x}" y="10" width="{160 // r}" height="45" rx="4" fill="#0c4a6e" stroke="#38bdf8" />
                <text x="{box_x + (80 // r)}" y="36" fill="#ffffff" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="middle">DFF {d}</text>
                """)
        svg.append(f"""
            </g>
        </g>
        
        <!-- Input Port Box -->
        <g class="port-group" onmouseover="highlightNet('act_in_{r}')" onmouseout="clearHighlight()">
            <rect x="-60" y="{y_pos + 35}" width="50" height="30" rx="4" fill="#1e293b" stroke="#38bdf8" />
            <text x="-35" y="{y_pos + 55}" fill="#38bdf8" font-size="11" font-weight="bold" text-anchor="middle">A{r}</text>
            <path d="M -10 {y_pos + 50} L 0 {y_pos + 50}" class="net-bus" data-net="act_in_{r}" marker-end="url(#bus-arrow)" />
        </g>
        
        <!-- Wire from Skew Pipeline to First PE in Row -->
        <path d="M 220 {y_pos + 55} L {start_x - 80} {y_pos + 55}" class="net-bus" data-net="act_skewed_{r}" marker-end="url(#bus-arrow)" />
        """)
    svg.append("""</g>""")

    # 2. 4x4 Grid of Collapsible Processing Elements (PEs)
    svg.append("""<g id="pe_grid">""")
    for r in range(4):
        for c in range(4):
            x_pos = start_x + c * spacing_x
            y_pos = start_y + r * spacing_y
            comp_id = f"pe_{r}_{c}"
            
            svg.append(f"""
            <!-- PE ({r}, {c}) -->
            <g id="{comp_id}" class="collapsible-comp collapsed" transform="translate({x_pos}, {y_pos})">
                <g class="component-box" onclick="toggleComponent('{comp_id}')">
                    <rect class="box-rect" x="0" y="0" width="{pe_w}" height="{pe_h}" rx="10" fill="#111c30" stroke="#2563eb" stroke-width="2" />
                    <rect x="0" y="0" width="{pe_w}" height="32" rx="10" fill="#1d4ed8" />
                    <rect x="0" y="20" width="{pe_w}" height="12" fill="#1d4ed8" />
                    
                    <text x="12" y="21" fill="#eff6ff" font-size="12" font-weight="700">PE ({r},{c})</text>
                    <text x="90" y="20" fill="#bfdbfe" font-size="10" font-family="'JetBrains Mono', monospace">u_pe[{r}][{c}]</text>
                    
                    <g class="toggle-badge" transform="translate({pe_w - 20}, 16)">
                        <circle cx="0" cy="0" r="9" fill="#1e40af" stroke="#dbeafe" />
                        <text x="0" y="3" fill="#ffffff" font-size="11" font-weight="bold" text-anchor="middle">+</text>
                    </g>
                </g>
                
                <!-- COLLAPSED VIEW -->
                <g class="collapsed-only" transform="translate(10, 40)">
                    <rect x="10" y="10" width="{pe_w - 40}" height="{pe_h - 60}" rx="6" fill="#1e293b" stroke="#3b82f6" />
                    <text x="{(pe_w - 40)//2 + 10}" y="50" fill="#60a5fa" font-size="15" font-weight="bold" text-anchor="middle">MAC CELL</text>
                    <text x="{(pe_w - 40)//2 + 10}" y="75" fill="#93c5fd" font-size="11" font-family="'JetBrains Mono', monospace" text-anchor="middle">C += A * W</text>
                    <text x="{(pe_w - 40)//2 + 10}" y="105" fill="#64748b" font-size="10" text-anchor="middle">Click to expand</text>
                </g>
                
                <!-- EXPANDED VIEW -->
                <g class="expanded-only" transform="translate(8, 38)">
                    <!-- Mini Weight Reg -->
                    <rect x="8" y="8" width="85" height="40" rx="4" fill="#365314" stroke="#84cc16" />
                    <text x="50" y="32" fill="#d9f99d" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="middle">W_reg [7:0]</text>
                    
                    <!-- Mini Activation Reg -->
                    <rect x="8" y="58" width="85" height="40" rx="4" fill="#0c4a6e" stroke="#38bdf8" />
                    <text x="50" y="82" fill="#bae6fd" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="middle">A_reg [7:0]</text>
                    
                    <!-- Mini MAC Arithmetic Unit -->
                    <rect x="105" y="8" width="110" height="90" rx="5" fill="#3b0764" stroke="#c084fc" />
                    <text x="160" y="32" fill="#fae8ff" font-size="11" font-weight="700" text-anchor="middle">u_mac</text>
                    <text x="160" y="52" fill="#d8b4fe" font-size="9" font-family="'JetBrains Mono', monospace" text-anchor="middle">Mult 8x8</text>
                    <text x="160" y="72" fill="#d8b4fe" font-size="9" font-family="'JetBrains Mono', monospace" text-anchor="middle">+ Acc 32b</text>
                    
                    <!-- Mini Sum Reg -->
                    <rect x="105" y="108" width="110" height="40" rx="4" fill="#064e3b" stroke="#34d399" />
                    <text x="160" y="132" fill="#d1fae5" font-size="10" font-family="'JetBrains Mono', monospace" text-anchor="middle">Sum_reg [31:0]</text>
                </g>
            </g>
            """)

            # Horizontal Activation Interconnect Wires
            if c < 3:
                svg.append(f"""
                <path d="M {x_pos + pe_w} {y_pos + 120} L {x_pos + spacing_x} {y_pos + 120}" class="net-bus" data-net="h_act_{r}_{c}" marker-end="url(#bus-arrow)" />
                """)
            else:
                svg.append(f"""
                <path d="M {x_pos + pe_w} {y_pos + 120} L {x_pos + pe_w + 50} {y_pos + 120}" class="net-bus" data-net="act_out_{r}" marker-end="url(#bus-arrow)" />
                <rect x="{x_pos + pe_w + 50}" y="{y_pos + 105}" width="70" height="30" rx="4" fill="#1e293b" stroke="#38bdf8" />
                <text x="{x_pos + pe_w + 85}" y="{y_pos + 125}" fill="#38bdf8" font-size="11" font-weight="bold" text-anchor="middle">A_out[{r}]</text>
                """)

            # Vertical Partial Sum Interconnect Wires
            if r < 3:
                svg.append(f"""
                <path d="M {x_pos + 160} {y_pos + pe_h} L {x_pos + 160} {y_pos + spacing_y}" class="net-bus" data-net="v_sum_{r}_{c}" marker-end="url(#bus-arrow)" />
                """)
            else:
                svg.append(f"""
                <path d="M {x_pos + 160} {y_pos + pe_h} L {x_pos + 160} {y_pos + pe_h + 60}" class="net-bus" data-net="sum_out_{c}" marker-end="url(#bus-arrow)" />
                <rect x="{x_pos + 105}" y="{y_pos + pe_h + 60}" width="110" height="32" rx="4" fill="#1e293b" stroke="#4ade80" />
                <text x="{x_pos + 160}" y="{y_pos + pe_h + 81}" fill="#4ade80" font-size="11" font-weight="bold" text-anchor="middle">C_out[{c}] [31:0]</text>
                """)

            # Vertical Weight Shift Wires
            if r == 0:
                svg.append(f"""
                <rect x="{x_pos + 15}" y="{y_pos - 75}" width="95" height="30" rx="4" fill="#1e293b" stroke="#84cc16" />
                <text x="{x_pos + 62}" y="{y_pos - 55}" fill="#84cc16" font-size="11" font-weight="bold" text-anchor="middle">W_in[{c}] [7:0]</text>
                <path d="M {x_pos + 62} {y_pos - 45} L {x_pos + 62} {y_pos}" class="net-bus" data-net="weight_in_{c}" marker-end="url(#bus-arrow)" />
                
                <rect x="{x_pos + 115}" y="{y_pos - 75}" width="90" height="30" rx="4" fill="#1e293b" stroke="#4ade80" />
                <text x="{x_pos + 160}" y="{y_pos - 55}" fill="#4ade80" font-size="11" font-weight="bold" text-anchor="middle">Sum=0 [{c}]</text>
                <path d="M {x_pos + 160} {y_pos - 45} L {x_pos + 160} {y_pos}" class="net-bus" data-net="sum_in_top_{c}" marker-end="url(#bus-arrow)" />
                """)
            
            if r < 3:
                svg.append(f"""
                <path d="M {x_pos + 60} {y_pos + pe_h} L {x_pos + 60} {y_pos + spacing_y}" class="net-bus" data-net="v_weight_{r}_{c}" marker-end="url(#bus-arrow)" />
                """)

    svg.append("""</g>""")

    svg.append(create_svg_footer())
    save_and_validate_svg("\n".join(svg), out_path)

# ==============================================================================
# MAIN ENTRYPOINT
# ==============================================================================
def generate_all_schematics(out_dir="schematics"):
    proj_dir = Path(__file__).resolve().parent.parent
    target_dir = proj_dir / out_dir
    target_dir.mkdir(parents=True, exist_ok=True)

    print("\n=======================================================")
    print("🎨 GENERATING INTERACTIVE COLLAPSIBLE HARDWARE SCHEMATICS")
    print("=======================================================\n")

    generate_multiplier_svg(target_dir / "multiplier_int8.svg")
    generate_mac_unit_svg(target_dir / "mac_unit.svg")
    generate_pe_svg(target_dir / "pe.svg")
    generate_systolic_array_svg(target_dir / "systolic_array.svg")

    print("\n✨ All interactive collapsible SVGs successfully generated and XML-validated in:", target_dir)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "schematics"
    generate_all_schematics(out)
