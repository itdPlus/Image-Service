# Winner Card Generator

Микросервис на FastAPI, который генерирует PNG-карточку победителя по имени, никнейму и эмодзи-аватару.

## Как это работает

Сервис принимает POST-запрос с данными пользователя, накладывает их на шаблон (`blank.jpg`) и возвращает готовое PNG-изображение.

## Требования

- Python 3.12+
- Либо Docker

## Запуск

### Локально

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8001
```

### Docker

```bash
docker build -t winner-card .
docker run -p 8001:8001 winner-card
```

После запуска сервис доступен на `http://localhost:8001`.  
Swagger UI — `http://localhost:8001/docs`.

## API

### `POST /save`

Генерирует карточку и возвращает PNG-файл.

**Тело запроса (JSON):**

| Поле          | Тип     | Обязательно | Описание                                    |
|---------------|---------|-------------|---------------------------------------------|
| `avatar`      | string  | ✅          | Эмодзи-аватар                               |
| `displayName` | string  | ✅          | Отображаемое имя (белый текст)              |
| `username`    | string  | ✅          | Никнейм (золотой текст, `@` добавляется автоматически) |
| `verified`    | boolean | ❌          | Показывать галочку верификации (по умолчанию `false`) |

**Пример запроса:**

```bash
curl -X POST http://localhost:8001/save \
  -H "Content-Type: application/json" \
  -d '{"avatar":"🏆","displayName":"Иван Иванов","username":"ivan","verified":true}' \
  --output card.png
```

```python
import requests

response = requests.post(
    "http://localhost:8001/save",
    json={
        "avatar": "🏆",
        "displayName": "Иван Иванов",
        "username": "ivan",
        "verified": True,
    },
)

with open("card.png", "wb") as f:
    f.write(response.content)
```

## Кастомизация

Все константы для позиционирования и стилей собраны в начале `main.py`:

| Константа                | Описание                                          |
|--------------------------|---------------------------------------------------|
| `FONT_SIZE_DISPLAY_NAME` | Размер шрифта имени                               |
| `FONT_SIZE_USERNAME`     | Размер шрифта никнейма                            |
| `FONT_SIZE_EMOJI`        | Размер эмодзи-аватара                             |
| `AVATAR_CENTER_X/Y`      | Центр области аватара на шаблоне                  |
| `EMOJI_OFFSET_X/Y`       | Точная подстройка позиции эмодзи                  |
| `DISPLAY_NAME_Y`         | Y-координата имени (X центрируется автоматически) |
| `USERNAME_Y`             | Y-координата никнейма                             |
| `COLOR_DISPLAY_NAME`     | Цвет имени (RGBA)                                 |
| `COLOR_USERNAME`         | Цвет никнейма (RGBA)                              |
| `VERIFICATION_CHECK_SIZE`| Размер иконки верификации (px)                    |
| `VERIFICATION_CHECK_GAP` | Отступ между именем и иконкой верификации         |

Чтобы поменять шаблон — замените `blank.jpg`, не меняя имя файла. Чтобы поменять шрифт — замените `OnestVariable.ttf` (нужен Variable Font с осью `wght`).

## Зависимости

| Пакет     | Назначение                            |
|-----------|---------------------------------------|
| FastAPI   | Веб-фреймворк                         |
| Uvicorn   | ASGI-сервер                           |
| Pillow    | Работа с изображениями                |
| pilmoji   | Корректный рендеринг цветных эмодзи   |
| Pydantic  | Валидация входящих данных             |
