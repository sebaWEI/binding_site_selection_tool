# Output schema

Each run contains:

- `manifest.json`: status, parameters, input SHA-256, model/tool versions,
  target metadata, and configured databases.
- `run.log`: stages plus complete external commands, stdout, and stderr.
- `inputs/target.fasta`: exact analyzed input.
- `all_candidates.tsv`: every generated window and its status/failure reason.
- `candidates.tsv`: only anchored, eligible candidates with deterministic rank.
- `blast_hits.tsv`: every raw BLAST hit plus self/risk decisions; always
  present with headers.

Candidate coordinates are 0-based half-open. RNAup's
`interaction_target_*` and `interaction_query_*` fields preserve its 1-based
inclusive local coordinates. `interaction_utr_*` are mapped 0-based half-open
UTR offsets. Energy fields are kcal/mol. `bd_sequence` is DNA notation.
`anchor_overlap` is the fraction of predicted target interaction contained in
the intended window.
