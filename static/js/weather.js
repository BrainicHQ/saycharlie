/*
 * # Copyright (c) 2024 by Silviu Stroe (brainic.io)
 * #
 * # This program is free software: you can redistribute it and/or modify
 * # it under the terms of the GNU General Public License as published by
 * # the Free Software Foundation, either version 3 of the License, or
 * # (at your option) any later version.
 * #
 * # This program is distributed in the hope that it will be useful,
 * # but WITHOUT ANY WARRANTY; without even the implied warranty of
 * # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * # GNU General Public License for more details.
 * #
 * # You should have received a copy of the GNU General Public License
 * # along with this program. If not, see <http://www.gnu.org/licenses/>.
 * #
 * # Created on 5/24/24, 6:58 PM
 * #
 * # Author: Silviu Stroe
 */
document.addEventListener('DOMContentLoaded', async function () {
    const weatherDisplay = document.getElementById('weather-emoji');

    try {
        const ipResponse = await fetch('https://ipv4-check-perf.radar.cloudflare.com/api/info');
        if (!ipResponse.ok) throw new Error('Failed to fetch IP location');
        const locationData = await ipResponse.json();
        const city = locationData.city;

        if (!city) throw new Error('City information is unavailable');
        const geocodingUrl = `https://geocoding-api.open-meteo.com/v1/search?name=${encodeURIComponent(city)}&count=1&language=en&format=json`;
        const geoResponse = await fetch(geocodingUrl);
        if (!geoResponse.ok) throw new Error('Failed to fetch geocoding data');
        const geoData = await geoResponse.json();

        if (geoData.results.length === 0) throw new Error('Geocoding results are empty');
        const lat = geoData.results[0].latitude;
        const lon = geoData.results[0].longitude;

        const weatherUrl = `https://api.open-meteo.com/v1/forecast?current_weather=true&latitude=${lat}&longitude=${lon}`;
        const weatherResponse = await fetch(weatherUrl);
        if (!weatherResponse.ok) throw new Error('Failed to fetch weather data');
        const weatherData = await weatherResponse.json();

        const weather = weatherData.current_weather.weathercode;
        const temperature = weatherData.current_weather.temperature;
        let emoji;

        switch (weather) {
            case 0: emoji = '☀️'; break;
            case 2: emoji = '⛅'; break;
            case 3: emoji = '☁️'; break;
            case 45:
            case 48: emoji = '🌫️'; break;
            case 51:
            case 53:
            case 55:
            case 56:
            case 57: emoji = '🌧️'; break;
            case 61:
            case 63:
            case 65:
            case 66:
            case 67: emoji = '☔'; break;
            case 71:
            case 73:
            case 75:
            case 77:
            case 85:
            case 86: emoji = '❄️'; break;
            case 80:
            case 81:
            case 82: emoji = '⛈️'; break;
            default: emoji = '🌡️'; // Unknown weather
        }

        weatherDisplay.textContent = `${emoji} ${temperature}°C`;
    } catch (error) {
        console.error('Error:', error);
        weatherDisplay.textContent = '🌡️'; // Display error message in UI
    }
});
