import argparse
import math
import re
import xml.etree.ElementTree as ElementTree
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol, Sequence

from PIL import Image, ImageDraw, ImageFile, ImageSequence

SVG_NAMESPACE = "http://www.w3.org/2000/svg"

type Point = tuple[float, float]
type Color = tuple[int, int, int, int]


class WordType(Enum):
    ADJECTIVE = "adjective"
    ADVERB = "adverb"
    ARTICLE = "article"
    CONJUNCTION = "conjunction"
    INTERJECTION = "interjection"
    NOUN = "noun"
    PREPOSITION = "preposition"
    PRONOUN = "pronoun"
    VERB = "verb"


@dataclass
class Config:
    input: Path
    word_type: WordType


def main():
    config = get_config()

    output_path = config.input.with_name(
        f"{config.input.stem}_marked{config.input.suffix}"
    )

    if config.input.suffix.lower() == ".svg":
        process_svg(
            word_type=config.word_type, input_path=config.input, output_path=output_path
        )
        return

    image = Image.open(fp=config.input)

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


class Canvas(Protocol):
    """The subset of `ImageDraw.ImageDraw` the markers are drawn with."""

    def polygon(self, xy: Sequence[Point], fill: Color) -> None: ...

    def ellipse(self, xy: Sequence[Point], fill: Color) -> None: ...

    def rectangle(self, xy: Sequence[Point], fill: Color) -> None: ...


class SvgCanvas:
    """Draws onto an SVG element by appending vector shapes to it."""

    def __init__(self, parent: ElementTree.Element):
        self.parent = parent

    def polygon(self, xy: Sequence[Point], fill: Color):
        points = " ".join(f"{x:.3f},{y:.3f}" for x, y in xy)
        self.add(tag="polygon", fill=fill, points=points)

    def ellipse(self, xy: Sequence[Point], fill: Color):
        (x0, y0), (x1, y1) = xy
        self.add(
            tag="ellipse",
            fill=fill,
            cx=f"{(x0 + x1) / 2:.3f}",
            cy=f"{(y0 + y1) / 2:.3f}",
            rx=f"{(x1 - x0) / 2:.3f}",
            ry=f"{(y1 - y0) / 2:.3f}",
        )

    def rectangle(self, xy: Sequence[Point], fill: Color):
        (x0, y0), (x1, y1) = xy
        self.add(
            tag="rect",
            fill=fill,
            x=f"{x0:.3f}",
            y=f"{y0:.3f}",
            width=f"{x1 - x0:.3f}",
            height=f"{y1 - y0:.3f}",
        )

    def add(self, tag: str, fill: Color, **attributes: str):
        red, green, blue, alpha = fill
        ElementTree.SubElement(
            self.parent,
            f"{{{SVG_NAMESPACE}}}{tag}",
            fill=f"rgb({red},{green},{blue})",
            **({"fill-opacity": f"{alpha / 255:.3f}"} if alpha != 255 else {}),
            **attributes,
        )


def process_svg(word_type: WordType, input_path: Path, output_path: Path):
    # Keep the file's namespace prefixes instead of ElementTree's ns0, ns1, …
    for _, (prefix, uri) in ElementTree.iterparse(input_path, events=["start-ns"]):
        ElementTree.register_namespace(prefix, uri)

    tree = ElementTree.parse(input_path)
    root = tree.getroot()
    min_x, min_y, width, height = get_svg_viewport(root=root)

    group = ElementTree.SubElement(
        root,
        f"{{{SVG_NAMESPACE}}}g",
        transform=f"translate({min_x},{min_y})",
    )
    draw_marker(
        canvas=SvgCanvas(parent=group),
        width=width,
        height=height,
        word_type=word_type,
    )

    tree.write(output_path, encoding="utf-8", xml_declaration=True)


def get_svg_viewport(root: ElementTree.Element) -> tuple[float, float, float, float]:
    view_box = root.get("viewBox")
    if view_box is not None:
        min_x, min_y, width, height = map(float, re.split(r"[\s,]+", view_box.strip()))
        return min_x, min_y, width, height

    width = parse_svg_length(value=root.get("width"))
    height = parse_svg_length(value=root.get("height"))
    if width is None or height is None:
        raise ValueError("SVG needs either a viewBox or a numeric width and height")
    return 0, 0, width, height


def parse_svg_length(value: str | None) -> float | None:
    if value is None:
        return None
    match = re.fullmatch(r"\s*([0-9.]+)\s*(px)?\s*", value)
    return float(match.group(1)) if match else None


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
    draw_marker(
        canvas=ImageDraw.Draw(image),
        width=image.width,
        height=image.height,
        word_type=word_type,
    )
    return image


