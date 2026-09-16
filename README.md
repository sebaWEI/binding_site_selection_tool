# bsst

`bsst` (Binding Site Selection Tool) is the dry-lab binding-domain ranker
for **iGEM PekingHSC 2026** (HEPHA-RNA). After a target gene is chosen, it
scores antisense binding domains (BDs) on that transcript’s 3′UTR for Hepha
element development.

- Model_repository: https://github.com/sebaWEI/PekingHSC-2026-Model
- Team: https://teams.igem.org/6371
- Wiki: https://2026.igem.wiki/pekinghsc/
- Model: https://2026.igem.wiki/pekinghsc/model
- Tutorial: https://2026.igem.wiki/pekinghsc/documents

Each run writes `runs/<timestamp>_<id>/` with the input, parameters, logs,
intermediate tables, and ranked candidates.

Hepha is specified to bind the **3′UTR**. Computational ranks still need
wet-lab validation: [docs/limitations.md](docs/limitations.md).

## What a run does

1. Slide 40 nt windows along a stored 3′UTR FASTA.
2. Drop extreme GC / homopolymers, optional dbSNP overlaps, and BLAST
   off-targets.
3. Reverse-complement each remaining window to a BD and score it with
   ViennaRNA **RNAup**.
4. Keep interactions that sit on the intended window; rank by total ΔG
   (more negative first).

Methods and output fields: [docs/methods.md](docs/methods.md).
Pinned files: [docs/resources.md](docs/resources.md).

## Setup

Do these in order. You need Git, `uv`, RNAup, BLAST+, ~2 GB disk, and
network to NCBI + EBI. `uv sync` does **not** install native binaries.

### 1. Clone

```bash
git clone https://github.com/sebaWEI/binding_site_selection_tool.git
cd binding_site_selection_tool
# or: git clone git@github.com:sebaWEI/binding_site_selection_tool.git
```

### 2. Python (`uv`)

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) if it
is missing, then restart the shell:

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
# macOS Homebrew:  brew install uv
# Windows:         irm https://astral.sh/uv/install.ps1 | iex

uv python install 3.12
uv sync          # lockfile is already in the repo; do not run uv lock
uv run bsst --help
```

### 3. Native tools

`uv run` uses `.venv` for Python, but finds `RNAup`, `blastn`,
`makeblastdb`, and `tabix` on **your shell `PATH`**. If you install them
with conda, activate that env in the same shell.

```bash
# macOS
brew tap brewsci/bio
brew install brewsci/bio/viennarna blast htslib

# Linux / macOS / Windows (portable)
conda install -c conda-forge -c bioconda viennarna blast htslib
```

ViennaRNA binaries: https://www.tbi.univie.ac.at/RNA/#download

```bash
RNAup --version && blastn -version && makeblastdb -version && tabix --version
uv run bsst check_requirements
```

`RNAup`, `blastn`, and `makeblastdb` must be `ok` (exit 1 otherwise).
`tabix` is optional but recommended. Missing BLAST/VCF files are expected
until the next step.

### 4. Databases

Downloads ~2 GB into `data/` if missing, then builds the BLAST database.
SHA-256 is checked against [docs/resources.md](docs/resources.md).
`makeblastdb` must already be on `PATH`.

```bash
uv run bsst resources
uv run bsst db init --dbsnp-common-all --gencode-v45-transcripts
uv run bsst check_requirements
```

After this, `blast_db` and `variant_vcf` should be `ok`, with no
`mismatch` rows. The example FASTA run below is then offline.
`run gene` still needs the Ensembl 111 archive.

## Usage

**Primary — stored FASTA** (reproducible; no Ensembl call). Sequence,
0-based BED coordinates, and strand are stored with the run:

```bash
uv run bsst run fasta examples/LETM1.fasta --gene LETM1
```

Reference inputs: `examples/LETM1.fasta`, `examples/NSD2.FASTA`.

**Convenience — gene symbol** (canonical coding 3′UTR from Ensembl REST
archive **111** only: `https://e111.rest.ensembl.org`). It never falls
back to live Ensembl. Save the FASTA if you need a durable copy.

```bash
uv run bsst run gene NSD2
```

`--skip-variants` / `--skip-blast` omit those stages. RNAup cannot be
skipped.

| Command | Role |
|---------|------|
| `bsst check_requirements` | PATH + pinned-file identity |
| `bsst resources` | Producer names and URLs |
| `bsst db init --dbsnp-common-all --gencode-v45-transcripts` | Download + index |
| `bsst run fasta FILE --gene SYMBOL` | Rank BDs |
| `bsst run gene SYMBOL` | Fetch 3′UTR, then rank |
| `bsst config show` | Local config |

Further reading: [docs/methods.md](docs/methods.md) ·
[docs/resources.md](docs/resources.md) ·
[docs/limitations.md](docs/limitations.md).
