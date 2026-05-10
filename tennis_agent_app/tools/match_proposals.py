import logging
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

DEFAULT_PROPOSALS_URL = (
    "https://cary.tennis-ladder.com/season/2026/spring/mens-30/proposals"
)


def fetch_available_proposals(
    url: str = DEFAULT_PROPOSALS_URL,
    timeout_ms: int = 15_000,
) -> list[dict]:
    """
    Scrape available match proposals from the Rival Tennis Ladder website.

    Opens the proposals page in a headless browser, clicks the "Available"
    filter, and extracts each proposal card's details.

    Returns a list of dicts with keys: player, ranking, date_time, location, notes.
    """
    proposals: list[dict] = []

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        page = browser.new_page()

        try:
            logger.info("Navigating to %s", url)
            page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            page.wait_for_timeout(2_000)

            available_btn = page.query_selector('button:has-text("Available")')
            if available_btn:
                available_btn.click()
                page.wait_for_timeout(2_000)
                logger.info("Clicked 'Available' filter")
            else:
                logger.warning("'Available' filter button not found — using default view")

            container = page.query_selector('[class*="proposals"]')
            if not container:
                logger.warning("Proposals container not found on page")
                return proposals

            cards = container.query_selector_all(":scope > *")
            logger.info("Found %d available proposal cards", len(cards))

            for card in cards:
                text = card.inner_text().strip()
                lines = [line.strip() for line in text.split("\n") if line.strip()]
                if len(lines) < 2:
                    continue

                name_el = card.query_selector('[class*="_name_"] a')
                player = name_el.inner_text().strip() if name_el else lines[0]

                badge_el = card.query_selector('[class*="_badge_"]')
                ranking = badge_el.inner_text().strip() if badge_el else ""

                date_time = lines[1] if len(lines) > 1 else ""
                location = lines[2] if len(lines) > 2 else ""
                notes = lines[3] if len(lines) > 3 else ""

                proposals.append({
                    "player": player,
                    "ranking": ranking,
                    "date_time": date_time,
                    "location": location,
                    "notes": notes,
                })

        finally:
            browser.close()

    return proposals


def format_proposals(proposals: list[dict]) -> str:
    """Turn a list of proposal dicts into a human-readable summary."""
    if not proposals:
        return "No available match proposals found at this time."

    header = f"Found {len(proposals)} available match proposal(s):\n"
    lines = []
    for i, p in enumerate(proposals, 1):
        parts = [
            f"{i}. {p['player']}",
            f"   Ranking: #{p['ranking']}" if p["ranking"] else "",
            f"   When:    {p['date_time']}" if p["date_time"] else "",
            f"   Where:   {p['location']}" if p["location"] else "",
            f"   Notes:   {p['notes']}" if p["notes"] else "",
        ]
        lines.append("\n".join(part for part in parts if part))

    return header + "\n\n".join(lines)
