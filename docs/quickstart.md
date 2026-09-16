# Quickstart

Check prerequisites and initialize local configuration:

```bash
uv run bsst doctor
uv run bsst resources
uv run bsst db init --dbsnp-common-all --gencode-v45-transcripts
```

Primary interface — a stored 3′UTR FASTA:

```bash
uv run bsst select fasta examples/NSD2.FASTA --gene NSD2
```

Convenience interface — canonical coding 3′UTR from the Ensembl **111** REST
archive (`https://e111.rest.ensembl.org`, paired with GENCODE 45). This is not
the live Ensembl server. If the archive is unreachable, use FASTA.

```bash
uv run bsst select gene NSD2
```

`--skip-variants` / `--skip-blast` remain available when a file is missing.
Every invocation writes a new `runs/<UTC timestamp>_<run id>/` directory.
