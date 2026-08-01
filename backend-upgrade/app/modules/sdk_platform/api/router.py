from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
import uuid

from app.modules.sdk_platform.domain.models import SdkLanguage, SdkRelease
from app.modules.sdk_platform.application.services import SdkRegistry

router = APIRouter(prefix="/v1/sdks", tags=["Public API - SDK Discovery"])

# Global mock registry
_registry = SdkRegistry()

# Seed registry
_registry.register_release(SdkRelease(
    id="sdk-py-1", language=SdkLanguage.PYTHON, version="1.2.0",
    download_url="https://pypi.org/project/avenor-sdk", install_command="pip install avenor-sdk",
    release_notes="Added auto-pagination for /companies", published_at=datetime.utcnow(), is_latest=True
))
_registry.register_release(SdkRelease(
    id="sdk-ts-1", language=SdkLanguage.TYPESCRIPT, version="2.0.1",
    download_url="https://npmjs.com/package/@avenor/sdk", install_command="npm install @avenor/sdk",
    release_notes="TypeScript definitions for Marketplaces Apps", published_at=datetime.utcnow(), is_latest=True
))

@router.get("/")
async def list_latest_sdks() -> List[dict]:
    """Returns the latest versions and installation commands for all official SDKs."""
    latest = []
    for lang in SdkLanguage:
        rel = _registry.get_latest(lang)
        if rel:
            latest.append({
                "language": rel.language,
                "version": rel.version,
                "install_command": rel.install_command,
                "download_url": rel.download_url
            })
    return latest

@router.get("/{language}")
async def get_sdk_by_language(language: str) -> dict:
    try:
        lang_enum = SdkLanguage(language)
    except ValueError:
        raise HTTPException(status_code=404, detail="Language not supported")
        
    rel = _registry.get_latest(lang_enum)
    if not rel:
        raise HTTPException(status_code=404, detail="No SDK releases found for this language")
        
    return {
        "language": rel.language,
        "version": rel.version,
        "install_command": rel.install_command,
        "release_notes": rel.release_notes
    }
