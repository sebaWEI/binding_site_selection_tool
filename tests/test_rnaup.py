import logging
from pathlib import Path

import pandas as pd

from bsst.models import SelectOptions, Target
from bsst.pipeline import (
    anchor_interaction,
    generate_windows,
    parse_rnaup_output,
    run_rnaup_candidate,
)


OUTPUT = "((((((&))))))  121,160 : 1,40  (-12.30 = -20.00 + 5.00 + 2.70)"


def test_parser_and_anchor_mapping() -> None:
    parsed = parse_rnaup_output(OUTPUT)
    assert parsed
    assert parsed["rnaup_dG_total"] == -12.3
    assert parsed["interaction_target_start"] == 121
    ok, overlap, start, end = anchor_interaction(parsed, 0, 120, 160)
    assert ok and overlap == 1.0 and (start, end) == (120, 160)
    off, _, _, _ = anchor_interaction(parsed, 1000, 120, 160)
    assert not off


def test_mock_rnaup_command_and_result(tmp_path: Path) -> None:
    executable = tmp_path / "RNAup"
    executable.write_text(
        "#!/bin/sh\n"
        "printf '>target\\n>query\\n((((((&))))))  121,160 : 1,40  "
        "(-12.30 = -20.00 + 5.00 + 2.70)\\n'\n"
    )
    executable.chmod(0o755)
    target = Target("ACGT" * 100, "target")
    row = generate_windows(target, 40).iloc[120]
    result = run_rnaup_candidate(
        target, row, SelectOptions(context=120), logging.getLogger("test"), str(executable)
    )
    assert result["status"] == "eligible"
    assert result["anchor_overlap"] == 1.0
