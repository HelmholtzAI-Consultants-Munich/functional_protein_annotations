"""Look up TIGRFAM/NCBIfams hits for WP_ IDs via NCBI GenPept records (batched).
Usage: python tigrfam_lookup.py wp_ids.txt   (needs: pip install biopython)
"""
import re, sys, time, gzip, requests
from Bio import Entrez, SeqIO

Entrez.email = "you@example.org"   # set your email
# Entrez.api_key = "..."           # optional: 10 req/s instead of 3

PAT = re.compile(r"TIGR\d{5}|NF\d{6}")
ids = [l.strip() for l in open(sys.argv[1]) if l.strip()]

# CDD PSSM id -> source accession, to catch hits that only appear as db_xref CDD:<id>
url = "https://ftp.ncbi.nih.gov/pub/mmdb/cdd/cddid.tbl.gz"

with requests.get(url, stream=True) as r:
    r.raise_for_status()
    with open("cddid.tbl.gz", "wb") as f:
        for chunk in r.iter_content(chunk_size=1024 * 1024):  # 1 MB at a time
            f.write(chunk)
cdd = {}
with gzip.open("cddid.tbl.gz", "rt") as fh:
    for line in fh:
        f = line.rstrip("\n").split("\t")
        if len(f) > 1 and PAT.fullmatch(f[1]):
            cdd[f[0]] = f[1]

found = {i: set() for i in ids}
for s in range(0, len(ids), 100):
    batch = ids[s:s+100]
    h = Entrez.efetch(db="protein", id=",".join(batch), rettype="gp", retmode="text")
    for rec in SeqIO.parse(h, "genbank"):
        for f in rec.features:
            if f.type != "Region":
                continue
            q = f.qualifiers
            text = " ".join(q.get("region_name", []) + q.get("note", []))
            hits = set(PAT.findall(text))
            for x in q.get("db_xref", []):
                if x.startswith("CDD:") and x[4:] in cdd:
                    hits.add(cdd[x[4:]])
            found[rec.id].update(hits)
    h.close()
    time.sleep(0.4)

with open("wp_tigrfam_hits.tsv", "w") as out:
    out.write("wp_id\taccessions\n")
    for i in ids:
        out.write(f"{i}\t{','.join(sorted(found[i]))}\n")

n_any   = sum(bool(v) for v in found.values())
n_tigr  = sum(any(a.startswith("TIGR") for a in v) for v in found.values())
print(f"{len(ids)} proteins | any TIGR/NF hit: {n_any} | TIGR-only: {n_tigr}")
