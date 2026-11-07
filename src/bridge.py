"""Core adapter and schema normalizer for regional MCP tool payloads."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import unicodedata


@dataclass
class MCPToolResponse:
    tool_name: str
    status: str
    content: List[Dict[str, Any]]
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "tool": self.tool_name,
            "status": self.status,
            "content": self.content,
            "metadata": self.metadata,
        }


def normalize_text(text: str) -> str:
    """Normalize mixed-script Unicode strings (NFC) and strip control chars."""
    if not isinstance(text, str):
        raise TypeError("Expected string input for normalization.")
    normalized = unicodedata.normalize("NFC", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch)[0] != "C" or ch in ("\n", "\t"))


def adapt_legacy_payload(tool_name: str, raw_payload: Dict[str, Any], required_keys: Optional[List[str]] = None) -> MCPToolResponse:
    """Validate and transform a legacy API dictionary into a standardized MCP response."""
    required_keys = required_keys or []
    missing = [k for k in required_keys if k not in raw_payload]
    if missing:
        return MCPToolResponse(
            tool_name=tool_name,
            status="error",
            content=[{"type": "text", "text": f"Missing required fields: {', '.join(missing)}"}],
        )

    sanitized_items: List[Dict[str, Any]] = []
    for key, value in raw_payload.items():
        clean_val = normalize_text(value) if isinstance(value, str) else value
        sanitized_items.append({"type": "text", "key": key, "value": clean_val})

    return MCPToolResponse(
        tool_name=tool_name,
        status="success",
        content=sanitized_items,
        metadata={"field_count": len(sanitized_items)},
    )
