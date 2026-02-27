"""
License key management for DevMaster Pro.

Simple file-based licensing system for MVP.
"""

import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

LICENSE_FILE = Path.home() / ".devmaster-license"


class License:
    """License management."""

    def __init__(self):
        self.license_data = self._load_license()

    def _load_license(self) -> dict:
        """Load license from disk."""
        if LICENSE_FILE.exists():
            try:
                with open(LICENSE_FILE) as f:
                    return json.load(f)
            except:
                return {}
        return {}

    def _save_license(self, data: dict):
        """Save license to disk."""
        with open(LICENSE_FILE, 'w') as f:
            json.dump(data, f, indent=2)

    def activate(self, license_key: str) -> bool:
        """
        Activate a license key.

        For MVP: Simple validation of key format.
        Later: API call to validate with backend.
        """
        # Validate key format (MVP: just check format)
        if not self._validate_key_format(license_key):
            return False

        # Parse license key
        license_info = self._parse_key(license_key)
        if not license_info:
            return False

        # Save license
        self.license_data = {
            "key": license_key,
            "tier": license_info["tier"],
            "activated_at": datetime.now().isoformat(),
            "email": license_info.get("email", ""),
        }
        self._save_license(self.license_data)
        return True

    def deactivate(self):
        """Deactivate license."""
        if LICENSE_FILE.exists():
            LICENSE_FILE.unlink()
        self.license_data = {}

    def is_active(self) -> bool:
        """Check if license is active."""
        return bool(self.license_data.get("key"))

    def get_tier(self) -> str:
        """Get license tier: free, pro, team, enterprise."""
        if not self.is_active():
            return "free"
        return self.license_data.get("tier", "free")

    def is_pro(self) -> bool:
        """Check if user has Pro features."""
        tier = self.get_tier()
        return tier in ["pro", "team", "enterprise"]

    def is_team(self) -> bool:
        """Check if user has Team features."""
        tier = self.get_tier()
        return tier in ["team", "enterprise"]

    def get_info(self) -> dict:
        """Get license info."""
        if not self.is_active():
            return {
                "tier": "free",
                "status": "inactive",
                "features": ["Local AI only", "Basic tools", "Community support"]
            }

        tier = self.get_tier()
        features = {
            "pro": [
                "✅ AI-Powered Auto-Fix",
                "✅ Cloud AI Providers (Claude, GPT-4, Groq)",
                "✅ Advanced Visualizations",
                "✅ Code Explanations",
                "✅ Priority Support",
                "✅ Export Reports",
            ],
            "team": [
                "✅ Everything in Pro",
                "✅ Team Dashboard",
                "✅ Shared Knowledge Graph",
                "✅ Code Review Automation",
                "✅ Team Analytics",
                "✅ CI/CD Integration",
                "✅ SSO/SAML",
            ],
        }

        return {
            "tier": tier,
            "status": "active",
            "activated": self.license_data.get("activated_at", ""),
            "features": features.get(tier, []),
        }

    def _validate_key_format(self, key: str) -> bool:
        """
        Validate license key format.

        Format: DM-{TIER}-{RANDOM}-{CHECKSUM}
        Example: DM-PRO-ABC123-XYZ789
        """
        parts = key.split("-")
        if len(parts) != 4:
            return False

        prefix, tier, random, checksum = parts

        if prefix != "DM":
            return False

        if tier not in ["PRO", "TEAM", "ENTERPRISE"]:
            return False

        if len(random) < 6:
            return False

        # Validate checksum (simple hash of first 3 parts)
        expected_checksum = self._generate_checksum(f"{prefix}-{tier}-{random}")
        return checksum == expected_checksum

    def _parse_key(self, key: str) -> Optional[dict]:
        """Parse license key to extract info."""
        parts = key.split("-")
        if len(parts) != 4:
            return None

        _, tier, _, _ = parts

        return {
            "tier": tier.lower(),
        }

    def _generate_checksum(self, data: str) -> str:
        """Generate checksum for license key."""
        return hashlib.sha256(data.encode()).hexdigest()[:6].upper()


# Global license instance
_license = None


def get_license() -> License:
    """Get global license instance."""
    global _license
    if _license is None:
        _license = License()
    return _license


def require_pro(feature_name: str = "This feature"):
    """
    Decorator to require Pro license.

    Raises exception if not Pro.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            license = get_license()
            if not license.is_pro():
                raise Exception(
                    f"{feature_name} requires DevMaster Pro.\n\n"
                    f"Upgrade at: https://devmaster.pro\n"
                    f"Or use local AI: debug-companion ai setup → choose ollama"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_team(feature_name: str = "This feature"):
    """Decorator to require Team license."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            license = get_license()
            if not license.is_team():
                raise Exception(
                    f"{feature_name} requires DevMaster Team.\n\n"
                    f"Upgrade at: https://devmaster.pro/team"
                )
            return func(*args, **kwargs)
        return wrapper
    return decorator
