"""Lets the "background" extension's script run in Positron.

Positron's workbench.html Content-Security-Policy lists a script nonce, and when a nonce is present
browsers ignore 'unsafe-inline', so the extension's injected <script> is silently blocked (no web,
and the "corrupt installation" toast isn't hidden). This copies the page's nonce onto that script.
Re-run it after changing background.* settings or updating Positron, since both rewrite the file.
"""
import re
import sys
from pathlib import Path

HTML = Path(sys.argv[1] if len(sys.argv) > 1 else
            "/Applications/Positron.app/Contents/Resources/app/out/vs/code/electron-browser/workbench/workbench.html")

s = HTML.read_text(encoding="utf-8")
m = re.search(r"'nonce-([^']+)'", s)
if "<!-- vscode-background-start" not in s:
    sys.exit("No background patch found: install the extension and click 'Apply and Reload' first.")
if not m:
    sys.exit("No nonce in this page's policy, so nothing to fix.")
a, b = s.index("<!-- vscode-background-start"), s.index("<!-- vscode-background-end")
block = re.sub(r"<script(?: nonce=\"[^\"]*\")?>", f'<script nonce="{m.group(1)}">', s[a:b])
assert block.count(f'nonce="{m.group(1)}"') == 1
HTML.write_text(s[:a] + block + s[b:], encoding="utf-8")
print("Done. Quit and reopen Positron.")
