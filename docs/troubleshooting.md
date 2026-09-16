# Troubleshooting

## RNAup or blastn is missing

Run `bsst doctor`. Install ViennaRNA and NCBI BLAST+ with a native package
manager. `uv sync` only installs Python dependencies. BLAST and variant stages
can be explicitly disabled with `--skip-blast` and `--skip-variants`.
`bsst resources` lists the pinned file names and producer URLs.

## BLAST database is missing

The subject must be GENCODE 45 `gencode.v45.transcripts.fa` built with
`makeblastdb` (see `docs/transcriptome.md`):

```bash
uv run bsst db init --gencode-v45-transcripts
```

Confirm 252930 FASTA records before treating the library as v45.

## Variant filtering was skipped

FASTA inputs need chromosome, 0-based BED start/end, and strand metadata.
Without complete coordinates the CLI warns and skips variant filtering.
If you expected filtering, run `bsst doctor` and confirm
`data/dbSNP_b151_GRCh38p7_common_all_20180418.vcf.gz` exists, or pass
`--dbsnp-common-all` to `bsst db init`. See `docs/variants.md`.

## No candidates remain

Inspect `all_candidates.tsv` and `failure_reason`. Common causes are sequence
complexity, variant overlap, BLAST risk, RNAup failure, or an off-anchor
interaction. Check `run.log` for complete external command output.

## Large VCF files are slow

The NCBI dbSNP `common_all` extract is about 1.5 GB. `bsst db init
--dbsnp-common-all` builds a tabix index when `tabix` is on `PATH`. Runtime
then queries only the target 3′UTR interval. Without an index the reader still
keeps only records on that chromosome and interval, but it must decompress the
whole file once.
