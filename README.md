# GhostRoute

**GhostRoute** — мобильное приложение (Android/iOS) с встроенным VPN-подключением по протоколу **VLESS**.

* **Backend:** FastAPI (связь с панелью **Marzban**).
* **Mobile:** React Native (bare, с нативными модулями) + sing-box/xray-core (через Android VpnService / iOS Network Extension).
* **Протокол:** VLESS (конфиги генерируются в Marzban и применяются прямо в приложении).


---

## 🚀 Функционал

* Авторизация пользователя (FastAPI + JWT).
* Получение доступных тарифов и узлов (из Marzban).
* Управление подпиской: активация, продление, просмотр статуса (трафик, срок).
* **Подключение VPN прямо в приложении**:

  * Android → `VpnService` + sing-box core.
  * iOS → `PacketTunnelProvider` (Network Extension) + sing-box core.
* Управление подключением: **Connect / Disconnect**, отображение скорости и трафика.
* Экспорт/копирование `vless://` и QR (опционально).

---

## 🧭 Архитектура

```
React Native (UI)
   │
   ▼
Native modules:
   ├─ Android: VpnService + sing-box AAR
   └─ iOS: NEPacketTunnelProvider + sing-box xcframework
   │
   ▼
Core (sing-box/xray) → Проксирование VLESS
   │
   ▼
Marzban → VLESS узлы/Xray
   │
   ▼
Интернет
```

**FastAPI** выступает как шлюз:

* `/auth` — авторизация (JWT).
* `/catalog` — тарифы/узлы.
* `/subscriptions` — подписки.
* `/config` — отдаёт нормализованный JSON-конфиг для core.

---

## 📦 Технологии

* **Backend**: Python 3.11+, FastAPI, SQLAlchemy/SQLModel, PostgreSQL/SQLite, Redis (кэш), Docker.
* **Marzban**: панель управления Xray (VLESS), API-токен.
* **Mobile**: React Native bare (Android/iOS), sing-box/xray-core (через gomobile), react-navigation, react-query, SecureStore/Keychain.

---

## 📁 Структура проекта

```
ghostroute/
├─ backend/         # FastAPI
│  ├─ app/
│  │  ├─ api/       # auth, catalog, subscriptions
│  │  ├─ core/      # config, security
│  │  ├─ models/    # user, subscription
│  │  └─ services/  # marzban client
│  └─ tests/
├─ mobile/          # React Native
│  ├─ android/      # VpnService + sing-box AAR
│  ├─ ios/          # PacketTunnelExtension + sing-box
│  ├─ src/          # RN UI (screens, api, hooks)
│  └─ native/       # JS bridge к VPN модулям
└─ docker/
```

---

## 🔧 Требования

* **Backend:** Python 3.11+, Docker, PostgreSQL (или SQLite dev).
* **Mobile:** Node 18+, Yarn, Xcode (iOS), Android Studio (Android).
* **Сборка core:** Go + gomobile (для sing-box/xray).

---

## 🏃 Быстрый старт (Dev)

### Backend

```bash
cd backend
cp .env.example .env
uvicorn app.main:app --reload --port 8000
```

### Mobile

```bash
cd mobile
yarn install
# Android
yarn android
# iOS
cd ios && pod install && cd ..
yarn ios
```

---

## ⚙️ Конфигурация

### Backend `.env`

```
APP_NAME=GhostRoute
SECRET_KEY=change_me
MARZBAN_BASE_URL=https://panel.example.com
MARZBAN_API_KEY=your_admin_token
DATABASE_URL=sqlite:///./ghostroute.db
```

### Mobile `.env`

```
API_BASE_URL=http://192.168.0.10:8000
```

---

## 📱 Основные экраны (RN)

* **Login** — авторизация.
* **Plans** — список тарифов.
* **Nodes** — доступные сервера.
* **My Subscription** — трафик, дата окончания.
* **Connect** — кнопка Connect/Disconnect, статус VPN, скорость.
* **Settings** — язык, тема.

---

## 🔌 Пример API → Core

`GET /subscriptions/{id}/config`

```json
{
  "outbounds": [
    {
      "type": "vless",
      "server": "example.com",
      "server_port": 443,
      "uuid": "UUID",
      "tls": {
        "enabled": true,
        "server_name": "sni.example.com"
      }
    }
  ],
  "inbounds": [
    { "type": "tun", "inet4_address": "10.0.0.2/30", "mtu": 1500 }
  ]
}
```

---

## 🔐 Безопасность

* HTTPS везде (API + Marzban).
* JWT access+refresh.
* Rate limiting на бекенде.
* SecureStore/Keychain для токенов.
* Опционально certificate pinning в мобильном.

---

## 📈 Roadmap

**Фаза 1 (MVP)**

* FastAPI: auth, catalog, subscriptions.
* Android: VpnService + sing-box, Connect/Disconnect.
* RN UI: Login, Plans, Nodes, Connect.

**Фаза 2**

* iOS: Network Extension (PacketTunnelProvider).
* Usage stats (трафик, скорость).
* Уведомления о 80/100% лимита.

**Фаза 3**

* CI/CD (GitHub Actions: backend build + mobile EAS/Gradle/Xcode).
* Мониторинг (Prometheus, Grafana, Sentry).
* Локализация, dark mode.
