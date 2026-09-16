import json
from pathlib import Path

from typer.testing import CliRunner

from bsst.cli import _header_metadata, app

runner = CliRunner()


def test_legacy_fasta_header_metadata() -> None:
    assert _header_metadata(
        "target chrom=4 start=10 end=20 strand=-"
    ) == {"chrom": "4", "start": "10", "end": "20", "strand": "-"}


def test_help_doctor_and_config(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setenv("BSST_HOME", str(tmp_path / "home"))
    assert runner.invoke(app, ["--help"]).exit_code == 0
    doctor = runner.invoke(app, ["doctor"])
    assert doctor.exit_code == 0
    assert "RNAup" in doctor.stdout
    listed = runner.invoke(app, ["resources"])
    assert listed.exit_code == 0
    assert "GENCODE" in listed.stdout
    assert "NCBI dbSNP" in listed.stdout
    shown = runner.invoke(app, ["config", "show"])
    assert shown.exit_code == 0
    assert "runs_dir" in shown.stdout


def test_small_select_with_mock_rnaup(tmp_path: Path, monkeypatch) -> None:
    executable = tmp_path / "RNAup"
    executable.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = \"--version\" ]; then echo 'RNAup mock 1'; exit 0; fi\n"
        "printf '>target\\n>query\\n.  1,40 : 1,40  (-10 = -15 + 3 + 2)\\n'\n"
    )
    executable.chmod(0o755)
    monkeypatch.setenv("PATH", f"{tmp_path}")
    fasta = tmp_path / "target.fa"
    fasta.write_text(">target\nACGTACGTACGTACGTACGTACGTACGTACGTACGTACGT\n")
    runs = tmp_path / "runs"
    result = runner.invoke(
        app,
        [
            "select", "fasta", str(fasta), "--runs-dir", str(runs),
            "--skip-blast", "--skip-variants", "--window-size", "40",
        ],
    )
    assert result.exit_code == 0, result.output
    run_dir = next(runs.iterdir())
    for name in (
        "run.log", "manifest.json", "inputs/target.fasta",
        "all_candidates.tsv", "candidates.tsv", "blast_hits.tsv",
    ):
        assert (run_dir / name).exists()
    assert json.loads((run_dir / "manifest.json").read_text())["status"] == "completed"
    all_candidates = (run_dir / "all_candidates.tsv").read_text()
    assert "anchor_overlap" in all_candidates
    assert "eligible" in all_candidates
