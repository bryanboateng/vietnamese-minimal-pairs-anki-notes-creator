from io import BytesIO
from pathlib import Path

from google.cloud import texttospeech
from pydub import AudioSegment
from tqdm import tqdm


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


def text_to_speech(texts: list[str]):
    client = texttospeech.TextToSpeechClient()
    for text in tqdm(texts, unit="text"):
        out_directory_path = Path("./out")
        file_path = out_directory_path / f"tts-{text}.wav"

        if file_path.exists():
            print(f'"{text}" already exists, skipping')
        else:
            print(f'Doing "{text}"...')
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
            out_directory_path.mkdir(parents=True, exist_ok=True)
            combined_audio.export(file_path, format="wav")
            print(f'Exported "{text}".')


def main():
    texts = Path("in.txt").read_text(encoding="utf-8").splitlines()
    text_to_speech(texts=texts)


if __name__ == "__main__":
    main()
