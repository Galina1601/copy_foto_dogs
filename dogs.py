import requests
import json

print ("Программа для резервного копирования фото собак")

breed = input ("Введите породу собаки (например, hound:")
yd_token = input ("Введите токен Яндекс диска:")
print ("Получаю фото")
dog_url = f"https://dog.ceo/api/breed/{breed}/images/random"
response = requests.get(dog_url)

if response.status_code != 200:
    print("Такой породы нет")
else:
    image_url = response.json()["message"]
    print(f"Ссылка на картинку: {image_url}")