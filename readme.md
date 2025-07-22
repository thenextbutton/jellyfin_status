# 🎬 Jellyfin Status for Home Assistant

Track real-time playback sessions from your Jellyfin media server — complete with user-friendly status updates, emoji-enhanced telemetry, and full multilingual support.

> ⚠️ **Note:** This integration is currently a work in progress. Functionality and translations may evolve as features are refined.

---

## 📦 Features

- 🧠 Reports "Active" or "Idle" status based on session playback  
- 👤 Lists who’s watching or listening, including media types and titles  
- 🎵 Supports 🎬 Movies, 📺 TV Episodes, 🎵 Audio — all with smart emoji  
- 🌍 Multilingual UI: English, German, French, Spanish, Chinese, Japanese, and more  
- 🛠️ Configurable polling, HTTPS flags, and server display name  
- 🎛️ Lovelace-friendly attributes for dashboards and cards  

---

## 🚀 Installation

Install via [HACS](https://hacs.xyz/) or manually:

```
custom_components/jellyfin_status/
├── __init__.py
├── sensor.py
├── config_flow.py
├── options_flow.py
├── coordinator.py
├── const.py
├── manifest.json
├── translations/
│   ├── en.json
│   ├── fr.json
│   ├── ...
└── ...
```

---

## 🧩 Configuration

1. 
2. 
3. Fill in:  
   - Host and Port  
   - API key  
   - Optional scan interval and HTTPS settings  
4. Save and enjoy live playback status in your dashboard  

---

## 🌐 Translations

Available languages:

| Code      | Language             |
|-----------|----------------------|
| `en`      | English 🇬🇧           |
| `de`      | German 🇩🇪            |
| `fr`      | French 🇫🇷            |
| `es`      | Spanish 🇪🇸           |
| `zh-Hans` | Simplified Chinese 🇨🇳 |
| `fr-CA`   | Canadian French 🇨🇦    |
| `de-CH`   | Swiss German 🇨🇭      |
| `ja`      | Japanese 🇯🇵          |

Sensor phrases like `is watching`, `is listening to`, and `Idle — nothing to see here` are fully localized.

---

## 📺 Telemetry Attributes

Example output:
```yaml
currently_playing: |
  🎬 Alice is watching Interstellar
  📺 Bob is watching The Office – Threat Level Midnight (S07 E17)
  🎵 Charlie is listening to Daft Punk – Instant Crush

active_session_count: 3
audio_session_count: 1
movie_session_count: 1
episode_session_count: 1
polling_enabled: true
last_updated: 2025-07-22T20:43:19Z
```

---

## ❤️ Credits

Powered by the Jellyfin API and Home Assistant ecosystem.

---

## 📄 License

This project is licensed under the MIT License.

