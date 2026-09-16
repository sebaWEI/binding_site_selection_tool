from __future__ import annotations

import json
import re
from pathlib import Path

import typer
from Bio import SeqIO
from rich.console import Console
from rich.table import Table

from .config import load_config
from .db import initialize, tool_report
from .fetch import EnsemblArchiveError, fetch_gene_utr
from .models import SelectOptions, Target
from .pipeline import select
from .resources import (
    DBSNP_B151_GRCH38P7_COMMON_ALL,
    GENCODE_V45_TRANSCRIPTS,
    catalog,
    discover_blast_db,
    discover_variant_vcf,
)

app = typer.Typer(help="bsst: Binding Site Selection Tool for Hepha antisense domains. Primary input is FASTA.")
db_app = typer.Typer(help="Manage local database configuration.")
select_app = typer.Typer(
    help="Select sites. Prefer `select fasta`; `select gene` fetches Ensembl 111 as a convenience."
)
config_app = typer.Typer(help="Inspect configuration.")
app.add_typer(db_app, name="db")
app.add_typer(select_app, name="select")
app.add_typer(config_app, name="config")
console = Console()


def _header_metadata(description: str) -> dict[str, str]:
    """Parse the key=value header emitted by this project and older fetchers."""
    return dict(re.findall(r"\b(chrom|start|end|strand)=([^\s]+)", description))


@db_app.command("init")
def db_init(
    db_dir: Path | None = typer.Option(None, help="Database directory."),
    variant_vcf: Path | None = typer.Option(
        None, exists=True, readable=True, help="Configure an existing .vcf or .vcf.gz."
    ),
    blast_db: str | None = typer.Option(None, help="Configure an existing BLAST DB prefix."),
    variant_url: str | None = typer.Option(None, help="Download a VCF from this URL."),
    transcriptome_url: str | None = typer.Option(
        None, help="Download FASTA(.gz) and build a BLAST database."
    ),
    variant_sha256: str | None = typer.Option(None, help="Expected VCF SHA-256."),
    transcriptome_sha256: str | None = typer.Option(None, help="Expected FASTA SHA-256."),
    assembly: str | None = typer.Option(None, help="Reference assembly, e.g. GRCh38."),
    variant_source: str | None = typer.Option(None, help="Variant resource name."),
    variant_release: str | None = typer.Option(None, help="Variant resource release."),
    transcriptome_release: str | None = typer.Option(None, help="Transcript annotation release."),
    transcriptome_source: str | None = typer.Option(None, help="Transcriptome resource name."),
    transcriptome_assembly: str | None = typer.Option(
        None, help="Transcriptome genome assembly, e.g. GRCh38.p14."
    ),
    dbsnp_common_all: bool = typer.Option(
        False,
        "--dbsnp-common-all",
        help=(
            "Use NCBI dbSNP b151 GRCh38.p7 common_all_20180418 "
            f"({DBSNP_B151_GRCH38P7_COMMON_ALL['filename']})."
        ),
    ),
    gencode_v45_transcripts: bool = typer.Option(
        False,
        "--gencode-v45-transcripts",
        help=(
            "Use GENCODE 45 CHR transcripts "
            f"({GENCODE_V45_TRANSCRIPTS['filename']}) as the BLAST subject."
        ),
    ),
    retries: int = typer.Option(3, min=1, max=10),
    force: bool = typer.Option(False, help="Replace existing downloaded data."),
) -> None:
    directory, path = initialize(
        db_dir,
        variant_vcf=variant_vcf,
        blast_db=blast_db,
        variant_url=variant_url,
        transcriptome_url=transcriptome_url,
        variant_sha256=variant_sha256,
        transcriptome_sha256=transcriptome_sha256,
        assembly=assembly,
        variant_source=variant_source,
        variant_release=variant_release,
        transcriptome_release=transcriptome_release,
        transcriptome_source=transcriptome_source,
        transcriptome_assembly=transcriptome_assembly,
        dbsnp_common_all=dbsnp_common_all,
        gencode_v45_transcripts=gencode_v45_transcripts,
        retries=retries,
        force=force,
    )
    console.print(f"Database directory: {directory}")
    console.print(f"Configuration: {path}")
    console.print("BLAST+ and RNAup are external system tools and are not installed by uv.")


@app.command()
def doctor() -> None:
    """Report tools and configured data; missing optional resources are non-fatal."""
    report = tool_report()
    table = Table("Resource", "Value", "Status")
    for row in report:
        table.add_row(row["resource"], row["value"], row["status"])
    console.print(table)
    console.print("FASTA input is the primary, reproducible interface.")
    console.print("`bsst select gene` is a convenience fetcher against Ensembl REST archive 111.")
    console.print("Use --skip-blast and/or --skip-variants when external data is unavailable.")
    console.print("Pinned names and URLs: `bsst resources`.")


@app.command("resources")
def resources_cmd() -> None:
    """Print the pinned scientific resources (producer names, not nicknames)."""
    table = Table("Role", "Producer / name", "Release", "Assembly", "URL / path")
    for item in catalog():
        table.add_row(
            str(item.get("role", "")),
            str(item.get("producer") or item.get("id")),
            str(
                item.get("variant_release")
                or item.get("transcriptome_release")
                or item.get("release")
                or item.get("ensembl_version")
                or item.get("task")
                or item.get("program")
                or ("live" if item.get("pinned") is False else "")
            ),
            str(item.get("assembly") or "—"),
            str(item.get("url") or item.get("base_url") or item.get("path") or item.get("manual") or item.get("docs_url") or ""),
        )
    console.print(table)
    console.print("Verification steps: docs/resources.md, docs/variants.md, docs/transcriptome.md")


