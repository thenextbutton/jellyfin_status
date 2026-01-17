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
| `{device}` | The hardware name | `Chrome`, `Roku` |
| `{client}` | The application used | `Jellyfin Web`, `Infuse` |
| `{title}` | Media title (Movie name, Episode title, or Song) | `Abominable` |
| `{audio}` | Audio Codec and Channels | `DTS 5.1`, `FLAC Stereo` |
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
| `{official_rating}` | Movie/TV series rating | `PG-13`, `R` |

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
Polling enabled: true
Polling interval: 10
Last updated: 17 January 2026 at 17:40:11
Server version: 10.11.5
Total movies: 519
Total tv shows: 61
Total episodes: 2,259
Total albums: 440
Total tracks: 8,848
Currently playing: ▶️ 🎬 Bart: The Amazing Spider-Man (01:49:55/02:16:17) 80% ▶️ 📺 Homer: Chucky – Death by Misadventure (00:09:09/00:46:28) 19% ▶️ 🎵 Marge: Queen – One Vision (00:00:43/00:04:04) 17%
Active sessions: 3
Audio sessions: 1
Episode sessions: 1
Movie sessions: 1
Detailed playback data: 

de3ad3aeb91124eb99fb5472d4030371:
user: Bart
device: Chrome
client: Jellyfin Web
media_type: Movie
title: The Amazing Spider-Man
official_rating: PG-13
quality: 1080p
audio: AC3 5.1
year: 2012
play_state: Playing
position: '01:49:55'
runtime: '02:16:17'
progress_percent: 80%
play_method: Transcode
transcode_progress: 81.2%
transcode_fps: 56
transcode_reasons: ContainerNotSupported, VideoCodecNotSupported, AudioCodecNotSupported

2a00d32ab76b355ad1edb576e5d33ed6:
user: Homer
device: NCC-1701-D
client: Jellyfin Media Player
media_type: Episode
title: Death by Misadventure
quality: 1080p
audio: AC3 5.1
series: Chucky
season_number: 1
episode_number: 1
year: 2021
play_state: Playing
position: '00:09:09'
runtime: '00:46:28'
progress_percent: 19%
play_method: DirectPlay

8049fb5e8b848a8880a071180c5df882:
user: Marge
device: Chrome
client: Jellyfin Web
media_type: Audio
title: One Vision
audio: FLAC Stereo
artist: Queen
year: 2009
play_state: Playing
position: '00:00:43'
runtime: '00:04:04'
progress_percent: 17%
play_method: DirectPlay
Provider
__jellyfin_status__
```


---
## 👨‍💻 Jinja2 Examples


Retreive a TOTAL of all Active sessions, Audio, Episodes and Movies across all the Jellyfin Status sensors.
```jinja2
{% set ns = namespace(active=0, audio=0, episode=0, movie=0) %}
{% for s in states.sensor %}
  {% set a = s.attributes %}
  {% if a.get('provider') == '__jellyfin_status__' %}
    {% set ns.active = ns.active + (a.get('active_session_count') | int(0)) %}
    {% set ns.audio = ns.audio + (a.get('audio_session_count') | int(0)) %}
    {% set ns.episode = ns.episode + (a.get('episode_session_count') | int(0)) %}
    {% set ns.movie = ns.movie + (a.get('movie_session_count') | int(0)) %}
  {% endif %}
{% endfor %}

▶️ **{{ '%02d' % ns.active }}** Active | 🎵 **{{ '%02d' % ns.audio }}** | 📺 **{{ '%02d' % ns.episode }}** | 🎥 **{{ '%02d' % ns.movie }}**
```

Result:
```
▶️ 00 Active | 🎵 00 | 📺 00 | 🎥 00
```

Using the playback states extended attribute

```jinja2
### 🎬 Jellyfin Status
---
{%- set sessions = state_attr('sensor.ncc_1701_d_status', 'playback_states') -%}
{%- if sessions -%}
{%- for session_id, data in sessions.items() %}
{%- if data.title != "Browsing" %}

