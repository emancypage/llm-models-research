"""Tests for the 26 November 2026 exploratory post hoc analysis after closeout."""

import pytest

from token_exposure import categories, choice_prediction, choice_tokens, counts_in, gsm_groups, record, reference_exposure


def test_reference_and_final_are_distinct_and_count_whole_ids():
    ids = {"solution": {64, 164, 810}, "final": {164}}
    flags = reference_exposure(ids, {64, 810}, {64})
    assert flags == {"solution_source_ids": [64, 810], "solution_any": True, "solution_digits": True,
                     "final_source_ids": [], "final_any": False, "final_digits": False}
    assert counts_in([164, 64, 64, 810], {64, 810}) == {"64": 2, "810": 1}


def test_category_boundaries_count_spaces_and_preserve_case():
    assert categories("00")["digits"]
    assert not categories("A0")["digits"]
    assert categories(" B")["answer_letters_trimmed"]
    assert categories(" a")["alphabetic_word_or_piece"]
    assert not categories(" a")["answer_letters_trimmed"]
    assert categories(".\n")["punctuation"] and not categories(".\n")["whitespace"]
    assert categories(":\n\n")["contains_newline"] and not categories(":\n\n")["two_characters_or_fewer"]
    assert categories("\n")["whitespace"]


class BoundaryTokenizer:
    def encode(self, text, add_special_tokens):
        assert not add_special_tokens
        return {"Q:": [8], "Q: A": [8, 17], "Q: B": [8, 18], "Q:A": [8, 4]}[text]


def test_choice_ids_include_delimiter_at_context_boundary():
    arguments = {"gen_args_0": {"arg_0": "Q: ", "arg_1": "A"},
                 "gen_args_1": {"arg_0": "Q: ", "arg_1": "B"}}
    assert choice_tokens(BoundaryTokenizer(), arguments) == [[17], [18]]
    arguments["gen_args_1"]["arg_0"] = "Q:"
    with pytest.raises(ValueError, match="contexts"):
        choice_tokens(BoundaryTokenizer(), arguments)


def test_arc_uses_answer_character_lengths_and_gsm_losses_are_paired():
    row = {"doc": {"choices": {"text": ["x", "longer"]}}, "filtered_resps": [[-1.0], [-3.0]]}
    assert choice_prediction(row, "arc") == 1
    groups = {}
    for a, b in [(1, 0), (0, 0), (0, 1), (1, 1)]:
        record(groups, "exposed", a, b)
    assert groups["exposed"] == {"items": 4, "original_correct": 2, "edited_correct": 2, "gains": 1, "losses": 1}


def test_review_subset_has_its_own_denominator_and_output_counts():
    selected, digits, review = {4, 31, 99}, {4, 31}, {4}
    rows = []
    scores = {("gsm1024", arm): {} for arm in ("S", "D500")}
    for idx, (piece, s, e) in enumerate([(4, 1, 0), (4, 0, 0), (31, 1, 1), (99, 0, 1)]):
        flags = reference_exposure({"solution": {piece}, "final": {piece}}, selected, digits)
        rows.append({"doc_id": idx, **flags, "original_source_counts_1024": {str(piece): 2},
                     "edited_source_counts_1024": {"99": 1} if idx == 3 else {}})
        for arm, score in (("S", s), ("D500", e)):
            scores["gsm1024", arm]["gsm8k", idx] = (None, score)
    groups, emissions = gsm_groups(rows, scores, "D500", selected, digits, review, 1024)
    assert groups["final_review_five_exposed"] == {"items": 2, "original_correct": 1, "edited_correct": 0,
                                                    "losses": 1, "gains": 0}
    assert groups["final_digits_exposed"]["items"] == 3
    assert groups["solution_any_unexposed"]["items"] == 0
    assert emissions["edited"]["source_occurrences_by_id"] == {99: 1}
    assert emissions["edited"]["with_digits"] == 0
