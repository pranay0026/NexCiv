"""
NEX-CIV Live Website Browser Automation & Visual Audit Script
Uses Playwright to audit https://nex-civ.vercel.app/ across viewports:
- Desktop: 1440x900
- Laptop: 1366x768
- Tablet: 768x1024
- Mobile: 390x844

Captures route screenshots and inspects network / console errors.
"""

import sys
import os
import json
import asyncio
from pathlib import Path
from playwright.async_api import async_playwright

BASE_URL = os.getenv("TARGET_URL", "https://nex-civ.vercel.app")
REPORT_DIR = Path("audit_reports/screenshots")
REPORT_DIR.mkdir(parents=True, exist_ok=True)

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "laptop": {"width": 1366, "height": 768},
    "tablet": {"width": 768, "height": 1024},
    "mobile": {"width": 390, "height": 844}
}

ROUTES = [
    {"path": "/", "name": "landing_page"},
    {"path": "/login", "name": "citizen_login"},
    {"path": "/department-login", "name": "department_login"},
    {"path": "/department", "name": "department_command_center"},
    {"path": "/employee", "name": "employee_workspace"},
    {"path": "/profile", "name": "citizen_profile"}
]


async def run_visual_audit():
    print("=" * 80)
    print(f"NEX-CIV PLAYWRIGHT VISUAL AUDIT: {BASE_URL}")
    print("=" * 80)

    audit_findings = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        for route in ROUTES:
            url = f"{BASE_URL}{route['path']}"
            print(f"\nAuditing Route: {route['path']} ({url})")

            for vp_name, vp in VIEWPORTS.items():
                context = await browser.new_context(
                    viewport=vp,
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
                )
                page = await context.new_page()

                console_errors = []
                page.on("console", lambda msg: console_errors.append(msg.text) if msg.type in ["error"] else None)

                failed_requests = []
                page.on("requestfailed", lambda req: failed_requests.append(f"{req.method} {req.url}: {req.failure}"))

                status_code = 200
                load_time_ms = 0
                import time
                t0 = time.time()
                try:
                    resp = await page.goto(url, wait_until="networkidle", timeout=25000)
                    if resp:
                        status_code = resp.status
                    load_time_ms = int((time.time() - t0) * 1000)
                except Exception as e:
                    print(f"  [Timeout/Note] {vp_name}: {e}")
                    load_time_ms = int((time.time() - t0) * 1000)

                # Capture Screenshot
                screenshot_filename = f"{route['name']}_{vp_name}.png"
                screenshot_path = REPORT_DIR / screenshot_filename
                try:
                    await page.screenshot(path=str(screenshot_path), full_page=False)
                    print(f"  [{vp_name.upper()} {vp['width']}x{vp['height']}] Loaded in {load_time_ms}ms -> Saved {screenshot_filename}")
                except Exception as ss_err:
                    print(f"  [{vp_name.upper()}] Screenshot note: {ss_err}")

                # Check horizontal scroll / overflow
                has_h_overflow = False
                try:
                    scroll_width = await page.evaluate("() => document.documentElement.scrollWidth")
                    client_width = await page.evaluate("() => document.documentElement.clientWidth")
                    has_h_overflow = scroll_width > (client_width + 5)
                except Exception:
                    pass

                audit_findings.append({
                    "route": route["path"],
                    "page_name": route["name"],
                    "viewport": vp_name,
                    "resolution": f"{vp['width']}x{vp['height']}",
                    "status_code": status_code,
                    "load_time_ms": load_time_ms,
                    "console_errors": console_errors[:3],
                    "failed_requests": failed_requests[:3],
                    "horizontal_overflow": has_h_overflow,
                    "screenshot": str(screenshot_path)
                })

                await context.close()

        await browser.close()

    summary_file = Path("audit_reports/visual_audit_summary.json")
    with open(summary_file, "w", encoding="utf-8") as f:
        json.dump(audit_findings, f, indent=2)
    print(f"\nVisual audit summary recorded to {summary_file}")
    return audit_findings

if __name__ == "__main__":
    asyncio.run(run_visual_audit())
