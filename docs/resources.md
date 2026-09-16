# Scientific resources

Pinned definitions live in `src/bsst/resources.py`. `bsst resources` prints
the same catalog. `bsst doctor` checks whether the local files and binaries
match those identities (VCF headers, GENCODE first FASTA header, BLAST
sequence count).

| Role | Producer name | Version / extract | Assembly | Pinned? |
|------|---------------|-------------------|----------|---------|
| Variant VCF | NCBI dbSNP `common_all_20180418.vcf.gz` | b151, 20180418 | GRCh38.p7 | Yes, local file |
| BLAST subject | GENCODE `gencode.v45.transcripts.fa.gz` | Release 45 = Ensembl 111, 2024-01, CHR | GRCh38.p14 | Yes, local file |
| Canonical 3′UTR fetch | Ensembl REST `https://e111.rest.ensembl.org` | Release 111 | GRCh38.p14 | Yes, versioned archive |
| Off-target search | NCBI BLAST+ `blastn -task blastn-short` | Local `blastn -version` | — | Local binary |
| Interaction energy | ViennaRNA `RNAup` | Local `RNAup --version` | — | Local binary |
| Example LETM1 | `examples/LETM1.fasta` | ENST00000302787; v45 LETM1-201 `.3` | chrom=4 BED | In repo |
| Example NSD2 | `examples/NSD2.FASTA` | ENST00000508803; v45 NSD2-218 `.6` | chrom=4 BED | In repo |

Setup:

- Variants: [variants.md](variants.md)
- Transcriptome BLAST: [transcriptome.md](transcriptome.md)

The VCF and the GENCODE FASTA are different GRCh38 patches. The pipeline
records each producer string separately and does not rename one as the other.

`select fasta` is the durable analysis path. `select gene` is a convenience
client of the Ensembl 111 archive only.
