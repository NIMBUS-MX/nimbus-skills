#!/usr/bin/env python3
"""
AI-transformation metrics collector for the CIDCA/Nimbus repos.
Emits a JSON blob of REAL git+gh data (no mocks) to stdout.

Usage:
  python3 collect_metrics.py [--since YYYY-MM-DD] [--from YYYY-MM-DD] [--json out.json]

- --since : the "AI era" boundary (default 2026-04-13, Claude Max plan start).
- --from  : earliest week shown on the timeline (default: since - 2*window, so the
            chart shows an equal "before" run-up to "after").
De-dup rule: cidca-platform holds the FULL history of ecg_auto + ecg-ui
(consolidated), so those two archived repos are marked legacy=True and are
EXCLUDED from every total. They are still collected for the "legacy tapered off"
narrative.
"""
import argparse, json, subprocess, datetime as dt, os, re, sys
from collections import defaultdict

HOME = os.path.expanduser("~/Development/nimbus")
REPOS = [
    dict(key="cidca-platform", path=f"{HOME}/cidca/cidca-platform",
         gh="NIMBUS-MX/cidca-platform", legacy=False, branch="dev",
         subpaths={"Backend (ecg_auto)": "ecg_auto", "Frontend (ecg-ui)": "ecg-ui",
                   "App iOS (cidca-doctor-ios)": "cidca-doctor-ios"}),
    dict(key="cidca-services", path=f"{HOME}/cidca/cidca-services",
         gh="NIMBUS-MX/cidca-services", legacy=False, branch="dev"),
    dict(key="ecg-trace-collector", path=f"{HOME}/ecg/ecg-trace-collector",
         gh="NIMBUS-MX/ecg-trace-collector-greengrass", legacy=False, branch="dev"),
    dict(key="cidca-infra", path=f"{HOME}/cidca/cidca-infra",
         gh="NIMBUS-MX/cidca-infra", legacy=False, branch="dev"),
    dict(key="cidca-context", path=f"{HOME}/cidca/cidca-context",
         gh="NIMBUS-MX/cidca-context", legacy=False, branch=None),
    dict(key="ecg_auto (legacy)", path=f"{HOME}/ecg/ecg_auto",
         gh="NIMBUS-MX/ecg_auto", legacy=True, branch=None),
    dict(key="ecg-ui (legacy)", path=f"{HOME}/ecg/ecg-ui",
         gh="NIMBUS-MX/ecg-ui", legacy=True, branch=None),
]

# Churn de-noising: exclude generated/vendored files so "líneas de código" stays meaningful.
EXCLUDES = [":(exclude,glob)**/*.lock", ":(exclude)package-lock.json", ":(exclude)poetry.lock",
            ":(exclude)yarn.lock", ":(exclude,glob)**/*.min.js", ":(exclude,glob)**/*.min.mjs",
            ":(exclude,glob)**/*.map", ":(exclude,glob)**/dist/**", ":(exclude,glob)**/build/**",
            ":(exclude,glob)**/node_modules/**", ":(exclude,glob)**/.yarn/**"]
TYPES = ["feat", "fix", "refactor", "test", "docs", "chore", "perf", "build", "ci", "style"]
CONV_RE = re.compile(r"^(%s)(\(|!|:)" % "|".join(TYPES))

# One human can commit under several git identities; fold them so per-person
# counts are real. Bots are dropped entirely.
ALIASES = {"Hector Duran": "Héctor", "Hector Durán": "Héctor", "hector97i": "Héctor",
           "Jorge Uribe": "Jorge", "Jorge Uribe Orizaga": "Jorge", "giorethKeenic": "Jorge",
           "giorethkeenic": "Jorge", "Nicolas Albo": "Nico", "Nicolas Gonzàlez Albo": "Nico",
           "albonicc": "Nico"}

def canon_author(name):
    n = (name or "").strip()
    low = n.lower()
    if not n or "[bot]" in low or "github-actions" in low or low.endswith("bot"):
        return None
    return ALIASES.get(n, n)

def git(path, *args, ref=None):
    cmd = ["git", "-C", path, "log"] + ([ref] if ref else ["--all"])
    cmd += list(args)
    try:
        return subprocess.run(cmd, capture_output=True, text=True, timeout=120).stdout
    except Exception:
        return ""

def commits(path, since, until, ref=None, pathspec=None):
    """Return list of (date, subject) for --no-merges commits in [since, until)."""
    args = ["--no-merges", f"--since={since}", f"--until={until}",
            "--date=short", "--pretty=%ad%x09%s"]
    if pathspec:
        args += ["--"] + pathspec
    out = git(path, *args, ref=ref)
    rows = []
    for line in out.splitlines():
        if "\t" in line:
            d, s = line.split("\t", 1)
            rows.append((d, s))
    return rows

def churn(path, since, until, ref=None, pathspec=None):
    """Sum insertions/deletions/files across --no-merges commits (generated files excluded)."""
    ps = (pathspec or ["."]) + EXCLUDES
    args = ["--no-merges", f"--since={since}", f"--until={until}", "--numstat",
            "--pretty=%x00"] + ["--"] + ps
    out = git(path, *args, ref=ref)
    ins = dele = files = 0
    seen = set()
    for line in out.splitlines():
        if not line or line.startswith("\x00"):
            continue
        parts = line.split("\t")
        if len(parts) == 3:
            a, d, f = parts
            if a.isdigit():
                ins += int(a)
            if d.isdigit():
                dele += int(d)
            files += 1
            seen.add(f)
    return dict(insertions=ins, deletions=dele, file_changes=files, distinct_files=len(seen))

