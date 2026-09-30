#!/usr/bin/env python3
"""
Devex funding scraper — Last 24h variant.

Uses StealthySession for anti-bot bypass + persistent browser profile so
authentication survives between runs.

The Devex funding page is a split view:
  left  → list of report-result items (20 per page)
  right → detail panel that updates in-place when an item is clicked

No page.go_back() is needed between items. After all 20 are processed,
the next-page button advances the left panel to the next batch.

Usage:
    python scraper.py

Environment variables (all optional — defaults match json.js):
    DEVEX_EMAIL        Login email           (default: )
    DEVEX_PASSWORD     Login password        (default: )
    DEVEX_TARGET_URL   Funding search URL    (default: video/photo/film… tenders+grants)
    HEADLESS           'true' = hidden browser (default: false — visible for first login)
    DELAY_MS           Delay between pages ms (default: 2000)
    TIMEOUT_MS         Playwright timeout ms  (default: 30000)
    MAX_PAGES          Stop after N pages, 0=unlimited (default: 100)
    TIME_FILTER        'false' to skip Last-24h filter (default: true)
    REAL_CHROME        'true' to use installed Chrome (default: false)
"""

import json
import os
import re
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import Page
from scrapling.fetchers import StealthySession
from scrapling.parser import Selector

load_dotenv()

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
CONFIG = {
    'email': os.getenv('DEVEX_EMAIL', ''),
    'password': os.getenv('DEVEX_PASSWORD', ''),
    'target_url': os.getenv(
        'DEVEX_TARGET_URL',
        (
"https://www.devex.com/funding/r?
        ),
    ),
    'headless': os.getenv('HEADLESS', 'false').lower() == 'true',
    'delay_ms': int(os.getenv('DELAY_MS', '3000')),
    'timeout_ms': int(os.getenv('TIMEOUT_MS', '30000')),
    'max_pages': int(os.getenv('MAX_PAGES', '100')),
    'apply_time_filter': os.getenv('TIME_FILTER', 'true').lower() != 'false',
    'real_chrome': os.getenv('REAL_CHROME', 'false').lower() == 'true',
}

USER_DATA_DIR = str(Path(__file__).parent / 'secrets' / 'browser-profile')
OUTPUT_PATH   = Path(__file__).parent / 'data' / 'scrape-results.json'

