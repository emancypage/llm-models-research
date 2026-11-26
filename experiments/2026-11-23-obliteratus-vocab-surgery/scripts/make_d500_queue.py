"""Writes queue-d500.txt for the D500 follow-up (no prefill runs), with literal paths in the delete steps."""
from pathlib import Path

W = Path(__file__).resolve().parent.parent
RUNS = W / "runs"
lines = ["# follow-up D500 (protocol entries 2026-11-24, before any measurement; no prefill runs)"]


def job(name, deps, cmd):
    lines.append(f"{name:20s} | {deps:45s} | {cmd}")


def delete(path):
    return f"rm -rf {path} && df -h /home"


previous = ""
for c in ("q7", "l8"):
    job(f"{c}-gen-r1", previous, f"bash scripts/gen.sh {c} 1 stock")
    job(f"{c}-discover-r1", f"{c}-gen-r1", f"bash scripts/discover.sh {c} 1 stock")
    job(f"{c}-apply-d500r1", f"{c}-discover-r1", f"bash scripts/apply.sh {c} d500-{c}-r1")
    job(f"{c}-gen-r2", f"{c}-apply-d500r1", f"bash scripts/gen.sh {c} 2 /work/runs/{c}/d500-{c}-r1/V")
    job(f"{c}-delete-d500r1", f"{c}-gen-r2", delete(RUNS / c / f"d500-{c}-r1" / "V"))
    job(f"{c}-discover-r2", f"{c}-delete-d500r1", f"bash scripts/discover.sh {c} 2 stock d500-{c}-r1")
    job(f"{c}-kr500-build", f"{c}-discover-r2", f"bash scripts/kr500.sh {c}")
    job(f"{c}-apply-d500", f"{c}-discover-r2", f"bash scripts/apply.sh {c} d500-{c}")
    job(f"{c}-check-d500", f"{c}-apply-d500", f"bash scripts/check_n.sh {c} d500-{c}")
    job(f"{c}-verify-A-d500", f"{c}-check-d500", f"KEEP_TEXTS=1 bash scripts/verify.sh {c} V-d500-{c} /work/runs/{c}/d500-{c}/V")
    job(f"{c}-probe-V-d500", f"{c}-check-d500", f"bash scripts/probe.sh {c} V-d500 /work/runs/{c}/d500-{c}/V")
    job(f"{c}-screen-V-d500", f"{c}-check-d500", f"bash scripts/screen.sh {c} V-d500 /work/runs/{c}/d500-{c}/V")
    job(f"{c}-delete-d500", f"{c}-verify-A-d500,{c}-probe-V-d500,{c}-screen-V-d500", delete(RUNS / c / f"d500-{c}" / "V"))
    job(f"{c}-apply-kr500", f"{c}-delete-d500,{c}-kr500-build", f"bash scripts/apply.sh {c} kr500-{c}")
    job(f"{c}-check-kr500", f"{c}-apply-kr500", f"bash scripts/check_n.sh {c} kr500-{c}")
    job(f"{c}-verify-A-kr500", f"{c}-check-kr500", f"KEEP_TEXTS=1 bash scripts/verify.sh {c} V-kr500-{c} /work/runs/{c}/kr500-{c}/V")
    job(f"{c}-delete-kr500", f"{c}-verify-A-kr500", delete(RUNS / c / f"kr500-{c}" / "V"))
    previous = f"{c}-delete-kr500"
(W / "queue-d500.txt").write_text("\n".join(lines) + "\n")
names = [l.split("|")[0].strip() for l in lines[1:]]
deps = [d.strip() for l in lines[1:] for d in l.split("|")[1].split(",") if d.strip()]
print(len(names), "jobs; unknown deps", [d for d in deps if d not in names])
