import argparse
from io import BytesIO
from pathlib import Path

from google.cloud import texttospeech
from pydub import AudioSegment


def synthesize_repeated_text(
    text: str, client: texttospeech.TextToSpeechClient, voice_name: str
):
    response = client.synthesize_speech(
        input=(texttospeech.SynthesisInput(text=f"{text}, {text}")),
        voice=(
            texttospeech.VoiceSelectionParams(language_code="vi-VN", name=voice_name)
        ),
        audio_config=(
            texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                effects_profile_id=["small-bluetooth-speaker-class-device"],
                speaking_rate=0,
                pitch=1.25,
            )
        ),
    )
    return response.audio_content


def text_to_speech(text: str):
    client = texttospeech.TextToSpeechClient()
    filename = f"tts-{text}.wav"

    female_audio = AudioSegment.from_wav(
        BytesIO(
            synthesize_repeated_text(
                text=text, client=client, voice_name="vi-VN-Neural2-A"
            )
        )
    )
    male_audio = AudioSegment.from_wav(
        BytesIO(
            synthesize_repeated_text(
                text=text, client=client, voice_name="vi-VN-Neural2-D"
            )
        )
    )

    silence_duration_ms = 500
    silence = AudioSegment.silent(duration=silence_duration_ms)
    combined_audio = female_audio + silence + male_audio
    out_directory_path = Path("./out")
    out_directory_path.mkdir(parents=True, exist_ok=True)
    combined_audio.export(out_directory_path / filename, format="wav")


def main():
    argument_parser = argparse.ArgumentParser(
        prog="Vietnamese Minimal Pairs Audio Creator"
    )
    argument_parser.add_argument("text", type=str)
    args = argument_parser.parse_args()
    text_to_speech(text=args.text)


if __name__ == "__main__":
    main()
