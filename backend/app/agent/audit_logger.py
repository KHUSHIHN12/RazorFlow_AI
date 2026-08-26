import datetime
from typing import List, Dict, Any, Optional

class AgentAuditLogger:
    """
    Transparent Audit Logger for CommercePilot AI Agent actions.
    Tracks step-by-step reasoning, intent parsing, candidate evaluation, tool calls, and guardrail checks.
    """
    def __init__(self):
        self.logs: List[Dict[str, Any]] = []

    def log(self, step: str, details: str, payload: Optional[Dict[str, Any]] = None):
        entry = {
            "timestamp": datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "step": step,
            "details": details,
            "payload": payload or {}
        }
        self.logs.append(entry)
        try:
            # Safe console print replacing unicode characters if needed for Windows terminal
            safe_details = details.encode('ascii', errors='replace').decode('ascii')
            print(f"[AgentAuditLog] [{entry['timestamp']}] {step.upper()}: {safe_details}")
        except Exception:
            pass

    def clear(self):
        self.logs = []

    def get_logs(self) -> List[Dict[str, Any]]:
        return self.logs

audit_logger = AgentAuditLogger()
