# Vietnamese Minimal Pairs Anki Notes Creator

This is a tool designed to assist in creating audio materials for practicing Vietnamese minimal pairs in Anki.
Minimal pairs are pairs of words or phrases in a language that differ by only a single sound, which can help in distinguishing similar sounds.
E.g., the Vietnamese words *cũng* and *cúng*.

This tool automates the process of generating audio files using Google Cloud Text-to-Speech and creating accompanying notes for easy import into Anki.

## Install Dependencies

```bash
pip install -r requirements.txt
```

## Configuration

1. **Google Cloud Setup**

   - **Enable Text-to-Speech API**:
     - Go to the [Google Cloud Console](https://console.cloud.google.com/).
     - Select your project or create a new one.
     - Navigate to **APIs & Services > Library**.
     - Search for **Text-to-Speech API** and enable it.

   - **Set Up Authentication**:
     - Navigate to **APIs & Services > Credentials**.
     - Click on **Create Credentials > Service Account**.
     - Follow the prompts to create a service account and download the JSON key file.
     - Set the `GOOGLE_APPLICATION_CREDENTIALS` environment variable to point to this JSON file:

       ```bash
       export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/service-account-file.json"
       ```

2. **Prepare Input File**

   - Create an `in.txt` file in the project root directory.
   - Organize your minimal pairs, separating groups with two newline characters (`\n\n`).
   - **Example format**:

     ```text
     bà
     ba
     bá

     cà
     ca
     cá
     ```

## Usage

Run the script using Python, specifying the path to your Anki media directory:

```bash
python minimal-pairs.py /path/to/anki/media
```

**Example:**

```bash
python minimal-pairs.py "~/Anki/User 1 collection.media"
```

## Output

Upon execution, the script generates the following:

1. **Audio Files**: For each unique text, two `.wav` files are created (one female and one male voice) in the specified Anki media directory.

   - **Naming Convention**:

     - **Female Voice**: `google-tts_vi-VN-Neural2-A_{text}, {text}.wav`
     - **Male Voice**: `google-tts_vi-VN-Neural2-D_{text}, {text}.wav`

     **Note:** The `{text}, {text}` part in the filename indicates that the audio file contains the text repeated twice, separated by a comma.

2. **Notes CSV**: A CSV file containing combinations of minimal pairs with references to their respective audio files.

   - The CSV file is saved in the `out/notes` directory with a timestamped filename (e.g., `note-2024-04-27-14h30m00s.csv`).

   - **CSV Structure**:

     Each row contains:

     - **Unique Key**: Combination of two texts (e.g., `bà,ba`)
     - **Female Audio of First Text**: `[sound:google-tts_vi-VN-Neural2-A_{first text}, {first text}.wav]`
     - **Male Audio of First Text**: `[sound:google-tts_vi-VN-Neural2-D_{first text}, {first text}.wav]`
     - **First Text**
     - **Female Audio of Second Text**: `[sound:google-tts_vi-VN-Neural2-A_{second text}, {second text}.wav]`
     - **Male Audio of Second Text**: `[sound:google-tts_vi-VN-Neural2-D_{second text}, {second text}.wav]`
     - **Second Text**

   These notes can then be imported into Anki for study.

## Additional Tool: Standalone Text-to-Speech Script

The `tts.py` script allows you to generate audio files for individual texts.

### Usage

Run the script with the desired text. Optionally, specify the voice gender.

```bash
python tts.py "your text here" [--gender GENDER]
```

- **Arguments**:
  - `text`: The text to synthesize.
  - `--gender`: Specify the voice gender (0 for male, 1 for female). If not provided, a random gender is chosen.

**Example:**

```bash
python tts.py "xin chào" --gender 1
```

This generates an audio file for "xin chào" using the female voice.

### Output

- The audio file is saved in the `out/standalone-audio` directory.
- **Naming Convention**: `google-tts_{voice_name}_{text}.wav`

## Notes

- Ensure that the `GOOGLE_APPLICATION_CREDENTIALS` environment variable is correctly set before running the scripts.
- The generated audio files are designed to be compatible with Anki's media folder and note format.
- If you modify the input file or the script, rerun the script to update the audio files and notes.
- The scripts use specific Google Cloud voices (`vi-VN-Neural2-A` for female and `vi-VN-Neural2-D` for male) to maintain consistency.
