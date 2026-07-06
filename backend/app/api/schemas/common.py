from enum import Enum


class Strategy(str, Enum):
    BALANCED = "balanced"
    SAFETY_FIRST = "safety_first"
    COST_OPTIMIZED = "cost_optimized"
    EQUITY_FOCUSED = "equity_focused"
    CUSTOM = "custom"
