# Installation

Requires Python 3.10+ and `uv`.

```bash
uv lock
uv sync
uv run bsst doctor
```

`uv sync` creates `.venv`. Install ViennaRNA/RNAup and NCBI BLAST+ separately
with your OS or conda package manager. They are native scientific programs and
are not Python dependencies; `uv` does not install them.

The pure-Python VCF reader supports `.vcf` and `.vcf.gz`. When `tabix` is
available, `bsst db init --dbsnp-common-all` indexes the bgzip VCF and region
queries use that index. `pysam` is not required.

Configure the pinned NCBI dbSNP extract and GENCODE 45 transcript BLAST
database (see `docs/resources.md`):

```bash
uv run bsst db init --dbsnp-common-all --gencode-v45-transcripts
uv run bsst resources
```

Or point at already downloaded copies with the producer names written into
config:

```bash
uv run bsst db init \
  --variant-vcf data/dbSNP_b151_GRCh38p7_common_all_20180418.vcf.gz \
  --assembly GRCh38.p7 \
  --variant-source "NCBI dbSNP" \
  --variant-release "b151 fileDate=20180418 common_all" \
  --blast-db data/gencode_v45_transcripts_db \
  --transcriptome-source GENCODE \
  --transcriptome-release "GENCODE 45 / Ensembl 111 / 2024-01 / CHR transcripts" \
  --transcriptome-assembly GRCh38.p14
```

A generic VCF or FASTA can still be downloaded with `--variant-url` /
`--transcriptome-url` and an optional SHA-256. Do not mix GRCh37 coordinates
with this pipeline. dbSNP b151 is GRCh38.p7; GENCODE 45 and Ensembl REST
archive 111 are GRCh38.p14. Record those strings separately.

`bsst select fasta` is the primary interface. `bsst select gene` is a
convenience lookup against `https://e111.rest.ensembl.org` only.
