from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
IMAGE_DIR = ROOT / "assets" / "images"
SOUND_DIR = ROOT / "assets" / "sounds"
FONT_DIR = ROOT / "assets" / "fonts"


def alpha_crop(image: Image.Image, padding: int = 10) -> Image.Image:
    rgba = image.convert("RGBA")
    bounds = rgba.getchannel("A").getbbox()
    if not bounds:
        raise ValueError("The source image has no visible content.")
    left, top, right, bottom = bounds
    return rgba.crop(
        (
            max(0, left - padding),
            max(0, top - padding),
            min(rgba.width, right + padding),
            min(rgba.height, bottom + padding),
        )
    )


def contain_on_square(image: Image.Image, size: int, margin: int = 18) -> Image.Image:
    sprite = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    trimmed = alpha_crop(image, padding=4)
    fitted = ImageOps.contain(trimmed, (size - margin * 2, size - margin * 2), Image.Resampling.LANCZOS)
    sprite.alpha_composite(fitted, ((size - fitted.width) // 2, (size - fitted.height) // 2))
    return sprite


def prepare_forest_background() -> None:
    source = IMAGE_DIR / "forest-background.png"
    target = IMAGE_DIR / "forest-background.jpg"
    if source.exists():
        image = Image.open(source).convert("RGB")
        image.save(target, "JPEG", quality=88, optimize=True, progressive=True)


def prepare_snake_sprites() -> None:
    source = Image.open(IMAGE_DIR / "snake-spritesheet.png").convert("RGBA")
    head = source.crop((18, 325, 488, 676))
    body = source.crop((500, 330, 1010, 674))
    head = contain_on_square(head, 480, margin=12)
    body = contain_on_square(body, 480, margin=10)
    head.save(IMAGE_DIR / "snake-head.png", optimize=True)
    body.save(IMAGE_DIR / "snake-body.png", optimize=True)

    tail = body.copy()
    mask = Image.new("L", tail.size, 0)
    draw = ImageDraw.Draw(mask)
    w, h = tail.size
    draw.polygon(
        ((0, h // 2), (54, 8), (w - 3, 8), (w - 3, h - 8), (54, h - 8)),
        fill=255,
    )
    tail.putalpha(ImageChops.multiply(tail.getchannel("A"), mask))
    tail.save(IMAGE_DIR / "snake-tail.png", optimize=True)


def prepare_fruit_and_mascot() -> None:
    fruit_path = IMAGE_DIR / "forest-fruit.png"
    fruit = alpha_crop(Image.open(fruit_path), padding=12)
    fruit.thumbnail((440, 440), Image.Resampling.LANCZOS)
    fruit.save(fruit_path, optimize=True)

    mascot_path = IMAGE_DIR / "snake-mascot.png"
    mascot = alpha_crop(Image.open(mascot_path), padding=8)
    mascot.thumbnail((900, 900), Image.Resampling.LANCZOS)
    mascot.save(mascot_path, optimize=True)


def _font(filename: str, size: int) -> ImageFont.FreeTypeFont:
    path = FONT_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Bundled logo font not found: {path}")
    return ImageFont.truetype(str(path), size=size)


def prepare_logo_and_icon() -> None:
    mascot = alpha_crop(Image.open(IMAGE_DIR / "snake-mascot.png"), padding=4)
    logo = Image.new("RGBA", (1500, 590), (0, 0, 0, 0))
    mascot = ImageOps.contain(mascot, (545, 545), Image.Resampling.LANCZOS)
    logo.alpha_composite(mascot, (5, (590 - mascot.height) // 2))

    draw = ImageDraw.Draw(logo)
    headline_font = _font("DejaVuSerif-Bold.ttf", 172)
    forest_font = _font("DejaVuSans-Bold.ttf", 126)
    title_x = 480
    first_y = 112
    second_y = 314
    draw.text(
        (title_x + 7, first_y + 11),
        "SNAKE",
        font=headline_font,
        fill=(9, 18, 12, 210),
        stroke_width=10,
        stroke_fill=(22, 33, 17, 220),
    )
    draw.text(
        (title_x, first_y),
        "SNAKE",
        font=headline_font,
        fill=(255, 209, 94, 255),
        stroke_width=5,
        stroke_fill=(96, 48, 17, 255),
    )
    draw.text(
        (title_x + 4, second_y + 9),
        "FOREST",
        font=forest_font,
        fill=(7, 21, 11, 220),
        stroke_width=8,
        stroke_fill=(20, 38, 17, 255),
    )
    draw.text(
        (title_x, second_y),
        "FOREST",
        font=forest_font,
        fill=(166, 232, 109, 255),
        stroke_width=4,
        stroke_fill=(39, 90, 32, 255),
    )
    leaf_y = 514
    draw.ellipse((title_x, leaf_y, title_x + 15, leaf_y + 8), fill=(95, 185, 64, 240))
    draw.ellipse((title_x + 21, leaf_y - 2, title_x + 36, leaf_y + 6), fill=(149, 216, 81, 240))
    logo.save(IMAGE_DIR / "logo.png", optimize=True)

    icon = Image.new("RGBA", (512, 512), (4, 24, 16, 255))
    pixels = icon.load()
    for y in range(512):
        for x in range(512):
            distance = math.sqrt((x - 256) ** 2 + (y - 236) ** 2) / 400
            glow = max(0.0, 1.0 - distance) * 20
            pixels[x, y] = (4 + int(glow * 0.45), 24 + int(glow), 16 + int(glow * 0.45), 255)
    border = ImageDraw.Draw(icon)
    border.rounded_rectangle((10, 10, 502, 502), radius=116, outline=(188, 151, 60, 255), width=10)
    border.rounded_rectangle((25, 25, 487, 487), radius=102, outline=(71, 133, 68, 255), width=4)
    icon_mascot = ImageOps.contain(mascot, (425, 425), Image.Resampling.LANCZOS)
    icon.alpha_composite(icon_mascot, ((512 - icon_mascot.width) // 2, (512 - icon_mascot.height) // 2))
    icon.save(IMAGE_DIR / "app_icon.png", optimize=True)
    icon.save(
        IMAGE_DIR / "app_icon.ico",
        format="ICO",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )


def write_sound(filename: str, partials: list[tuple[float, float, float]]) -> None:
    """Create an original short game sound from enveloped sine-wave notes."""
    sample_rate = 44100
    samples: list[int] = []
    absolute_time = 0.0
    for frequency, duration, secondary in partials:
        sample_count = int(sample_rate * duration)
        for index in range(sample_count):
            time_in_note = index / sample_rate
            attack = min(1.0, time_in_note / 0.018)
            release = min(1.0, max(0.0, duration - time_in_note) / 0.045)
            envelope = attack * release * math.exp(-2.8 * time_in_note / duration)
            fundamental = math.sin(2 * math.pi * frequency * time_in_note)
            harmonic = math.sin(2 * math.pi * (frequency * 2.01) * time_in_note) * 0.18
            overtone = math.sin(2 * math.pi * secondary * time_in_note) * 0.16
            click = math.sin(2 * math.pi * 1700 * time_in_note) * math.exp(-85 * time_in_note) * 0.10
            sample = (fundamental * 0.62 + harmonic + overtone + click) * envelope * 0.44
            samples.append(max(-32767, min(32767, int(sample * 32767))))
        absolute_time += duration

    with wave.open(str(SOUND_DIR / filename), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(sample_rate)
        output.writeframes(struct.pack(f"<{len(samples)}h", *samples))


def prepare_sounds() -> None:
    SOUND_DIR.mkdir(parents=True, exist_ok=True)
    sound_designs = {
        "ui-click.wav": [(720, 0.045, 1080), (940, 0.07, 1410)],
        "collect.wav": [(660, 0.09, 990), (880, 0.10, 1320), (1320, 0.20, 1980)],
        "game-start.wav": [(440, 0.13, 660), (554, 0.16, 831), (659, 0.23, 988)],
        "pause.wav": [(540, 0.09, 810), (410, 0.12, 615)],
        "game-over.wav": [(392, 0.16, 588), (330, 0.2, 495), (262, 0.26, 393)],
        "high-score.wav": [(523, 0.12, 784), (659, 0.12, 988), (784, 0.13, 1176), (1047, 0.25, 1570)],
    }
    for filename, notes in sound_designs.items():
        write_sound(filename, notes)


def main() -> None:
    IMAGE_DIR.mkdir(parents=True, exist_ok=True)
    FONT_DIR.mkdir(parents=True, exist_ok=True)
    prepare_forest_background()
    prepare_snake_sprites()
    prepare_fruit_and_mascot()
    prepare_logo_and_icon()
    prepare_sounds()
    print("Prepared logo, desktop icon, snake sprites, compressed images, and six offline sounds.")


if __name__ == "__main__":
    main()
