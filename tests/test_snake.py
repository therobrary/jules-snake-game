"""
Automated Playwright Test for Snake Game

Usage:
1. Ensure the game is running on http://localhost:8000 (e.g., `python3 -m http.server 8000`)
2. Run this script: `python3 tests/test_snake.py`

This script verifies:
- Start screen elements
- Gameplay initialization
- Wrap-around movement logic
- Game Over state and high score persistence
"""

import time
from playwright.sync_api import sync_playwright, expect

def test_snake_game():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        print("Loading game...")
        page.goto("http://localhost:8000/docs/index.html")

        # --- Test 1: Start Screen Verification ---
        print("Verifying Start Screen...")
        expect(page.get_by_text("Serpent", exact=True)).to_be_visible()
        expect(page.get_by_text("INITIATE")).to_be_visible()
        page.screenshot(path="tests/screenshot_01_start_screen.png")
        print("Start Screen verified and screenshot taken.")

        # --- Test 2: Gameplay and Movement ---
        print("Starting Game...")
        page.get_by_text("INITIATE").click()
        time.sleep(0.5) # Wait for game to run a bit

        # Check score is 0 initially
        score = page.evaluate("window.score")
        assert score == 0, f"Expected initial score 0, got {score}"

        # Move around
        page.keyboard.press("d") # Right
        time.sleep(0.2)
        page.keyboard.press("s") # Down
        time.sleep(0.2)

        page.screenshot(path="tests/screenshot_02_gameplay.png")
        print("Gameplay verified and screenshot taken.")

        # --- Test 3: Wrap Around Logic ---
        print("Testing Wrap Around...")
        # Inject state: Place snake at the right edge facing right
        page.evaluate("""
            window.game.snake = [{x: window.game.tileCountX - 1, y: 10}];
            window.game.dx = 1; window.game.dy = 0;
        """)
        # Wait for roughly one/two game ticks (gameSpeed is ~120ms)
        time.sleep(0.15)

        # Check snake head position. Should be 0 (wrapped) or 1 (wrapped + moved)
        head_x = page.evaluate("window.game.snake[0].x")
        assert head_x == 0 or head_x == 1, f"Expected snake to wrap to 0 or 1, but got {head_x}"
        print("Wrap around logic verified.")

        # --- Test 4: Speed Increase Verification ---
        print("Testing Speed Increase...")
        # Reset state: snake near food
        page.evaluate("""
            window.game.snake = [{x: 10, y: 10}];
            window.game.food = {x: 11, y: 10, type: 'regular', color: '#ffffff', value: 10, glow: 10};
            window.game.dx = 1; window.game.dy = 0;
            window.game.gameSpeed = 100; // Reset speed
        """)

        # Wait for collision/eating
        time.sleep(0.3)

        # Check if speed decreased (gameSpeed < 100)
        new_speed = page.evaluate("window.gameSpeed")
        assert new_speed < 100, f"Expected gameSpeed to decrease below 100, but got {new_speed}"
        print(f"Speed increase verified. New speed: {new_speed}ms")

        # --- Test 5: New High Score Entry ---
        print("Testing New High Score Entry...")

        # Pause the game to prevent score changes from the game loop
        page.evaluate("window.game.state = 2")  # STATE.PAUSED = 2

        # Set a score higher than current high score (0)
        page.evaluate("window.game.score = 500")
        page.evaluate("window.game.updateHUD()")

        # Force game over
        page.evaluate("window.triggerGameOver()")
        time.sleep(0.5)

        # Should see "MISSION FAILED" and high score input
        expect(page.get_by_text("MISSION FAILED")).to_be_visible()

        # Enter initials
        page.fill("#hs-input", "ACE")
        page.keyboard.press("Enter")
        time.sleep(0.5)

        # Should now see updated leaderboard
        expect(page.get_by_text("ACE")).to_be_visible()

        # Take screenshot
        page.screenshot(path="tests/screenshot_03_high_score.png")
        print("High score entry verified and screenshot taken.")

        # Check localStorage
        stored = page.evaluate("JSON.parse(localStorage.getItem('snakeLeaderboard') || '[]')")
        assert len(stored) >= 1, "Expected at least 1 leaderboard entry"
        assert stored[0]['score'] == 500, f"Expected score 500, got {stored[0]['score']}"
        assert stored[0]['name'] == 'ACE', f"Expected name ACE, got {stored[0]['name']}"
        print("Persistence verified.")

        browser.close()
        print("All tests passed!")

if __name__ == "__main__":
    try:
        test_snake_game()
    except Exception as e:
        print(f"Test failed: {e}")
        exit(1)
