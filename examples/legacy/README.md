# Legacy outputs

The historical LETM1 and NSD2 candidate tables in `examples/legacy/` were
produced by the pre-refactor RNAplfold/RNAduplex composite model. They are
retained only as records and are not regression references for the anchored
RNAup model.

Generate current, auditable results with `bsst select`. Do not compare old
and current score columns as if they represented the same model.
