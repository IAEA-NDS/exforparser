"""Tests for exfor_reaction.py parser functions."""
import pytest
from exforparser.parser.exfor_reaction import (
    parse_nuclide,
    parse_reaction_parts,
    split_sf,
    parse_operators,
    parse_parenthesis,
)


class TestParseNuclide:
    def test_basic_nuclide(self):
        assert parse_nuclide("92-U-235") == "92-U-235"

    def test_nuclide_with_isomer(self):
        assert parse_nuclide("52-TE-127-M") == "52-TE-127-M"

    def test_no_match_returns_none(self):
        assert parse_nuclide("invalid") is None

    def test_nuclide_with_leading_text(self):
        # parse_nuclide uses re.match so only matches from start
        assert parse_nuclide("not-a-nuclide") is None


class TestSplitSf:
    def test_full_sf(self):
        result = split_sf(["SF4", "SF5", "SF6", "SF7", "SF8", "SF9"])
        assert result == {
            "sf4": "SF4",
            "sf5": "SF5",
            "sf6": "SF6",
            "sf7": "SF7",
            "sf8": "SF8",
            "sf9": "SF9",
        }

    def test_partial_sf_fills_none(self):
        result = split_sf(["ELEM/MASS", None, "FY"])
        assert result["sf4"] == "ELEM/MASS"
        assert result["sf5"] is None
        assert result["sf6"] == "FY"
        assert result["sf7"] is None

    def test_minimal_sf(self):
        result = split_sf(["46-PD-106"])
        assert result["sf4"] == "46-PD-106"
        assert result["sf5"] is None


class TestParseReactionParts:
    def test_simple_reaction(self):
        result = parse_reaction_parts("(92-U-235(N,F),,SIG)")
        assert result["target"] == "92-U-235"
        assert result["process"] == "N,F"
        assert result["sf6"] == "SIG"

    def test_reaction_with_product(self):
        result = parse_reaction_parts("(26-FE-56(N,P)25-MN-56,,SIG)")
        assert result["target"] == "26-FE-56"
        assert result["sf4"] == "25-MN-56"

    def test_empty_reaction_returns_empty_dict(self):
        result = parse_reaction_parts("no parentheses here")
        assert result == {}

    def test_partial_reaction(self):
        result = parse_reaction_parts("(92-U-235(N,F)ELEM/MASS,CUM,FY)")
        assert result["sf4"] == "ELEM/MASS"
        assert result["sf5"] == "CUM"
        assert result["sf6"] == "FY"


class TestParseOperators:
    def test_single_divide(self):
        code = "((78-PT-198(G,N)78-PT-197,,SIG,,BRA)/(79-AU-197(G,N)79-AU-196,,SIG,,BRA))"
        ops = parse_operators(code)
        assert len(ops) == 1
        assert ops[0]["operator"] == "/"

    def test_double_slash_ratio(self):
        code = "((83-BI-209(N,EL)83-BI-209,,DA)//(83-BI-209(N,EL)83-BI-209,,DA))"
        ops = parse_operators(code)
        assert len(ops) == 1
        assert ops[0]["operator"] == "//"
        assert ops[0]["main"] is True

    def test_addition(self):
        code = "((46-PD-106(N,X)45-RH-105,,SIG)+(46-PD-105(N,P)45-RH-105,,SIG,,RAB))"
        ops = parse_operators(code)
        assert len(ops) == 1
        assert ops[0]["operator"] == "+"

    def test_no_operators(self):
        ops = parse_operators("(92-U-235(N,F),,SIG)")
        assert ops == []


class TestParseParenthesis:
    def test_balanced_simple(self):
        left, right = parse_parenthesis("(abc)", 0)
        assert left == [0]
        assert right == [4]

    def test_nested(self):
        left, right = parse_parenthesis("((a)(b))", 0)
        assert len(left) == len(right)

    def test_balanced_counts(self):
        expr = "((92-U-235(N,F),,SIG)/(79-AU-197(G,N)79-AU-196,,SIG))"
        left, right = parse_parenthesis(expr, 0)
        assert len(left) == len(right)
