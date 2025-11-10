#!/usr/bin/env python3
# safe_canonize_works.py
"""
Sichere Canonization von Work-URIs basierend auf actualizedIn / manifestedIn.
Ersetzt nur, wenn mehrere Sicherheitschecks erfüllt sind.
Erzeugt:
 - MusicHistoryGraph_TwelveToneMusic_CANONIZED_SAFE.ttl
 - Canonization_Log_safe.csv (automatisch angewendete Replacements)
 - Canonization_Review.csv (Vorschläge zur manuellen Prüfung)
"""
from rdflib import Graph, Namespace, URIRef
from pathlib import Path
from difflib import SequenceMatcher
from unidecode import unidecode
import re
import csv

# ---- Konfiguration ----
INPUT_FILE = "MusicHistoryGraph_TwelveToneMusic_NEW.ttl"   # original (parsebar)
OUTPUT_FILE = "MusicHistoryGraph_TwelveToneMusic_CANONIZED_SAFE.ttl"
LOG_CSV = "Canonization_Log_safe.csv"
REVIEW_CSV = "Canonization_Review.csv"
# -----------------------

# Namespaces
MHG = Namespace("http://music-history-graph.ch/twelve-tone-onto#")
FRBR = Namespace("http://purl.org/vocab/frbr/core/")
DCTERMS = Namespace("http://purl.org/dc/terms/")

# Hilfsfunktionen
def norm_str(s: str) -> str:
    """Normalisiere einen URI-LocalPart: ascii, lower, non-alnum -> underscore."""
    s2 = unidecode(s)
    s2 = s2.lower()
    s2 = re.sub(r'[^a-z0-9]+', '_', s2)
    s2 = re.sub(r'_+', '_', s2).strip('_')
    return s2

def token_set(s: str):
    return set(t for t in s.split('_') if t)

