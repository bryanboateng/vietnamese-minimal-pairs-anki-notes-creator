import argparse
import csv
import itertools
from datetime import datetime
from pathlib import Path

from google.cloud import texttospeech
from tqdm import tqdm


def remove_duplicates(input_list):
    unique_items = []
    for item in input_list:
        if item not in unique_items:
            unique_items.append(item)
    return unique_items


def create_notes(texts: list[str]):
    output_directory_path = Path("./out-notes")
    output_directory_path.mkdir(parents=True, exist_ok=True)
    with (
        output_directory_path
        / f"note-{datetime.now().strftime('%Y-%m-%d-%Hh%Mm%Ss')}.csv"
    ).open(mode="w") as file:
        writer = csv.writer(file, delimiter=";")
        writer.writerows(
            [
                [
                    f"[sound:tts-viet-{first}-female.wav]",
                    f"[sound:tts-viet-{first}-male.wav]",
                    first,
                    f"[sound:tts-viet-{second}-female.wav]",
                    f"[sound:tts-viet-{second}-male.wav]",
                    second,
                ]
                for first, second in itertools.combinations(texts, 2)
            ]
        )


def synthesize_repeated_text(
    text: str,
    voice_is_female: bool,
    client: texttospeech.TextToSpeechClient,
    out_directory_path: Path,
):
    voice_name = "vi-VN-Neural2-A" if voice_is_female else "vi-VN-Neural2-D"
    gender = "female" if voice_is_female else "male"
    file_path = out_directory_path / f"tts-viet-{text}-{gender}.wav"
    if file_path.exists():
        print(f'"{text}" already exists, skipping')
    else:
        print(f'Doing "{text}" {gender}...')
        response = client.synthesize_speech(
            input=(texttospeech.SynthesisInput(text=f"{text}, {text}")),
            voice=(
                texttospeech.VoiceSelectionParams(
                    language_code="vi-VN", name=voice_name
                )
            ),
            audio_config=(
                texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                    effects_profile_id=["small-bluetooth-speaker-class-device"],
                    speaking_rate=1,
                    pitch=0,
                )
            ),
        )
        file_path.write_bytes(response.audio_content)
        print(f'Exported "{text}" {gender}.')


def text_to_speech(texts: list[str], anki_media_directory_path: Path):
    client = texttospeech.TextToSpeechClient()
    for text in tqdm(texts, unit="text"):
        synthesize_repeated_text(
            text=text,
            voice_is_female=True,
            client=client,
            out_directory_path=anki_media_directory_path,
        )
        synthesize_repeated_text(
            text=text,
            voice_is_female=False,
            client=client,
            out_directory_path=anki_media_directory_path,
        )


def main():
    texts = Path("in.txt").read_text(encoding="utf-8").splitlines()
    argument_parser = argparse.ArgumentParser(
        prog="Vietnamese Minimal Pairs Audio Creator"
    )
    argument_parser.add_argument(
        "anki_media_directory_path", metavar="anki-media-directory-path", type=Path
    )
    args = argument_parser.parse_args()
    character_order = {
        character: index
        for index, character in enumerate(
            "aàáạảãăằắặẳẵâầấậẩẫbcdđeèéẹẻẽêềếệểễghiìíịỉĩklmnoòóọỏõôồốộổỗơờớợởỡpqrstuùúụủũưừứựửữvxyỳýỵỷỹ"
        )
    }
    processed_texts = sorted(
        remove_duplicates([text.strip().lower() for text in texts]),
        key=lambda string: [character_order[character] for character in string],
    )
    create_notes(texts=processed_texts)
    text_to_speech(
        texts=processed_texts, anki_media_directory_path=args.anki_media_directory_path
    )


if __name__ == "__main__":
    main()
