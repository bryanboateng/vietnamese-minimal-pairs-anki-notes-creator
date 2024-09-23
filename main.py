import argparse
from pathlib import Path

from google.cloud import texttospeech
from tqdm import tqdm


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
                    speaking_rate=1.4,
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
    text_to_speech(
        texts=texts, anki_media_directory_path=args.anki_media_directory_path
    )


if __name__ == "__main__":
    main()
