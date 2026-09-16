# Pipeline

1. Generate transcript-oriented 3′UTR windows (40 nt by default).
2. Reject extreme GC and homopolymers.
3. Optionally reject BED-overlapping VCF records, with chromosome
   normalization. The project default extract is NCBI dbSNP b151
   `common_all_20180418` on GRCh38.p7 (unprefixed chromosome names; frequencies
   in `CAF` / `TOPMED`, not `AF=`). `--min-af` uses `AF` if present, otherwise
   the largest non-reference `CAF` value; records without either field are
   ignored when the threshold is set. With no `--min-af`, every record in the
   file is used. With a tabix index (`bsst db init --dbsnp-common-all`), only
   the target 3′UTR interval is read.
4. Optionally run NCBI BLAST+ `blastn -task blastn-short` against the pinned
   GENCODE 45 CHR transcript sequences (`data/gencode_v45_transcripts_db`;
   GRCh38.p14; 252930 transcripts, all biotypes). Queries remain DNA (`T`,
   never `U`). A non-self hit of **≥ 20 nt** flags the window as off-target.
   Identity and coverage floors default to 0 because many windows are available
   and extra pruning is acceptable. Self hits match gene symbols and transcript
   accessions with or without a trailing `.version`.
5. Reverse-complement each target window to produce its BD.
6. Run RNAup separately for each candidate against a target slice carrying
   120 nt context on each side.
7. Invoke RNAup with `--interaction_first --window N --temp T` and optionally
   `--include_both`.
8. Map RNAup's 1-based local interaction coordinates back to 0-based UTR
   coordinates. By default, the complete predicted target interaction must
   lie inside the intended candidate window.
9. Exclude off-anchor interactions and rank eligible candidates by total
   interaction free energy (more negative first).

No legacy composite score is used. Energy components are retained separately.
