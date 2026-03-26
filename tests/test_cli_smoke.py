from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def test_runtime_directory_is_gitignored():
    gitignore = REPO_ROOT / ".gitignore"
    assert gitignore.exists()
    content = gitignore.read_text(encoding="utf-8")
    assert ".link-research/" in content


def test_tools_package_marker_exists():
    assert (REPO_ROOT / "tools" / "__init__.py").exists()