PAGINATION_SELECTORS = [
    '.next-button-link',
    'a.next_page',
    '.pagination .next a',
    "a[rel='next']",
    'li.next > a',
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def extract_report_id(url: str) -> str | None:
    m = re.search(r'report=([^&]+)', url)
    return m.group(1) if m else None


def has_captcha(page: Page) -> bool:
    try:
        return page.locator('iframe[src*="captcha-delivery.com"]').count() > 0
    except Exception:
        return False


def dismiss_session_popup(page: Page) -> None:
    """Dismiss any 'active session' or confirmation modal that Devex shows after login."""
    try:
        # Try Escape first — works for most modal implementations
        page.keyboard.press('Escape')
        page.wait_for_timeout(500)
    except Exception:
        pass

    try:
        btn = page.locator(
            # Common X / close button patterns
            'button.close, '
            'button.btn-close, '
            'button.modal-close, '
            '.modal .close, '
            '.modal .btn-close, '
            '.modal button[aria-label="Close"], '
            '.modal button[aria-label="close"], '
            '.modal button[aria-label="Dismiss"], '
            '[role="dialog"] .close, '
            '[role="dialog"] .btn-close, '
            '[role="dialog"] button[aria-label="Close"], '
            '[role="dialog"] button[aria-label="close"], '
            '[role="dialog"] button[aria-label="Dismiss"], '
            # Buttons with × or ✕ symbol
            'button:has-text("×"), '
            'button:has-text("✕"), '
            'button:has-text("✖"), '
            # Text-based dismiss buttons
            '.modal button:has-text("Continue"), '
            '.modal button:has-text("OK"), '
            '.modal button:has-text("Got it"), '
            '[role="dialog"] button:has-text("Continue"), '
            '[role="dialog"] button:has-text("OK"), '
            '[role="dialog"] button:has-text("Got it")'
        ).first
        if btn.count() > 0:
            btn.click()
            page.wait_for_timeout(1000)
            print('Session popup dismissed')
    except Exception:
        pass


def dismiss_toast_notification(page: Page) -> None:
    """Dismiss the Devex concurrent-login alert banner (#alerts-container)."""
    try:
        btn = page.locator('#alerts-container button.dismiss-alert').first
        if btn.count() > 0 and btn.is_visible():
            btn.click()
            page.wait_for_timeout(500)
            print('Concurrent-login alert dismissed')
    except Exception:
        pass


# ---------------------------------------------------------------------------
# Page actions
# ---------------------------------------------------------------------------
def make_scrape_action(config: dict, results: list, processed_ids: set, errors: list):
    """
    Passed to session.fetch(TARGET_URL).
    The browser lands on TARGET_URL — the funding search page — which also
    carries the sign-in button. Auth is handled here before scraping begins.

    Split-view logic:
      - Left panel: list of report-result elements (20 per page)
      - Right panel: #detail updates in-place when an item is clicked
      - No go_back() needed — just click the next item directly
      - After all 20 items, click the next-page button and repeat
    """
    def scrape_action(page: Page):
        page.wait_for_load_state('domcontentloaded')
        page.wait_for_timeout(2000)

        # ---- Auth ----------------------------------------------------------
        if has_captcha(page):
            print('⚠️  CAPTCHA detected — solve it in the browser window (up to 5 min)')
            page.wait_for_selector('.user-menu-toggle-btn', timeout=300_000)
            print('✅ CAPTCHA resolved\n')

        if page.locator('.user-menu-toggle-btn').count() == 0:
            print('Not logged in — signing in...')

            # Dismiss the concurrent-login banner before it blocks the sign-in button
            dismiss_toast_notification(page)

            # Sometimes the form is shown inline
            email_field = page.locator(
                '#user_email, input[name="email"], input[type="email"]'
            ).first
            if email_field.count() > 0:
                email_field.fill(config['email'])
                page.locator(
                    '#user_password, input[name="password"], input[type="password"]'
                ).first.fill(config['password'])
                page.locator(
                    'input[type="submit"], button[type="submit"], .btn-primary'
                ).first.click()
            else:
                # Click the sign-in button to open the modal
                sign_in = page.locator(
                    '[data-testid="header-sign-in-button"], '
                    'a[href*="sign_in"], a[href*="login"], '
                    'a:has-text("Sign in"), button:has-text("Sign in")'
                ).first
                sign_in.click()
                dismiss_toast_notification(page)
                page.wait_for_selector('input[type="email"]', state='visible')
                page.locator('input[name="email"], input[type="email"]').first.fill(config['email'])
                page.locator('input[name="password"], input[type="password"]').first.fill(config['password'])
                page.get_by_role('button', name='Sign in', exact=True).click()

            page.wait_for_selector('.user-menu-toggle-btn', timeout=config['timeout_ms'])
            page.wait_for_timeout(1500)
            dismiss_session_popup(page)
            dismiss_toast_notification(page)
            print('Authenticated\n')
        else:
            print('Already logged in\n')

        # Dismiss any leftover popup/toast before interacting with the page
        dismiss_session_popup(page)
        dismiss_toast_notification(page)
        page.wait_for_selector('report-result', state='attached', timeout=config['timeout_ms'])

        # Optional: narrow results to Last month
        if config['apply_time_filter']:
            try:
                toggle = page.locator('.btn-time > .btn').first
                if toggle.count() > 0:
                    toggle.click()
                    option = page.locator('.btn-time li').filter(has_text='Last 24h').first
                    option.wait_for(state='visible', timeout=5000)
                    option.click()
                    page.wait_for_timeout(2000)
                    n = page.locator('report-result').count()
                    if n == 0:
                        print('⚠️  No results after Last 24h filter — continuing without it')
                    else:
                        print(f'Time filter applied (Last 24h) — {n} results\n')
            except Exception as e:
                print(f'Time filter skipped ({e})\n')

        current_page   = 1
        total_visited  = 0

        while True:
            print(f'========== PAGE {current_page} ==========')
            page.wait_for_selector('report-result', state='attached', timeout=config['timeout_ms'])
            items      = page.locator('report-result')
            item_count = items.count()
            print(f'Items: {item_count}\n')
            if item_count == 0:
                break

            for i in range(item_count):
                total_visited += 1
                print(f'[{total_visited}] Item {i + 1}/{item_count}')
                try:
                    item = items.nth(i)
                    item.wait_for(state='visible', timeout=10_000)
                    item.click()

                    # Right panel updates in-place — just wait for #detail
                    page.wait_for_selector('#detail', state='attached', timeout=config['timeout_ms'])
                    page.wait_for_timeout(1500)
                    dismiss_toast_notification(page)

                    report_id = extract_report_id(page.url)
                    if not report_id:
                        print(f'  ⚠️  No report= in URL: {page.url}')
                        continue
                    if report_id in processed_ids:
                        print(f'  Skip duplicate: {report_id}')
                        continue
                    processed_ids.add(report_id)

                    data: dict = {
                        'id':         report_id,
                        'url':        f'https://www.devex.com/funding/r?report={report_id}',
                        'scraped_at': datetime.now(timezone.utc).isoformat(),
                    }

                    # Use Scrapling's adaptive parser so extraction survives
                    # CSS class renames (auto_save fingerprints the element;
                    # adaptive=True relocates it by fingerprint if selector breaks).
                    try:
                        html      = page.content()
                        page_sel  = Selector(html, adaptive=True, url='www.devex.com')
                        content_el = page_sel.css('.paywalled-content', auto_save=True)
                        if not content_el:
                            content_el = page_sel.css('.paywalled-content', adaptive=True)
                        if content_el:
                            data['content'] = content_el.get()
                    except Exception as ce:
                        errors.append({'id': report_id, 'error': str(ce)})
                        print(f'  Content error: {ce}')

                    results.append(data)
                    print(f'  ✓ {report_id}')

                except Exception as e:
                    print(f'  Error on item {i + 1}: {e}')
                    errors.append({'page': current_page, 'index': i, 'error': str(e)})

            # ---- Pagination ------------------------------------------------
            if config['max_pages'] > 0 and current_page >= config['max_pages']:
                print('\nMax pages reached')
                break

            advanced = False
            for sel in PAGINATION_SELECTORS:
                try:
                    btn = page.locator(sel).first
                    if btn.count() == 0:
                        continue
                    disabled = btn.evaluate(
                        '(el) => el.classList.contains("disabled") '
                        '     || el.hasAttribute("disabled") '
                        '     || (el.parentElement && el.parentElement.classList.contains("disabled"))'
                    )
                    if disabled:
                        print('Next button disabled — end of results')
                        break
                    btn.click()
                    page.wait_for_timeout(2000)
                    page.wait_for_selector(
                        'report-result', state='attached', timeout=config['timeout_ms']
                    )
                    current_page += 1
                    print(f'\n→ Page {current_page} loaded')
                    advanced = True
                    break
                except Exception:
                    continue

            if not advanced:
                print('No next page — done')
                break

            page.wait_for_timeout(config['delay_ms'])

        print(f'\n========== SUMMARY ==========')
        print(f'Pages scraped : {current_page}')
        print(f'Items visited : {total_visited}')
        print(f'Unique results: {len(processed_ids)}')
        if errors:
            print(f'Errors        : {len(errors)}')

    return scrape_action


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def main() -> None:
    results:       list[dict] = []
    processed_ids: set[str]   = set()
    errors:        list[dict] = []

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    Path(USER_DATA_DIR).mkdir(parents=True, exist_ok=True)

    print(f'Headless     : {CONFIG["headless"]}')
    print(f'Real Chrome  : {CONFIG["real_chrome"]}')
    print(f'Time filter  : {CONFIG["apply_time_filter"]}')
    print(f'Max pages    : {CONFIG["max_pages"]}')
    print(f'Profile dir  : {USER_DATA_DIR}\n')

    with StealthySession(
        headless=CONFIG['headless'],
        user_data_dir=USER_DATA_DIR,
        timeout=CONFIG['timeout_ms'],
        real_chrome=CONFIG['real_chrome'],
    ) as session:

        # Navigate directly to the funding search URL — the sign-in button
        # lives on that page, so auth and scraping happen in one shot.
        session.fetch(
            CONFIG['target_url'],
            page_action=make_scrape_action(CONFIG, results, processed_ids, errors),
        )

    OUTPUT_PATH.write_text(json.dumps(results, indent=2, ensure_ascii=False))
    print(f'\nSaved {len(results)} results → {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
