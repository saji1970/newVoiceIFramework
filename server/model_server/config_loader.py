from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)


class NodeConfig(BaseModel):
    id: str
    type: str  # llm, api, transform, condition, loop, tool
    config: dict[str, Any] = Field(default_factory=dict)

    # Allow extra fields to be merged into config
    model_config = {"extra": "allow"}

    def merged_config(self) -> dict:
        """Merge top-level extra fields into config dict."""
        extra = {}
        for k, v in self.__pydantic_extra__.items():
            extra[k] = v
        return {**self.config, **extra}


class PipelineConfig(BaseModel):
    name: str
    version: str = "1.0"
    description: str = ""
    trigger: str = "chat"  # chat, voice, api, webhook
    nodes: list[NodeConfig]
    variables: dict[str, Any] = Field(default_factory=dict)

    @field_validator("nodes")
    @classmethod
    def validate_unique_ids(cls, nodes: list[NodeConfig]) -> list[NodeConfig]:
        ids = [n.id for n in nodes]
        dupes = [x for x in ids if ids.count(x) > 1]
        if dupes:
            raise ValueError(f"Duplicate node IDs: {set(dupes)}")
        return nodes


def load_pipeline_yaml(path: str | Path) -> PipelineConfig:
    """Load and validate a pipeline from a YAML file."""
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"Pipeline file not found: {path}")

    raw = yaml.safe_load(path.read_text(encoding="utf-8"))
    return _parse_pipeline_dict(raw)


def load_pipeline_json(path: str | Path) -> PipelineConfig:
    """Load and validate a pipeline from a JSON file."""
    path = Path(path)
    raw = json.loads(path.read_text(encoding="utf-8"))
    return _parse_pipeline_dict(raw)


def parse_pipeline_dict(data: dict) -> PipelineConfig:
    """Parse and validate a pipeline from a dict (e.g., from API request)."""
    return _parse_pipeline_dict(data)


def _parse_pipeline_dict(data: dict) -> PipelineConfig:
    """Internal parser that normalizes node configs."""
    nodes = []
    for node_data in data.get("nodes", []):
        # Extract known fields, put the rest in config
        node_id = node_data.pop("id")
        node_type = node_data.pop("type")
        config = node_data.pop("config", {})
        # Remaining fields become part of config
        config.update(node_data)
        nodes.append(NodeConfig(id=node_id, type=node_type, config=config))

    return PipelineConfig(
        name=data.get("name", "unnamed"),
        version=data.get("version", "1.0"),
        description=data.get("description", ""),
        trigger=data.get("trigger", "chat"),
        nodes=nodes,
        variables=data.get("variables", {}),
    )
