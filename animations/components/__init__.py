"""
Hardware AI Acceleration - Standard Cell Animation Library
Modular, parameter-driven components for broadcast-quality hardware masterclasses.
"""

from components.layout import (
    HardwareConfig,
    StageLayout,
    TextRole,
    SemanticText,
    SemanticMath,
    HStack,
    VStack,
    ConstraintAnchor,
    fit_to_bounds,
)
from components.kinematics import (
    SiliconCameraRig,
    KineticSiliconScene,
    VoiceoverTracker,
    StageContext,
)
from components.signals import (
    KineticClock,
    LiveOscilloscope,
    StoryboardTimeline,
)
from components.dataflow import (
    SiliconWire,
    LaserPacketStream,
)
from components.arithmetic import (
    TwosComplementWheel,
    FullAdderGateSchematic,
    RippleCarryChain,
    AccumulatorGauge,
)
from components.trace_engine import (
    TracePlayback,
    TraceDrivenController,
    SchematicNetlist,
)
from components.silicon_cells import (
    PinProbe,
    DieFootprint,
    MemoryEnergyBar,
    ProcessingElementCell,
)

__all__ = [
    "HardwareConfig",
    "StageLayout",
    "TextRole",
    "SemanticText",
    "SemanticMath",
    "HStack",
    "VStack",
    "ConstraintAnchor",
    "fit_to_bounds",
    "SiliconCameraRig",
    "KineticSiliconScene",
    "VoiceoverTracker",
    "StageContext",
    "KineticClock",
    "LiveOscilloscope",
    "StoryboardTimeline",
    "SiliconWire",
    "LaserPacketStream",
    "TwosComplementWheel",
    "FullAdderGateSchematic",
    "RippleCarryChain",
    "AccumulatorGauge",
    "TracePlayback",
    "TraceDrivenController",
    "SchematicNetlist",
    "PinProbe",
    "DieFootprint",
    "MemoryEnergyBar",
    "ProcessingElementCell",
]
