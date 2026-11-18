#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright==1.62.0"]
# ///
"""Record the home page's gameplay montage from the simulator.

For each level in LEVELS the script runs the simulator's default controller
without a window and saves a recording. It then serves that recording with
``cook replay --no-window``, opens it in headless Chromium with the panels
hidden, and captures the kitchen as video. ffmpeg cuts a clip from each
capture and joins the clips into ``public/videos/hero.mp4`` and ``hero.webm``,
with the first frame saved as ``public/images/hero-poster.jpg``.

Usage:

    uv run scripts/record-hero.py
    uv run scripts/record-hero.py --simulator ../overcooked-2 --clip-seconds 6

It needs uv, ffmpeg, and a Chromium for Playwright
(``uv run --with playwright==1.62.0 playwright install chromium``).
"""

from __future__ import annotations

import argparse
import os
import re
import shutil
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from urllib.request import urlopen

ROOT = Path(__file__).resolve().parent.parent
VIDEO_OUT = ROOT / "public" / "videos"
POSTER_OUT = ROOT / "public" / "images" / "hero-poster.jpg"

# Levels in montage order, relative to the simulator's levels/ directory.
LEVELS = [
    "0_i_can_cook/2_2_cheeseburger_from_scratch.yaml",
    "1_we_can_cook/1_2_sushi_divided_3p.yaml",
    "2_overcooked/0_0_black_forest_cake_shared_stations_2p.yaml",
    "1_we_can_cook/2_1_chicken_and_chips_parallel_stations_4p.yaml",
    "1_we_can_cook/0_3_cheeseburger_divided_pass_through_2p.yaml",
    "2_overcooked/3_0_sushi_rush_hour_3p.yaml",
]

SIZE = (1280, 720)
SERVER_START_TIMEOUT = 40.0
PAGE_READY_TIMEOUT = 30.0

# Counts sprite sheet loads, which Playwright's network idle state misses.
TRACK_IMAGE_LOADS = """
(() => {
  window.__sheets = { started: 0, finished: 0 };
  const descriptor = Object.getOwnPropertyDescriptor(HTMLImageElement.prototype, 'src');
  Object.defineProperty(HTMLImageElement.prototype, 'src', {
    configurable: true,
    get() { return descriptor.get.call(this); },
    set(value) {
      window.__sheets.started += 1;
      const done = () => { window.__sheets.finished += 1; };
      this.addEventListener('load', done, { once: true });
      this.addEventListener('error', done, { once: true });
      descriptor.set.call(this, value);
    },
  });
})();
"""

# True once every sprite sheet has loaded and the kitchen has been drawn.
PAGE_READY = """
() => {
  const sheets = window.__sheets;
  if (!sheets || sheets.started === 0 || sheets.finished < sheets.started) return false;
  const canvases = [...document.querySelectorAll('.sprite-canvas canvas')];
  return canvases.some(canvas => canvas.width > 0 && canvas.height > 0);
}
"""


def cook(simulator: Path, *args: str, **kwargs) -> subprocess.Popen:
    env = {**os.environ, "PYTHONUNBUFFERED": "1", "TERM": "dumb"}
    return subprocess.Popen(
        ["uv", "run", "cook", *args],
        cwd=simulator,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        **kwargs,
    )


def record_run(simulator: Path, level: str, out: Path) -> None:
    """Run the default controller on a level and save the recording."""
    process = cook(
        simulator,
        "agent",
        "--level",
        f"levels/{level}",
        "--headless",
        "--record",
        "--recording-out-file",
        str(out),
        "--quiet",
    )
    output, _ = process.communicate(timeout=300)
    if process.returncode != 0 or '"reason": "completed"' not in output:
        raise RuntimeError(f"{level} did not complete:\n{output[-2000:]}")


class ReplayServer:
    """``cook replay --no-window`` running in a child process."""

    URL_PATTERN = re.compile(r"http://127\.0\.0\.1:(\d+)/")

    def __init__(self, simulator: Path, recording: Path) -> None:
        self.process = cook(
            simulator, "replay", "--recording-path", str(recording), "--no-window"
        )
        self.output: list[str] = []
        self.url: str | None = None
        self._ready = threading.Event()
        threading.Thread(target=self._read, daemon=True).start()

    def _read(self) -> None:
        assert self.process.stdout is not None
        for line in self.process.stdout:
            self.output.append(line)
            found = self.URL_PATTERN.search(line)
            if found and self.url is None:
                self.url = f"http://127.0.0.1:{found.group(1)}/"
                self._ready.set()
        self._ready.set()

    def wait(self) -> str:
        deadline = time.monotonic() + SERVER_START_TIMEOUT
        while time.monotonic() < deadline and not self.url:
            self._ready.wait(timeout=0.2)
            if self.process.poll() is not None:
                break
        if not self.url:
            raise RuntimeError(
                "The replay server did not print a URL:\n" + "".join(self.output[-20:])
            )
        while time.monotonic() < deadline:
            try:
                urlopen(self.url + "_too-many-chefs/alive", timeout=0.5)
                return self.url
            except OSError:
                time.sleep(0.1)
        raise RuntimeError(f"The replay server at {self.url} did not answer")

    def stop(self) -> None:
        if self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait()


