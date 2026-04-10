from vosk import Model, KaldiRecognizer
import torch
import time
import sounddevice as sd
import queue
import sys
import json

voskModel = Model("model")
rec = KaldiRecognizer(voskModel, 16000)
device = torch.device("cpu")
torch.set_num_threads(4)
variant = "v4_ru"

print("Загрузка модели синтеза речи...")
model, _ = torch.hub.load(repo_or_dir='snakers4/silero-models',
                          model='silero_tts',
                          language='ru',
                          speaker=variant)
model.to(device)

data_queue = queue.Queue()


def callback(indata, frames, time, status):
    if status:
        print(status, file=sys.stderr)
    data_queue.put(bytes(indata))


# Создаем поток, но пока не запускаем через with
stream = sd.RawInputStream(samplerate=16000, blocksize=8000, device=None,
                           dtype='int16', channels=1, callback=callback)


def synth(text, speaker='xenia', rate='medium'):
    ssml_payload = (
        f'<speak>'
        f'<prosody rate="{rate}">'
        f'<break time="200ms"/>{text}<break time="500ms"/>'
        f'</prosody>'
        f'</speak>'
    )
    audio = model.apply_tts(ssml_text=ssml_payload, speaker=speaker, sample_rate=24000)
    sd.play(audio.numpy(), 24000)
    sd.wait()  # Ждем окончания

try:
    stream.start()
    print("\nСЛУШАЮ...")

    while True:
        data = data_queue.get()
        if rec.AcceptWaveform(data):
            result_json = json.loads(rec.Result())
            text = result_json.get("text", "")

            if text:
                print(f"Вы сказали: {text}")
                stream.stop()
                synth(text)
                with data_queue.mutex:
                    data_queue.queue.clear()
                stream.start()
                print("Слушаю снова...")

except KeyboardInterrupt:
    print("\nПрограмма остановлена.")
finally:
    stream.close()