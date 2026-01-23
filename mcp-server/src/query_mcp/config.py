"""Configuration management for query-mcp."""

import json
import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Config:
    """Server configuration."""

    context_dir: Path = field(default_factory=lambda: Path("context"))
    prompt_file: Path | None = None
    log_level: str = "INFO"

    @classmethod
    def load(cls, config_path: Path | None = None) -> "Config":
        """Load config from file, env, or defaults."""
        # Priority: explicit path > env var > default location
        path = (
            config_path
            or (Path(p) if (p := os.environ.get("QUERY_MCP_CONFIG")) else None)
            or Path("config/query-mcp.json")
        )

        if path.exists():
            return cls._from_file(path)
        return cls._from_env()

    @classmethod
    def _from_file(cls, path: Path) -> "Config":
        """Load from JSON config file."""
        data = json.loads(path.read_text())
        return cls(
            context_dir=Path(data.get("context_dir", "context")),
            prompt_file=Path(p) if (p := data.get("prompt_file")) else None,
            log_level=data.get("log_level", "INFO"),
        )

    @classmethod
    def _from_env(cls) -> "Config":
        """Load from environment variables."""
        return cls(
            context_dir=Path(os.environ.get("CONTEXT_DIR", "context")),
            prompt_file=Path(p) if (p := os.environ.get("PROMPT_FILE")) else None,
            log_level=os.environ.get("LOG_LEVEL", "INFO"),
        )