@config_app.command("show")
def config_show() -> None:
    console.print_json(json.dumps(load_config()))


def _options(
    window_size: int,
    step: int,
    context: int,
    temperature: float,
    include_both: bool,
    min_anchor_overlap: float,
    min_af: float | None,
) -> SelectOptions:
    return SelectOptions(
        window_size=window_size,
        step=step,
        context=context,
        temperature=temperature,
        include_both=include_both,
        min_anchor_overlap=min_anchor_overlap,
        min_af=min_af,
    )


def _run(
    target: Target,
    runs_dir: Path | None,
    variant_vcf: Path | None,
    blast_db: str | None,
    skip_variants: bool,
    skip_blast: bool,
    options: SelectOptions,
) -> None:
    cfg = load_config()
    resolved_vcf = variant_vcf or (
        Path(cfg["variant_vcf"]) if cfg.get("variant_vcf") else discover_variant_vcf()
    )
    resolved_blast = blast_db or cfg.get("blast_db") or discover_blast_db()
    run_dir = select(
        target,
        options,
        runs_dir=runs_dir or Path(cfg["runs_dir"]),
        variant_vcf=resolved_vcf,
        blast_db=resolved_blast,
        skip_variants=skip_variants,
        skip_blast=skip_blast,
        self_tokens=[token for token in (target.gene, target.transcript_id) if token],
    )
    console.print(f"Run completed: {run_dir}")


@select_app.command("gene")
def select_gene(
    gene: str = typer.Argument(..., help="Gene symbol looked up on Ensembl REST archive 111."),
    runs_dir: Path | None = typer.Option(None, help="Override configured runs directory."),
    species: str = typer.Option("homo_sapiens"),
    variant_vcf: Path | None = typer.Option(None, "--variant-vcf"),
    blast_db: str | None = typer.Option(None),
    skip_variants: bool = typer.Option(False),
    skip_blast: bool = typer.Option(False),
    window_size: int = typer.Option(40),
    step: int = typer.Option(1),
    context: int = typer.Option(120),
    temperature: float = typer.Option(37.0),
    include_both: bool = typer.Option(False),
    min_anchor_overlap: float = typer.Option(1.0),
    min_af: float | None = typer.Option(
        None, min=0.0, max=1.0, help="Only filter variants with AF at least this value."
    ),
) -> None:
    try:
        target = fetch_gene_utr(gene, species)
    except EnsemblArchiveError as exc:
        console.print(f"[red]{exc}[/red]")
        raise typer.Exit(code=1) from exc
    _run(
        target, runs_dir, variant_vcf, blast_db, skip_variants, skip_blast,
        _options(window_size, step, context, temperature, include_both, min_anchor_overlap, min_af),
    )


@select_app.command("fasta")
def select_fasta(
    fasta: Path = typer.Argument(..., exists=True, readable=True),
    runs_dir: Path | None = typer.Option(None, help="Override configured runs directory."),
    chrom: str | None = typer.Option(None),
    start: int | None = typer.Option(None, help="0-based BED start."),
    end: int | None = typer.Option(None, help="0-based BED end."),
    strand: str | None = typer.Option(
        None, help="+ or -; inferred from a compatible header, otherwise +."
    ),
    gene: str | None = typer.Option(None),
    variant_vcf: Path | None = typer.Option(None, "--variant-vcf"),
    blast_db: str | None = typer.Option(None),
    skip_variants: bool = typer.Option(False),
    skip_blast: bool = typer.Option(False),
    window_size: int = typer.Option(40),
    step: int = typer.Option(1),
    context: int = typer.Option(120),
    temperature: float = typer.Option(37.0),
    include_both: bool = typer.Option(False),
    min_anchor_overlap: float = typer.Option(1.0),
    min_af: float | None = typer.Option(
        None, min=0.0, max=1.0, help="Only filter variants with AF at least this value."
    ),
) -> None:
    if strand is not None and strand not in {"+", "-"}:
        raise typer.BadParameter("strand must be + or -")
    record = SeqIO.read(fasta, "fasta")
    header = _header_metadata(record.description)
    chrom = chrom or header.get("chrom")
    start = start if start is not None else (
        int(header["start"]) if "start" in header else None
    )
    end = end if end is not None else (
        int(header["end"]) if "end" in header else None
    )
    strand = strand or (
        header["strand"] if header.get("strand") in {"+", "-"} else "+"
    )
    transcript_id = None
    name_match = re.fullmatch(
        r"([A-Za-z0-9.-]+)_(ENST[0-9]+(?:\.[0-9]+)?)", record.id
    )
    if name_match:
        gene = gene or name_match.group(1)
        transcript_id = name_match.group(2)
    target = Target(
        sequence=str(record.seq).upper(), name=record.id, chrom=chrom,
        start=start, end=end, strand=strand, gene=gene,
        transcript_id=transcript_id, source=f"FASTA: {fasta}",
    )
    if variant_vcf and (chrom is None or start is None or end is None):
        console.print("[yellow]Warning: no complete coordinates; variant filtering will be skipped.[/yellow]")
    _run(
        target, runs_dir, variant_vcf, blast_db, skip_variants, skip_blast,
        _options(window_size, step, context, temperature, include_both, min_anchor_overlap, min_af),
    )


if __name__ == "__main__":
    app()
