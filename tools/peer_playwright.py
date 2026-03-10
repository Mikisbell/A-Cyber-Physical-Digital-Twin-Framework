#!/usr/bin/env python3
"""
PEER NGA-West2 Downloader via Playwright (headless Chromium)
=============================================================
Uses a real browser to navigate PEER's JavaScript-heavy interface.
This is the only reliable way to automate PEER downloads since the
AT2 download links are rendered dynamically via React/JS.

Requirements:
    pip install playwright
    playwright install chromium

Usage:
    python3 tools/peer_playwright.py --rsn 766
    python3 tools/peer_playwright.py --rsn 766 1158 4517

Credentials from .env (gitignored):
    PEER_EMAIL=your@email.com
    PEER_PASSWORD=yourpassword
"""

import argparse
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_OUT = ROOT / "db" / "excitation" / "records"

PEER_BASE = "https://ngawest2.berkeley.edu"


def load_credentials() -> tuple[str, str]:
    env_path = ROOT / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if "=" in line and not line.startswith("#"):
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())
    email = os.environ.get("PEER_EMAIL", "")
    password = os.environ.get("PEER_PASSWORD", "")
    if not email or not password:
        print("ERROR: Set PEER_EMAIL and PEER_PASSWORD in .env", file=sys.stderr)
        sys.exit(1)
    return email, password


def download_records_playwright(
    rsns: list[int],
    out_dir: Path = DEFAULT_OUT,
    verbose: bool = True,
) -> dict[int, list[Path]]:
    """Download AT2 records using Playwright headless browser."""
    try:
        from playwright.sync_api import sync_playwright, TimeoutError as PWTimeout
    except ImportError:
        print(
            "ERROR: playwright not installed.\n"
            "  pip install playwright && playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(1)

    email, password = load_credentials()
    out_dir.mkdir(parents=True, exist_ok=True)
    results: dict[int, list[Path]] = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(accept_downloads=True)
        page = ctx.new_page()

        # ----- LOGIN -----
        if verbose:
            print(f"[PEER] Navigating to login page…")
        page.goto(f"{PEER_BASE}/members/sign_in", timeout=90_000)
        page.fill("input#member_email", email)
        page.fill("input#member_password", password)
        page.click("input[name='commit']")
        page.wait_for_load_state("networkidle", timeout=30_000)

        if "sign_in" in page.url and "Invalid" in page.content():
            print("ERROR: PEER login failed — invalid credentials", file=sys.stderr)
            browser.close()
            return {rsn: [] for rsn in rsns}

        if verbose:
            print(f"[PEER] Login successful (at {page.url})")

        # ----- DOWNLOAD EACH RSN -----
        for rsn in rsns:
            rsn_files: list[Path] = []

            # Skip if already downloaded
            existing = (
                list(out_dir.glob(f"RSN{rsn}_*.AT2"))
                + list(out_dir.glob(f"RSN{rsn}.AT2"))
            )
            if existing:
                if verbose:
                    print(f"[PEER] RSN{rsn}: already downloaded, skipping")
                results[rsn] = existing
                continue

            if verbose:
                print(f"[PEER] RSN{rsn}: searching…")

            try:
                # Navigate to spectras/new with RSN — this is the per-record page
                page.goto(
                    f"{PEER_BASE}/spectras/new?sourceDb_flag=1&rsn={rsn}",
                    timeout=60_000,
                )
                page.wait_for_load_state("networkidle", timeout=20_000)

                # Find download links/buttons for AT2 files
                # PEER renders these as <a> tags with .AT2 in href, or download buttons
                at2_links = page.evaluate("""
                    () => {
                        const links = [];
                        document.querySelectorAll('a').forEach(a => {
                            const h = (a.href || '').toLowerCase();
                            const t = (a.textContent || '').toLowerCase();
                            if (h.includes('.at2') || h.includes('download') ||
                                t.includes('at2') || t.includes('download')) {
                                links.push({href: a.href, text: a.textContent.trim()});
                            }
                        });
                        return links;
                    }
                """)

                if verbose:
                    print(f"[PEER] RSN{rsn}: found {len(at2_links)} potential links")
                    for lnk in at2_links[:5]:
                        print(f"  → {lnk}")

                # Click download buttons or follow AT2 links
                for lnk in at2_links[:3]:
                    href = lnk.get("href", "")
                    if not href or href == page.url:
                        continue
                    try:
                        with page.expect_download(timeout=60_000) as dl_info:
                            page.goto(href, timeout=30_000)
                        download = dl_info.value
                        fname = download.suggested_filename or f"RSN{rsn}.AT2"
                        dest = out_dir / fname
                        download.save_as(dest)
                        if verbose:
                            print(f"[PEER] RSN{rsn}: saved {fname} ({dest.stat().st_size//1024}KB)")
                        rsn_files.append(dest)
                    except PWTimeout:
                        pass
                    except Exception as exc:
                        if verbose:
                            print(f"[PEER] RSN{rsn}: link error: {exc}")
                    if rsn_files:
                        break

                if not rsn_files:
                    # Try selecting all records and downloading ZIP
                    try:
                        dl_btn = page.locator(
                            "button:has-text('Download'), a:has-text('Download'), "
                            "input[value*='Download']"
                        ).first
                        if dl_btn.is_visible():
                            with page.expect_download(timeout=120_000) as dl_info:
                                dl_btn.click()
                            download = dl_info.value
                            fname = download.suggested_filename or f"RSN{rsn}.zip"
                            tmp = out_dir / fname
                            download.save_as(tmp)
                            if fname.lower().endswith(".zip"):
                                from tools.peer_downloader import _extract_zip
                                rsn_files = _extract_zip(tmp, out_dir, rsn)
                                tmp.unlink(missing_ok=True)
                            else:
                                rsn_files = [tmp]
                            if verbose:
                                print(f"[PEER] RSN{rsn}: downloaded via button → {[f.name for f in rsn_files]}")
                    except Exception as exc:
                        if verbose:
                            print(f"[PEER] RSN{rsn}: button download failed: {exc}")

            except PWTimeout:
                if verbose:
                    print(f"[PEER] RSN{rsn}: page timeout")
            except Exception as exc:
                if verbose:
                    print(f"[PEER] RSN{rsn}: ERROR — {exc}")

            if not rsn_files:
                print(
                    f"[PEER] RSN{rsn}: automatic download failed.\n"
                    f"  Manual: {PEER_BASE}/spectras/new?sourceDb_flag=1&rsn={rsn}"
                )

            results[rsn] = rsn_files
            time.sleep(1)

        browser.close()

    return results


def main() -> None:
    p = argparse.ArgumentParser(
        description="Download PEER NGA-West2 AT2 records via Playwright"
    )
    p.add_argument("--rsn", nargs="+", type=int, required=True)
    p.add_argument("--out", type=Path, default=DEFAULT_OUT)
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args()

    results = download_records_playwright(args.rsn, args.out, verbose=not args.quiet)
    print("\n=== PEER Playwright Summary ===")
    total = 0
    for rsn, files in results.items():
        if files:
            print(f"  RSN{rsn}: {len(files)} file(s) → {', '.join(f.name for f in files)}")
            total += len(files)
        else:
            print(f"  RSN{rsn}: FAILED — {PEER_BASE}/spectras/new?sourceDb_flag=1&rsn={rsn}")
    print(f"Total: {total} .AT2 file(s) → {args.out}")


if __name__ == "__main__":
    main()
