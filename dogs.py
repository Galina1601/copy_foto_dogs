import requests
import json
import sys

#  Функция № 1
def look_for_breed(breed):
    try:
        url = "https://dog.ceo/api/breeds/list/all"
        response = requests.get(url, timeout=30)

        if response.status_code != 200:
            print("Ошибка получения списка пород")
            sys.exit(1)

        breeds_data = response.json()['message']

        if breed not in breeds_data:
            print('Такой породы нет')
            sys.exit(0)

        return breeds_data[breed]

    except:
        print('Ошибка при проверке породы')
        sys.exit(0)


#  Функция № 2
def make_folder(breed, token):
    try:
        url = "https://cloud-api.yandex.net/v1/disk/resources"
        headers = {'Authorization': f'OAuth {token}'}
        params = {'path': breed}

        response = requests.put(url, headers=headers, params=params, timeout=30)

        print(f"Код ответа: {response.status_code}")
        print(f"Текст ответа: {response.text}")

        if response.status_code == 201:
            print("Папка создана")
        elif response.status_code == 409:
            print("Папка уже существует")
        else:
            print("Ошибка создания папки")
            sys.exit(1)

    except:
        print("Ошибка при создании папки")
        sys.exit(1)



#  Функция №3
def copy_photo(breed, sub_breed):
    try:
        if sub_breed:
            url = f"https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random"
        else:
            url = f"https://dog.ceo/api/breed/{breed}/images/random"


        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print("Ошибка получения картинки")
            return None, None, None

        image_url = response.json()['message']
        print(f"URL картинки: {image_url}")

        if sub_breed:
            file_name = f"{breed}_{sub_breed}_{image_url.split('/')[-1]}"
        else:
            file_name = f"{breed}_{image_url.split('/')[-1]}"

        print(f"URL картинки: {image_url}")
        print(f"Имя файла: {file_name}")


        try:
            img_response = requests.get(image_url, timeout=30)
            if img_response.status_code != 200:
                print('Ошибка скачивания')
                return None, None, None
        except:
            print("Ошибка скачивания (сайт не отвечает)")
            return None, None, None

        if img_response.status_code != 200:
            print("Ошибка скачивания (плохой статус)")
            return None, None, None

        if len(img_response.content) < 1000:
            print("Фото слишком маленькое")
            return None, None, None

        print(f"Размер: {len(img_response.content)} байт")
        return img_response.content, file_name, image_url

    except:
        print("Ошибка при получении фото")
        return None, None, None


    # ФУНКЦИЯ 4: Загрузка на Яндекс-диск
def upload_photo(photo_data, file_name, breed, token):
    try:
        url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
        headers = {'Authorization': f'OAuth {token}'}
        params = {'path': f"{breed}/{file_name}"}

        response = requests.get(url, headers=headers, params=params, timeout=30)

        if response.status_code != 200:
            print("Ошибка получения ссылки")
            return "False"

        upload_url = response.json()['href']

        put_response = requests.put(upload_url, data=photo_data, timeout=30)

        if put_response.status_code in [200, 201]:
            print(f"Загружено: {file_name}")
            return "True"
        else:
            print(f"Ошибка загрузки")
            return "False"

    except:
        print("Ошибка при загрузке")
        return "False"

breed = input("Введите породу собаки (по-английски): ").lower().strip()
token = input("Введите токен Яндекса: ")

sub_breeds = look_for_breed(breed)
print(f"Найдены подпороды: {sub_breeds}")




make_folder(breed, token)


report = {}

if sub_breeds:
    for sub in sub_breeds:
        print(f"\n Обрабатываю подпороду: {sub} ")
        photo_data, file_name, image_url = copy_photo(breed, sub)
        if photo_data:
            result = upload_photo(photo_data, file_name, breed, token)
            if result == "True":
                report[file_name] = {
                    "порода": breed,
                    "подпорода": sub,
                    "url": image_url,
                    "путь": f"{breed}/{file_name}",
                    "размер": len(photo_data)
                }
else:
    print("\n Нет подпород, загружаю основную породу ")
    photo_data, file_name, image_url = copy_photo(breed, None)
    if photo_data:
        result = upload_photo(photo_data, file_name, breed, token)
        if result == "True":
            report[file_name] = {
                "порода": breed,
                "подпорода": "нет",
                "url": image_url,
                "путь": f"{breed}/{file_name}",
                "размер": len(photo_data)
            }

with open('report.json', 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=2)

print(f"\n+ Загружено файлов: {len(report)}")
print("Отчёт сохранён в report.json")