def capture(browser, url: str, seconds: float, work: Path) -> tuple[Path, float]:
    """Play a replay and return the captured video and where playback starts in it."""
    context = browser.new_context(
        viewport={"width": SIZE[0], "height": SIZE[1]},
        device_scale_factor=1,
        record_video_dir=str(work),
        record_video_size={"width": SIZE[0], "height": SIZE[1]},
    )
    page = context.new_page()
    started = time.monotonic()
    page.add_init_script(TRACK_IMAGE_LOADS)
    page.goto(url, wait_until="networkidle")
    page.wait_for_function(PAGE_READY, timeout=PAGE_READY_TIMEOUT * 1000)
    page.wait_for_timeout(800)
    page.keyboard.press("h")  # hide the panels
    page.wait_for_timeout(400)
    page.keyboard.press("Space")  # start playback
    offset = time.monotonic() - started
    page.wait_for_timeout(int(seconds * 1000) + 500)
    video = page.video
    context.close()
    return Path(video.path()), offset


def ffmpeg(*args: str) -> None:
    subprocess.run(["ffmpeg", "-v", "error", "-y", *args], check=True)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--simulator", type=Path, default=ROOT.parent / "overcooked-2")
    parser.add_argument("--clip-seconds", type=float, default=6.0)
    parser.add_argument("--skip-seconds", type=float, default=1.0)
    parser.add_argument("--keep", type=Path, help="Keep the raw captures in this folder")
    options = parser.parse_args()
    simulator = options.simulator.resolve()

    from playwright.sync_api import sync_playwright

    work = options.keep or Path(tempfile.mkdtemp(prefix="hero-"))
    work.mkdir(parents=True, exist_ok=True)
    clips: list[Path] = []
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            for index, level in enumerate(LEVELS):
                print(f"[{index + 1}/{len(LEVELS)}] {level}")
                recording = work / f"{index}.yaml"
                record_run(simulator, level, recording)
                server = ReplayServer(simulator, recording)
                try:
                    length = options.skip_seconds + options.clip_seconds
                    raw, offset = capture(browser, server.wait(), length, work)
                finally:
                    server.stop()
                clip = work / f"clip-{index}.mp4"
                ffmpeg(
                    "-ss", f"{offset + options.skip_seconds:.2f}",
                    "-t", f"{options.clip_seconds:.2f}",
                    "-i", str(raw),
                    "-an", "-r", "25", "-c:v", "libx264", "-crf", "12",
                    "-pix_fmt", "yuv420p", str(clip),
                )  # fmt: skip
                clips.append(clip)
            browser.close()

        listing = work / "clips.txt"
        listing.write_text("".join(f"file '{clip}'\n" for clip in clips))
        joined = work / "joined.mp4"
        ffmpeg("-f", "concat", "-safe", "0", "-i", str(listing), "-c", "copy", str(joined))

        VIDEO_OUT.mkdir(parents=True, exist_ok=True)
        POSTER_OUT.parent.mkdir(parents=True, exist_ok=True)
        ffmpeg(
            "-i", str(joined), "-an", "-c:v", "libx264", "-preset", "slow",
            "-crf", "26", "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            str(VIDEO_OUT / "hero.mp4"),
        )  # fmt: skip
        ffmpeg(
            "-i", str(joined), "-an", "-c:v", "libvpx-vp9", "-crf", "36",
            "-b:v", "0", "-row-mt", "1", str(VIDEO_OUT / "hero.webm"),
        )  # fmt: skip
        ffmpeg("-i", str(joined), "-frames:v", "1", "-q:v", "4", str(POSTER_OUT))
        for path in (VIDEO_OUT / "hero.mp4", VIDEO_OUT / "hero.webm", POSTER_OUT):
            print(f"{path.relative_to(ROOT)}  {path.stat().st_size / 1024:.0f} KiB")
    finally:
        if not options.keep:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    main()
