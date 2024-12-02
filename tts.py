import argparse
import random
from pathlib import Path

from google.cloud import texttospeech


def synthesize_speech(
    text: str,
    voice_is_female: bool,
    client: texttospeech.TextToSpeechClient,
    out_directory_path: Path,
):
    voice_name = "vi-VN-Neural2-A" if voice_is_female else "vi-VN-Neural2-D"

    file_path = out_directory_path / f"google-tts_{voice_name}_{text}.wav"
    if not file_path.exists():
        response = client.synthesize_speech(
            input=(texttospeech.SynthesisInput(text=text)),
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


def main():
    argument_parser = argparse.ArgumentParser(prog="Vietnamese Text-To-Speech")
    argument_parser.add_argument("text", type=str)
    argument_parser.add_argument(
        "--gender",
        type=int,
        choices=[0, 1],
        help="Specify the gender (0 for male, 1 for female). If not provided, a random gender will be chosen.",
        default=None,
    )

    arguments = argument_parser.parse_args()
    gender = arguments.gender if arguments.gender is not None else random.choice([0, 1])

    output_directory_path = Path("./out") / "standalone-audio"
    output_directory_path.mkdir(parents=True, exist_ok=True)
    synthesize_speech(
        text=arguments.text.strip(),
        voice_is_female=gender == 1,
        client=texttospeech.TextToSpeechClient(),
        out_directory_path=output_directory_path,
    )


if __name__ == "__main__":
    main()
