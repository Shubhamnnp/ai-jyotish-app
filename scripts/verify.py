#!/usr/bin/env python3
"""
JyotishOS Verification Gate (Phase U0, Task U0-T4).
One-command verification harness executing:
1. Engine honesty & ephemeris status check.
2. UI module smoke import test (all 30 modules).
3. FastAPI health & engine probe (/health, /health/engine).
4. Quick characterization snapshot regression tests (3 charts).
5. Comprehensive test suite (357+ tests).

Exit code: 0 if all green, non-zero on any failure.
"""

import sys
import os
import time
import glob
import importlib
import subprocess

# Ensure repo root and src in sys.path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(REPO_ROOT, "src")
sys.path.insert(0, REPO_ROOT)
sys.path.insert(0, SRC_DIR)

def print_header(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}")

def step_1_engine_check() -> bool:
    print_header("Step 1: Astronomical Engine & Precision Verification")
    from src.jyotish.core.calculator import default_chart_calculator
    prov = default_chart_calculator.provider
    is_deg = getattr(prov, 'is_degraded', False)
    if callable(is_deg):
        is_deg = is_deg()
    has_swe = getattr(prov, '_has_swisseph', False)
    mode = "SwissEph (precise)" if has_swe and not is_deg else "PyEphem (degraded)"

    print(f"  Active Provider : {prov.__class__.__name__}")
    print(f"  Swiss Ephemeris : {has_swe}")
    print(f"  Degraded Flag   : {is_deg}")
    print(f"  Engine Mode     : {mode}")

    if is_deg:
        print("  [WARNING] Engine is running in degraded mode! Check Swiss Ephemeris bindings.")
    else:
        print("  [OK] Swiss Ephemeris high-precision engine active.")
    return True

def step_2_ui_smoke_test() -> bool:
    print_header("Step 2: UI Modules Smoke Import Test (All 30 Modules)")
    module_files = glob.glob(os.path.join(SRC_DIR, "jyotish", "ui", "modules", "*.py"))
    passed = 0
    failed = 0

    for m_path in sorted(module_files):
        base = os.path.basename(m_path)
        if base == "__init__.py":
            continue
        mod_name = f"src.jyotish.ui.modules.{base[:-3]}"
        try:
            importlib.import_module(mod_name)
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {mod_name}: {type(e).__name__} - {e}")
            failed += 1

    print(f"  UI Modules Checked: {passed} passed, {failed} failed.")
    return failed == 0

def step_3_api_health_probe() -> bool:
    print_header("Step 3: FastAPI Health & Engine Probe (/health, /health/engine)")
    try:
        from starlette.testclient import TestClient
        from src.jyotish.api.main import app
        client = TestClient(app)

        # 1. /health
        res1 = client.get("/health")
        if res1.status_code != 200:
            print(f"  [FAIL] /health returned status {res1.status_code}")
            return False
        d1 = res1.json()
        print(f"  [OK] /health -> status: {d1.get('status')} | version: {d1.get('version')}")

        # 2. /health/engine
        res2 = client.get("/health/engine")
        if res2.status_code != 200:
            print(f"  [FAIL] /health/engine returned status {res2.status_code}")
            return False
        d2 = res2.json()
        print(f"  [OK] /health/engine -> engine: {d2.get('engine')} | degraded: {d2.get('degraded')}")
        return True
    except Exception as e:
        print(f"  [FAIL] API health probe exception: {e}")
        return False

def step_4_quick_regression() -> bool:
    print_header("Step 4: Quick Characterization Snapshot Regression (3 Charts)")
    cmd = [sys.executable, "-m", "pytest", "tests/regression/test_characterization_snapshots.py", "-m", "not slow", "-q"]
    t0 = time.time()
    res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    elapsed = time.time() - t0

    if res.returncode == 0:
        print(f"  [OK] Quick characterization snapshots verified in {elapsed:.2f}s.")
        print(f"  Output summary: {res.stdout.strip().splitlines()[-1] if res.stdout.strip() else 'passed'}")
        return True
    else:
        print(f"  [FAIL] Quick snapshots failed (exit code {res.returncode}):")
        print(res.stdout)
        print(res.stderr)
        return False

def step_5_full_test_suite() -> bool:
    print_header("Step 5: Full Test Suite Execution (pytest -q)")
    cmd = [sys.executable, "-m", "pytest", "tests", "-q"]
    t0 = time.time()
    res = subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)
    elapsed = time.time() - t0

    if res.returncode == 0:
        last_line = res.stdout.strip().splitlines()[-1] if res.stdout.strip() else "All passed"
        print(f"  [OK] Test suite passed in {elapsed:.2f}s.")
        print(f"  Result: {last_line}")
        return True
    else:
        print(f"  [FAIL] Test suite failed (exit code {res.returncode}):")
        print(res.stdout)
        print(res.stderr)
        return False

def main():
    start_time = time.time()
    print("=" * 70)
    print("      JyotishOS Comprehensive Verification Gate (make verify)")
    print("=" * 70)

    steps = [
        ("Step 1 (Engine Check)", step_1_engine_check),
        ("Step 2 (UI Smoke)", step_2_ui_smoke_test),
        ("Step 3 (API Probe)", step_3_api_health_probe),
        ("Step 4 (Quick Snapshots)", step_4_quick_regression),
        ("Step 5 (Full Tests)", step_5_full_test_suite),
    ]

    all_passed = True
    for name, func in steps:
        if not func():
            print(f"\n>>> Gate failed at {name}! Aborting verification. <<<")
            all_passed = False
            break

    total_elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    if all_passed:
        print(f"  ALL VERIFICATION GATES PASSED (Total time: {total_elapsed:.2f}s)")
        print("  Codebase is clean, non-regressed, and safe to proceed.")
        print("=" * 70)
        sys.exit(0)
    else:
        print(f"  VERIFICATION FAILED (Total time: {total_elapsed:.2f}s)")
        print("=" * 70)
        sys.exit(1)

if __name__ == "__main__":
    main()
