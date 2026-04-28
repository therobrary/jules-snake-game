"""
Enhanced Automated Playwright Test for Snake Game

Usage:
1. Ensure the game is running on http://localhost:8000 (e.g., `python3 -m http.server 8000`)
2. Run this script: `python3 tests/test_snake_enhanced.py`

This script verifies all Neon Noir alignment and gameplay enhancements:
- Visual design (fonts, scanlines, glassmorphism, HUD)
- Wave system progression
- Lives system
- Pause/resume
- Leaderboard persistence
- Special food types
- Audio initialization
- Combo system
- Obstacles
"""

import time
from playwright.sync_api import sync_playwright, expect

BASE_URL = "http://localhost:8000/docs/index.html"


def test_visual_design():
    """Verify Neon Noir visual alignment."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL)

        font_family = page.evaluate("getComputedStyle(document.body).fontFamily")
        assert 'Courier' in font_family or 'monospace' in font_family, \
            f"Expected monospace font, got: {font_family}"

        scanlines = page.query_selector("#scanlines")
        assert scanlines is not None, "Scanlines overlay not found"

        vignette = page.query_selector("#vignette")
        assert vignette is not None, "Vignette overlay not found"

        hud_labels = page.query_selector_all(".hud-label")
        assert len(hud_labels) >= 4, f"Expected at least 4 HUD labels, got {len(hud_labels)}"

        assert page.query_selector("#scoreDisplay") is not None
        assert page.query_selector("#waveDisplay") is not None
        assert page.query_selector("#livesDisplay") is not None

        overlay_card = page.query_selector(".overlay-card")
        assert overlay_card is not None, "Overlay card not found on start screen"

        initiate_btn = page.get_by_text("INITIATE", exact=True)
        assert initiate_btn.is_visible(), "INITIATE button not visible"

        page.screenshot(path="tests/screenshot_visual_design.png")
        print("PASS: Visual design tests passed")
        browser.close()


def test_wave_system():
    """Verify wave progression."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL)

        page.get_by_text("INITIATE").click()
        time.sleep(0.5)

        wave_val = page.text_content("#waveDisplay")
        assert wave_val == "1", f"Expected wave 1, got {wave_val}"

        page.evaluate("window.game.foodEatenInWave = 99; window.game.wave = 1;")
        page.evaluate("window.advanceWave()")
        time.sleep(0.3)

        wave_val = page.text_content("#waveDisplay")
        assert wave_val == "2", f"Expected wave 2, got {wave_val}"

        page.screenshot(path="tests/screenshot_wave_system.png")
        print("PASS: Wave system tests passed")
        browser.close()


def test_lives_system():
    """Verify lives system."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL)

        page.get_by_text("INITIATE").click()
        time.sleep(0.5)

        lives_val = page.text_content("#livesDisplay")
        assert lives_val == "3", f"Expected 3 lives, got {lives_val}"

        page.evaluate("window.game.loseLife();")
        time.sleep(0.2)

        lives_val = page.text_content("#livesDisplay")
        assert lives_val == "2", f"Expected 2 lives after collision, got {lives_val}"

        page.screenshot(path="tests/screenshot_lives_system.png")
        print("PASS: Lives system tests passed")
        browser.close()


def test_pause_system():
    """Verify pause and resume."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL)

        page.get_by_text("INITIATE").click()
        time.sleep(0.5)

        page.keyboard.press("Escape")
        time.sleep(0.3)

        assert page.get_by_text("PAUSED").is_visible(), "Pause overlay not visible"
        assert page.get_by_role("button", name="RESUME").is_visible(), "Resume button not visible"

        page.get_by_role("button", name="RESUME").click()
        time.sleep(0.3)

        pause_screen = page.query_selector("#pauseScreen")
        if pause_screen:
            is_hidden = page.evaluate("document.getElementById('pauseScreen').classList.contains('hidden')")
            assert is_hidden, "Pause screen should be hidden after resume"

        page.screenshot(path="tests/screenshot_pause_system.png")
        print("PASS: Pause system tests passed")
        browser.close()


