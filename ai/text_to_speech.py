from gtts import gTTS
import pygame
import os
from config import Config


async def text_to_speech(text):
    language = 'en-us'

    if os.path.exists(Config().filename):
        os.remove(Config().filename)
    myobj = gTTS(text=text, lang=language, slow=False)

    try:
        myobj.save(Config().filename)
    except PermissionError:
        print(f"Permission denied: Unable to save file to {Config().filename}")
        return

    pygame.mixer.init()
    pygame.mixer.music.load(Config().filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)
    pygame.mixer.music.stop()
    pygame.mixer.quit()


if __name__ == '__main__':
    text_to_speech("“Hey there, little buddy! How exciting! If you could create something amazing at the fair, what would it be? I’d love to hear your ideas!”")
