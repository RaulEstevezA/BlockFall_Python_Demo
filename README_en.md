# BlockFall · Web Demo

> [!IMPORTANT]
> **This is not the main repository of the game.**
> This repository only contains the **web demo** published on my website.
> The original desktop game (source code, gameplay video and instructions to run it) lives here:
>
> **[RaulEstevezA/BlockFall_Python](https://github.com/RaulEstevezA/BlockFall_Python)**

**Live demo:** [raulesteveza.github.io/demos/BlockFall_Python](https://raulesteveza.github.io/demos/BlockFall_Python/)

<p align="center">
  <a href="https://raulesteveza.github.io/demos/BlockFall_Python/">
    <img src="docs/images/web_demo.png" alt="BlockFall web demo running inside a macOS window" width="720">
  </a>
</p>

## What is this repository for?

BlockFall is a falling blocks game I built from scratch in Python with Pygame, designed for the desktop. To show it on my website, this repository contains an adapted copy that:

1. **Runs in the browser.** The Python code is compiled to WebAssembly with [pygbag](https://pygame-web.github.io/): it is the same game, not a JavaScript rewrite.
2. **Can be played on a phone**, with touch buttons below the board.
3. **Deploys itself**: every push to `main` runs the tests, builds the game and publishes it with GitHub Actions.

On a computer the demo is shown inside a macOS window and played with the keyboard; on a phone it runs full screen with the buttons.

## Differences from the original game

| | Original game ([BlockFall_Python](https://github.com/RaulEstevezA/BlockFall_Python)) | This demo |
|---|---|---|
| Platform | Desktop (Windows / macOS) | Browser (desktop and mobile) |
| Window | Landscape, 1300 × 800 | Portrait, 540 × 960 (phone format) |
| Controls | Keyboard | Keyboard, mouse and touch buttons |
| Main loop | Synchronous, with blocking loops on game over and key setup | Asynchronous (`asyncio`), no blocking loops, as pygbag requires |
| Library | `pygame` | `pygame-ce` (the one pygbag uses); the code works with both |

### Code changes

- **`main.py`** (formerly `tetris.py`): the game is now a `Game` class with an `async` loop that yields to the browser every frame. The game over and key setup screens no longer block the loop: they are just more game states.
- **`controls.py`** (new): D-pad, round rotate and drop buttons and a pause button, drawn with simple shapes. They support several fingers at once, repeat while held and sliding a finger from one arrow to another.
- **Hard drop** now locks the piece immediately (it used to lock on the next automatic drop step).
- **Auto pause** when switching tabs or windows.
- Board, pieces, rotation and scoring logic are the same as in the original.

## Music

The background music is **Korobeiniki**, a 19th-century Russian folk song in the public domain. No third-party recording or arrangement is used: the sound is generated from scratch by [`tool/generate_music.py`](tool/generate_music.py) (square wave for the melody, triangle wave for the bass and noise for percussion), using only the Python standard library.

```bash
python tool/generate_music.py   # regenerates music/theme.ogg (needs ffmpeg)
```

## Controls

| Action | Keyboard | Phone |
|---|---|---|
| Move | ← → | D-pad arrows (hold to repeat) |
| Soft drop | ↓ | Down arrow |
| Rotate | ↑ | Up arrow or "ROTAR" button |
| Hard drop | Space | "SOLTAR" button |
| Pause | Esc | Pause button |
| Start | Enter | Tap the screen |
| Configure keys | C (in the menu) | — |

## Structure

```
main.py                 Async main loop and game states
board.py                Board and side panel (next piece, level, score)
pieces.py               Pieces, movement and rotation
controls.py             Touch buttons
menu.py                 Menu, pause, game over and key setup
settings.py             Sizes, colours, controls and scoring
music/theme.ogg         Background music (generated)
tests/                  Headless game tests
web/template.tmpl       pygbag HTML template (loading screen and styles)
web/favicon.png         Icon
tool/build_web.sh       Web build
tool/generate_music.py  Music generator
showcase/index.html     Presentation page with the macOS window
.github/workflows/      Automatic tests, build and deployment
```

## Run locally

As a desktop game:

```bash
pip install -r requirements.txt
python main.py
```

In the browser:

```bash
pip install -r requirements-web.txt
./tool/build_web.sh --serve
# Open http://127.0.0.1:8000
```

> Open it with `127.0.0.1`, not `localhost`: on `localhost` pygbag looks for its packages on its own development server and the game does not start.

Tests:

```bash
python -m unittest discover tests
```

To see it exactly as published (page with the macOS window and the game in `app/`):

```bash
./tool/build_web.sh
mkdir -p /tmp/site/demos/BlockFall_Python
cp -R showcase/. /tmp/site/demos/BlockFall_Python/
cp -R build/blockfall/build/web /tmp/site/demos/BlockFall_Python/app
python3 -m http.server 8000 --directory /tmp/site
# Open http://127.0.0.1:8000/demos/BlockFall_Python/
```

## Deployment

The [`deploy-demo.yml`](.github/workflows/deploy-demo.yml) workflow runs on every push to `main` (and manually from Actions):

1. Runs the tests.
2. Builds the game for the web with pygbag.
3. Copies `showcase/` and the built game into `demos/BlockFall_Python/` of the [RaulEstevezA.github.io](https://github.com/RaulEstevezA/RaulEstevezA.github.io) repository, which GitHub Pages serves.

It needs the `PORTFOLIO_DEPLOY_TOKEN` Actions secret: a *fine-grained* token with **Contents: Read and write** permission on `RaulEstevezA.github.io` only.

The site's `demos/BlockFall_Python/` folder is fully replaced on every deployment, so it must not be edited by hand.

## Developer

**Raul Estevez**

- [Personal Website](https://raulesteveza.github.io/)
- [LinkedIn Profile](https://www.linkedin.com/in/raulesteveza/)

[Back to the main README](./README.md)
