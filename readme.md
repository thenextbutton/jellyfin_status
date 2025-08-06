# 🎬 Jellyfin Status for Home Assistant

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Home Assistant Ready](https://img.shields.io/badge/Home%20Assistant-Ready-orange?logo=home-assistant&logoColor=white)](https://www.home-assistant.io/)
[![Jellyfin Badge](https://img.shields.io/badge/Jellyfin-Community-blue?logo=jellyfin&logoColor=white)](https://jellyfin.org/)
[![GitHub last commit](https://img.shields.io/github/last-commit/thenextbutton/jellyfin_status)](https://github.com/thenextbutton/jellyfin_status/commits/main)
[![GitHub Issues](https://img.shields.io/github/issues/thenextbutton/jellyfin_status)](https://github.com/thenextbutton/jellyfin_status/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/thenextbutton/jellyfin_status)](https://github.com/thenextbutton/jellyfin_status/pulls)
[![GitHub Stars](https://img.shields.io/github/stars/thenextbutton/jellyfin_status?style=social)](https://github.com/thenextbutton/jellyfin_status/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/thenextbutton/jellyfin_status/blob/main/LICENSE) 

---

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

### 🔧 Add via HACS (Custom Repository)

1. In Home Assistant, go to **HACS → Integrations**
2. Click the **⋮ three-dot menu** (top right) → **Custom repositories**
3. Add your GitHub repository URL  
   (e.g. `https://github.com/thenextbutton/jellyfin_status`)
4. Set category to **Integration**
5. Click **Add**
6. Now search for `Jellyfin Status` inside HACS and install it

> 🔁 Don’t forget to **restart Home Assistant** after installation to ensure it’s fully loaded.


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

### 🛠️ Manual Scanner Updates

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
Server version: 10.10.7
Provider: __jellyfin_status__
```




<img width="300" alt="image" src="https://github.com/user-attachments/assets/b20f5cbf-b204-4a44-a1be-9d9f4155b9d2" />
<img width="300" alt="image" src="https://github.com/user-attachments/assets/c15e8579-221f-44e0-afd5-6c30aa4d28b1" />
<img width="300" alt="image" src="https://github.com/user-attachments/assets/4196088a-da27-458f-b90f-4ee1c8ca62da" />

---
## 👨‍💻 Jinja2 Examples


Retreive a TOTAL of all Active sessions, Audio, Episodes and Movies across all the Jellyfin Status sensors.
```jinja2
{% set ns = namespace(active=0, audio=0, episode=0, movie=0) %}
{% for s in states.sensor %}
  {% set a = s.attributes %}
  {% if a.get('provider') == '__jellyfin_status__' %}
    {% if a.get('active_session_count') is number %}{% set ns.active = ns.active + a.get('active_session_count') %}{% endif %}
    {% if a.get('audio_session_count') is number %}{% set ns.audio = ns.audio + a.get('audio_session_count') %}{% endif %}
    {% if a.get('episode_session_count') is number %}{% set ns.episode = ns.episode + a.get('episode_session_count') %}{% endif %}
    {% if a.get('movie_session_count') is number %}{% set ns.movie = ns.movie + a.get('movie_session_count') %}{% endif %}
  {% endif %}
{% endfor %}
Active: {{ '%02d' % ns.active }}, Audio: {{ '%02d' % ns.audio }}, Episodes: {{ '%02d' % ns.episode }}, Movies: {{ '%02d' % ns.movie }}
```

Result:
```
Active: 00, Audio: 00, Episodes: 00, Movies: 00
```
---

## ❤️ Credits

Powered by the Jellyfin API and Home Assistant ecosystem.

---

## 📄 License

This project is licensed under the MIT License.

