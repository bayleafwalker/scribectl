import shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "fixtures" / "fertile-flames"


@pytest.fixture
def fixture_root() -> Path:
    return FIXTURE


@pytest.fixture
def vault(fixture_root):
    from scribectl.core.vault import Vault

    return Vault.load(fixture_root)


@pytest.fixture
def scratch_root(tmp_path) -> Path:
    """A fresh vault root holding a mutable copy of the fixture project."""
    root = tmp_path / "Creative"
    shutil.copytree(FIXTURE, root / "Works" / "Fertile Flames")
    return root


@pytest.fixture
def scratch_project(scratch_root) -> Path:
    return scratch_root / "Works" / "Fertile Flames"
