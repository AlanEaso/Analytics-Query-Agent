from enum import Enum

class AgentState(Enum):
    INITIALIZING = "initializing"
    SEARCHING = "searching"
    PROBING = "probing"
    ANALYZING = "analyzing"
    ESCALATING = "escalating"
    COMPLETE = "complete"
