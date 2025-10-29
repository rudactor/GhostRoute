# GhostRoute

**Стек:**

* **Протокол:** VLESS
* **Панель узлов:** **Marzban** (управляет юзерами/подписками/узлами)
* **Backend:** FastAPI (тонкий шлюз к API Marzban + своя авторизация/JWT)
* **Mobile:** React Native (Android/iOS) — авторизация, выбор узла/тарифа, получение `vless://`/QR

---

## Архитектура (коротко)

```
RN App ──HTTPS──► FastAPI (GhostRoute API) ──► Marzban API ──► Узлы VLESS
             ▲             │
             └──── JWT ────┘
```

* **Marzban** хранит пользователей, планы, подписки, трафик, генерирует VLESS-конфиги.
* **FastAPI**: ваша бизнес-логика, собственные аккаунты, лимиты, биллинг (опц.), кэш витрин.
* **Мобильное приложение**: логин, просмотр планов/узлов, получение `vless://`/QR, просмотр статистики.

---

## Backend (FastAPI) — ENV

`.env` пример:

```
APP_NAME=GhostRoute
ENV=dev
SECRET_KEY=change_me

# Marzban
MARZBAN_BASE_URL=https://marzban.example.com
MARZBAN_API_KEY=xxxxx   # admin token
MARZBAN_TIMEOUT=10

# CORS
CORS_ORIGINS=["http://localhost:19006","http://localhost:8081"]
```

### Минимальные эндпоинты

* `GET /health` — жив ли шлюз
* `POST /auth/login` — ваш логин → JWT (внутренняя учётка GhostRoute)
* `GET /catalog/plans` — список тарифов из Marzban
* `GET /catalog/nodes` — список узлов/регионов (агрегация из Marzban)
* `POST /subscriptions` — создать/продлить подписку (создать/обновить user в Marzban, назначить план, дедлайн/трафик)
* `GET /subscriptions/{id}` — статус (трафик used/limit, expiry)
* `GET /subscriptions/{id}/config` — **VLESS**: `vless://...` + QR (base64 PNG/SVG)
* `POST /me/devices/register` — регистрируем устройство (fingerprint)
* `GET /me/usage` — агрегированная статистика по Marzban

> Все «мутации» делаются через **Marzban API** (админ-токен), GhostRoute только валидирует и кэширует.

### Быстрый запуск

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

---

## Mobile (React Native)

* Экраны: **Login → Plans → Nodes → MySub → Get Config**
* Получение `vless://` + QR с `/subscriptions/{id}/config`.
* Кнопки: **Copy**, **Show QR**, **Open in…** (передача `vless://` в установленный клиент или сохранение в файл).
* Токены хранить в **SecureStore/Keychain**.

`.env`

```
API_BASE_URL=http://192.168.0.10:8000
```

---

## Примеры ответов

`GET /catalog/plans`

```json
[
  {"id":"basic-50","name":"Basic 50GB","traffic_gb":50,"period_days":30,"price":0},
  {"id":"pro-200","name":"Pro 200GB","traffic_gb":200,"period_days":30,"price":0}
]
```

`GET /subscriptions/123/config`

```json
{
  "uri": "vless://UUID@host:443?encryption=none&security=reality&sni=...#GhostRoute-Pro",
  "qr": "data:image/png;base64,iVBORw0KGgo..."
}
```

---

## Подключение к Marzban (шлюз)

* Авторизация к Marzban: заголовок `Authorization: Bearer <MARZBAN_API_KEY>`.
* Основные операции:

  * **Создать/обновить пользователя** (`/api/user`) с лимитами трафика/сроком.
  * Получить **линки**/подписки пользователя (`/api/user/{username}` → links).
  * Статистика трафика и expiry — также из `/api/user/...`.

> Рекомендуется кэшировать справочники (планы/узлы) на 60–300с.

---

## Безопасность

* Только **HTTPS**; ограничить CORS, включить rate-limit на мутации.
* Админ-токен Marzban хранить как секрет, не возвращать в ответы.
* Логи — без чувствительных данных.
* Опционно: сертификат-пиннинг в мобильном клиенте.

---

## Ограничения приложения

* GhostRoute **не** выполняет системный VPN внутри RN. Он **выдаёт конфиг** (`vless://`/QR) для клиента, поддерживающего VLESS, или для системного VPN-профиля через нативный модуль (если вы добавите его отдельно).
* Инструкции по обходу ограничений не предоставляются.

---

## Roadmap (по делу)

* [ ] Локальные роли (user/admin) + аудит
* [ ] Квоты/лифты (soft/hard cap), уведомления о 80/100%
* [ ] Вебхуки/CRON: авто-продление, авто-дизабл просроченных
* [ ] Локализация RU/EN, тёмная тема
* [ ] E2E Detox + simple CI
