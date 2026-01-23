"""Context loading and management."""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class ContextStore:
    """Stores loaded database context."""

    def __init__(self) -> None:
        self.tables: list[dict] = []
        self.schema: dict = {}

    def load(self, context_dir: Path) -> None:
        """Load all context files from directory."""
        self._load_tables(context_dir)
        self._load_schema(context_dir)

    def _load_tables(self, context_dir: Path) -> None:
        """Load table descriptions."""
        # Find any *context*.json file
        for f in context_dir.glob("*context*.json"):
            with open(f) as fp:
                self.tables = json.load(fp)
            logger.info(f"Loaded {len(self.tables)} tables from {f.name}")
            return
        logger.warning("No context file found")

    def _load_schema(self, context_dir: Path) -> None:
        """Load schema file."""
        for f in context_dir.glob("*schema*.json"):
            with open(f) as fp:
                self.schema = json.load(fp)
            logger.info(f"Loaded schema from {f.name}")
            return
        logger.warning("No schema file found")
