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

    print("Скачиваю картинку...")
image_response = requests.get(image_url)

if image_response.status_code == 200:
    file_name = image_url.split("/")[-1]
    print(f"Имя файла: {file_name}")

    # Создаём папку на Яндекс.Диске
    print("Создаю папку на Яндекс.Диске...")
    folder_name = breed
    url_create = "https://cloud-api.yandex.net/v1/disk/resources"
    headers = {"Authorization": f"OAuth {yd_token}"}
    params = {"path": folder_name}

    response = requests.put(url_create, headers=headers, params=params)

    if response.status_code == 201:
        print("Папка создана")
    elif response.status_code == 409:
        print("Папка уже существует")
    else:
        print("Ошибка создания папки")
else:
    print("Не удалось скачать картинку")
