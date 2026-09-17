# Binding Site Selection Tool

`bsst` (Binding Site Selection Tool) is the dry-lab binding-domain ranker
for **iGEM PekingHSC 2026** (HEPHA-RNA). After a target gene is chosen, it
scores antisense binding domains (BDs) on that transcript’s 3′UTR for Hepha
element development.

- Model_repository: [https://github.com/sebaWEI/PekingHSC-2026-Model](https://github.com/sebaWEI/PekingHSC-2026-Model)
- Team: [https://teams.igem.org/6371](https://teams.igem.org/6371)
- Wiki: [https://2026.igem.wiki/pekinghsc/](https://2026.igem.wiki/pekinghsc/)
- Wiki model page: [https://2026.igem.wiki/pekinghsc/model](https://2026.igem.wiki/pekinghsc/model)
- Wiki tutorial page: [https://2026.igem.wiki/pekinghsc/documents](https://2026.igem.wiki/pekinghsc/documents)

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

Do the steps **in order** in a terminal. `uv sync` installs Python
packages only; RNAup, BLAST+, and the two databases are separate.

You will put four layers on the machine:


| Layer | What you install                        | What it is for                                   |
| ----- | --------------------------------------- | ------------------------------------------------ |
| 1     | Git                                     | Download this repository                         |
| 2     | `uv` + Python 3.12                      | Run the `bsst` commands                          |
| 3     | RNAup, `blastn`, `makeblastdb`, `tabix` | Score binding, search off-targets, index the VCF |
| 4     | dbSNP VCF + GENCODE BLAST database      | Variant filter and off-target filter             |


**Need:** internet (GitHub, NCBI, EBI), about **3 GB** free disk, and
20–40 minutes the first time (most of that is a ~2 GB download).

Pick **one** OS column and stay with it. After any installer that says
“restart the shell” or “add to PATH”, close the terminal, open a new one,
and `cd` back into the repo folder.

### 1. Open a terminal and install Git

- **macOS:** open **Terminal**. If `git --version` fails, install the
developer tools (this also provides Git):
  ```bash
  xcode-select --install
  ```
- **Windows:** install [Git for Windows](https://git-scm.com/download/win),
then open **PowerShell** or **Git Bash**.
- **Linux (Debian/Ubuntu):**
  ```bash
  sudo apt update
  sudo apt install -y git curl
  ```

Check:

```bash
git --version
```



### 2. Download this repository

```bash
git clone https://github.com/sebaWEI/binding_site_selection_tool.git
cd binding_site_selection_tool
```

SSH alternative: `git clone git@github.com:sebaWEI/binding_site_selection_tool.git`

Every later command assumes you are still inside `binding_site_selection_tool`.
If you open a new terminal, run `cd` to that folder again.

### 3. Install `uv` and the Python project

`uv` downloads Python 3.12 and creates `.venv` in this folder.

**macOS / Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows (PowerShell):**

```powershell
irm https://astral.sh/uv/install.ps1 | iex
```

macOS Homebrew alternative: `brew install uv`.

Close the terminal, open a new one, then:

```bash
cd binding_site_selection_tool   # if you are no longer in the repo
uv python install 3.12
uv sync                          # lockfile is already in the repo; do not run uv lock
uv run bsst --help
```

You should see the `bsst` help text (`check_requirements`, `resources`,
`db`, `run`, `config`). From now on, always prefix commands with
`uv run bsst …` so they use this project’s `.venv`.

### 4. Install RNAup, BLAST+, and tabix

These are **system programs**. Python cannot provide them. They must be
on your shell `PATH` in the same terminal where you later run `bsst`.

**macOS (Homebrew).** If `brew --version` fails, install Homebrew first
from [https://brew.sh](https://brew.sh) (the site shows the current install command), then
follow the “Next steps” it prints so `brew` is on `PATH`. Then:

```bash
brew tap brewsci/bio
brew install brewsci/bio/viennarna blast htslib
```

**Linux / Windows / macOS (conda).** Install
[Miniforge](https://github.com/conda-forge/miniforge#miniforge3) or
Anaconda, open a terminal where `conda` works, then:

```bash
conda install -c conda-forge -c bioconda viennarna blast htslib
```

Keep that conda environment **activated** for every later `bsst` command.
ViennaRNA official builds: [https://www.tbi.univie.ac.at/RNA/#download](https://www.tbi.univie.ac.at/RNA/#download)

Check that the four binaries respond:

```bash
RNAup --version
blastn -version
makeblastdb -version
tabix --version
```

Then let the project inspect `PATH`:

```bash
uv run bsst check_requirements
```

**Stop here until** `RNAup`, `blastn`, and `makeblastdb` are `ok`.
`tabix` should be `ok` if the install above worked (optional but
recommended). `blast_db`, `gencode_fasta`, and `variant_vcf` will still
be `missing/optional` — that is expected until the next step.

If a binary is `missing`, the program is not on `PATH` (conda env not
activated, or Homebrew not on `PATH`). Do not continue to step 5:
`db init` needs `makeblastdb` to build the BLAST database.

### 5. Download the two databases and build BLAST

Type **only this** (still in the repo folder). Do not download the FASTA
or VCF in a browser, and do not run `makeblastdb` yourself unless the
recovery note at the end of this step applies.

```bash
uv run bsst resources
uv run bsst db init --dbsnp-common-all --gencode-v45-transcripts
```

That single `db init` command, in order:

1. Downloads NCBI dbSNP b151 `common_all` (~1.5 GB) to
  `data/dbSNP_b151_GRCh38p7_common_all_20180418.vcf.gz`.
2. If `tabix` is on `PATH`, builds `…vcf.gz.tbi` so region queries are
  fast.
3. Downloads GENCODE 45 CHR transcripts
  (`gencode.v45.transcripts.fa.gz`) into `data/`.
4. Uncompresses them to `data/gencode.v45.transcripts.fa` (~454 MB).
5. **Builds the BLAST nucleotide database** by running `makeblastdb`
  for you. Output prefix: `data/gencode_v45_transcripts_db`.
6. Checks SHA-256 against [docs/resources.md](docs/resources.md). A
  mismatch aborts (wrong or truncated file). Re-run with `--force` only
   if you intend to replace the local copies.

Wait until the command returns to the prompt. Then you should have at
least:

```text
data/dbSNP_b151_GRCh38p7_common_all_20180418.vcf.gz
data/dbSNP_b151_GRCh38p7_common_all_20180418.vcf.gz.tbi   # if tabix was found
data/gencode.v45.transcripts.fa
data/gencode_v45_transcripts_db.nhr
data/gencode_v45_transcripts_db.nin
data/gencode_v45_transcripts_db.nsq
```

Verify:

```bash
uv run bsst check_requirements
```

These rows must be `ok` (no `missing`, no `mismatch`): `RNAup`,
`blastn`, `makeblastdb`, `blast_db`, `blast_db_identity`,
`gencode_fasta`, `gencode_fasta_identity`, `variant_vcf`,
`variant_vcf_identity`. After that, the example FASTA run below does not
need the network. `run gene` still needs Ensembl 111 (step 7).

**Recovery — FASTA is present but BLAST files are not.** Only then type
this yourself. Do **not** add `-parse_seqids` (GENCODE headers contain
`|`):

```bash
makeblastdb \
  -in data/gencode.v45.transcripts.fa \
  -dbtype nucl \
  -out data/gencode_v45_transcripts_db \
  -title "GENCODE v45 transcripts CHR GRCh38.p14"
```



## Usage

**Primary — stored FASTA** (reproducible; no Ensembl call). Sequence,
0-based BED coordinates, and strand are stored with the run. First
ranking, using the bundled LETM1 3′UTR:

```bash
uv run bsst run fasta examples/LETM1.fasta --gene LETM1
```

When it finishes it prints `Run completed: runs/<timestamp>_<id>/`.
Open that folder:


| File                 | What to look at                             |
| -------------------- | ------------------------------------------- |
| `candidates.tsv`     | Ranked BDs (more negative ΔG first)         |
| `all_candidates.tsv` | Every window, including why it was dropped  |
| `run.log`            | Commands that were actually executed        |
| `manifest.json`      | Tool versions and which databases were used |


The other bundled input is `examples/NSD2.FASTA`.

**Convenience — gene symbol** (canonical coding 3′UTR from Ensembl REST
archive **111** only: `https://e111.rest.ensembl.org`). It never falls
back to live Ensembl. Needs the network. Save the FASTA from the run
folder if you need a durable copy.

```bash
uv run bsst run gene NSD2
```

`--skip-variants` / `--skip-blast` omit those stages. RNAup cannot be
skipped.


| Command                                                            | When you type it                          |
| ------------------------------------------------------------------ | ----------------------------------------- |
| `uv run bsst --help`                                               | Confirm the CLI is installed              |
| `uv run bsst check_requirements`                                   | After steps 4 and 5: PATH + pinned files  |
| `uv run bsst resources`                                            | Print producer names and download URLs    |
| `uv run bsst db init --dbsnp-common-all --gencode-v45-transcripts` | Download both databases and build BLAST   |
| `uv run bsst run fasta FILE --gene SYMBOL`                         | Rank BDs from a stored 3′UTR              |
| `uv run bsst run gene SYMBOL`                                      | Fetch a 3′UTR from Ensembl 111, then rank |
| `uv run bsst config show`                                          | Show local config paths                   |


Further reading: [docs/methods.md](docs/methods.md) ·
[docs/resources.md](docs/resources.md) ·
[docs/limitations.md](docs/limitations.md).