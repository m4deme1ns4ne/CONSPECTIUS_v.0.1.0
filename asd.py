from speechkit import ShortAudioRecognition


# Читаем файл
with open('voice.wav', 'rb') as f:
    data = f.read()
    
# Создаем экземпляр класса с помощью `session` полученного ранее
recognizeShortAudio = ShortAudioRecognition(session)

# Передаем файл и его формат в метод `.recognize()`, 
# который возвращает строку с текстом
text = recognizeShortAudio.recognize(
		data, format='lpcm', sampleRateHertz='48000')
print(text)