def authors(path, since, until, ref=None):
    out = git(path, "--no-merges", f"--since={since}", f"--until={until}", "--pretty=%an", ref=ref)
    return sorted(set(a.strip() for a in out.splitlines() if a.strip()))

def author_counts(path, since, until, ref=None):
    """Commits per human (aliases folded, bots dropped)."""
    out = git(path, "--no-merges", f"--since={since}", f"--until={until}", "--pretty=%an", ref=ref)
    c = {}
    for line in out.splitlines():
        n = canon_author(line)
        if n:
            c[n] = c.get(n, 0) + 1
    return c

def classify(subjects):
    dist = {t: 0 for t in TYPES}
    conv = 0
    for s in subjects:
        m = CONV_RE.match(s.strip())
        if m:
            conv += 1
            dist[m.group(1)] += 1
    return dist, conv

def merged_prs(gh_repo, since):
    """Count merged PRs since `since` via gh (real). Returns int or None."""
    try:
        out = subprocess.run(
            ["gh", "pr", "list", "--repo", gh_repo, "--state", "merged",
             "--search", f"merged:>={since}", "--limit", "1000", "--json", "number"],
            capture_output=True, text=True, timeout=90).stdout
        return len(json.loads(out or "[]"))
    except Exception:
        return None

def window_stats(r, since, until):
    ref = r["branch"]
    subs = commits(r["path"], since, until, ref=ref)
    subjects = [s for _, s in subs]
    dist, conv = classify(subjects)
    ch = churn(r["path"], since, until, ref=ref)
    total = len(subs)
    return dict(
        commits=total,
        **ch,
        features=dist["feat"],
        fixes=dist["fix"],
        type_dist=dist,
        conventional_pct=round(100 * conv / total, 1) if total else 0.0,
        authors=authors(r["path"], since, until, ref=ref),
        author_counts=author_counts(r["path"], since, until, ref=ref),
    )

def weekly(r, frm, until):
    ref = r["branch"]
    counts = defaultdict(int)
    for d, _ in commits(r["path"], frm, until, ref=ref):
        y, m, day = map(int, d.split("-"))
        wk = dt.date(y, m, day)
        wk = wk - dt.timedelta(days=wk.weekday())  # ISO Monday
        counts[wk.isoformat()] += 1
    return counts

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", default="2026-04-13")
    ap.add_argument("--from", dest="frm", default=None)
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    since = dt.date.fromisoformat(a.since)
    today = dt.date.today()
    win = (today - since).days
    before_start = since - dt.timedelta(days=win)
    frm = dt.date.fromisoformat(a.frm) if a.frm else before_start
    S, B, T, F = since.isoformat(), before_start.isoformat(), today.isoformat(), frm.isoformat()

    # union of week keys across all repos for a stable x-axis
    all_weeks = set()
    repo_out = []
    for r in REPOS:
        if not os.path.isdir(r["path"]):
            continue
        after = window_stats(r, S, T)
        before = window_stats(r, B, S)
        wk = weekly(r, F, T)
        all_weeks |= set(wk.keys())
        entry = dict(key=r["key"], gh=r["gh"], legacy=r["legacy"],
                     before=before, after=after, weekly=wk,
                     merged_prs_after=merged_prs(r["gh"], S) if not r["legacy"] else None)
        if r.get("subpaths"):
            entry["subpaths"] = {}
            for label, sp in r["subpaths"].items():
                subs = commits(r["path"], S, T, ref=r["branch"], pathspec=[sp])
                ch = churn(r["path"], S, T, ref=r["branch"], pathspec=[sp])
                d, _ = classify([s for _, s in subs])
                entry["subpaths"][label] = dict(commits=len(subs), features=d["feat"], **ch)
        repo_out.append(entry)

    weeks = sorted(all_weeks)
    active = [r for r in repo_out if not r["legacy"]]

    def tot(win_key, field):
        return sum(r[win_key][field] for r in active)

    totals = dict(
        after=dict(commits=tot("after", "commits"),
                   insertions=tot("after", "insertions"),
                   deletions=tot("after", "deletions"),
                   features=tot("after", "features"),
                   fixes=tot("after", "fixes"),
                   merged_prs=sum((r["merged_prs_after"] or 0) for r in active)),
        before=dict(commits=tot("before", "commits"),
                    insertions=tot("before", "insertions"),
                    deletions=tot("before", "deletions"),
                    features=tot("before", "features"),
                    fixes=tot("before", "fixes")),
    )
    # per-human commit totals across active repos, both windows (aliases folded)
    def by_author(win_key):
        agg = {}
        for r in active:
            for name, n in r[win_key]["author_counts"].items():
                agg[name] = agg.get(name, 0) + n
        return dict(sorted(agg.items(), key=lambda kv: -kv[1]))
    totals["by_author"] = dict(after=by_author("after"), before=by_author("before"))
    # per-repo commits in both windows (for the repo-level antes/después chart)
    totals["by_repo"] = [dict(repo=r["key"], before=r["before"]["commits"],
                              after=r["after"]["commits"]) for r in active]

    all_authors = sorted(set(x for r in active for x in r["after"]["authors"]))

    result = dict(
        generated_at=dt.datetime.now().isoformat(timespec="seconds"),
        since=S, before_start=B, today=T, timeline_from=F, window_days=win,
        weeks=weeks, repos=repo_out, totals=totals, contributors=all_authors,
        excludes_note="Churn excluye lockfiles y artefactos generados (*.lock, dist/, build/, *.min.js, *.map).",
    )
    js = json.dumps(result, indent=2, ensure_ascii=False)
    if a.json:
        open(a.json, "w").write(js)
        print(f"wrote {a.json}", file=sys.stderr)
    print(js)

if __name__ == "__main__":
    main()
