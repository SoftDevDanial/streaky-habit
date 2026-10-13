# Finalize, Streaky Habit v1.1.0

**Date.** 2026-10-13 · **Approved by.** the owner, 2026-10-11 23:45 (`../RULINGS.md`, Finalize gate)

## What moved
`../final/` was copied into `docs/design/` by `finalize_copy.py`. 23 files, the nine goldens with their `.md`, `system.css`, `system.md`, `sample-history.json`, `LINKS.json` and `MANIFEST.md`. 12 are new and 11 replace 1.0's goldens, which stay in tag `v1.0.0`. Every copy has the SHA-256 of its source. `../RULINGS.md` sits beside 1.0's rulings as `docs/design/RULINGS-v1.1.0.md`, as 1.0's finalize copied its rulings.

`../final/checks/` and `../final/SELF-CRITIQUE.md` stay here. The checks reach `round-2/f2.html`, so they only run from the explore folder.

## The checks from the new place
`rehome_checks.py` copies `../final/checks/*.py` to a scratch folder with the golden folder set to `docs/design/` and every `round-2/` lookup kept on this folder. Then `check.py` ran from there.

| Run | Asserts | Results |
|---|---|---|
| `../final/checks/results.json` (2026-10-11) | 97 of 97 | |
| `check-results.json` (2026-10-13, goldens read from `docs/design/`) | 97 of 97 | every section equal to the 2026-10-11 run |

## Run again
```
python -B finalize_copy.py <app root> --dry
python -B rehome_checks.py <app root> <scratch folder>
python -B <scratch folder>/check.py
```
