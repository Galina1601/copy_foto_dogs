import requests
import json
import sys


breed = input ("Введите породу собаки (по английски:")
yd_token = input ("Введите токен Яндекса:")
print ("Получение фото")
url_breeds = f"https://dog.ceo/api/breeds/list/all"
response_breeds = requests.get(url_breeds)
if response_breeds.status_code != 200:
    print("Ошибка получения списка пород")
    sys.exit(0)

    breeds_data = response_breeds.json()['message']
    if breed not in breeds_data:
        print ("Такой породы нет")
        sys.exit(0)
        sub_breeds = breeds_data[breed]
        # Создание папки
url_create_folder = 'https://cloud-api.yandex.net/v1/disk/resources'
headers = {'Authorization': f'OAuth {yd_token}'}
params = {'path': breed}
response = requests.put(url_create_folder, headers=headers, params=params)

if response.status_code == 201:
    print('Папка создана')
elif response.status_code == 409:
    print('Папка уже существует')
else:
    print('Ошибка создания папки')
    sys.exit(0)

# Словарь для отчёта
report = {}





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
if response.status_code == 201 or response.status_code == 409:
    print("Получаю ссылку для загрузки...")

    url_upload = "https://cloud-api.yandex.net/v1/disk/resources/upload"
    params = {"path": f"{folder_name}/{file_name}", "overwrite": "true"}

    response = requests.get(url_upload, headers=headers, params=params)

    if response.status_code == 200:
        upload_url = response.json()["href"]

        print("Загружаю файл на Яндекс.Диск...")
        with open(file_name, "wb") as f:
            f.write(image_response.content)

        with open(file_name, "rb") as f:
            upload_response = requests.put(upload_url, files={"file": f})

        if upload_response.status_code in [200, 201]:
            print("Файл успешно загружен")

            # Сохраняем отчёт
            print("Сохраняю отчёт...")
            report = [{
                "breed": breed,
                "file_name": file_name,
                "size": len(image_response.content),
                "url": image_url,
                "remote_path": f"{folder_name}/{file_name}"
            }]

            with open("report.json", "w", encoding="utf-8") as f:
                json.dump(report, f, ensure_ascii=False, indent=2)

            print("Отчёт сохранён в файл report.json")
        else:
            print("Ошибка загрузки")
    else:
        print("Не удалось получить ссылку для загрузки")