# Local scientific data (not Git-tracked)

Large files named in `src/bsst/resources.py`. Verify contents, not nicknames.
Setup and identity checks: [docs/resources.md](../docs/resources.md).

| File | Producer | Identity |
|------|----------|----------|
| `dbSNP_b151_GRCh38p7_common_all_20180418.vcf.gz` (~1.5 GB) | NCBI dbSNP b151, GRCh38.p7, `common_all` 20180418 | `##source=dbSNP`, `##dbSNP_BUILD_ID=151`, `##reference=GRCh38.p7`; chrom `1` not `chr1` |
| `gencode.v45.transcripts.fa` (~454 MB) + `gencode_v45_transcripts_db` | GENCODE 45 / Ensembl 111 / GRCh38.p14 / CHR | 252930 records; first header `DDX11L2-202`; last `MT-TP-201` |

dbSNP b151 is GRCh38.**p7**. GENCODE 45 and Ensembl REST archive 111 are
GRCh38.**p14**. `bsst check_requirements` and each run `manifest.json` record
those fields separately.
