#!/usr/bin/env python3
"""WCAG 2.x contrast ratio between two hex colors.

Usage: python contrast.py "#1A1A1A" "#FFFFFF" [--large]
Prints the ratio and pass/fail for AA and AAA. Exists so the report never
states a contrast value that was not measured.
"""
import argparse
import sys

AA_NORMAL, AA_LARGE, AAA_NORMAL, AAA_LARGE = 4.5, 3.0, 7.0, 4.5


def parse_hex(value: str) -> tuple[int, int, int]:
    digits = value.strip().lstrip("#")
    if len(digits) == 3:
        digits = "".join(ch * 2 for ch in digits)
    if len(digits) != 6:
        raise ValueError(f"invalid hex color: {value}")
    return tuple(int(digits[i:i + 2], 16) for i in (0, 2, 4))


def relative_luminance(rgb: tuple[int, int, int]) -> float:
    def channel(c: int) -> float:
        s = c / 255
        return s / 12.92 if s <= 0.04045 else ((s + 0.055) / 1.055) ** 2.4

    r, g, b = (channel(c) for c in rgb)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted(
        (relative_luminance(parse_hex(foreground)), relative_luminance(parse_hex(background))),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def verdict(ratio: float, large_text: bool) -> dict[str, bool]:
    return {
        "AA": ratio >= (AA_LARGE if large_text else AA_NORMAL),
        "AAA": ratio >= (AAA_LARGE if large_text else AAA_NORMAL),
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("foreground")
    parser.add_argument("background")
    parser.add_argument("--large", action="store_true", help="text >= 18pt or 14pt bold")
    args = parser.parse_args(argv)
    ratio = contrast_ratio(args.foreground, args.background)
    result = verdict(ratio, args.large)
    print(f"{ratio:.2f}:1 AA={'pass' if result['AA'] else 'fail'} AAA={'pass' if result['AAA'] else 'fail'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
