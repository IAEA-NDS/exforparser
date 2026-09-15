"""Tests for observable CLI orchestration."""

import sys

from exforparser import main_cli


class _AvailableEngine:
    def connect(self):
        return object()


def _record_observable_calls(monkeypatch):
    calls = []
    observable_functions = (
        "crosssection",
        "angular_distribution",
        "energy_distribution",
        "double_differential_cross_section",
        "fission_yield",
        "neutron_observables",
        "resonance_integral",
        "macs",
        "gamma_gamma",
        "resonance_spacing",
        "resonance_parameter",
        "level_density",
        "strength_function",
        "transmission",
        "thermal",
    )
    for function_name in observable_functions:
        monkeypatch.setattr(
            main_cli,
            function_name,
            lambda *args, _name=function_name, **kwargs: calls.append(
                (_name, args, kwargs)
            ),
        )
    return calls


def test_all_writes_only_to_pure_exfor_tree(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["exforparser", "-o", "all"])
    monkeypatch.setitem(main_cli.engines, "exfor", _AvailableEngine())
    calls = _record_observable_calls(monkeypatch)

    main_cli.cli()

    assert calls == [
        ("crosssection", (), {}),
        ("angular_distribution", (), {}),
        ("energy_distribution", (), {}),
        ("double_differential_cross_section", (), {}),
        ("fission_yield", (), {}),
        ("neutron_observables", (), {}),
        ("resonance_integral", (), {"pure_exfor": True}),
        ("macs", (), {"pure_exfor": True}),
        ("gamma_gamma", (), {"pure_exfor": True}),
        ("resonance_spacing", (), {"pure_exfor": True}),
        ("resonance_parameter", (), {"pure_exfor": True}),
        ("level_density", (), {"pure_exfor": True}),
        ("strength_function", (), {"pure_exfor": True}),
        ("transmission", (), {"pure_exfor": True}),
        ("thermal", ("thermal",), {"pure_exfor": True}),
    ]


def test_legacy_writes_only_legacy_outputs(monkeypatch):
    monkeypatch.setattr(sys, "argv", ["exforparser", "-o", "legacy"])
    monkeypatch.setitem(main_cli.engines, "exfor", _AvailableEngine())
    calls = _record_observable_calls(monkeypatch)

    main_cli.cli()

    assert calls == [
        ("thermal", ("thermal",), {}),
        ("resonance_integral", (), {}),
        ("macs", (), {}),
        ("gamma_gamma", (), {}),
        ("resonance_spacing", (), {}),
        ("resonance_parameter", (), {}),
        ("level_density", (), {}),
        ("strength_function", (), {}),
    ]
