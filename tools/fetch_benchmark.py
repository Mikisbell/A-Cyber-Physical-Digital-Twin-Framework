#!/usr/bin/env python3
"""
tools/fetch_benchmark.py — Ground Motion Record Manifest Verifier (EIU)
========================================================================
Verify and manage ground motion records against db/manifest.yaml.

Checks that required seismic records are present in db/excitation/records/,
validates their format, and reports what needs to be downloaded.

Previously: generated synthetic .AT2 files (removed — papers need real data).

Usage:
    python3 tools/fetch_benchmark.py                    # Status report
    python3 tools/fetch_benchmark.py --verify           # Validate .AT2 headers
    python3 tools/fetch_benchmark.py --scan             # List all records found
    python3 tools/fetch_benchmark.py --update-manifest  # Sync manifest
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

ROOT = Path(__file__).resolve().parent.parent
RECORDS_DIR = ROOT / "db" / "excitation" / "records"
MANIFEST_PATH = ROOT / "db" / "manifest.yaml"

PEER_URL = "https://ngawest2.berkeley.edu/"


# ---------------------------------------------------------------------------
# .AT2 validation
# ---------------------------------------------------------------------------

def validate_at2(filepath: Path) -> dict:
    """Validate a .AT2 file against PEER NGA-West2 format expectations.

    Returns dict with keys: valid (bool), filename, errors (list[str]),
    npts (int|None), dt (float|None).
    """
    result = {"valid": True, "filename": filepath.name, "errors": [], "npts": None, "dt": None}

    try:
        lines = filepath.read_text(errors="replace").splitlines()
    except Exception as exc:
        result["valid"] = False
        result["errors"].append(f"Cannot read file: {exc}")
        return result

    if len(lines) < 5:
        result["valid"] = False
        result["errors"].append(f"Too few lines ({len(lines)}); expected at least 5")
        return result

    # Line 1: should contain "PEER" or a known header keyword
    header_keywords = ["PEER", "STRONG MOTION", "ACCELERATION", "COSMOS", "RECORD"]
    if not any(kw in lines[0].upper() for kw in header_keywords):
        result["errors"].append(f"Line 1 missing recognizable header (got: {lines[0][:60]})")
        result["valid"] = False

    # Line 4 (index 3): NPTS= and DT=
    meta_line = lines[3]
    npts_match = re.search(r"NPTS\s*=\s*(\d+)", meta_line, re.IGNORECASE)
    dt_match = re.search(r"DT\s*=\s*([\d.Ee+-]+)", meta_line, re.IGNORECASE)

    if not npts_match:
        result["errors"].append(f"Line 4 missing NPTS= (got: {meta_line[:60]})")
        result["valid"] = False
    else:
        result["npts"] = int(npts_match.group(1))

    if not dt_match:
        result["errors"].append(f"Line 4 missing DT= (got: {meta_line[:60]})")
        result["valid"] = False
    else:
        result["dt"] = float(dt_match.group(1))

    # Data lines (from line 5 onward): spot-check first 10 data lines
    data_lines = lines[4:]
    if not data_lines:
        result["errors"].append("No data lines after header")
        result["valid"] = False
    else:
        num_pattern = re.compile(r"[+-]?\d+\.?\d*[Ee]?[+-]?\d*")
        checked = 0
        for dl in data_lines[:10]:
            stripped = dl.strip()
            if not stripped:
                continue
            nums = num_pattern.findall(stripped)
            if not nums:
                result["errors"].append(f"Non-numeric data line: {stripped[:60]}")
                result["valid"] = False
                break
            checked += 1
        if checked == 0 and not result["errors"]:
            result["errors"].append("Data section appears empty")
            result["valid"] = False

    return result


# ---------------------------------------------------------------------------
# Manifest helpers
# ---------------------------------------------------------------------------

def load_manifest() -> dict | None:
    """Load db/manifest.yaml.  Returns None if file missing or unparseable."""
    if not MANIFEST_PATH.exists():
        return None
    if not HAS_YAML:
        print("ERROR: PyYAML not installed.  pip install pyyaml")
        sys.exit(2)
    try:
        with open(MANIFEST_PATH) as f:
            data = yaml.safe_load(f) or {}
        return data
    except Exception as exc:
        print(f"ERROR: Cannot parse {MANIFEST_PATH}: {exc}")
        return None


def get_needed_records(manifest: dict) -> list[dict]:
    """Extract list of needed records from manifest.

    Each entry is a dict with at least 'filename' or 'rsn'.
    Accepts either a list of dicts or a list of strings.
    """
    exc = manifest.get("excitation", {})
    needed = exc.get("records_needed", [])
    if not needed:
        return []

    out = []
    for entry in needed:
        if isinstance(entry, dict):
            out.append(entry)
        elif isinstance(entry, str):
            out.append({"filename": entry})
        else:
            out.append({"filename": str(entry)})
    return out


def scan_records() -> list[Path]:
    """Return sorted list of .AT2 files in RECORDS_DIR."""
    if not RECORDS_DIR.exists():
        RECORDS_DIR.mkdir(parents=True, exist_ok=True)
        return []
    files = sorted(RECORDS_DIR.glob("*.AT2"), key=lambda p: p.name.upper())
    # Also catch lowercase extension
    files_lower = sorted(RECORDS_DIR.glob("*.at2"), key=lambda p: p.name.upper())
    seen = {f.name for f in files}
    for f in files_lower:
        if f.name not in seen:
            files.append(f)
    return sorted(files, key=lambda p: p.name.upper())


def match_record(needed: dict, present_names: set[str]) -> str | None:
    """Check if a needed record is present.  Returns matched filename or None."""
    fname = needed.get("filename", "")
    if fname and fname in present_names:
        return fname

    # Try matching by RSN prefix
    rsn = needed.get("rsn")
    if rsn:
        prefix = f"RSN{rsn}"
        for name in present_names:
            if name.upper().startswith(prefix.upper()):
                return name

    return None


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def cmd_status(do_verify: bool = False):
    """Main status report: compare manifest vs present files."""
    manifest = load_manifest()
    if manifest is None:
        print("=== GROUND MOTION RECORDS STATUS ===")
        print(f"Manifest: {MANIFEST_PATH.relative_to(ROOT)}")
        print()
        print("NOT CONFIGURED — manifest.yaml not found or empty.")
        print("Run select_ground_motions.py first to define needed records,")
        print("or create db/manifest.yaml manually.")
        print("====================================")
        sys.exit(2)

    needed = get_needed_records(manifest)
    if not needed:
        print("=== GROUND MOTION RECORDS STATUS ===")
        print(f"Manifest: {MANIFEST_PATH.relative_to(ROOT)}")
        print()
        print("NOT CONFIGURED — excitation.records_needed is empty.")
        print("Run select_ground_motions.py first to define needed records.")
        print("====================================")
        sys.exit(2)

    source = manifest.get("excitation", {}).get("source", "NGA-West2")
    quartile = manifest.get("quartile", "unknown")

    present_files = scan_records()
    present_names = {f.name for f in present_files}

    # Validate if requested
    validations = {}
    if do_verify:
        for fp in present_files:
            validations[fp.name] = validate_at2(fp)

    # Match needed vs present
    matched = []     # (needed_entry, matched_filename)
    missing = []     # needed_entry
    for entry in needed:
        m = match_record(entry, present_names)
        if m:
            matched.append((entry, m))
        else:
            missing.append(entry)

    n_needed = len(needed)
    n_present = len(matched)
    n_missing = len(missing)

    # --- Print report ---
    print("=== GROUND MOTION RECORDS STATUS ===")
    print(f"Manifest: {MANIFEST_PATH.relative_to(ROOT)}")
    print(f"Source:   {source}")
    print(f"Quartile: {quartile}")
    print()
    print(f"Records needed:  {n_needed}")
    print(f"Records present: {n_present}")
    print(f"Records missing: {n_missing}")
    print()

    if matched:
        print("PRESENT:")
        for entry, fname in matched:
            label = entry.get("label", entry.get("filename", fname))
            if do_verify and fname in validations:
                v = validations[fname]
                tag = "valid .AT2" if v["valid"] else "INVALID"
            else:
                tag = "found"
            print(f"  + {fname:<40s} ({label}, {tag})")
        print()

    if do_verify:
        # Report validation details for invalid files
        invalids = [v for v in validations.values() if not v["valid"]]
        if invalids:
            print("VALIDATION ERRORS:")
            for v in invalids:
                print(f"  ! {v['filename']}:")
                for err in v["errors"]:
                    print(f"      {err}")
            print()

    if missing:
        print("MISSING (download from {source}):")
        rsn_list = []
        for entry in missing:
            rsn = entry.get("rsn")
            fname = entry.get("filename", "")
            label = entry.get("label", "")
            if rsn:
                rsn_list.append(str(rsn))
                print(f"  x RSN{rsn:<8s} — {label or 'Search in PEER database'}")
            else:
                print(f"  x {fname:<12s} — {label or 'Search in PEER database'}")
        print()

        print("DOWNLOAD INSTRUCTIONS:")
        print(f"  1. Go to {PEER_URL}")
        if rsn_list:
            print(f"  2. Search for RSN: {', '.join(rsn_list)}")
        else:
            print(f"  2. Search for the filenames listed above")
        print("  3. Add to cart -> Download ZIP")
        print(f"  4. Unzip .AT2 files into {RECORDS_DIR.relative_to(ROOT)}/")
        print("  5. Run: python3 tools/fetch_benchmark.py --verify")
        print()

    print("====================================")

    if n_missing > 0:
        sys.exit(1)
    sys.exit(0)


def cmd_scan():
    """List all .AT2 files found in db/excitation/records/."""
    files = scan_records()
    print(f"=== SCAN: {RECORDS_DIR.relative_to(ROOT)} ===")
    if not files:
        print("No .AT2 files found.")
    else:
        print(f"Found {len(files)} record(s):\n")
        for fp in files:
            size_kb = fp.stat().st_size / 1024
            print(f"  {fp.name:<45s} ({size_kb:6.1f} KB)")
    print("=" * 42)


def cmd_verify_all():
    """Validate all .AT2 files in records directory."""
    files = scan_records()
    print(f"=== VERIFY: {RECORDS_DIR.relative_to(ROOT)} ===")
    if not files:
        print("No .AT2 files to verify.")
        print("=" * 42)
        return

    n_valid = 0
    n_invalid = 0
    for fp in files:
        v = validate_at2(fp)
        if v["valid"]:
            npts = v["npts"] or "?"
            dt = f"{v['dt']:.5f}" if v["dt"] else "?"
            print(f"  + {fp.name:<40s} VALID  (NPTS={npts}, DT={dt})")
            n_valid += 1
        else:
            print(f"  ! {fp.name:<40s} INVALID")
            for err in v["errors"]:
                print(f"      {err}")
            n_invalid += 1

    print()
    print(f"Valid: {n_valid}  Invalid: {n_invalid}  Total: {len(files)}")
    print("=" * 42)


def cmd_update_manifest():
    """Update manifest.yaml with records found on disk."""
    if not HAS_YAML:
        print("ERROR: PyYAML not installed.  pip install pyyaml")
        sys.exit(2)

    manifest = load_manifest()
    if manifest is None:
        print(f"Creating new manifest at {MANIFEST_PATH.relative_to(ROOT)}")
        manifest = {"excitation": {}}

    files = scan_records()
    present = []
    for fp in files:
        v = validate_at2(fp)
        entry = {
            "filename": fp.name,
            "valid": v["valid"],
        }
        if v["npts"]:
            entry["npts"] = v["npts"]
        if v["dt"]:
            entry["dt"] = v["dt"]
        present.append(entry)

    manifest.setdefault("excitation", {})
    manifest["excitation"]["records_present"] = present

    MANIFEST_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(MANIFEST_PATH, "w") as f:
        yaml.dump(manifest, f, default_flow_style=False, sort_keys=False)

    print(f"=== MANIFEST UPDATED ===")
    print(f"File: {MANIFEST_PATH.relative_to(ROOT)}")
    print(f"Records present: {len(present)}")
    for entry in present:
        tag = "valid" if entry["valid"] else "INVALID"
        print(f"  {entry['filename']:<40s} ({tag})")
    print("========================")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Verify and manage ground motion records against db/manifest.yaml."
    )
    parser.add_argument(
        "--verify", action="store_true",
        help="Validate .AT2 file headers for PEER format compliance."
    )
    parser.add_argument(
        "--scan", action="store_true",
        help="List all .AT2 files found in db/excitation/records/."
    )
    parser.add_argument(
        "--update-manifest", action="store_true",
        help="Update manifest.yaml excitation.records_present with found records."
    )
    args = parser.parse_args()

    # Ensure records directory exists
    RECORDS_DIR.mkdir(parents=True, exist_ok=True)

    if args.scan:
        cmd_scan()
    elif args.update_manifest:
        cmd_update_manifest()
    elif args.verify:
        # Standalone verify (no manifest comparison)
        cmd_verify_all()
    else:
        # Default: status report (optionally with verification)
        cmd_status(do_verify=False)


if __name__ == "__main__":
    main()
