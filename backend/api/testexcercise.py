import requests
import json

def test_audio_transcription():
    url = 'http://localhost:8001/api/transcribe-audio/'
    audio_file_path = 'test_audio.wav'
    
    try:
        with open(audio_file_path, 'rb') as audio_file:
            headers = {
            }
            files = {
                'audio': ('test_audio.mp3', audio_file, 'audio/mpeg')
            }
            response = requests.post(url, headers=headers, files=files)
            print("Status Code:", response.status_code)
            print("Response:", json.dumps(response.json(), indent=2))
            
    except FileNotFoundError:
        print(f"Error: Audio file not found at {audio_file_path}")
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    test_audio_transcription()