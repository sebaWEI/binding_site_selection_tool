# Methods

Default: 40 nt windows, step 1, on a transcript-oriented 3′UTR. Eligible
binding domains (BDs) are ranked by RNAup total ΔG (more negative first).
There is no composite score; energy terms stay separate.

```text
3′UTR FASTA
    → windows (40 nt)
    → drop extreme GC / homopolymers
    → optional dbSNP overlap filter
    → optional BLAST off-target filter
    → reverse-complement → BD
    → RNAup vs window + 120 nt flanks
    → keep only on-window (anchored) interactions
    → rank by ΔG_total
```

## Filters

**Variants.** NCBI dbSNP b151 `common_all_20180418` on GRCh38.p7
(chromosome names `1`, `4`, … not `chr1`). Frequencies are `CAF` / `TOPMED`,
not `AF=`. With no `--min-af`, every record in the extract is used. With
`--min-af`, the reader takes `AF` if present, else the largest
non-reference `CAF`; records with neither field are ignored. A tabix index
reads only the target 3′UTR; without it the same interval is kept, but the
~1.5 GB file is decompressed once.

FASTA inputs need `chrom`, 0-based BED `start`/`end`, and strand.
Incomplete coordinates skip variant filtering.

**BLAST.** `blastn -task blastn-short` against GENCODE 45 CHR transcripts
(GRCh38.p14, 252930 sequences, all biotypes). Queries are DNA (`T`, never
`U`). A non-self hit of **≥ 20 nt** flags the window. Identity and coverage
floors default to 0. Self hits match gene symbols and ENST accessions with
or without `.version`. Do not pass `-parse_seqids` to `makeblastdb`
(GENCODE headers contain `|`).

## RNAup

Each BD is scored against a target slice with 120 nt context on each side:

`--interaction_first --window N --temp T` (optional `--include_both`).

RNAup reports 1-based local coordinates; bsst maps them to 0-based UTR
offsets. By default the whole predicted target interaction must lie inside
the intended window (`anchor_overlap = 1`). Off-anchor hits are dropped.
RNAup cannot be skipped; `--skip-variants` / `--skip-blast` omit only those
stages.

A long run of `(` / `)` in RNAup output is expected: the BD is the reverse
complement of the window, so the MFE is usually a ~40 bp intermolecular
helix. A `.` is an unpaired base (often a weak terminal A-U), not a crash.

## Run directory

Every invocation writes `runs/<UTC timestamp>_<run id>/`:

| File | Contents |
|------|----------|
| `manifest.json` | status, parameters, input SHA-256, tool versions, databases |
| `run.log` | stages plus full external commands, stdout, stderr |
| `inputs/target.fasta` | exact analyzed sequence |
| `all_candidates.tsv` | every window and `failure_reason` |
| `candidates.tsv` | anchored eligible BDs, deterministic rank |
| `blast_hits.tsv` | raw BLAST hits plus self/risk flags |

| Field | Meaning |
|-------|---------|
| genomic `start`/`end` | 0-based half-open |
| `interaction_target_*`, `interaction_query_*` | RNAup 1-based inclusive, local |
| `interaction_utr_*` | mapped 0-based half-open UTR offsets |
| energy columns | kcal/mol |
| `bd_sequence` | DNA notation |
| `anchor_overlap` | fraction of predicted target interaction inside the window |

If nothing is eligible, read `all_candidates.tsv` → `failure_reason`
(complexity, variant overlap, BLAST, RNAup, off-anchor). Do not mix
pre-refactor tables with current ranks.

Pinned files: [resources.md](resources.md).
What the scores are not: [limitations.md](limitations.md).

## References

Tool and database papers the pipeline uses. Titles are the publishers’
article titles.

- Mückstein et al. (2006). Thermodynamics of RNA–RNA binding. *Bioinformatics*
  **22**, 1177–1182. https://doi.org/10.1093/bioinformatics/btl024
- Lorenz et al. (2011). ViennaRNA Package 2.0. *Algorithms for Molecular
  Biology* **6**, 26. https://doi.org/10.1186/1748-7188-6-26
- Camacho et al. (2009). BLAST+: architecture and applications. *BMC
  Bioinformatics* **10**, 421. https://doi.org/10.1186/1471-2105-10-421
- Frankish et al. (2023). GENCODE: reference annotation for the human and
  mouse genomes in 2023. *Nucleic Acids Research* **51**, D942–D949.
  https://doi.org/10.1093/nar/gkac1071
- Harrison et al. (2024). Ensembl 2024. *Nucleic Acids Research* **52**,
  D891–D899. https://doi.org/10.1093/nar/gkad1049
- Sherry et al. (2001). dbSNP: the NCBI database of genetic variation.
  *Nucleic Acids Research* **29**, 308–311.
  https://doi.org/10.1093/nar/29.1.308
- Li (2011). Tabix: fast retrieval of sequence features from generic
  TAB-delimited files. *Bioinformatics* **27**, 718–719.
  https://doi.org/10.1093/bioinformatics/btq671
