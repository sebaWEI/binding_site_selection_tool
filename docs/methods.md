# Methods

Windows are generated on a transcript-oriented 3′UTR (40 nt, step 1 by
default). Extreme GC and homopolymers are rejected. Remaining windows may be
dropped for variant overlap or BLAST off-target risk, then reverse-complemented
to a binding domain (BD) and scored with ViennaRNA RNAup. Eligible BDs are
ranked by total interaction free energy (more negative first). There is no
legacy composite score; energy components are kept separate.

## Filters

Variant overlap uses NCBI dbSNP b151 `common_all_20180418` on GRCh38.p7
(unprefixed chromosome names; frequencies in `CAF` / `TOPMED`, not `AF=`).
`--min-af` uses `AF` if present, otherwise the largest non-reference `CAF`
value; records without either field are ignored when the threshold is set.
With no `--min-af`, every record in the extract is used. A tabix index
restricts reads to the target 3′UTR; without it the reader still keeps only
that interval, but must decompress the whole ~1.5 GB file once.

FASTA inputs need `chrom`, 0-based BED `start`/`end`, and strand. Incomplete
coordinates skip variant filtering.

Off-target search is `blastn -task blastn-short` against GENCODE 45 CHR
transcripts (`data/gencode_v45_transcripts_db`; GRCh38.p14; 252930 sequences,
all biotypes). Queries stay DNA (`T`, never `U`). A non-self hit of **≥ 20 nt**
flags the window. Identity and coverage floors default to 0. Self hits match
gene symbols and transcript accessions with or without a trailing `.version`.
Do not build the BLAST database with `-parse_seqids`: GENCODE headers use `|`.

## RNAup

Each BD is scored against a target slice with 120 nt context on each side,
invoked as `--interaction_first --window N --temp T` (optionally
`--include_both`). RNAup's 1-based local interaction coordinates are mapped
back to 0-based UTR coordinates. By default the complete predicted target
interaction must lie inside the intended window (`anchor_overlap`). Off-anchor
interactions are excluded.

RNAup cannot be skipped. `--skip-variants` / `--skip-blast` omit those stages
only.

## Run directory

Every invocation writes `runs/<UTC timestamp>_<run id>/`:

| File | Contents |
|------|----------|
| `manifest.json` | status, parameters, input SHA-256, model/tool versions, target metadata, configured databases |
| `run.log` | stages plus complete external commands, stdout, and stderr |
| `inputs/target.fasta` | exact analyzed sequence |
| `all_candidates.tsv` | every generated window and `failure_reason` |
| `candidates.tsv` | anchored eligible candidates, deterministic rank |
| `blast_hits.tsv` | every raw BLAST hit plus self/risk flags (headers always present) |

Candidate coordinates are 0-based half-open. `interaction_target_*` and
`interaction_query_*` keep RNAup's 1-based inclusive local coordinates.
`interaction_utr_*` are mapped 0-based half-open UTR offsets. Energies are
kcal/mol. `bd_sequence` is DNA notation. `anchor_overlap` is the fraction of
predicted target interaction inside the intended window.

If no candidates remain, inspect `all_candidates.tsv` and `failure_reason`
(complexity, variant overlap, BLAST risk, RNAup failure, off-anchor).
Pre-refactor result files used a different model; do not pool them with
current ranks.

Pinned files and verification: [resources.md](resources.md).
What the scores are not: [limitations.md](limitations.md).