{# --- Metadata & Icons --- #}
{%- set artist_part = (data.artist ~ " - ") if data.artist is defined else "" -%}
{%- set series_part = (data.series ~ " - ") if data.series is defined else "" -%}
{%- set ep_part = ("S" ~ '%02d' % data.season_number ~ "E" ~ '%02d' % data.episode_number ~ " - ") if data.season_number is defined else "" -%}
{%- set title_line = series_part ~ ep_part ~ artist_part ~ data.title -%}

{%- set official_rating = data.official_rating | default('') -%}

{%- if data.media_type == "Audio" -%}{%- set m_icon = "🎵" -%}
{%- elif data.series is defined or data.season_number is defined -%}{%- set m_icon = "📺" -%}
{%- else -%}{%- set m_icon = "🎥" -%}{%- endif -%}
{%- set p_icon = "▶️" if data.play_state == "Playing" else "⏸️" -%}

{# --- Improved Countdown Logic --- #}
{%- set countdown = "" -%}
{%- if data.media_type != "Audio" -%}
  {%- set cur = data.position.split(':') -%}
  {%- set tot = data.runtime.split(':') -%}
  {%- set diff = ((tot[0]|int*3600)+(tot[1]|int*60)+(tot[2]|int)) - ((cur[0]|int*3600)+(cur[1]|int*60)+(cur[2]|int)) -%}
  {%- if diff > 60 -%}
    {%- set countdown = " (" ~ (diff/60)|round(0)|int ~ "m left)" -%}
  {%- elif diff > 0 -%}
    {%- set countdown = " (" ~ diff ~ "s left)" -%}
  {%- endif -%}
{%- endif -%}

{# --- Transcode Badge --- #}
{%- set is_transcoding = data.play_method is defined and data.play_method != "DirectPlay" -%}
{%- set raw_tp = data.transcode_progress | default('0') | string -%}
{%- set tp_num = raw_tp.replace('%', '') | float(0) -%}
{%- set fps = data.transcode_fps if data.transcode_fps is defined else none -%}
{%- if is_transcoding -%}
  {%- if tp_num >= 100 %}{%- set t_badge = " | ⚙️👍" -%}
  {%- elif fps is not none and fps | float < 24 %}{%- set t_badge = " | ⚙️⚠️" -%}
  {%- else %}{%- set t_badge = " | ⚙️♻️" -%}{%- endif -%}
{%- else %}{%- set t_badge = "" -%}{%- endif -%}

{# --- Elastic Bar Logic --- #}
{%- set title_length = title_line | length -%}
{%- set min_width, max_width = 25, 40 -%}
{%- if title_length < min_width %}{%- set dynamic_width = min_width -%}
{%- elif title_length > max_width %}{%- set dynamic_width = max_width -%}
{%- else %}{%- set dynamic_width = title_length -%}{%- endif -%}

{%- set raw_progress = data.progress_percent | default('0') | string -%}
{%- set progress = raw_progress.replace('%', '') | float(0) -%}
{%- set filled = (progress / (100 / dynamic_width)) | int -%}
{%- set empty = dynamic_width - filled -%}
{%- set bar = "█" * filled + "░" * empty -%}

{{ p_icon }} **{{ data.user }}** | 💻 {{ data.device }}{{ t_badge }} {% if is_transcoding and tp_num < 100 and fps is not none %}({{ fps | int }} fps){% endif %}
{{ m_icon }} {{ title_line }}{% if data.official_rating is defined %} | 🔞 {{ data.official_rating }}{% endif %}
🕒 *{{ data.position }} / {{ data.runtime }}{{ countdown }}*
`{{ bar }}` {{ progress | int }}%

---
{%- endif %}
{%- endfor %}
{%- else %}
💤 Nothing Playing
{%- endif %}
```

Result:
```text
🎬 Jellyfin Status

▶️ Bart | 💻 Chrome | ⚙️👍
📺 Chucky - S01E01 - Death by Misadventure
🕒 00:00:01 / 00:46:28 (46m left)
░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0%

▶️ Homer | 💻 NCC-1701-D
🎵 The Offspring - Have You Ever
🕒 00:01:46 / 00:03:56
████████████░░░░░░░░░░░░░░░░░ 44%

▶️ Marge | 💻 Chrome | ⚙️♻️ (62 fps)
🎥 The Amazing Spider-Man | 🔞 PG-13
🕒 01:15:59 / 02:16:17 (60m left)
█████████████░░░░░░░░░░░░ 55%
```

---

## ❤️ Credits

Powered by the Jellyfin API and Home Assistant ecosystem.

---

## 📄 License

This project is licensed under the MIT License.

