"""
Hardware AI Acceleration - Standard Cell Animation Library
Modular, parameter-driven components for broadcast-quality hardware masterclasses.
"""

from components.layout import HardwareConfig, StageLayout
from components.kinematics import SiliconCameraRig
from components.signals import KineticClock, LiveOscilloscope, StoryboardTimeline
from components.dataflow import SiliconWire, LaserPacketStream
from components.arithmetic import (
    TwosComplementWheel,
    FullAdderGateSchematic,
    RippleCarryChain,
    AccumulatorGauge,
)
from components.trace_engine import TracePlayback, SchematicNetlist

__all__ = [
    "HardwareConfig",
    "StageLayout",
    "SiliconCameraRig",
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
    "SchematicNetlist",
]

