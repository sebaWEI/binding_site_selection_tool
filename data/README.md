# Local scientific data (not Git-tracked)

This directory holds the large reference files named in
`src/bsst/resources.py`. Verify them from the file contents, not from
nicknames.

## NCBI dbSNP b151 / GRCh38.p7 `common_all`

File: `dbSNP_b151_GRCh38p7_common_all_20180418.vcf.gz` (~1.5 GB)

Producer metadata **inside the file header**:

- `##source=dbSNP`
- `##dbSNP_BUILD_ID=151`
- `##reference=GRCh38.p7`
- `##fileDate=20180418`

Official bytes:

https://ftp.ncbi.nih.gov/snp/organisms/human_9606_b151_GRCh38p7/VCF/common_all_20180418.vcf.gz

`common_all` is NCBI's subset of RefSNPs with `COMMON=1`: at least one 1000
Genomes population has a minor-allele frequency ≥ 1%, with ≥ 2 founders
contributing to that allele. Chromosome names are **unprefixed** (`1`, `4`,
`X`). Frequencies are in `CAF` (1000 Genomes) and `TOPMED`, not in an `AF=`
field. Setup: `docs/variants.md`.

## GENCODE Release 45 CHR transcripts (BLAST subject)

File: `gencode.v45.transcripts.fa` (~454 MB uncompressed)

BLAST prefix: `gencode_v45_transcripts_db`

Official archive:

https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_45/gencode.v45.transcripts.fa.gz

This is GENCODE **45** (Ensembl **111**, January 2024) transcript sequences on
**reference chromosomes including MT**, genome assembly **GRCh38.p14**. It is
the comprehensive transcript set (protein_coding, lncRNA, NMD, retained_intron,
pseudogenes, …), not the protein-coding-only `pc_transcripts` file.

Confirm: 252930 FASTA records; first header is `DDX11L2-202` / `ENST00000456328.2`;
last mitochondrial header is `MT-TP-201`. Setup: `docs/transcriptome.md`.

## These are not the same assembly patch

dbSNP b151 is GRCh38.**p7**. GENCODE 45 and Ensembl REST archive 111 are
GRCh38.**p14**. `bsst doctor` and each run `manifest.json` record those
fields separately.