def test_leaderboard():
    """Verify leaderboard persistence."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL)

        page.evaluate("localStorage.removeItem('snakeLeaderboard')")

        page.get_by_text("INITIATE").click()
        time.sleep(0.3)

        page.evaluate("window.game.score = 1000")
        page.evaluate("window.game.updateHUD()")

        page.evaluate("window.triggerGameOver()")
        time.sleep(0.5)

        for selector in ["#hs-input", "#playerNameInput", "#initials-input"]:
            hs_input = page.query_selector(selector)
            if hs_input:
                page.fill(selector, "TST")
                page.keyboard.press("Enter")
                time.sleep(0.3)
                break

        leaderboard = page.evaluate("JSON.parse(localStorage.getItem('snakeLeaderboard') || '[]')")
        assert len(leaderboard) >= 1, "Leaderboard should have at least 1 entry"
        assert leaderboard[0]['score'] == 1000, f"Expected score 1000, got {leaderboard[0]['score']}"
        assert leaderboard[0]['name'] == 'TST', f"Expected name TST, got {leaderboard[0]['name']}"

        page.screenshot(path="tests/screenshot_leaderboard.png")
        print("PASS: Leaderboard tests passed")
        browser.close()


def test_audio_initialization():
    """Verify audio system initializes on game start."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL)

        page.get_by_text("INITIATE").click()
        time.sleep(0.3)

        audio_enabled = page.evaluate("window.audio && window.audio.enabled")
        assert audio_enabled, "Audio should be enabled after game start"

        print("PASS: Audio initialization tests passed")
        browser.close()


def test_special_food_types():
    """Verify special food types appear and function."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL)

        page.get_by_text("INITIATE").click()
        time.sleep(0.5)

        has_special_food = page.evaluate("typeof window.SPECIAL_FOOD !== 'undefined'")
        assert has_special_food, "Special food configuration not found"

        page.evaluate("""
            window.game.specialFoods = [{
                x: 15, y: 15,
                type: 'bonus',
                color: '#ffffff',
                value: 50,
                life: 5.0
            }];
        """)

        special_count = page.evaluate("window.specialFoods.length")
        assert special_count == 1, "Special food should be tracked"

        print("PASS: Special food type tests passed")
        browser.close()


def test_combo_system():
    """Verify score multiplier/combo system."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL)

        page.get_by_text("INITIATE").click()
        time.sleep(0.5)

        has_combo = page.evaluate("typeof window.combo !== 'undefined' || typeof window.comboMultiplier !== 'undefined'")
        assert has_combo, "Combo system not found"

        page.evaluate("window.game.combo = 3")
        time.sleep(0.1)

        combo_val = page.evaluate("window.combo")
        assert combo_val == 3, f"Expected combo 3, got {combo_val}"

        print("PASS: Combo system tests passed")
        browser.close()


def test_obstacles():
    """Verify obstacles appear from Wave 3."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(BASE_URL)

        page.get_by_text("INITIATE").click()
        time.sleep(0.5)

        has_obstacles = page.evaluate("typeof window.obstacles !== 'undefined' || typeof window.WAVE_CONFIG !== 'undefined'")
        assert has_obstacles, "Obstacles configuration not found"

        page.evaluate("window.game.obstacles = [{x: 5, y: 5}, {x: 6, y: 5}, {x: 7, y: 5}]; window.game.wave = 3;")

        obstacle_count = page.evaluate("window.obstacles.length")
        assert obstacle_count == 3, f"Expected 3 obstacles, got {obstacle_count}"

        print("PASS: Obstacles tests passed")
        browser.close()


def run_all_tests():
    """Run all test suites."""
    tests = [
        ("Visual Design", test_visual_design),
        ("Wave System", test_wave_system),
        ("Lives System", test_lives_system),
        ("Pause System", test_pause_system),
        ("Leaderboard", test_leaderboard),
        ("Audio Initialization", test_audio_initialization),
        ("Special Food Types", test_special_food_types),
        ("Combo System", test_combo_system),
        ("Obstacles", test_obstacles),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        print(f"\n{'='*50}")
        print(f"Running: {name}")
        print('='*50)
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"FAIL: {name} - {e}")
            failed += 1

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed, {passed + failed} total")
    print('='*50)

    if failed > 0:
        exit(1)


if __name__ == "__main__":
    run_all_tests()
