import requests
import json
import sys

breed = input("Введите породу собаки (по-английски): ")
breed = breed.lower().strip()
yd_token = input("Введите токен Яндекса: ")
print("Получение фото")

# Получаем список всех пород
url_breeds = "https://dog.ceo/api/breeds/list/all"
response = requests.get(url_breeds, timeout=10)

if response.status_code != 200:
    print("Ошибка получения списка пород")
    sys.exit(1)

breeds_data = response.json()['message']

if breed not in breeds_data:
    print("Такой породы нет")
    sys.exit(1)

sub_breeds = breeds_data[breed]

# Создание папки на Яндекс.Диске
url_create_folder = 'https://cloud-api.yandex.net/v1/disk/resources'
headers = {'Authorization': f'OAuth {yd_token}'}
params = {'path': breed}
response = requests.put(url_create_folder, headers=headers, params=params, timeout=10)

if response.status_code == 201:
    print('Папка создана')
elif response.status_code == 409:
    print('Папка уже существует')
else:
    print('Ошибка создания папки')
    sys.exit(1)

# Словарь для отчёта
report = {}

if sub_breeds:
    print(f"Найдены подпороды: {sub_breeds}")

    for sub in sub_breeds:
        print(f"\n Обрабатываю подпороду: {sub}")

        # Получаем случайную картинку для подпороды
        dog_url = f'https://dog.ceo/api/breed/{breed}/{sub}/images/random'
        print(f"Запрос к API: {dog_url}")
        response = requests.get(dog_url, timeout=10)

        if response.status_code != 200:
            print(f'Ошибка получения картинки для {sub}')
            continue

        image_url = response.json()['message']
        file_name = f"{breed}_{sub}_{image_url.split('/')[-1]}"
        print(f"URL картинки: {image_url}")
        print(f"Имя файла: {file_name}")

        # Скачиваем картинку
        print("начало скачивания.")
        try:
            response_image = requests.get(image_url, timeout=10)
            print(f"Статус скачивания: {response_image.status_code}")
            if response_image.status_code != 200:
                print(f'Ошибка скачивания {file_name}, статус {response_image.status_code}')
                continue
            data_image = response_image.content
            print(f"Размер: {len(data_image)} байт")
        except:
            print(f"Не удалось скачать {file_name} (таймаут или ошибка). Перехожу к следующей подпороде.")
            continue

        # Получаем ссылку для загрузки на Я.Диск
        url_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
        params = {'path': f'{breed}/{file_name}'}
        print('Запрашиваю ссылку.')
        upload_response = requests.get(url_upload, headers=headers, params=params, timeout=10)

        if upload_response.status_code != 200:
            print(f'Ошибка получения ссылки для {file_name}')
            continue

        upload_url = upload_response.json()['href']
        print("Ссылка для загрузки получена")

        # Загружаем на Я.Диск
        print('Загружаю файл на Я.Диск')
        put_response = requests.put(upload_url, data=data_image, timeout=10)
        print(f"Статус загрузки: {put_response.status_code}")

        if put_response.status_code in [200, 201]:
            print(f'Загружен: {file_name}')
            report[file_name] = len(data_image)
        else:
            print(f'Ошибка загрузки {file_name} (код {put_response.status_code})')

else:
        #  Подпород нет– загружаем одну картинку основной породы
    print("\n Нет подпород, загружаем основную породу ")

    dog_url = f'https://dog.ceo/api/breed/{breed}/images/random'
    print(f"Запрос к: {dog_url}")
    response = requests.get(dog_url, timeout=10)

    if response.status_code != 200:
        print('Ошибка получения картинки')
        sys.exit(1)

    image_url = response.json()['message']
    file_name = f"{breed}_{image_url.split('/')[-1]}"
    print(f"URL картинки: {image_url}")
    print(f"Имя файла: {file_name}")

    # Скачиваем картинку
    print("Начинаю скачивание картинки...")
    img_response = requests.get(image_url, timeout=10)

    if img_response.status_code != 200:
        print('Ошибка скачивания')
        sys.exit(1)

    print(f"Размер: {len(img_response.content)} байт")

    # Получаем ссылку для загрузки на Я.Диск
    url_upload = 'https://cloud-api.yandex.net/v1/disk/resources/upload'
    params = {'path': f'{breed}/{file_name}'}
    print("Запрашиваю ссылку для загрузки...")
    upload_response = requests.get(url_upload, headers=headers, params=params, timeout=10)
    print(f"Статус получения ссылки: {upload_response.status_code}")

    if upload_response.status_code != 200:
        print('Ошибка получения ссылки')
        sys.exit(1)

    upload_url = upload_response.json()['href']
    print("Ссылка для загрузки получена")

    # Загружаем на Я.Диск
    print("Загружаю файл на Яндекс.Диск...")
    put_response = requests.put(upload_url, data=img_response.content, timeout=10)
    print(f"Статус загрузки: {put_response.status_code}")
        
    if put_response.status_code in [200, 201]:
        print(f'Загружен: {file_name}')
        report[file_name] = len(img_response.content)
    else:
        print(f'Ошибка загрузки (код {put_response.status_code})')

# Сохраняем отчёт в JSON
with open('report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print(f'\nОтчёт сохранён в report.json. Загружено файлов: {len(report)}')