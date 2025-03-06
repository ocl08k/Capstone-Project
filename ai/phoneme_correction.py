import json
import re
import subprocess
import wave
import dotenv
import pyaudio
import requests
from sequence_align.pairwise import needleman_wunsch
from speech_to_text_model import loading_model, speech_to_text
import asyncio
from config import Config
import os

dotenv.load_dotenv()

# HF INFERENCE API
#headers = {"Authorization": f"Bearer {API_TOKEN}"}

#PHONEME_API_URL = "https://api-inference.huggingface.co/models/mrrubino/wav2vec2-large-xlsr-53-l2-arctic-phoneme"


async def remove_ansi_escape_sequences(text):
    ansi_escape = re.compile(r'\x1b\[[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', text)


async def query(filename, API_URL):
    with open(filename, "rb") as f:
        data = f.read()
    response = requests.request("POST", API_URL, headers=headers, data=data,
                                json={"options": {"wait_for_model": True, "return_timestamps": True}})
    return json.loads(response.content.decode("utf-8"))


async def record_audio(duration, filename):
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    print("Recording...")

    frames = []

    for i in range(0, int(RATE / CHUNK * duration)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Recording finished.")

    stream.stop_stream()
    stream.close()
    p.terminate()

    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(p.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()


async def generate_reference_phoneme(reference_text):
    # Remove ANSI escape sequences before processing
    clean_text = await remove_ansi_escape_sequences(reference_text)
    text = re.sub(r'[;:,.!"?()]', '', clean_text)
    ref_words = [w.lower() for w in text.strip().split() if w]

    lexicon = []
    for word in ref_words:
        try:
            result = subprocess.run(['espeak', '-q', '--ipa', word], capture_output=True, text=True)
            phonemes = result.stdout.strip()
            phonemes = re.sub(r'[ˈˌ]', '', phonemes)
            lexicon.append((word, phonemes))
        except Exception as e:
            print(f"Error processing word '{word}': {e}")
            lexicon.append((word, ''))

    return lexicon, ref_words


async def find_word_start_positions(reference_sequence):
    words = reference_sequence.split()
    start_positions = []
    current_position = 0
    for word in words:
        start_positions.append(current_position)
        current_position += len(word) + 1
    return start_positions


async def split_recorded_sequence(recorded_sequence, start_positions):
    split_words = []
    for i in range(len(start_positions)):
        start = start_positions[i]
        if i == len(start_positions) - 1:
            end = len(recorded_sequence)
        else:
            end = start_positions[i + 1]
        word = recorded_sequence[start:end]
        split_words.append(word)
    return split_words


async def sentence_presentation(word_comparison_list, max_length):
    error_phonemes = []
    for w, ref_w, rec_w in word_comparison_list:
        word = f"\033[1m{w}\033[0m".ljust(max_length)
        rec_string = ""
        all_match = True

        for c1, c2 in zip(ref_w, rec_w):
            if c1 != c2:
                rec_string += f"\033[91m{c2}\033[0m"
                all_match = False
            else:
                rec_string += c2

        if all_match:
            rec_string = f"\033[92m{rec_w}\033[0m".ljust(max_length)

        rec_string = rec_string.ljust(max_length)

        if not all_match:
            error_phonemes.append(
                (
                    w, ref_w,
                    await remove_ansi_escape_sequences(rec_string)))  # Store original word without ANSI sequences

        # print(word, ref_w, rec_string)

    return error_phonemes


async def wait_for_file():
    while not os.path.exists(Config().audio_path):
        print(f"Wait for {Config().audio_path}...")
        await asyncio.sleep(0.1)
    print(f"File {Config().audio_path} found!")


async def delete_audio_files():
    if os.path.exists(Config().audio_path):
        os.remove(Config().audio_path)
        print(f"File {Config().audio_path} has been deleted.")
    else:
        print(f"File {Config().audio_path} not found.")


async def process_audio_and_compare():
    # print(f'Read out loud: "{reference_text}"')
    # await record_audio(duration=5, filename=Config().audio_path)
    # print("Audio recorded. Processing...")
    await wait_for_file()
    try:
        api_response = await query(Config().audio_path, PHONEME_API_URL)
        # print("API Response:", json.dumps(api_response, indent=2))
        if 'text' not in api_response:
            print("Error: 'text' key.txt not found in API response.")
            if 'error' in api_response:
                print("API Error:", api_response['error'])
            return None, None

        recorded_phoneme = api_response['text']
    except Exception as e:
        print(f"Error querying the API: {str(e)}")
        return None, None
    processor, model = await loading_model()
    reference_text = await speech_to_text(Config().audio_path, processor, model)
    reference_text = reference_text[0]
    await delete_audio_files()
    lexicon, ref_words = await generate_reference_phoneme(reference_text)
    reference_phoneme = ' '.join([phon for w, phon in lexicon])

    seq_a = reference_phoneme
    seq_b = list(recorded_phoneme.replace(' ', ''))

    aligned_seq_a, aligned_seq_b = needleman_wunsch(
        seq_a,
        seq_b,
        match_score=1.0,
        mismatch_score=-1.0,
        indel_score=-1.0,
        gap="_",
    )

    aligned_reference_seq = ''.join(aligned_seq_a)
    aligned_recorded_seq = ''.join(aligned_seq_b)

    ref_start_positions = await find_word_start_positions(''.join(aligned_reference_seq))

    rec_split_words = await split_recorded_sequence(''.join(aligned_recorded_seq), ref_start_positions)
    rec_split_words = [re.sub('( |\\_)$', '', w) for w in rec_split_words]

    ref_split_words = await split_recorded_sequence(''.join(aligned_reference_seq), ref_start_positions)
    ref_split_words = [re.sub('(\\_| )$', '', w) for w in ref_split_words]

    word_comparison_list = list(zip(ref_words, ref_split_words, rec_split_words))
    if not word_comparison_list:  # 检查列表是否为空
        max_length = 0  # 如果列表为空，则最长长度为0
    else:
        max_length = max(len(w) for w, _, _ in word_comparison_list)

    return word_comparison_list, max_length, reference_text


async def sentence_test():
    word_comparison_list, max_length, reference_text = await process_audio_and_compare()
    error_phonemes = await sentence_presentation(word_comparison_list, max_length)
    return error_phonemes, reference_text


if __name__ == '__main__':
    error_sentence, reference_text = asyncio.run(sentence_test())
    print(error_sentence)
    print(reference_text)
