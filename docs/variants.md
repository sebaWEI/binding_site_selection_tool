# Variant file: NCBI dbSNP b151 (GRCh38.p7)

bsst variant filtering reads **VCF / VCF.GZ**. The project file is NCBI dbSNP
build **151**, reference **GRCh38.p7**, extract **common_all**, date
**20180418**. Do not call it by another database's name.

## Which file to download

Site: NCBI dbSNP FTP (human, build 151, GRCh38.p7)

Directory:

https://ftp.ncbi.nih.gov/snp/organisms/human_9606_b151_GRCh38p7/VCF/

File:

`common_all_20180418.vcf.gz`

Full URL:

https://ftp.ncbi.nih.gov/snp/organisms/human_9606_b151_GRCh38p7/VCF/common_all_20180418.vcf.gz

Local name (rename only):

`data/dbSNP_b151_GRCh38p7_common_all_20180418.vcf.gz`

```bash
uv run bsst db init --dbsnp-common-all
```

If `tabix` is installed, this also writes `*.vcf.gz.tbi`. Runtime queries use
that index for the target 3′UTR interval instead of scanning 1.5 GB.

Manual download:

```bash
mkdir -p data
curl -L --continue-at - \
  -o data/dbSNP_b151_GRCh38p7_common_all_20180418.vcf.gz \
  "https://ftp.ncbi.nih.gov/snp/organisms/human_9606_b151_GRCh38p7/VCF/common_all_20180418.vcf.gz"
gzip -t data/dbSNP_b151_GRCh38p7_common_all_20180418.vcf.gz
tabix -p vcf data/dbSNP_b151_GRCh38p7_common_all_20180418.vcf.gz
```

## How to confirm it matches the FASTA coordinates

Read the compressed header (do not trust the file name):

```bash
gzip -dc data/dbSNP_b151_GRCh38p7_common_all_20180418.vcf.gz | head -n 20
uv run bsst doctor
```

Required:

| Header field | Requirement |
|--------------|-------------|
| `##source=dbSNP` | Producer is NCBI dbSNP |
| `##dbSNP_BUILD_ID=151` | Build 151 |
| `##reference=GRCh38.p7` | Reference GRCh38 patch 7 |
| `##fileDate=20180418` | Extract date |
| Data `#CHROM` is `1`, not `chr1` | Matches Ensembl `seq_region_name` |

Target checks:

- Example FASTA headers use `chrom=4` (no `chr` prefix) and 0-based BED. The
  VCF uses `4` and 1-based `POS` (the reader subtracts 1).
- Do **not** filter these FASTA files with a GRCh37 / hg19 VCF.
- Ensembl 111 / GENCODE 45 primary-chromosome 3′UTRs for LETM1 and NSD2 share
  these chr4 coordinates with GRCh38.p7. Do not mix this VCF with alt contigs
  or later patch sequences.

## What `COMMON=1` means here

NCBI defines `COMMON=1` as: at least one 1000 Genomes population has a minor
allele frequency ≥ 1%, with ≥ 2 founders contributing that allele. This file
is already that subset.

Frequency fields are `CAF` (1000 Genomes; first value is the reference allele)
and `TOPMED`. There is no standard `AF=`. Without `--min-af`, every record in
the file is used. With `--min-af`, the reader takes `AF=` if present, otherwise
the largest non-reference `CAF` value.

## Size

About 1.5 GB, not stored in Git. Place it in `data/` so `bsst` can discover it.
