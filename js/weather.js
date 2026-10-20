async function fetchWeather() {
    const timelineContainer = document.getElementById('weather-timeline');
    const latitude = 41.9028; // Rome
    const longitude = 12.4964;

    try {
        // Fetch forecast for "tomorrow" relative to now to ensure we get a full day's data for demonstration
        // For the static date Jan 3 2026, we'd normally need historical or specified past data if it's passed, 
        // or future forecast. Since 2026 is future, real accurate forecast isn't possible yet.
        // We will fetch the current standard forecast but label it for our timeline hours (5, 9, 13, 17 etc)

        const response = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&hourly=temperature_2m,precipitation_probability,weathercode&timezone=Europe%2FRome&forecast_days=2`);
        const data = await response.json();

        if (!data || !data.hourly) {
            timelineContainer.innerHTML = '<p>Dati meteo non disponibili.</p>';
            return;
        }

        timelineContainer.innerHTML = ''; // Clear loading

        // We'll show the next 24h chunk or just a fixed set of hours to simulate the day
        const hourly = data.hourly;
        const now = new Date();
        const startHour = 5; // Start showing from 5 AM
        const endHour = 20; // Until 8 PM

        // Loop through the first 24 indices (roughly first day) and pick hours
        for (let i = 0; i < 24; i++) {
            const timeStr = hourly.time[i]; // ISO string
            const dateObj = new Date(timeStr);
            const hour = dateObj.getHours();

            if (hour >= startHour && hour <= endHour) {
                const temp = Math.round(hourly.temperature_2m[i]);
                const rainProb = hourly.precipitation_probability[i];
                const code = hourly.weathercode[i];

                const item = document.createElement('div');
                item.className = 'weather-item';
                item.innerHTML = `
                    <div class="weather-time">${hour}:00</div>
                    <div class="weather-icon">${getWeatherIcon(code)}</div>
                    <div class="weather-temp">${temp}°C</div>
                    <div class="weather-rain">
                        <span class="material-symbols-outlined" style="font-size:12px">water_drop</span> ${rainProb}%
                    </div>
                `;
                timelineContainer.appendChild(item);
            }
        }

    } catch (error) {
        console.error("Weather fetch failed:", error);
        timelineContainer.innerHTML = '<p style="color:red; font-size: 0.8rem;">Meteo offline</p>';
    }
}

function getWeatherIcon(code) {
    // WMO Weather interpretation codes (WW)
    // 0: Clear sky
    // 1, 2, 3: Mainly clear, partly cloudy, and overcast
    // 45, 48: Fog
    // 51, 53, 55: Drizzle
    // 61, 63, 65: Rain
    // 71, 73, 75: Snow
    // 95, 96, 99: Thunderstorm

    if (code === 0) return '☀️';
    if (code >= 1 && code <= 3) return '⛅';
    if (code >= 45 && code <= 48) return '🌫️';
    if (code >= 51 && code <= 67) return '🌧️';
    if (code >= 71 && code <= 77) return '❄️';
    if (code >= 95) return '⛈️';
    return '❓';
}

// Init
fetchWeather();
