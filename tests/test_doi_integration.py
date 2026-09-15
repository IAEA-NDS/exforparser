from pathlib import Path

from exforparser import main_cli


def test_process_updated_dois_passes_only_changed_entries(monkeypatch, tmp_path):
    (tmp_path / "main.py").touch()
    calls = []
    monkeypatch.setattr(main_cli, "DOI_REF_PARSING_DIR", str(tmp_path))
    monkeypatch.setattr(
        main_cli.subprocess,
        "run",
        lambda command, **kwargs: calls.append((command, kwargs)),
    )

    main_cli.process_updated_dois(["10001", "A0001"])

    command, kwargs = calls[0]
    assert command == [
        main_cli.sys.executable,
        str(Path(tmp_path) / "main.py"),
        "updated",
        "10001",
        "A0001",
    ]
    assert kwargs == {"cwd": str(tmp_path), "check": True}


def test_process_updated_dois_is_disabled_without_configuration(monkeypatch):
    monkeypatch.setattr(main_cli, "DOI_REF_PARSING_DIR", None)
    monkeypatch.setattr(
        main_cli.subprocess,
        "run",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("unexpected call")),
    )

    main_cli.process_updated_dois(["10001"])
