# bsst

`bsst` (Binding Site Selection Tool) ranks antisense binding domains (BDs)
for **Hepha** against a transcript-oriented 3′UTR. Each run writes an
immutable directory with inputs, parameters, logs, intermediate tables, and
ranked candidates.

> 3′UTR targeting is a project-specific Hepha hypothesis. Classical antisense
> translation activators usually overlap the translation initiation region.
> Computational scores are ranking hypotheses, not proof of up-regulation.
> Validate every selected site experimentally.

## Setup

Do these steps in order. A first full run needs Git, `uv`, ViennaRNA
(`RNAup`), NCBI BLAST+, a ~2 GB download (NCBI + GENCODE), and then an
example FASTA. `uv sync` never installs the native binaries.

### 1. Clone

```bash
git clone https://github.com/sebaWEI/binding_site_selection_tool.git
cd binding_site_selection_tool
```

SSH, if you already have GitHub keys:

```bash
git clone git@github.com:sebaWEI/binding_site_selection_tool.git
cd binding_site_selection_tool
```

### 2. Python (`uv`)

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if it is
not already on `PATH`:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# macOS Homebrew
brew install uv

# Windows PowerShell
irm https://astral.sh/uv/install.ps1 | iex
```

Restart the shell so `uv` is on `PATH`, then install Python 3.10+ and the
project (the lockfile is already in the repo; do not run `uv lock`):

```bash
uv python install 3.12
uv sync
```

This creates `.venv`. Confirm: `uv run bsst --help`.

### 3. Native tools

`uv run` uses the project venv for Python, but it looks up `RNAup`, `blastn`,
`makeblastdb`, and `tabix` on **your shell `PATH`**. Install them before
`db init`. If you use conda for these binaries, activate that environment in
the same shell as `uv run`.

macOS (Homebrew):

```bash
brew tap brewsci/bio
brew install brewsci/bio/viennarna blast htslib
```

Linux / macOS / Windows (Bioconda; the portable option):

```bash
conda install -c conda-forge -c bioconda viennarna blast htslib
```

ViennaRNA official binaries and source:
https://www.tbi.univie.ac.at/RNA/#download

Confirm the binaries, then the required rows of `check_requirements`:

```bash
RNAup --version
blastn -version
makeblastdb -version
tabix --version
uv run bsst check_requirements
```

`RNAup`, `blastn`, and `makeblastdb` must be `ok` or the command exits 1.
`tabix` is optional (without it, variant filtering still works but scans the
whole ~1.5 GB VCF). BLAST databases and the VCF are still missing until the
next step; that is expected.

### 4. Databases

`bsst resources` prints the pinned producer names and URLs.
`--dbsnp-common-all` and `--gencode-v45-transcripts` download those files into
`data/` only if they are missing, then build a BLAST database.

Expect **~2 GB** on disk, NCBI + EBI network access, and several minutes.
`makeblastdb` must already be on `PATH` or this step fails.

```bash
uv run bsst resources
uv run bsst db init --dbsnp-common-all --gencode-v45-transcripts
uv run bsst check_requirements
```

After a successful init, `blast_db` and `variant_vcf` should be `ok`, and
identity rows must not say `mismatch`. Then the example FASTA run below is a
local, offline analysis (`run gene` still needs the Ensembl 111 archive).

#### Variant file (NCBI dbSNP b151, GRCh38.p7)

Variant filtering reads a **VCF**. This project uses NCBI dbSNP **build 151**,
reference **GRCh38.p7**, extract **common_all**, file date **20180418**.

- Directory: https://ftp.ncbi.nih.gov/snp/organisms/human_9606_b151_GRCh38p7/VCF/
- File: `common_all_20180418.vcf.gz`
- URL: https://ftp.ncbi.nih.gov/snp/organisms/human_9606_b151_GRCh38p7/VCF/common_all_20180418.vcf.gz
- Local name: `data/dbSNP_b151_GRCh38p7_common_all_20180418.vcf.gz` (~1.5 GB, not in Git)

`db init` also builds a tabix index when `tabix` is on `PATH`.
Confirm identity with `gzip -dc … | head`: headers must be `##source=dbSNP`,
`##dbSNP_BUILD_ID=151`, `##reference=GRCh38.p7`; data rows use `1`/`4`, not
`chr1`/`chr4`. Do not use a GRCh37/hg19 VCF. Details:
[docs/resources.md](docs/resources.md).

#### Transcriptome BLAST subject (GENCODE 45, GRCh38.p14, CHR)

Off-target filtering needs a **transcript nucleotide FASTA**, not a genome.
This project uses GENCODE **Release 45** (Ensembl **111**, 2024-01)
`gencode.v45.transcripts.fa.gz` (**CHR**: reference chromosomes + MT).

- Directory: https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_45/
- File: `gencode.v45.transcripts.fa.gz` (Transcript sequences, CHR; not `pc_transcripts`)
- URL: https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_45/gencode.v45.transcripts.fa.gz
- Local FASTA: `data/gencode.v45.transcripts.fa` (~454 MB, not in Git)
- BLAST prefix: `data/gencode_v45_transcripts_db`

Confirm identity: `grep -c '^>'` must be **252930**; the first header must be
`ENST00000456328.2|…|DDX11L2-202|DDX11L2|1657|lncRNA|`; the file ends at
mitochondrial `MT-TP-201`. GENCODE 47+ has ~385k transcripts; the first header
alone is not enough. This subject's genome background is **GRCh38.p14**. The
variant VCF is **GRCh38.p7**. Ensembl 111 archive sequences use the GENCODE 45
coordinate system. Catalog and verification: [docs/resources.md](docs/resources.md).

## Usage

### Primary interface: FASTA

Day-to-day analysis uses a stored 3′UTR FASTA. That file is the reproducible
input: sequence, 0-based BED coordinates, and strand travel with the run.

```bash
uv run bsst run fasta examples/LETM1.fasta --gene LETM1
```

`examples/LETM1.fasta` and `examples/NSD2.FASTA` are the reference inputs for
this project. This command does not call Ensembl.

### Convenience interface: `run gene`

`bsst run gene SYMBOL` looks up the canonical coding 3′UTR on the **Ensembl
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
uv run bsst run gene NSD2
```

`--skip-variants` / `--skip-blast` remain available when you intentionally
omit those stages. Missing RNAup is never skippable.

Commands:

```text
bsst db init
bsst db init --dbsnp-common-all
bsst db init --gencode-v45-transcripts
bsst check_requirements
bsst resources
bsst config show
bsst run fasta target.fasta --gene SYMBOL
bsst run gene GENE
```

Further reading: [docs/methods.md](docs/methods.md) (pipeline and run
outputs), [docs/resources.md](docs/resources.md) (pinned files),
[docs/limitations.md](docs/limitations.md) (what the scores are not).
