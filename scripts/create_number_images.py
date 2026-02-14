import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


def main():
    numbers = get_numbers()
    for number in numbers:
        create_number_image(number=number)


def get_numbers() -> list[int]:
    argument_parser = argparse.ArgumentParser(description="Create number images")
    argument_parser.add_argument(
        "numbers",
        nargs="+",
        type=int,
        help="Numbers to generate images for (e.g. 30 31 32)",
    )
    arguments = argument_parser.parse_args()
    return arguments.numbers


def create_number_image(number: int):
    margin = 80
    width = 1_280
    height = 720

    formatted_number = format_integer(integer=number)

    image = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(image)

    fitting_font = get_fitting_font(
        text=formatted_number,
        max_text_width=width - margin * 2,
        max_text_height=height - margin * 2,
        draw=draw,
    )

    draw_text(
        text=formatted_number,
        font=fitting_font,
        image_width=width,
        image_height=height,
        image_draw=draw,
    )

    output_directory_path = Path("../out") / "number-image"
    output_directory_path.mkdir(parents=True, exist_ok=True)
    image.save(output_directory_path / f"số-{number}.png")


def format_integer(integer):
    return f"{integer:,.0f}".replace(",", ".")


def get_fitting_font(
    text: str, max_text_width: int, max_text_height: int, draw: ImageDraw.ImageDraw
):
    lower_bound_size = 10
    upper_bound_size = 500

    best_font = None

    while lower_bound_size <= upper_bound_size:
        candidate_size = (lower_bound_size + upper_bound_size) // 2
        font = load_font(size=candidate_size)

        bounding_box = draw.textbbox((0, 0), text, font=font)
        text_width = bounding_box[2] - bounding_box[0]
        text_height = bounding_box[3] - bounding_box[1]

        text_fits = text_width <= max_text_width and text_height <= max_text_height
        if text_fits:
            best_font = font
            lower_bound_size = candidate_size + 1
        else:
            upper_bound_size = candidate_size - 1

    return best_font


def load_font(size: float):
    font = ImageFont.truetype(
        font=Path("/home/bryan_oppong/.local/share/fonts/InterVariable.ttf"), size=size
    )
    font.set_variation_by_name("SemiBold")
    return font


def draw_text(
    text: str,
    font,
    image_width: int,
    image_height: int,
    image_draw: ImageDraw.ImageDraw,
):
    text_bounding_box = image_draw.textbbox(xy=(0, 0), text=text, font=font)

    text_width = text_bounding_box[2] - text_bounding_box[0]
    text_height = text_bounding_box[3] - text_bounding_box[1]

    x = (image_width - text_width) / 2 - text_bounding_box[0]
    y = (image_height - text_height) / 2 - text_bounding_box[1]

    image_draw.text(xy=(x, y), text=text, font=font, fill="black")


if __name__ == "__main__":
    main()
