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

1. Go to **Settings → Devices & Services**  
2. Click **Add Integration** → select `Jellyfin Status` 
3. Fill in:  
   - Host and Port  
   - API key  
   - Optional scan interval and HTTPS settings  
4. Save and enjoy live playback status in your dashboard  

---

### 🛠️ Manual Updates

If the **scan interval is set to `0`**, the integration disables automatic polling.  
This allows you to **manually trigger updates via automation**, such as:

```yaml
service: homeassistant.update_entity
target:
  entity_id: sensor.jellyfin_status
```

Useful for scheduled syncs, conditional refreshes, or power-saving modes.

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
Polling enabled: true
Polling interval: 10
Last updated: 28 July 2025 at 21:43:38
currently_playing: |
  🎬 Bart: Interstellar
  📺 Homer: Wednesday's Child Is Full of Woe (S01 E01)
  🎵 Marge: Britney Spears – Oops!…I Did It Again

active_session_count: 3
audio_session_count: 1
movie_session_count: 1
episode_session_count: 1
```




<img height="500" alt="image" src="https://github.com/user-attachments/assets/695d208f-40f0-4078-a786-89a1045d517b" />


---

## ❤️ Credits

Powered by the Jellyfin API and Home Assistant ecosystem.

---

## 📄 License

This project is licensed under the MIT License.

