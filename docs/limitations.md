# Scientific limitations

This tool ranks antisense binding domains on the **3′UTR**. That is how
Hepha is specified. The limits below are about scoring and data, not about
that target region.

The ranks are computational hypotheses, not proof of up-regulation.

## What the scores omit

RNAup is a thermodynamic RNA–RNA model. It does not know about:

- protein occupancy or RBP maps
- cellular compartment, modifications, or degradation
- isoform abundance or construct context
- genome (DNA) off-targets — BLAST here is against **transcripts**

BLAST and variant filters depend on the pinned files and the flags you
pass (`--min-af`, `--skip-blast`, `--skip-variants`).

**`run fasta`** is the reproducible path. **`run gene`** always takes the
Ensembl 111 archive’s canonical coding transcript, which may not be the
isoform you want, and the archive will eventually retire.

## Pinned data (not interchangeable)

| Resource | What it actually is |
|----------|---------------------|
| BLAST subject | GENCODE 45 / Ensembl 111 / GRCh38.**p14** / all CHR transcripts |
| Variant VCF | NCBI dbSNP b151 `common_all` / GRCh38.**p7** |
| `run gene` | Ensembl REST **archive 111** only (`e111.rest.ensembl.org`) |

Catalog and verification: [resources.md](resources.md).

## After ranking

Review candidates, then test in the lab: negative controls, dose response,
RNA and protein readouts, and replication. Old result files used a
different model; do not pool them with current ranks.

Tool and database citations: [methods.md](methods.md#references).