def seq_ratio(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def extract_op_number(s: str):
    """Versucht Opus-Nummer wie 'op23' oder 'op_23' oder 'op23_5' zu finden; gibt Hauptzahl oder None."""
    m = re.search(r'op[_\-]?(\d+)', s, re.I)
    if m:
        return m.group(1)
    return None

# ---- Lade Graph ----
g = Graph()
g.parse(INPUT_FILE, format="turtle")

# ---- Sammle kanonische Werke ----
canonical = set()
# 1) direct objects of mhg:actualizedIn where object is a URI
for s, p, o in g.triples((None, MHG.actualizedIn, None)):
    if isinstance(o, URIRef) and str(o).startswith(str(MHG)):
        canonical.add(str(o).split('#',1)[1])  # Local part

# 2) manifestedIn can be either direct triple or blank node with mhg:manifestedIn inside
for s, p, o in g.triples((None, MHG.manifestedIn, None)):
    # direct URI object
    if isinstance(o, URIRef) and str(o).startswith(str(MHG)):
        canonical.add(str(o).split('#',1)[1])
    else:
        # if o is a BNode, find mhg:manifestedIn inside it
        for b_s, b_p, b_o in g.triples((o, MHG.manifestedIn, None)):
            if isinstance(b_o, URIRef) and str(b_o).startswith(str(MHG)):
                canonical.add(str(b_o).split('#',1)[1])

print(f"📘 Kanonische Werke gefunden: {len(canonical)}")

# ---- Sammle Work -> Creator und Creator -> Works ----
work_creator = {}   # work_local -> creator_local (if available)
creator_works = {}  # creator_local -> set(work_local)

# from work to creator (frbr:creator)
for s, p, o in g.triples((None, FRBR.creator, None)):
    if isinstance(s, URIRef) and isinstance(o, URIRef) and str(s).startswith(str(MHG)) and str(o).startswith(str(MHG)):
        w = str(s).split('#',1)[1]
        c = str(o).split('#',1)[1]
        work_creator[w] = c
        creator_works.setdefault(c, set()).add(w)

# from creator to works via frbr:creatorOf
for s, p, o in g.triples((None, FRBR.creatorOf, None)):
    if isinstance(s, URIRef) and isinstance(o, URIRef) and str(s).startswith(str(MHG)) and str(o).startswith(str(MHG)):
        c = str(s).split('#',1)[1]
        w = str(o).split('#',1)[1]
        work_creator.setdefault(w, c)
        creator_works.setdefault(c, set()).add(w)

print(f"🔗 Work->Creator Einträge: {len(work_creator)}")

# ---- Alle mhg: URIs (LocalParts) ----
all_mhg = set()
for s in g.subjects():
    if isinstance(s, URIRef) and str(s).startswith(str(MHG)):
        all_mhg.add(str(s).split('#',1)[1])
for p in g.predicates():
    if isinstance(p, URIRef) and str(p).startswith(str(MHG)):
        all_mhg.add(str(p).split('#',1)[1])
for o in g.objects():
    if isinstance(o, URIRef) and str(o).startswith(str(MHG)):
        all_mhg.add(str(o).split('#',1)[1])

print(f"🔎 Gesamt mhg: URIs: {len(all_mhg)}")

# ---- Build canonical dict by creator for faster lookup ----
canon_by_creator = {}
for w in canonical:
    c = work_creator.get(w)
    if c:
        canon_by_creator.setdefault(c, set()).add(w)
    else:
        canon_by_creator.setdefault(None, set()).add(w)  # canonic without known creator

# ---- Matching & Regeln ----
automatic_replacements = {}   # old_local -> new_local
review_candidates = []        # tuples (old, best_candidate, ratio, token_overlap, reason)

for old in sorted(all_mhg):
    if old in canonical:
        continue

    # consider only work-like names: heuristic: contains '_' and letters; skip pure prefix names like 'isoCountryCode'
    if not re.search(r'[A-Za-z]', old) or len(old) < 4:
        continue

    # prefer canonical forms from same creator if known
    creator = work_creator.get(old)
    candidates = set()
    if creator and creator in canon_by_creator:
        candidates |= canon_by_creator[creator]
    # also include global canonicals (no creator)
    candidates |= canon_by_creator.get(None, set())

    if not candidates:
        continue

    old_norm = norm_str(old)
    old_tokens = token_set(old_norm)
    old_op = extract_op_number(old_norm)

    best = None
    best_score = 0.0
    best_token_overlap = 0.0

    for cand in candidates:
        cand_norm = norm_str(cand)
        cand_tokens = token_set(cand_norm)
        cand_op = extract_op_number(cand_norm)

        # if both have op numbers and they differ -> skip candidate
        if old_op and cand_op and old_op != cand_op:
            continue

        ratio = seq_ratio(old_norm, cand_norm)
        shared = old_tokens.intersection(cand_tokens)
        token_overlap = len(shared) / max(1, max(len(old_tokens), len(cand_tokens)))

        # scoring: we keep both ratio and token_overlap for decisions
        # choose best candidate by ratio then token_overlap
        if ratio > best_score or (abs(ratio - best_score) < 1e-9 and token_overlap > best_token_overlap):
            best = cand
            best_score = ratio
            best_token_overlap = token_overlap

    if not best:
        continue

    # Decision rules (conservative):
    # Rule A: very high seq ratio -> auto replace
    # Rule B: high ratio + high token overlap -> auto replace
    # Otherwise: add to review list if moderate similarity
    if best_score >= 0.95 and best_token_overlap >= 0.65:
        automatic_replacements[old] = best
    elif best_score >= 0.98:  # extremely strict overall match
        automatic_replacements[old] = best
    elif best_score >= 0.85 and best_token_overlap >= 0.5:
        # borderline -> add to review
        review_candidates.append((old, best, best_score, best_token_overlap, "borderline"))
    else:
        # lower similarity -> skip
        pass

print(f"✅ Automatische Ersetzungen (vor Anwendung): {len(automatic_replacements)}")
print(f"📝 Review-Vorschläge: {len(review_candidates)}")

# ---- Apply replacements to file text (safe regex with word boundaries) ----
orig_text = Path(INPUT_FILE).read_text(encoding="utf-8")

# Make a copy of text and apply replacements
new_text = orig_text
# Sort replacements by descending old length to avoid partial overlap issues
for old, new in sorted(automatic_replacements.items(), key=lambda x: -len(x[0])):
    # replace mhg:Old only (word boundary after local)
    pattern = re.compile(rf'\bmhg:{re.escape(old)}\b')
    new_text, n = pattern.subn(f"mhg:{new}", new_text)
    # optional: log n for debug
    # print(f"Replaced {old} -> {new} ({n} occurrences)")

# ---- Write outputs ----
Path(OUTPUT_FILE).write_text(new_text, encoding="utf-8")
with open(LOG_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["old_local", "new_local"])
    for old, new in sorted(automatic_replacements.items()):
        writer.writerow([old, new])

with open(REVIEW_CSV, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["old_local", "best_candidate", "ratio", "token_overlap", "reason"])
    for (old, best, ratio, tover, reason) in review_candidates:
        writer.writerow([old, best, f"{ratio:.4f}", f"{tover:.4f}", reason])

print(f"🔁 Ergebnis geschrieben: {OUTPUT_FILE}")
print(f"📄 Log (automatisch): {LOG_CSV}")
print(f"📋 Review-Liste: {REVIEW_CSV}")
