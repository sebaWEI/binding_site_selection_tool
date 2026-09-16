# Transcriptome BLAST subject: GENCODE 45 (GRCh38.p14, CHR)

Off-target filtering runs `blastn -task blastn-short` on each 40 nt **DNA**
window. Queries use `T`, never `U`. The subject must be transcript nucleotide
sequence, not a genome.

This project uses **GENCODE Release 45** reference-chromosome transcripts
(`gencode.v45.transcripts.fa.gz`, CHR, including MT). That release is
**Ensembl 111**, assembly **GRCh38.p14**, dated **2024-01**.

Do not call this file RefSeq, NCBI RNA, or an unversioned "human transcriptome".

## Which file to download

Site: GENCODE human Release 45 FTP

Directory:

https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_45/

Release notes: https://www.gencodegenes.org/human/release_45.html

Statistics: https://www.gencodegenes.org/human/stats_45.html

File (Transcript sequences, **CHR**, not ALL / PRI, not `.pc_transcripts`):

`gencode.v45.transcripts.fa.gz`

Full URL:

https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_45/gencode.v45.transcripts.fa.gz

Local uncompressed name (same bytes after gunzip):

`data/gencode.v45.transcripts.fa`

BLAST prefix:

`data/gencode_v45_transcripts_db`

```bash
uv run bsst db init --gencode-v45-transcripts
uv run bsst doctor
```

Manual build:

```bash
mkdir -p data
curl -L --continue-at - \
  -o data/gencode.v45.transcripts.fa.gz \
  "https://ftp.ebi.ac.uk/pub/databases/gencode/Gencode_human/release_45/gencode.v45.transcripts.fa.gz"
gzip -dc data/gencode.v45.transcripts.fa.gz > data/gencode.v45.transcripts.fa
makeblastdb -in data/gencode.v45.transcripts.fa -dbtype nucl \
  -out data/gencode_v45_transcripts_db \
  -title "GENCODE v45 transcripts CHR GRCh38.p14"
```

Do not pass `-parse_seqids`: GENCODE headers use `|`, and BLAST seqid parsing
splits them incorrectly. The pipeline treats the full header as `sseqid` and
recognises self hits by gene symbol or transcript accession, **with or without**
a trailing `.version`.

## How to confirm it is v45 CHR

```bash
grep -c '^>' data/gencode.v45.transcripts.fa
head -n 1 data/gencode.v45.transcripts.fa
uv run bsst doctor
```

All of the following must hold:

| Check | Requirement |
|-------|-------------|
| Record count | **252930** (GENCODE 45 CHR total transcripts) |
| First header | `>ENST00000456328.2\|ENSG00000290825.1\|-\|OTTHUMT00000362751.1\|DDX11L2-202\|DDX11L2\|1657\|lncRNA\|` |
| Last (MT) header | `MT-TP-201` / `Mt_tRNA` |
| Header fields | `transcript_id\|gene_id\|havana_gene\|havana_transcript\|transcript_name\|gene_name\|length\|biotype\|` |
| `protein_coding` | 89110 |
| `nonsense_mediated_decay` | 21427 |
| `lncRNA` | 57722 |

GENCODE 47+ jumps to ~385k transcripts and may still start with DDX11L2. Do
not identify the release from the first header alone.
`gencode.v45.pc_transcripts.fa.gz` is the coding subset and will not match.

## Assembly relationship

| Resource | Producer assembly |
|----------|-------------------|
| Variant VCF | NCBI dbSNP b151, **GRCh38.p7** |
| BLAST subject | GENCODE 45 transcripts, **GRCh38.p14** |
| `bsst select gene` | Ensembl REST **archive 111** (GENCODE 45) |

BLAST compares transcript sequence, not genomic coordinates, so p7 vs p14
patch differences do not shift VCF-style intervals. Scientifically this means
the off-target subject is the **January 2024 GENCODE 45 comprehensive
transcript set** (lncRNA, NMD, retained_intron, …), not a protein-coding
subset and not live Ensembl.

Example FASTA accessions `ENST00000302787` / `ENST00000508803` are LETM1-201
(`.3`) and NSD2-218 (`.6`) in v45. The bundled files match Ensembl 111
`lookup/symbol` canonical 3′UTRs and `sequence/region` for those BED
intervals. Minus-strand LETM1 windows equal the reverse complement of the
plus-strand genome slice. Self-hit matching uses the gene symbol and the
stable ENST id with the version suffix ignored.

## Size

About 454 MB uncompressed plus ~150 MB BLAST files. Not stored in Git.
