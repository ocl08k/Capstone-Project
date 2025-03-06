import librosa
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import asyncio


async def speech_to_text(file, processor_whisper, model_whisper):
    audio, sampling_rate = librosa.load(file, sr=None)
    if sampling_rate != 16000:
        audio = librosa.resample(audio, orig_sr=sampling_rate, target_sr=16000)
        sampling_rate = 16000
    input_features = processor_whisper(audio, sampling_rate=sampling_rate, return_tensors="pt").input_features
    forced_decoder_ids = processor_whisper.get_decoder_prompt_ids(language='en', task="transcribe")
    predicted_ids = model_whisper.generate(input_features, forced_decoder_ids=forced_decoder_ids)
    transcription = processor_whisper.batch_decode(predicted_ids, skip_special_tokens=True)
    return transcription


async def loading_model():
    processor_whisper = WhisperProcessor.from_pretrained("openai/whisper-small")
    model_whisper = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")
    return processor_whisper, model_whisper


if __name__ == '__main__':
    processor, model = asyncio.run(loading_model())
    file_path = "data/audio/output.wav"
    text = asyncio.run(speech_to_text(file_path, processor, model))
    print(text[0])
