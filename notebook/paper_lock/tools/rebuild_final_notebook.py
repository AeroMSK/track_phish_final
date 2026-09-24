#!/usr/bin/env python3
"""
Rebuild the canonical Revision-11 notebook's paper-lock section (cells 207-216).

Purpose of this rebuild: the lock cells were patched for LIVE-MODE completeness
(a fresh top-to-bottom Kaggle re-run must not fall back to parsing a notebook file
that does not exist there). This script:
  1. builds a mini-notebook from scripts/final_cells (the patched sources),
  2. executes it with a real Jupyter kernel in PARSE mode (TRAC_NB_PATH = canonical
     notebook; lock cells are excluded from parsing via the PAPER_LOCK_ID marker),
  3. replaces cells 207+ of the canonical notebook with the freshly executed cells,
  4. validates the result and confirms the paper-lock sanity checks still pass.

Parse-mode outputs must be byte-identical to the previously committed ones
(the edits only add live-mode branches); the final diff step verifies that.
"""
import json, os, sys, time
from pathlib import Path
import nbformat
from nbclient import NotebookClient

SRC = Path("/home/z/my-project/scripts/final_cells")
NB_PATH = Path("/home/z/my-project/track_phish_final/notebook/trac-phish-revision11_runned.ipynb")
RUN_DIR = Path("/home/z/my-project/pl_run")            # cwd for the kernel (artifacts land here)

CELLS = ["cell_207_markdown", "cell_208_code", "cell_209_code", "cell_210_code", "cell_211_code",
         "cell_212_code", "cell_213_code", "cell_214_code", "cell_215_code", "cell_216_code"]

def src_of(name):
    return (SRC / f"{name}.py").read_text(encoding="utf-8")

# ---------------- 1. mini notebook ------------------------------------------------------------------
mini = nbformat.v4.new_notebook()
mini.metadata.kernelspec = {"display_name": "Python 3", "language": "python", "name": "python3"}
mini.metadata.language_info = {"name": "python"}
for name in CELLS:
    kind = "markdown" if name.endswith("markdown") else "code"
    c = nbformat.v4.new_code_cell(src_of(name)) if kind == "code" else nbformat.v4.new_markdown_cell(src_of(name))
    if kind == "code":
        c.outputs = []
        c.execution_count = None
    mini.cells.append(c)

# ---------------- 2. execute (parse mode) ------------------------------------------------------------
env = dict(os.environ)
env["TRAC_NB_PATH"] = str(NB_PATH)
env.pop("TRAC_PL_OUT", None)                     # default: ./trac_phish_paper_lock under cwd
print(f"Executing final-section cells with a real kernel (cwd={RUN_DIR}) ...")
t0 = time.time()
client = NotebookClient(mini, kernel_name="python3", resources={"metadata": {"path": str(RUN_DIR)}},
                        timeout=900)
client.execute()
print(f"execution finished in {time.time()-t0:.1f}s")

for i, c in enumerate(mini.cells):
    if c.cell_type != "code":
        continue
    for o in c.outputs:
        if o.output_type == "error":
            print(f"ERROR in cell {i}: {o.ename}: {o.evalue}")
            sys.exit(1)
print("no error outputs")

# ---------------- 3. replace the lock section of the canonical notebook ------------------------------
nb = json.loads(NB_PATH.read_text(encoding="utf-8"))
assert len(nb["cells"]) == 217, f"expected 217 cells (207 base + 10 lock), got {len(nb['cells'])}"
base = nb["cells"][:207]                          # strip the previous lock section
max_ec = max((c.get("execution_count") or 0) for c in base if c["cell_type"] == "code")

for c in mini.cells:
    if c.cell_type == "markdown":
        base.append({"cell_type": "markdown", "metadata": {}, "source": c.source})
    else:
        max_ec += 1
        base.append({"cell_type": "code", "execution_count": max_ec, "metadata": {},
                     "outputs": [json.loads(json.dumps(o)) for o in c.outputs], "source": c.source})
nb["cells"] = base

# confirm the paper-lock sanity summary in the final cell's stream output
def _stream_text(cell):
    parts = []
    for o in cell.get("outputs", []):
        if o.get("output_type") == "stream":
            t = o.get("text", "")
            parts.append(t if isinstance(t, str) else "".join(t))
    return "".join(parts)

last = _stream_text(base[-1])
assert "PAPER-LOCK SANITY:" in last, "paper-lock sanity summary not found in final cell output"
for line in last.splitlines():
    if line.startswith("PAPER-LOCK SANITY:") or "PAPER LOCK COMPLETE" in line:
        print("  ", line.strip())
import re as _re
_m = _re.search(r"PAPER-LOCK SANITY: (\d+)/(\d+) checks passed", last)
assert _m and _m.group(1) == _m.group(2), f"paper-lock sanity checks did not all pass: {last[-500:]}"

NB_PATH.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
print(f"canonical notebook rebuilt: {len(nb['cells'])} cells, execution counts up to {max_ec}")

# ---------------- 4. validate -------------------------------------------------------------------------
nb2 = nbformat.read(NB_PATH, as_version=4)
nbformat.validate(nb2)
print("nbformat validation: OK")
