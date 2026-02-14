import argparse
import math
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from PIL import Image, ImageDraw, ImageFile, ImageSequence


class WordType(Enum):
    ADJECTIVE = "adjective"
    NOUN = "noun"
    VERB = "verb"


@dataclass
class Config:
    input: Path
    word_type: WordType


def main():
    config = get_config()
    image = Image.open(fp=config.input)

    output_path = config.input.with_name(
        f"{config.input.stem}_marked{config.input.suffix}"
    )

    if image_is_animated(image=image):
        process_animated_image(
            word_type=config.word_type, image=image, output_path=output_path
        )
    else:
        process_static_image(
            word_type=config.word_type, image=image, output_path=output_path
        )


def get_config():
    argument_parser = argparse.ArgumentParser()
    argument_parser.add_argument("input", type=Path)
    argument_parser.add_argument(
        "--type",
        required=True,
        choices=[word_type.value for word_type in WordType],
        help="Type of marker to draw",
    )
    args = argument_parser.parse_args()
    return Config(input=args.input, word_type=WordType(args.type))


def image_is_animated(image: ImageFile.ImageFile):
    try:
        image.seek(1)
        image.seek(0)
        return True
    except EOFError:
        return False


def process_animated_image(
    word_type: WordType, image: ImageFile.ImageFile, output_path: Path
):
    frames = []
    durations = []

    for frame in ImageSequence.Iterator(image):
        frame = frame.convert("RGBA")
        processed = process_image(image=frame, word_type=word_type)
        frames.append(processed)
        durations.append(frame.info.get("duration", image.info.get("duration", 100)))

    frames[0].save(
        fp=output_path,
        save_all=True,
        append_images=frames[1:],
        loop=image.info.get("loop", 0),
        duration=durations,
        disposal=2,
    )


def process_static_image(
    word_type: WordType, image: ImageFile.ImageFile, output_path: Path
):
    image = image.convert("RGBA")
    image = process_image(image=image, word_type=word_type)

    # JPEG cannot handle RGBA
    if output_path.suffix.lower() in [".jpg", ".jpeg"]:
        image = image.convert("RGB")

    image.save(fp=output_path)


def process_image(image: Image.Image, word_type: WordType):
    image_width, image_height = image.size
    reference = math.sqrt(image_width**2 + image_height**2)

    size = reference * 0.05
    margin = reference * 0.03

    anchor_x = image_width - margin
    anchor_y = image_height - margin

    draw = ImageDraw.Draw(image)

    match word_type:
        case WordType.ADJECTIVE:
            draw_triangle(x=anchor_x, y=anchor_y, height=size, draw=draw)
        case WordType.NOUN:
            draw_square(x=anchor_x, y=anchor_y, size=size, draw=draw)
        case WordType.VERB:
            draw_oval(x=anchor_x, y=anchor_y, height=size, draw=draw)

    return image


def draw_triangle(x: float, y: float, height: float, draw: ImageDraw.ImageDraw):
    side_length = (height * 2) / math.sqrt(3)

    draw.polygon(
        xy=[
            (x, y),
            (x - side_length, y),
            (x - side_length / 2, y - height),
        ],
        fill=(255, 204, 0, 255),
    )


def draw_square(x: float, y: float, size: float, draw: ImageDraw.ImageDraw):
    draw.rectangle(
        xy=[
            (x - size, y - size),
            (x, y),
        ],
        fill=(0, 136, 255, 255),
    )


def draw_oval(x: float, y: float, height: float, draw: ImageDraw.ImageDraw):
    width = height * 1.4
    draw.ellipse(
        xy=[
            (x - width, y - height),
            (x, y),
        ],
        fill=(255, 56, 60, 255),
    )


if __name__ == "__main__":
    main()
