"""
CourtTrack: replace static per-team admin bypass UUIDs with a session-based
unlock, across all coach + family pages.

USAGE:
  1. Copy this file into your repo root (same folder as sync.py), e.g.
     D:\\JB Stuff\\Court_Track\\Court_Track_Website\\fix_admin_bypass.py
  2. Open a terminal there and run:
       python fix_admin_bypass.py
  3. It will print which files it changed. Review with `git diff` before
     committing.
  4. If a file wasn't found or didn't match, it's printed as SKIPPED —
     tell me and we'll check that file by hand rather than guessing.
"""

import re
import os

FILES = [
    "eltham-122/index.html",
    "eltham-122/family/index.html",
    "eltham-121/index.html",
    "eltham-121/family/index.html",
    "dv-121/index.html",
    "dv-121/family/index.html",
    "darebin-121/index.html",
    "darebin-121/family/index.html",
]

# Matches the whole old IIFE regardless of which UUID that particular file
# uses, so this works across all 8 files without hardcoding each token.
OLD_BLOCK_RE = re.compile(
    r"<script>\s*"
    r"//\s*──\s*ADMIN BYPASS.*?"
    r"\(function\(\)\{.*?\}\)\(\);\s*"
    r"//\s*──+\s*"
    r"</script>",
    re.DOTALL,
)

NEW_BLOCK = """<script>
// \u2500\u2500 ADMIN SESSION UNLOCK \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
// No static bypass secret in this file anymore. If this browser tab already
// logged into /admin this session (server-validated via validate-code),
// sessionStorage carries that flag here automatically \u2014 one login covers
// every team.
(function(){
if(sessionStorage.getItem('ct_admin') === '1'){
window.__ADMIN_BYPASS__ = true;
}
})();
// \u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500
</script>"""


def main():
    for rel_path in FILES:
        if not os.path.exists(rel_path):
            print(f"SKIPPED (not found): {rel_path}")
            continue

        with open(rel_path, "r", encoding="utf-8") as f:
            content = f.read()

        new_content, n = OLD_BLOCK_RE.subn(NEW_BLOCK, content, count=1)

        if n == 0:
            print(f"SKIPPED (no bypass block matched): {rel_path}")
            continue

        with open(rel_path, "w", encoding="utf-8") as f:
            f.write(new_content)

        print(f"FIXED: {rel_path}")


if __name__ == "__main__":
    main()
