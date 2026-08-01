from dataclasses import dataclass
from enum import Enum
from typing import List, Optional
from datetime import datetime

class SdkLanguage(str, Enum):
    PYTHON = "Python"
    TYPESCRIPT = "TypeScript"
    NODEJS = "Node.js"
    GO = "Go"
    JAVA = "Java"

@dataclass
class SdkConfig:
    """Standardized configuration bounds enforced across all SDKs."""
    max_retries: int = 3
    timeout_seconds: int = 30
    user_agent_prefix: str = "avenor-sdk"
    enable_telemetry: bool = True

@dataclass
class SdkRelease:
    id: str
    language: SdkLanguage
    version: str
    download_url: str
    install_command: str
    release_notes: str
    published_at: datetime
    is_latest: bool
