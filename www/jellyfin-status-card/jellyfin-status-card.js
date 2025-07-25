import { LitElement, html, css } from '/local/jellyfin-status-card-deps/lit-element.js';

class JellyfinStatusCard extends LitElement {
    static get properties() {
        return {
            hass: {},
            config: {},
        };
    }

    // Set the card configuration
    setConfig(config) {
        // 'entities' is now an optional array of entity IDs to monitor.
        // If not provided, the card will attempt to auto-discover.
        if (config.entities && !Array.isArray(config.entities)) {
            throw new Error('Config "entities" must be an array of entity IDs.');
        }
        this.config = config;
    }

    // Helper function for translations
    _localize(key, fallback = '') {
        // The `hass.localize` function is the standard way to get translations in HA frontend.
        // It expects keys in the format 'component.string.key' or 'custom_component.<domain>.string.key'.
        // For custom cards, we can define our own keys under a 'card' section in strings.json.
        return this.hass.localize(`component.jellyfin_status.card.${key}`) || fallback;
    }

    // Define the card's UI
    render() {
        if (!this.hass || !this.config) {
            return html``;
        }

        let monitoredEntityIds = [];

        if (this.config.entities && this.config.entities.length > 0) {
            // User specified specific entities to monitor
            monitoredEntityIds = this.config.entities;
        } else {
            // Auto-discover all individual Jellyfin server sensors if no specific entities are provided
            for (const entityId in this.hass.states) {
                if (entityId.startsWith('sensor.jellyfin_status_') && entityId !== 'sensor.jellyfin_overall_status') {
                    monitoredEntityIds.push(entityId);
                }
            }
        }

        if (monitoredEntityIds.length === 0) {
            return html`
                <ha-card>
                    <div class="card-content">
                        <p class="error">${this._localize('error.no_servers_found', 'No Jellyfin server entities found or configured for monitoring.')}</p>
                    </div>
                </ha-card>
            `;
        }

        let totalActiveSessionCount = 0;
        let totalMovieSessionCount = 0;
        let totalEpisodeSessionCount = 0;
        let totalAudioSessionCount = 0;
        let allPlayingLines = [];

        monitoredEntityIds.forEach(entityId => {
            const state = this.hass.states[entityId];
            if (state && state.state !== 'unavailable' && state.state !== 'unknown') {
                const attributes = state.attributes;
                totalActiveSessionCount += attributes.active_session_count || 0;
                totalMovieSessionCount += attributes.movie_session_count || 0;
                totalEpisodeSessionCount += attributes.episode_session_count || 0;
                totalAudioSessionCount += attributes.audio_session_count || 0;

                const currentlyPlaying = attributes.currently_playing;
                // The backend sensor already provides translated idle message, so we check for it.
                if (currentlyPlaying && currentlyPlaying !== this.hass.localize('component.jellyfin_status.sensor.idle_message', '😴 Idle — nothing to see here')) {
                    allPlayingLines = allPlayingLines.concat(currentlyPlaying.split('\n'));
                }
            }
        });

        const displayPlayingLines = allPlayingLines.length > 0 ? allPlayingLines : [this.hass.localize('component.jellyfin_status.sensor.idle_message', '😴 Idle — nothing to see here')];

        return html`
            <ha-card>
                <div class="card-header">
                    <!-- Logo source now points to the same directory as the card file -->
                    <img src="Jellyfin_-_banner-dark.svg" class="logo" alt="Jellyfin Logo">
                </div>
                <div class="card-content">
                    <div class="section-title">${this._localize('title', 'List of Media Playing')}</div>
                    <div class="media-list">
                        ${displayPlayingLines.map(line => html`<p>${line}</p>`)}
                    </div>
                    <div class="stats-row">
                        <div class="stat-item">
                            <span class="stat-value">${totalActiveSessionCount}</span>
                            <span class="stat-icon">👥</span> <!-- Users online (active sessions) -->
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${totalMovieSessionCount}</span>
                            <span class="stat-icon">🎬</span> <!-- Movies playing -->
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${totalEpisodeSessionCount}</span>
                            <span class="stat-icon">📺</span> <!-- Episodes playing -->
                        </div>
                        <div class="stat-item">
                            <span class="stat-value">${totalAudioSessionCount}</span>
                            <span class="stat-icon">🎵</span> <!-- Audio playing -->
                        </div>
                    </div>
                </div>
            </ha-card>
        `;
    }

    // Define the card's styling
    static get styles() {
        return css`
            ha-card {
                background-color: #3e005d; /* Dark purple background */
                color: white;
                border-radius: 12px;
                overflow: hidden;
                font-family: 'Inter', sans-serif;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            }
            .card-header {
                background-color: #5a008a; /* Slightly lighter purple for header */
                padding: 20px;
                display: flex;
                justify-content: center;
                align-items: center;
                border-bottom: 2px solid #7b00b8; /* Border for separation */
            }
            .logo {
                width: 150px; /* Adjust size as needed */
                height: auto;
            }
            .card-content {
                padding: 20px;
            }
            .section-title {
                font-size: 1.5em;
                font-weight: bold;
                margin-bottom: 15px;
                text-align: center;
                color: #ffffff;
            }
            .media-list {
                background-color: #000000; /* Black background for media list */
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
                min-height: 100px; /* Ensure some height even if empty */
                display: flex;
                flex-direction: column;
                justify-content: center; /* Center content vertically */
                align-items: center; /* Center content horizontally */
                text-align: center;
            }
            .media-list p {
                margin: 5px 0;
                font-size: 1.1em;
                color: #e0e0e0;
            }
            .media-list p:last-child {
                margin-bottom: 0;
            }
            .stats-row {
                display: flex;
                justify-content: space-around;
                align-items: center;
                padding-top: 15px;
                border-top: 1px solid rgba(255, 255, 255, 0.2);
            }
            .stat-item {
                display: flex;
                flex-direction: column;
                align-items: center;
                font-size: 1.2em;
                font-weight: bold;
                color: #ffffff;
            }
            .stat-value {
                font-size: 1.8em;
                margin-bottom: 5px;
                color: #a0f0ff; /* Light blue for numbers */
            }
            .stat-icon {
                font-size: 2em; /* Larger icons */
                margin-top: 5px;
            }
            .error {
                color: #ff6b6b;
                text-align: center;
                font-weight: bold;
            }
        `;
    }
}

// Register the custom element with the browser
customElements.define('jellyfin-status-card', JellyfinStatusCard);
