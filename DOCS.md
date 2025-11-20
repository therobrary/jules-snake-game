# Documentation

## Setup and Running

This game is a standalone web application contained within a single HTML file. This makes it incredibly easy to run without any complex build steps or server requirements.

### Prerequisites

- A modern web browser (Chrome, Firefox, Safari, Edge, etc.).

### How to Run

1.  **Download**: Clone this repository.
2.  **Open**: Double-click `docs/index.html` to open it in your default web browser.
3.  **Play**: Follow the on-screen instructions to start the game.

## GitHub Pages Deployment

This repository is configured to serve the game using **GitHub Pages** from the `/docs` folder.

1. Go to your repository **Settings**.
2. Navigate to the **Pages** section.
3. Under **Build and deployment** > **Source**, select **Deploy from a branch**.
4. Under **Branch**, select `main` and then select `/docs` folder.
5. Click **Save**.

The game will be available at `https://<your-username>.github.io/<repo-name>/`.

## Cloudflare Pages Deployment

This project is fully compatible with **Cloudflare Pages** as a static site.

1. **Log in** to the [Cloudflare Dashboard](https://dash.cloudflare.com/) and go to **Workers & Pages**.
2. Click **Create Application** > **Pages** > **Connect to Git**.
3. Select this repository.
4. **Build Settings**:
   - **Framework preset**: `None`
   - **Build command**: *(Leave blank)*
   - **Build output directory**: `docs`
5. Click **Save and Deploy**.

### Resetting High Score

To reset your high score:
1. Open the game in your browser.
2. Open the Developer Tools (usually F12 or Ctrl+Shift+I).
3. Go to the "Application" tab (or "Storage" in Firefox).
4. Clear the "Local Storage" for the file.
5. Refresh the page.

## Automated Testing

The repository includes an automated test suite using **Playwright** to verify game functionality.

### Prerequisites
- Python 3.x
- Playwright (`pip install playwright` and `playwright install`)

### Running Tests

1. Start a local web server in the project root:
   ```bash
   python3 -m http.server 8000
   ```

2. Run the test script:
   ```bash
   python3 tests/test_snake.py
   ```

The test will verify the Start Screen, Gameplay movement, Wrap-around logic, and High Score persistence. Screenshots of the test run will be saved in the `tests/` directory.
