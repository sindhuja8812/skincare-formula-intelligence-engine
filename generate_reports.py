"""
generate_reports.py
Run from project root:  python generate_reports.py

Produces three files inside  reports/
  ├── test_report.txt          — full pytest terminal output
  ├── coverage_report.txt      — line-by-line coverage summary
  └── coverage_report.html     — browsable HTML coverage (open in browser)
"""

import subprocess
import sys
from pathlib import Path
from datetime import datetime

# ── Output directory ──────────────────────────────────────────────────────────
REPORTS_DIR = Path("reports")
REPORTS_DIR.mkdir(exist_ok=True)

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
divider   = "=" * 70


def run(cmd: list[str]) -> tuple[str, int]:
    """Run a subprocess and return (combined output, return_code)."""
    result = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return result.stdout, result.returncode


# ── 1. Test report ────────────────────────────────────────────────────────────
print("Running tests ...")
test_output, test_code = run([
    sys.executable, "-m", "pytest",
    "--tb=short",          # short tracebacks on failure
    "-v",                  # verbose: one line per test
])

test_report_path = REPORTS_DIR / "test_report.txt"
test_report_path.write_text(
    f"SKINCARE FORMULA INTELLIGENCE ENGINE — TEST REPORT\n"
    f"Generated : {timestamp}\n"
    f"{divider}\n\n"
    f"{test_output}",
    encoding="utf-8",
)
print(f"  Saved → {test_report_path}")


# ── 2. Coverage summary (text) ────────────────────────────────────────────────
print("Running coverage ...")
cov_output, cov_code = run([
    sys.executable, "-m", "pytest",
    "--cov=utils",
    "--cov-report=term-missing",
    "-q",                  # quiet: no per-test lines, just summary
])

cov_report_path = REPORTS_DIR / "coverage_report.txt"
cov_report_path.write_text(
    f"SKINCARE FORMULA INTELLIGENCE ENGINE — COVERAGE REPORT\n"
    f"Generated : {timestamp}\n"
    f"{divider}\n\n"
    f"{cov_output}",
    encoding="utf-8",
)
print(f"  Saved → {cov_report_path}")


# ── 3. Coverage HTML ──────────────────────────────────────────────────────────
print("Generating HTML coverage ...")
html_dir = REPORTS_DIR / "coverage_html"
_, html_code = run([
    sys.executable, "-m", "pytest",
    "--cov=utils",
    f"--cov-report=html:{html_dir}",
    "-q",
])
print(f"  Saved → {html_dir}/index.html")


# ── 4. Summary to terminal ────────────────────────────────────────────────────
print(f"\n{divider}")
print("REPORTS GENERATED")
print(f"{divider}")
print(f"  Test report    : {test_report_path}")
print(f"  Coverage text  : {cov_report_path}")
print(f"  Coverage HTML  : {html_dir / 'index.html'}")
print(f"{divider}")
print(f"Exit code: {'0 (all passed)' if test_code == 0 else test_code}")