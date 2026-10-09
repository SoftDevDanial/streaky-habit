README command checks, regression code-review finder (read-only), 2026-10-09, project HEAD b5b1f86 (src, index.html and tests identical to 9ebc54e).

1. Unit tests, README "Test it":
   command: node --test "tests/**/*.test.js"
   result:  tests 99, pass 99, fail 0, cancelled 0, skipped 0 (duration about 0.55 s)

2. README claim "A bare node --test tests/ fails on Node 24":
   command: node --test tests/      (node v24.11.1)
   result:  "test at tests:1:1 ... 'test failed'", failing, as the README and CLAUDE.md say

3. Browser tests, README "Test it":
   command: PYTHONDONTWRITEBYTECODE=1 python -m pytest tests/browser -q -p no:cacheprovider
   result:  176 passed in 44.96s. conftest started two http.server children (pid 50956 on 127.0.0.1:21781, pid 51992 on 127.0.0.1:21779)
            and stopped both, printing "refuses connections" for each. git status was clean afterwards.

4. README "Run it" and "Works right (live gate)", by readme_commands_check.py (port chosen free, 7939 here):
   [server] started pid 49468: python -m http.server 7939 --bind 127.0.0.1 (cwd = project root)
   [server] GET / -> 200, 3397 bytes
   [gate] tests/browser/live_e2e.py --base-url http://127.0.0.1:7939/ --out docs/modules/app/qa/regression-code-review/20261009T221155/live-e2e-check/
   PASS open the app
   PASS click the field, type a name, click Add
   PASS type a name, press Enter
   PASS click T's bead of both rows
   PASS click Y's bead of Read
   PASS reload
   PASS click Delete Stretch 10 minutes
   PASS click Cancel
   PASS wait, click the trash button, wait, click Delete habit, wait
   PASS type a duplicate name, press Enter
   PASS reload
   GATE PASS
   [gate] exit code 0
   [server] stopped pid 49468; 127.0.0.1:7939 accepts connections: False
   summary.json in live-e2e-check/: steps 11, steps_passed 11, requests 21, requests_outside_the_rule 0, console_errors 0, page_errors 0,
   pass true, void_if_the_date_changed false, Chromium 149.0.7827.55.
   Note: the README's --out example is docs/modules/app/qa/live-e2e/<ts>/ (the official evidence folder), so this check wrote into this
   review's own folder. It proves the command runs and passes on the current code. It is not the official gate.

5. Fidelity row of the README table: the command lives in docs/modules/app/qa.md, "Fidelity gate". Not re-run here (the economy ruling
   keeps the fidelity verdict of 321329c, whose src is identical to 9ebc54e: git diff 321329c 9ebc54e -- src index.html is empty).
