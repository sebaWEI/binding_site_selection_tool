from bsst.resources import (
    DBSNP_B151_GRCH38P7_COMMON_ALL,
    ENSEMBL_REST,
    GENCODE_V45_TRANSCRIPTS,
    bundled_gencode_fasta,
    catalog,
)


def test_pinned_resource_identifiers() -> None:
    assert DBSNP_B151_GRCH38P7_COMMON_ALL["assembly"] == "GRCh38.p7"
    assert "human_9606_b151_GRCh38p7" in DBSNP_B151_GRCH38P7_COMMON_ALL["url"]
    assert GENCODE_V45_TRANSCRIPTS["n_transcripts"] == 252930
    assert GENCODE_V45_TRANSCRIPTS["ensembl_version"] == "111"
    assert GENCODE_V45_TRANSCRIPTS["assembly"] == "GRCh38.p14"
    assert GENCODE_V45_TRANSCRIPTS["url"].endswith("release_45/gencode.v45.transcripts.fa.gz")
    assert ENSEMBL_REST["pinned"] is True
    assert ENSEMBL_REST["base_url"] == "https://e111.rest.ensembl.org"
    assert ENSEMBL_REST["ensembl_version"] == "111"
    ids = [item["id"] for item in catalog()]
    assert ids == [
        "dbsnp_b151_grch38p7_common_all",
        "gencode_v45_transcripts_chr",
        "ensembl_rest_111",
        "blastn_short",
        "rnaup",
        "example_letm1",
        "example_nsd2",
    ]


def test_bundled_gencode_fasta_matches_v45_if_present() -> None:
    path = bundled_gencode_fasta()
    if not path.is_file():
        return
    first = ""
    n_seq = 0
    with path.open() as handle:
        for line in handle:
            if line.startswith(">"):
                n_seq += 1
                if not first:
                    first = line[1:].strip()
    assert first == GENCODE_V45_TRANSCRIPTS["first_header"]
    assert n_seq == GENCODE_V45_TRANSCRIPTS["n_transcripts"]