def draw_marker(canvas: Canvas, width: float, height: float, word_type: WordType):
    reference = math.sqrt(width**2 + height**2)

    size = reference * 0.05
    margin = reference * 0.03

    anchor_x = width - margin
    anchor_y = height - margin

    # Montessori grammar symbols, sized relative to the noun triangle and
    # coloured with the Apple HIG system colours (light appearance).
    # https://www.montessorialbum.com/montessori/index.php/Grammar_Symbols
    noun_side_length = (size * 2) / math.sqrt(3)

    match word_type:
        case WordType.ADJECTIVE:
            draw_triangle(
                x=anchor_x,
                y=anchor_y,
                base=noun_side_length * 2 / 3,
                fill=(0, 136, 255, 255),
                draw=canvas,
            )
        case WordType.ADVERB:
            draw_circle(
                x=anchor_x,
                y=anchor_y,
                diameter=noun_side_length * 0.5,
                fill=(255, 141, 40, 255),
                draw=canvas,
            )
        case WordType.ARTICLE:
            draw_triangle(
                x=anchor_x,
                y=anchor_y,
                base=noun_side_length * 0.47,
                fill=(0, 192, 232, 255),
                draw=canvas,
            )
        case WordType.CONJUNCTION:
            draw_bar(
                x=anchor_x,
                y=anchor_y,
                width=noun_side_length * 0.5,
                height=noun_side_length * 0.13,
                fill=(255, 138, 196, 255),
                draw=canvas,
            )
        case WordType.INTERJECTION:
            draw_keyhole(
                x=anchor_x,
                y=anchor_y,
                width=noun_side_length * 0.28,
                fill=(255, 204, 0, 255),
                draw=canvas,
            )
        case WordType.NOUN:
            draw_triangle(
                x=anchor_x,
                y=anchor_y,
                base=noun_side_length,
                fill=(0, 0, 0, 255),
                draw=canvas,
            )
        case WordType.PREPOSITION:
            draw_crescent(
                x=anchor_x,
                y=anchor_y,
                diameter=noun_side_length * 0.5,
                fill=(52, 199, 89, 255),
                draw=canvas,
            )
        case WordType.PRONOUN:
            draw_triangle(
                x=anchor_x,
                y=anchor_y,
                base=noun_side_length * 0.62,
                height=size,
                fill=(203, 48, 224, 255),
                draw=canvas,
            )
        case WordType.VERB:
            draw_circle(
                x=anchor_x,
                y=anchor_y,
                diameter=noun_side_length,
                fill=(255, 56, 60, 255),
                draw=canvas,
            )


def draw_triangle(
    x: float,
    y: float,
    base: float,
    fill: Color,
    draw: Canvas,
    height: float | None = None,
):
    """Draws an isosceles triangle, equilateral unless a height is given."""
    if height is None:
        height = base * math.sqrt(3) / 2

    draw.polygon(
        xy=[
            (x, y),
            (x - base, y),
            (x - base / 2, y - height),
        ],
        fill=fill,
    )


def draw_circle(
    x: float,
    y: float,
    diameter: float,
    fill: Color,
    draw: Canvas,
):
    draw.ellipse(
        xy=[
            (x - diameter, y - diameter),
            (x, y),
        ],
        fill=fill,
    )


def draw_bar(
    x: float,
    y: float,
    width: float,
    height: float,
    fill: Color,
    draw: Canvas,
):
    draw.rectangle(
        xy=[
            (x - width, y - height),
            (x, y),
        ],
        fill=fill,
    )


def draw_keyhole(
    x: float,
    y: float,
    width: float,
    fill: Color,
    draw: Canvas,
):
    """Draws an upside-down triangle whose tip ends in a circle."""
    circle_diameter = width * 0.72
    top = y - width * 1.75
    center_x = x - width / 2
    circle_center_y = y - circle_diameter / 2

    draw.polygon(
        xy=[
            (x - width, top),
            (x, top),
            (center_x, circle_center_y),
        ],
        fill=fill,
    )
    draw.ellipse(
        xy=[
            (center_x - circle_diameter / 2, y - circle_diameter),
            (center_x + circle_diameter / 2, y),
        ],
        fill=fill,
    )


def draw_crescent(
    x: float,
    y: float,
    diameter: float,
    fill: Color,
    draw: Canvas,
):
    """Draws a crescent opening downwards: a circle with a same-sized circle
    cut out slightly below it."""
    radius = diameter / 2
    offset = diameter * 0.24
    center_x = x - radius
    center_y = y - offset / 2

    # Angle between the horizontal and the points where both circles intersect
    angle = math.asin((offset / 2) / radius)
    steps = 64

    outer_arc = [
        (
            center_x + radius * math.cos(phi),
            center_y - radius * math.sin(phi),
        )
        for phi in (
            -angle + (math.pi + 2 * angle) * step / steps for step in range(steps + 1)
        )
    ]
    inner_arc = [
        (
            center_x + radius * math.cos(phi),
            center_y + offset - radius * math.sin(phi),
        )
        for phi in (
            math.pi - angle - (math.pi - 2 * angle) * step / steps
            for step in range(steps + 1)
        )
    ]

    draw.polygon(xy=outer_arc + inner_arc, fill=fill)


if __name__ == "__main__":
    main()
