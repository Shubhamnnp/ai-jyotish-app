"""
Multi-Agent Structured Evidence Pack Communication Protocol (Phase 7, Task P7-T2).
Reference: docs/upgrade/MASTER_10_PHASE_ROADMAP.md (Phase 7).

Defines the intra-agent message schema and validation guards ensuring
that AI agents communicate strictly via structured, mathematically-grounded Evidence Packs.
"""

from typing import Dict, List, Optional, Any
from datetime import datetime, timezone
from pydantic import BaseModel, Field
import uuid

from ..evidence.pack import EvidenceFinding, EvidencePack


class AgentMessage(BaseModel):
    """Structured message passed between specialist agents and orchestrator."""
    message_id: str = Field(default_factory=lambda: f"MSG-{uuid.uuid4().hex[:8]}")
    sender_agent_id: str
    recipient_agent_id: str
    domain: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    confidence_score: float = Field(ge=0.0, le=1.0)
    evidence_findings: List[EvidenceFinding] = Field(default_factory=list)
    provenance_rule_ids: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_audited: bool = False


class AgentProtocolValidator:
    """Validates intra-agent messages to prevent hallucination or malformed payloads."""

    @classmethod
    def validate_message(cls, msg: AgentMessage) -> bool:
        """Guarantees message adherence to Daivajna Brain communication invariants."""
        if not msg.sender_agent_id or not msg.recipient_agent_id:
            raise ValueError("AgentMessage must specify both sender and recipient agent IDs.")

        if msg.confidence_score < 0.0 or msg.confidence_score > 1.0:
            raise ValueError(f"Confidence score {msg.confidence_score} out of valid bounds [0.0, 1.0].")

        # Every finding must have valid non-empty claims and bounded strength
        for f in msg.evidence_findings:
            if not f.claim_en or not f.claim_hi:
                raise ValueError(f"Finding {f.finding_id} missing required bilingual claims.")
            if f.strength < 0.0 or f.strength > 1.0:
                raise ValueError(f"Finding {f.finding_id} strength {f.strength} out of bounds.")

        return True

    @classmethod
    def create_response(
        cls,
        sender_id: str,
        recipient_id: str,
        domain: str,
        findings: List[EvidenceFinding],
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentMessage:
        rule_ids = []
        for f in findings:
            rule_ids.extend(f.rule_ids)

        msg = AgentMessage(
            sender_agent_id=sender_id,
            recipient_agent_id=recipient_id,
            domain=domain,
            confidence_score=round(confidence, 3),
            evidence_findings=findings,
            provenance_rule_ids=list(set(rule_ids)),
            metadata=metadata or {},
            is_audited=False
        )
        cls.validate_message(msg)
        return msg


default_protocol_validator = AgentProtocolValidator()
