"""Generate the tiny vanilla-style gear button without external image libraries."""
from pathlib import Path
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "common/src/main/resources/assets/torch_bag/textures/gui/gear_button.png"
WIDTH, HEIGHT = 20, 40
pixels = [[(0, 0, 0, 0) for _ in range(WIDTH)] for _ in range(HEIGHT)]


def fill(x1, y1, x2, y2, color):
    for y in range(y1, y2):
        for x in range(x1, x2):
            pixels[y][x] = color


def button(y, hovered):
    face = (198, 198, 198, 255) if not hovered else (216, 216, 216, 255)
    fill(0, y, 20, y + 20, face)
    fill(0, y, 20, y + 1, (255, 255, 255, 255))
    fill(0, y, 1, y + 20, (255, 255, 255, 255))
    fill(1, y + 1, 19, y + 2, (223, 223, 223, 255))
    fill(1, y + 1, 2, y + 19, (223, 223, 223, 255))
    fill(0, y + 19, 20, y + 20, (0, 0, 0, 255))
    fill(19, y, 20, y + 20, (0, 0, 0, 255))
    fill(1, y + 18, 19, y + 19, (85, 85, 85, 255))
    fill(18, y + 1, 19, y + 19, (85, 85, 85, 255))

    # A square, toothed cog based on the visual language of inventory mods.
    # The broken outer rim and hollow hub stay readable at Minecraft GUI scale.
    rows = {
        3:  {4, 15},
        4:  set(range(3, 17)),
        5:  {4, 15},
        6:  {4, 6, 7, 9, 10, 12, 13, 15},
        7:  {4, *range(6, 14), 15},
        8:  {4, *range(7, 13), 15},
        9:  {4, 6, 7, 8, 11, 12, 13, 15},
        10: {4, 6, 7, 8, 11, 12, 13, 15},
        11: {4, *range(7, 13), 15},
        12: {4, *range(6, 14), 15},
        13: {4, 6, 7, 9, 10, 12, 13, 15},
        14: {4, 15},
        15: set(range(3, 17)),
        16: {4, 15},
    }
    dark = (55, 55, 55, 255)
    for py, columns in rows.items():
        for px in columns:
            pixels[y + py][px] = dark


button(0, False)
button(20, True)


def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xFFFFFFFF)


raw = b"".join(b"\x00" + bytes(channel for pixel in row for channel in pixel) for row in pixels)
png = b"\x89PNG\r\n\x1a\n"
png += chunk(b"IHDR", struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 6, 0, 0, 0))
png += chunk(b"IDAT", zlib.compress(raw, 9))
png += chunk(b"IEND", b"")
OUTPUT.parent.mkdir(parents=True, exist_ok=True)
OUTPUT.write_bytes(png)
print(OUTPUT)
