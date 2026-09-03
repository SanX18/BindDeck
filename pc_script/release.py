#!/usr/bin/env python3
"""
One-shot release helper for BindDeck.

Bumps CURRENT_VERSION, rebuilds the ESP32 firmware and the Windows app, and
publishes both as assets on a single GitHub Release tagged "BindDeck_<version>"
so the in-app auto-updater (firmware.bin + BindDeck.exe) can find them.

Usage:
    python release.py V1.0.0.8
    python release.py V1.0.0.8 --skip-firmware        # reuse existing pc_script/firmware.bin
    python release.py V1.0.0.8 --notes "Fixes X and Y"
"""
import argparse
import os
import re
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))            # pc_script/
PROJECT_ROOT = os.path.dirname(ROOT)                          # repo root
PC_MONITOR = os.path.join(ROOT, "pc_monitor.py")
FIRMWARE_SRC = os.path.join(PROJECT_ROOT, ".pio", "build", "esp32dev", "firmware.bin")
FIRMWARE_DST = os.path.join(ROOT, "firmware.bin")
DIST_EXE = os.path.join(ROOT, "dist", "BindDeck.exe")
SPEC_FILE = "BindDeck.spec"
GITHUB_REPO = "SanX18/BindDeck"

VERSION_RE = re.compile(r'^V\d+\.\d+\.\d+\.\d+$')


def find_platformio():
    candidates = [
        os.path.join(os.environ.get("USERPROFILE", ""), ".platformio", "penv", "Scripts", "platformio.exe"),
        shutil.which("platformio"),
        shutil.which("pio"),
    ]
    for c in candidates:
        if c and os.path.exists(c):
            return c
    return None


def run(cmd, cwd=None):
    print(f"$ {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd)
    if result.returncode != 0:
        sys.exit(f"Command failed ({result.returncode}): {' '.join(cmd)}")


def confirm(prompt):
    return input(f"{prompt} [y/N] ").strip().lower() == "y"


def bump_version(version):
    with open(PC_MONITOR, "r", encoding="utf-8") as f:
        content = f.read()
    new_content, count = re.subn(
        r'CURRENT_VERSION = "V[\d.]+"',
        f'CURRENT_VERSION = "{version}"',
        content,
    )
    if count != 1:
        sys.exit("Could not find a single CURRENT_VERSION line in pc_monitor.py")
    with open(PC_MONITOR, "w", encoding="utf-8") as f:
        f.write(new_content)
    print(f"-> CURRENT_VERSION set to {version} in pc_monitor.py")


def build_firmware():
    pio = find_platformio()
    if not pio:
        sys.exit(
            "PlatformIO CLI not found (checked PATH and the VS Code extension's "
            "bundled venv). Install it, or rerun with --skip-firmware to reuse "
            "the existing pc_script/firmware.bin."
        )
    print("Building ESP32 firmware...")
    run([pio, "run"], cwd=PROJECT_ROOT)
    if not os.path.exists(FIRMWARE_SRC):
        sys.exit(f"Firmware build did not produce {FIRMWARE_SRC}")
    shutil.copyfile(FIRMWARE_SRC, FIRMWARE_DST)
    print(f"-> Copied firmware to {FIRMWARE_DST}")


def build_app():
    print("Building BindDeck.exe (this can take a minute)...")
    run([sys.executable, "-m", "PyInstaller", "--noconfirm", SPEC_FILE], cwd=ROOT)
    if not os.path.exists(DIST_EXE):
        sys.exit(f"PyInstaller did not produce {DIST_EXE}")
    print(f"-> Built {DIST_EXE}")


def create_release(version, notes):
    tag = f"BindDeck_{version}"
    print(f"\nAbout to publish GitHub release '{tag}' to {GITHUB_REPO} with:")
    print(f"  - {DIST_EXE}")
    print(f"  - {FIRMWARE_DST}")
    if not confirm("Continue?"):
        print("Aborted before publishing the release. Nothing was uploaded to GitHub.")
        return False
    run([
        "gh", "release", "create", tag,
        DIST_EXE, FIRMWARE_DST,
        "--repo", GITHUB_REPO,
        "--title", f"BindDeck {version}",
        "--notes", notes or f"BindDeck {version}",
    ])
    print(f"-> Published: https://github.com/{GITHUB_REPO}/releases/tag/{tag}")
    return True


def git_commit_and_push(version):
    if not confirm("\nCommit these changes to git and push to origin/master?"):
        print("Skipped git commit/push - remember to do it yourself so the source matches the release.")
        return
    run([
        "git", "add",
        "pc_script/pc_monitor.py",
        "pc_script/firmware.bin",
        "pc_script/dist/BindDeck.exe",
        "pc_script/build/BindDeck",
    ], cwd=PROJECT_ROOT)
    commit_message = f"release: {version}\n\nCo-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
    run(["git", "commit", "-m", commit_message], cwd=PROJECT_ROOT)
    run(["git", "push", "origin", "master"], cwd=PROJECT_ROOT)


def main():
    parser = argparse.ArgumentParser(description="Build and publish a BindDeck release (firmware + app).")
    parser.add_argument("version", help="New version, e.g. V1.0.0.8")
    parser.add_argument("--skip-firmware", action="store_true",
                         help="Reuse the existing pc_script/firmware.bin instead of rebuilding it")
    parser.add_argument("--notes", default="", help="Release notes text")
    args = parser.parse_args()

    if not VERSION_RE.match(args.version):
        sys.exit(f"Version must look like V1.0.0.8, got: {args.version}")

    bump_version(args.version)

    if args.skip_firmware:
        if not os.path.exists(FIRMWARE_DST):
            sys.exit(f"--skip-firmware was passed but {FIRMWARE_DST} doesn't exist")
        print(f"-> Skipping firmware build, reusing existing {FIRMWARE_DST}")
    else:
        build_firmware()

    build_app()

    notes = args.notes or input("Release notes (one line, optional): ").strip()
    if create_release(args.version, notes):
        git_commit_and_push(args.version)


if __name__ == "__main__":
    main()
