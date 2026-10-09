#!/usr/bin/env python3
"""Turns a bug video into the frames worth looking at: scene changes plus a contact sheet.

Usage: python video_frames.py <video.mp4|mov> [--out frames/] [--threshold 0.3] [--fps 1] [--json]

Scene-change frames (ffmpeg `select='gt(scene,T)'`) are the moments the screen changed: a tap,
a navigation, a crash. Each is saved as sc_NNN.png with its timestamp, so the report can say
"at 00:12 the sheet closed". The contact sheet (fps=1, 4x4 tiles) gives the whole video in one
image to read before the frames. Uses -fps_mode when the local ffmpeg has it (-vsync is gone in ffmpeg 8+), else -vsync.
Then look at the PNGs with Read: this script extracts, it does not interpret.
"""
import argparse
import json
import os
import re
import subprocess
import sys


_VFR: list[str] | None = None


def vfr_flag() -> list[str]:
    """-fps_mode vfr on ffmpeg 5.1+ (where -vsync was later removed), -vsync vfr on older builds."""
    global _VFR
    if _VFR is None:
        probe = subprocess.run(["ffmpeg", "-hide_banner", "-h", "long"], capture_output=True, text=True)
        _VFR = ["-fps_mode", "vfr"] if "fps_mode" in (probe.stdout + probe.stderr) else ["-vsync", "vfr"]
    return _VFR


def commands(video: str, out: str, threshold: float = 0.3, fps: float = 1.0) -> list[list[str]]:
    scene = ["ffmpeg", "-hide_banner", "-loglevel", "info", "-y", "-i", video,
             "-vf", f"select='gt(scene,{threshold})',showinfo", *vfr_flag(), os.path.join(out, "sc_%03d.png")]
    sheet = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y", "-i", video,
             "-vf", f"fps={fps},scale=360:-1,tile=4x4", "-frames:v", "1", os.path.join(out, "sheet.png")]
    return [scene, sheet]


def extract(video: str, out: str, threshold: float = 0.3, fps: float = 1.0) -> dict:
    os.makedirs(out, exist_ok=True)
    scene_cmd, sheet_cmd = commands(video, out, threshold, fps)
    scene_run = subprocess.run(scene_cmd, capture_output=True, text=True)
    if scene_run.returncode != 0:
        raise RuntimeError(scene_run.stderr.strip().splitlines()[-1] if scene_run.stderr else "ffmpeg failed")
    times = [float(t) for t in re.findall(r"pts_time:\s*([\d.]+)", scene_run.stderr)]
    frames = sorted(f for f in os.listdir(out) if f.startswith("sc_") and f.endswith(".png"))
    sheet_run = subprocess.run(sheet_cmd, capture_output=True, text=True)
    sheet = os.path.join(out, "sheet.png") if sheet_run.returncode == 0 else ""
    return {"video": video, "scene_frames": [os.path.join(out, f) for f in frames], "scene_times": times[:len(frames)],
            "contact_sheet": sheet}


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("video")
    parser.add_argument("--out", default="frames")
    parser.add_argument("--threshold", type=float, default=0.3)
    parser.add_argument("--fps", type=float, default=1.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = extract(args.video, args.out, args.threshold, args.fps)
    if args.json:
        print(json.dumps(result, indent=2))
        return 0
    print(f"{len(result['scene_frames'])} mudanças de cena; contact sheet: {result['contact_sheet'] or 'falhou'}")
    for frame, t in zip(result["scene_frames"], result["scene_times"]):
        print(f"  {int(t // 60):02d}:{t % 60:05.2f}  {frame}")
    if not result["scene_frames"]:
        print("nenhuma mudança acima do limiar; tente --threshold 0.15")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
