---
name: pinterest
description: Интеграция с Pinterest API v5. Позволяет создавать и читать пины, управлять досками, получать данные профиля и аналитику. Используйте этот навык, когда пользователю нужно автоматизировать работу с Pinterest или получить данные из своего аккаунта.
---

# Pinterest API v5 Skill

Этот навык предоставляет инструменты и инструкции для работы с Pinterest API v5.

## Быстрый старт

1. **Создайте приложение**: Следуйте гайду в [references/setup_guide.md](references/setup_guide.md), чтобы получить `App ID` и `App Secret`.
2. **Получите токен**: Запустите скрипт авторизации:
   ```bash
   python3 scripts/auth.py
   ```
   Скрипт откроет браузер, проведет OAuth-авторизацию и выведет `Access Token`.

## Основные возможности

### 1. Управление Пинами (Pins)
- **Создание пина**: `POST /v5/pins`
- **Получение информации о пине**: `GET /v5/pins/{pin_id}`
- **Удаление пина**: `DELETE /v5/pins/{pin_id}`

### 2. Управление Досками (Boards)
- **Создание доски**: `POST /v5/boards`
- **Список досок**: `GET /v5/boards`
- **Пины на доске**: `GET /v5/boards/{board_id}/pins`

### 3. Аналитика
- **Аналитика аккаунта**: `GET /v5/user_account/analytics`
- **Аналитика пинов**: `GET /v5/pins/{pin_id}/analytics`

Подробный список эндпоинтов и примеров запросов см. в [references/api_reference.md](references/api_reference.md).

## Примеры использования

### Создание пина (Heuristics)
При создании пина обязательно укажите `board_id` и `media_source`. 
Пример тела запроса:
```json
{
  "title": "My Awesome Pin",
  "description": "Check this out!",
  "board_id": "123456789",
  "media_source": {
    "source_type": "image_url",
    "url": "https://example.com/image.jpg"
  }
}
```

### Получение всех досок
Используйте `GET /v5/boards`, чтобы найти нужный `board_id` перед созданием пина.
