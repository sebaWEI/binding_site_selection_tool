"""Integration tests that need native ViennaRNA RNAup."""

from __future__ import annotations

import logging

import pytest

from bsst.models import SelectOptions, Target
from bsst.pipeline import generate_windows, resolve_executable, run_rnaup_candidate


@pytest.mark.integration
def test_real_rnaup_scores_one_window() -> None:
    exe = resolve_executable("RNAup")
    if not exe:
        pytest.skip("RNAup is not installed")
    # Mixed 40 nt window plus flanking context so RNAup can place the interaction.
    sequence = ("ACGTACCGTTGCATAGCTAG" * 12)[:200]
    target = Target(sequence, "rnaup_integration")
    row = generate_windows(target, window_size=40).iloc[2]
    result = run_rnaup_candidate(
        target,
        row,
        SelectOptions(window_size=40, context=40, temperature=37.0),
        logging.getLogger("test_rnaup_integration"),
        exe,
    )
    assert result["status"] in {"eligible", "failed"}
    if result["status"] == "failed":
        assert result["failure_reason"] == "off_anchor_interaction"
        return
    assert isinstance(result["rnaup_dG_total"], float)
    assert result["anchor_overlap"] == 1.0
