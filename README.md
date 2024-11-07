# Vietnamese Minimal Pairs Anki Notes Creator


This is a tool designed to assist me in creating audio materials for practicing Vietnamese minimal pairs in Anki.
Minimal pairs are pairs of words or phrases in a language that differ by only a single sound, which can help in distinguishing similar sounds.
E.g. the Vietnamese words *cũng* and *cúng*.

This tool automates the process of generating audio files using Google Cloud Text-to-Speech, and creating accompanying notes for easy import into Anki.

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
   - Example format:
        ```text
        bà
        ba
        bá

        cà
        ca
        cá
        ```

## Usage

Run the script using Python, specifying the path to your Anki media directory.

```bash
python main.py /path/to/anki/media
```

**Example:**

```bash
python main.py "~/Anki/User\ 1\ collection.media"
```

## Output

Upon execution, the script generates the following:

1. **Audio Files**: For each unique text, two `.wav` files are created (one female and one male voice) in the specified Anki media directory.

   - Naming convention:
     - Female voice: `tts-viet-{text}-female.wav`
     - Male voice: `tts-viet-{text}-male.wav`

2. **Notes CSV**: A CSV file containing combinations of minimal pairs with references to their respective audio files.
This file is saved in the `out-notes` directory with a timestamped filename (e.g., `note-2024-04-27-14h30m00s.csv`).

   - **CSV Structure**:
     - Each row contains:
       - Unique Key: Combination of two texts (e.g., `bà,ba`)
       - Reference to the female audio of the first text
       - Reference to the male audio of the first text
       - First text
       - Reference to the female audio of the second text
       - Reference to the male audio of the second text
       - Second text

    These notes can then be imported into Anki.
