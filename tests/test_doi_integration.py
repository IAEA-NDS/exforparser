from exforparser import main_cli


def test_updated_cli_passes_changed_entries_to_installed_module(monkeypatch):
    calls = []
    monkeypatch.setattr(
        main_cli,
        "process_updated_entry",
        lambda **kwargs: ["10001", "A0001"],
    )
    monkeypatch.setattr(
        main_cli,
        "process_updated_entries",
        lambda entries: calls.append(entries),
    )
    monkeypatch.setattr(
        main_cli.argparse.ArgumentParser,
        "parse_args",
        lambda self: type(
            "Args",
            (),
            {
                "init": False,
                "load": False,
                "history": False,
                "convert": None,
                "tabulate": "updated",
                "observables": None,
            },
        )(),
    )

    main_cli.cli()

    assert calls == [["10001", "A0001"]]
