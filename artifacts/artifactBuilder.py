"""
ArtifactBuilder class definition
"""

from __future__ import annotations
from typing import Any
from pathlib import Path
from identifiers.identifier import Identifier


class ArtifactBuilder:
    """ArtifactBuilder class definition
    """

    vault: Path

    @classmethod
    def save(cls, artifact: Any) -> None:
        raise NotImplementedError("save method must be implemented by subclass")
    
    @classmethod
    def load(cls, identifier: Identifier) -> Any:
        raise NotImplementedError("load method must be implemented by subclass")
    
    @classmethod
    def build(cls, artifact_data: Any) -> Any:
        raise NotImplementedError("buildArtifact method must be implemented by subclass")
    
    @classmethod
    def parse(cls, artifact_class: type, markdown_str: str):
        raise NotImplementedError("parse method must be implemented by subclass")
    
    @classmethod
    def set_vault(cls, vault: str):
        if not Path(vault).exists():
            raise ValueError(f"Vault-Path does not exist\n{vault}")
        cls.vault = vault
        
    
