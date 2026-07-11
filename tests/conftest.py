import shutil
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
FIXTURE = REPO / "fixtures" / "fertile-flames"
RUNOSONG = REPO / "fixtures" / "runosong"


@pytest.fixture
def fixture_root() -> Path:
    return FIXTURE


@pytest.fixture
def runosong_root() -> Path:
    return RUNOSONG


@pytest.fixture
def vault(fixture_root):
    from scribectl.core.vault import Vault

    return Vault.load(fixture_root)


@pytest.fixture
def fiction():
    from scribectl.templateset import load_set

    return load_set("fiction")


@pytest.fixture
def gamedev():
    from scribectl.templateset import load_set

    return load_set("gamedev")


@pytest.fixture
def scratch_runosong(tmp_path) -> Path:
    """A fresh vault root holding a mutable copy of the runosong project only."""
    root = tmp_path / "Creative"
    shutil.copytree(RUNOSONG, root / "Works" / "Runosong")
    return root


@pytest.fixture
def scratch_root(tmp_path) -> Path:
    """A fresh vault root holding a mutable copy of the fixture project."""
    root = tmp_path / "Creative"
    shutil.copytree(FIXTURE, root / "Works" / "Fertile Flames")
    return root


@pytest.fixture
def scratch_project(scratch_root) -> Path:
    return scratch_root / "Works" / "Fertile Flames"
