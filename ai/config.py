class Config:
    def __init__(self,
                 openai_api="../ai/data/apikey.txt",
                 prompt_report="../ai/data/prompt/prompt_v3.txt",
                 prompt_animal="../ai/data/prompt/prompt_animal.txt",
                 prompt_dolphon="../ai/data/prompt/prompt_dolphon.txt",
                 prompt_garden="../ai/data/prompt/prompt_garden.txt",
                 prompt_music="../ai/data/prompt/prompt_music.txt",
                 prompt_teddybear="../ai/data/prompt/prompt_teddybear.txt",
                 chroma_directory="../ai/chroma",
                 openai_embedding="text-embedding-3-large",
                 openai_chat="gpt-4o",
                 json_jq_schema='.[].history[].[1]',
                 audio_path="../backend/uploads/recording.wav",
                #  filename="../ai/data/audio/welcome.mp3"
                 ):
        self.openai_api = openai_api
        self.prompt_report = prompt_report
        self.prompt_animal = prompt_animal
        self.prompt_dolphon = prompt_dolphon
        self.prompt_garden = prompt_garden
        self.prompt_music = prompt_music
        self.prompt_teddybear = prompt_teddybear
        self.chroma_directory = chroma_directory
        self.openai_embedding = openai_embedding
        self.openai_chat = openai_chat
        self.json_jq_schema = json_jq_schema
        self.audio_path = audio_path
        # self.filename = filename
