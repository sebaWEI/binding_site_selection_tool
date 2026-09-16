# bsst

`bsst` (Binding Site Selection Tool) ranks antisense binding domains (BDs)
for **Hepha** against a transcript-oriented 3′UTR. Each run writes an
immutable directory with inputs, parameters, logs, intermediate tables, and
ranked candidates.

> 3′UTR targeting is a project-specific Hepha hypothesis. Classical antisense
> translation activators usually overlap the translation initiation region.
> Computational scores are ranking hypotheses, not proof of up-regulation.
> Validate every selected site experimentally.

## Primary interface: FASTA

Day-to-day analysis uses a stored 3′UTR FASTA. That file is the reproducible
input: sequence, 0-based BED coordinates, and strand travel with the run.

```bash
uv lock
uv sync
uv run bsst doctor
uv run bsst resources
uv run bsst db init --dbsnp-common-all --gencode-v45-transcripts
uv run bsst select fasta examples/LETM1.fasta --gene LETM1
```

`examples/LETM1.fasta` and `examples/NSD2.FASTA` are the reference inputs for
this project.

## Convenience interface: `select gene`

`bsst select gene SYMBOL` looks up the canonical coding 3′UTR on the **Ensembl
111 REST archive** (`https://e111.rest.ensembl.org`), which is the Ensembl
release paired with GENCODE 45. It does **not** call `https://rest.ensembl.org`
and it does **not** fall back to the live server if the archive is down.

Limits of this convenience command:

- It requires network access to a time-limited Ensembl archive (typically kept
  about five years). If `e111.rest.ensembl.org` is retired, the command fails
  and you must use a FASTA.
- It always fetches the archive's canonical coding transcript, which may not be
  the isoform you want.
- Save the FASTA from a successful fetch if you need a durable copy.

```bash
uv run bsst select gene NSD2
```

RNAup (ViennaRNA), NCBI BLAST+, and tabix are native tools. `uv sync` does not
install them. `--dbsnp-common-all` and `--gencode-v45-transcripts` use the
pinned files in `data/` (download only if missing).

Commands:

```text
bsst db init
bsst db init --dbsnp-common-all
bsst db init --gencode-v45-transcripts
bsst doctor
bsst resources
bsst config show
bsst select fasta target.fasta --gene SYMBOL
bsst select gene GENE
```

See `docs/` for installation, methods, output fields, limitations, and
troubleshooting. Resource catalog: `docs/resources.md`. Variant file:
`docs/variants.md`. Transcriptome / BLAST: `docs/transcriptome.md`.
Pre-refactor result files are legacy outputs and must not be compared as if
they used the current anchored model.

## Variant file (NCBI dbSNP b151, GRCh38.p7)

Variant filtering reads a **VCF**. This project uses NCBI dbSNP **build 151**,
reference **GRCh38.p7**, extract **common_all**, file date **20180418**.

- Directory: https://ftp.ncbi.nih.gov/snp/organisms/human_9606_b151_GRCh38p7/VCF/
- File: `common_all_20180418.vcf.gz`
- URL: https://ftp.ncbi.nih.gov/snp/organisms/human_9606_b151_GRCh38p7/VCF/common_all_20180418.vcf.gz
- Local name: `data/dbSNP_b151_GRCh38p7_common_all_20180418.vcf.gz` (~1.5 GB, not in Git)

```bash
uv run bsst db init --dbsnp-common-all
uv run bsst doctor
```

`db init` also builds a tabix index when the `tabix` binary is on `PATH`.
Confirm identity with `gzip -dc … | head`: headers must be `##source=dbSNP`,
`##dbSNP_BUILD_ID=151`, `##reference=GRCh38.p7`; data rows use `1`/`4`, not
`chr1`/`chr4`. Do not use a GRCh37/hg19 VCF. Details:
[docs/variants.md](docs/variants.md).

## Transcriptome BLAST subject (GENCODE 45, GRCh38.p14, CHR)

Off-target filtering needs a **transcript nucleotide FASTA**, not a genome.
This project uses GENCODE **Release 45** (Ensembl **111**, 2024-01)
`gencode.v45.transcripts.fa.gz` (**CHR**: reference chromosomes + MT).

- Directory: https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_45/
- File: `gencode.v45.transcripts.fa.gz` (Transcript sequences, CHR; not `pc_transcripts`)
- URL: https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_45/gencode.v45.transcripts.fa.gz
- Local FASTA: `data/gencode.v45.transcripts.fa` (~454 MB, not in Git)
- BLAST prefix: `data/gencode_v45_transcripts_db`

```bash
uv run bsst db init --gencode-v45-transcripts
uv run bsst doctor
```

Confirm identity: `grep -c '^>'` must be **252930**; the first header must be
`ENST00000456328.2|…|DDX11L2-202|DDX11L2|1657|lncRNA|`; the file ends at
mitochondrial `MT-TP-201`. GENCODE 47+ has ~385k transcripts; the first header
alone is not enough. This subject's genome background is **GRCh38.p14**. The
variant VCF is **GRCh38.p7**. Ensembl 111 archive sequences use the GENCODE 45
coordinate system. Details: [docs/transcriptome.md](docs/transcriptome.md).
Catalog: [docs/resources.md](docs/resources.md).
