"""
Configuration management
"""
import json
import os
from typing import Dict, List, Optional
from pathlib import Path


class Config:
    """Load and validate configuration"""

    def __init__(self, config_path: str):
        self.config_path = Path(config_path)
        self.config = self._load()

    def _load(self) -> Dict:
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")

        with open(self.config_path) as f:
            return json.load(f)

    def get_sources(self) -> Dict[str, List[str]]:
        """Get sources dict"""
        sources = self.config.get("sources", {})

        # Normalize format
        normalized = {}
        for source_type, config in sources.items():
            if isinstance(config, dict):
                # New format: {"boards": [...]}
                key = list(config.keys())[0]
                normalized[source_type] = config[key]
            else:
                # Old format: direct list
                normalized[source_type] = config

        return normalized

    def get_filters(self) -> Dict:
        """Get filters dict"""
        return self.config.get("filters", {})

    def get_state_path(self) -> str:
        """Get state DB path"""
        return self.config.get("state_path", ".state/jobhunt.sqlite")

    def get_slack_webhook(self) -> Optional[str]:
        """Get Slack webhook URL"""
        # Try environment variable first (for GitHub Actions)
        webhook = os.getenv("SLACK_WEBHOOK_URL")
        if webhook:
            return webhook

        # Fallback to config
        alerts = self.config.get("alerts", {})
        slack_config = alerts.get("slack", {})

        if not slack_config.get("enabled", False):
            return None

        env_var = slack_config.get("webhook_env", "SLACK_WEBHOOK_URL")
        return os.getenv(env_var)

