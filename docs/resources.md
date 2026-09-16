# Scientific resources

Pinned names live in `src/bsst/resources.py`. `bsst resources` prints this
catalog. `bsst check_requirements` checks local files and binaries against
those identities (VCF headers, GENCODE first FASTA header, BLAST sequence
count). The VCF and the GENCODE FASTA are different GRCh38 patches; the
pipeline records each producer string separately.

| Role | Producer name | Version / extract | Assembly | Pinned? |
|------|---------------|-------------------|----------|---------|
| Variant VCF | NCBI dbSNP `common_all_20180418.vcf.gz` | b151, 20180418 | GRCh38.p7 | Yes, local file |
| BLAST subject | GENCODE `gencode.v45.transcripts.fa.gz` | Release 45 = Ensembl 111, 2024-01, CHR | GRCh38.p14 | Yes, local file |
| Canonical 3′UTR fetch | Ensembl REST `https://e111.rest.ensembl.org` | Release 111 | GRCh38.p14 | Yes, versioned archive |
| Off-target search | NCBI BLAST+ `blastn -task blastn-short` | Local `blastn -version` | — | Local binary |
| Interaction energy | ViennaRNA `RNAup` | Local `RNAup --version` | — | Local binary |
| Example LETM1 | `examples/LETM1.fasta` | ENST00000302787; v45 LETM1-201 `.3` | chrom=4 BED | In repo |
| Example NSD2 | `examples/NSD2.FASTA` | ENST00000508803; v45 NSD2-218 `.6` | chrom=4 BED | In repo |

`run fasta` is the durable analysis path. `run gene` is a convenience client
of the Ensembl 111 archive only. Example accessions match Ensembl 111
`lookup/symbol` canonical 3′UTRs and `sequence/region` for those BED
intervals; minus-strand LETM1 windows equal the reverse complement of the
plus-strand genome slice.

```bash
uv run bsst db init --dbsnp-common-all --gencode-v45-transcripts
```

Already-downloaded copies:

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

## Variant VCF (NCBI dbSNP b151, GRCh38.p7)

https://ftp.ncbi.nih.gov/snp/organisms/human_9606_b151_GRCh38p7/VCF/common_all_20180418.vcf.gz

Local name: `data/dbSNP_b151_GRCh38p7_common_all_20180418.vcf.gz` (~1.5 GB, not
in Git). Chromosome names are unprefixed (`1`, `4`, `X`). NCBI `COMMON=1`
means at least one 1000 Genomes population has a minor-allele frequency ≥ 1%,
with ≥ 2 founders contributing that allele. Frequencies are in `CAF` (first
value is the reference allele) and `TOPMED`. There is no standard `AF=`.

Confirm from the file, not the name:

```bash
gzip -dc data/dbSNP_b151_GRCh38p7_common_all_20180418.vcf.gz | head -n 20
```

| Header field | Requirement |
|--------------|-------------|
| `##source=dbSNP` | Producer is NCBI dbSNP |
| `##dbSNP_BUILD_ID=151` | Build 151 |
| `##reference=GRCh38.p7` | Reference GRCh38 patch 7 |
| `##fileDate=20180418` | Extract date |
| Data `#CHROM` is `1`, not `chr1` | Matches Ensembl `seq_region_name` |

Example FASTA headers use `chrom=4` and 0-based BED; the VCF uses `4` and
1-based `POS` (the reader subtracts 1). Do not filter with a GRCh37/hg19 VCF
or later-patch / alt-contig coordinates.

## BLAST subject (GENCODE 45, GRCh38.p14, CHR)

https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_45/gencode.v45.transcripts.fa.gz

Release notes: https://www.gencodegenes.org/human/release_45.html

Local FASTA: `data/gencode.v45.transcripts.fa` (~454 MB). BLAST prefix:
`data/gencode_v45_transcripts_db`. This is the comprehensive CHR transcript
set (including MT), not `pc_transcripts`. Queries are DNA (`T`, never `U`).

Do not pass `-parse_seqids` to `makeblastdb`: GENCODE headers use `|`.

```bash
grep -c '^>' data/gencode.v45.transcripts.fa
head -n 1 data/gencode.v45.transcripts.fa
```

| Check | Requirement |
|-------|-------------|
| Record count | **252930** |
| First header | `ENST00000456328.2` / `DDX11L2-202` / `lncRNA` |
| Last (MT) header | `MT-TP-201` / `Mt_tRNA` |
| `protein_coding` | 89110 |
| `nonsense_mediated_decay` | 21427 |
| `lncRNA` | 57722 |

GENCODE 47+ has ~385k transcripts and may still start with DDX11L2. Do not
identify the release from the first header alone.

BLAST compares transcript sequence, not genomic intervals, so the p7 VCF vs
p14 transcriptome patch difference does not shift VCF-style coordinates. The
off-target subject is the January 2024 GENCODE 45 comprehensive set, not live
Ensembl.
