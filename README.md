<img width="100" alt="image" src="https://github.com/user-attachments/assets/c0965977-df9c-42aa-abc5-f874dedb03a0" /><br>
# Jellyfin Status for Home Assistant

[![HACS Badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![Home Assistant 2024.6.0+](https://img.shields.io/badge/Home%20Assistant-2024.6.0+-orange?logo=home-assistant&logoColor=white)](https://www.home-assistant.io/)
[![Jellyfin Badge](https://img.shields.io/badge/Jellyfin-Community-blue?logo=jellyfin&logoColor=white)](https://jellyfin.org/)
[![GitHub release downloads](https://img.shields.io/github/downloads/thenextbutton/jellyfin_status/total)](https://github.com/thenextbutton/jellyfin_status/releases)

[![GitHub release date](https://img.shields.io/github/release-date/thenextbutton/jellyfin_status)](https://github.com/thenextbutton/jellyfin_status/releases)
[![GitHub release (latest by date)](https://img.shields.io/github/v/release/thenextbutton/jellyfin_status)](https://github.com/thenextbutton/jellyfin_status/releases)
[![GitHub Stars](https://img.shields.io/github/stars/thenextbutton/jellyfin_status?style=social)](https://github.com/thenextbutton/jellyfin_status/stargazers)

[![GitHub Issues](https://img.shields.io/github/issues/thenextbutton/jellyfin_status)](https://github.com/thenextbutton/jellyfin_status/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/thenextbutton/jellyfin_status)](https://github.com/thenextbutton/jellyfin_status/pulls)

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/thenextbutton/jellyfin_status/blob/main/LICENSE)

---

<br>Track real-time playback sessions from your Jellyfin media server — complete with user-friendly status updates, emoji-enhanced telemetry, and full multilingual support.
<br><br>


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
   - Playback format: `{play_icon} {media_icon} {user}: {artist} – {title} ({playing_position}/{playback_runtime}) {playback_percentage}`†
   - idle message: `💤 Nothing Playing.`
4. Save and enjoy live playback status in your dashboard  

† playback format is used for producing the currently playing output in extended attributes, when using {artist} this will be removed when a movie is playing and on an episode it will replace it with series name.

---
### 🧩 Template Fields

| Field | Description | Example Output |
| :--- | :--- | :--- |
| `{user}` | Jellyfin username | `homer` |
| `{title}` | Media title (Movie name, Episode title, or Song) | `Abominable` |
| `{quality}` | Resolution and Dynamic Range (Video only) | `4K HDR`, `1080p` |
| `{series}` | TV Series name | `The Bear` |
| `{season}` | Season number | `2` |
| `{episode}` | Episode number | `1` |
| `{artist}` | Artist name (Audio only) | `Pink Floyd` |
| `{media_icon}` | Emoji for media type | 🎬, 📺, 🎵 |
| `{play_icon}` | Playback state icon | ▶️, ⏸️ |
| `{playing_position}` | Current playback time | `00:15:30` |
| `{playback_runtime}` | Total file duration | `01:37:13` |
| `{playback_percentage}` | Progress as percentage | `45%` |
| `{play_method}` | How the file is being served | `DirectPlay`, `Transcode` |
| `{transcode_info}` | Formatted string for active transcoding | `[⚡ 14 fps \| 1.5%]` |
| `{transcode_percentage}` | Server transcode buffer/completion | `100%` |

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

Use my Blueprint for [Jellyfin Webhooks](https://github.com/thenextbutton/home_assistant/tree/main/blueprints/jellyfin_webhook_handler_v2) and use the Generic Playback Actions for playback start and playback stop events. Add an action to update the Jellyfin status sensor; this will refresh the data whenever the playback state changes.

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
```text
Friendly name: Jellyfin Status
Server version: 10.10.7
Last updated: 14 January 2026 at 22:59:00
Total Movies: 1250
Total TV Shows: 145
Total Episodes: 8420
Total Albums: 530
Total Tracks: 12400

Currently playing: |
  ▶️ Homer: The Amazing Spider-Man [4K HDR] (00:14:39 / 02:16:17)
  ▶️ Marge: The Good Place - S01E01 - Everything Is Fine [1080p] (00:03:31 / 00:26:16) [⚡ 45 fps | 15.5%]

Active session count: 2
Audio session count: 0
Episode session count: 1
Movie session count: 1

Playback states:
  Homer:
    media_type: Movie
    quality: 4K HDR
    title: The Amazing Spider-Man
    year: 2012
    play_state: Playing
    position: '00:14:39'
    runtime: '02:16:17'
    progress_percent: 10%
    play_method: DirectPlay
  Marge:
    media_type: Episode
    quality: 1080p
    title: Everything Is Fine
    series: The Good Place
    season_number: 1
    episode_number: 1
    play_state: Playing
    position: '00:03:31'
    runtime: '00:26:16'
    progress_percent: 13%
    play_method: Transcode
    transcode_progress: 15.5%
    transcode_fps: 45
    transcode_reasons: ContainerNotSupported, VideoCodecNotSupported

Provider: __jellyfin_status__
```




<img width="300" alt="image" src="https://github.com/user-attachments/assets/3757a367-9d29-419a-ab34-98977c784a78" />
<br>
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

Using the playback states extended attribute

```jinja2
{% set sessions = state_attr('sensor.<server_name>_status', 'playback_states') %}
{% if sessions %}
  {%- for user, data in sessions.items() %}
    {% set icon = "▶️" if data.play_state == "Playing" else "⏸️" %}
    {{ icon }} {{ user }}: 
    {%- if data.series %} {{ data.series }} - {% endif %}
    {%- if data.season_number %}S{{ '%02d' % data.season_number }}E{{ '%02d' % data.episode_number }} - {% endif %}
    {%- if data.artist %} {{ data.artist }} - {% endif %}
    {{- data.title }} 
    {%- if data.quality %} [{{ data.quality }}]{% endif %}
    ({{ data.position }} / {{ data.runtime }})
  {%- endfor %}
{% else %}
  💤 Nothing Playing
{% endif %}

```

Result:
```
▶️ Homer: The Amazing Spider-Man [4K HDR] (00:39:50 / 02:16:17)
▶️ Marge: The Good Place - S01E01 - Everything Is Fine [1080p] (00:03:31 / 00:26:16)
▶️ Lisa: The Beatles - Eight Days a Week (00:00:29 / 00:02:43)


💤 Nothing Playing
```

---

## ❤️ Credits

Powered by the Jellyfin API and Home Assistant ecosystem.

---

## 📄 License

This project is licensed under the MIT License.

