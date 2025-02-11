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
document.addEventListener('DOMContentLoaded', function () {
    const weatherDisplay = document.getElementById('weather-emoji');

    async function updateWeather() {

        try {
            // Using MaxMind GeoIP2 City database to get the location data
            geoip2.city(onSuccess, onError);
        } catch (error) {
            console.error('Error:', error);
            weatherDisplay.textContent = 'Error initializing weather update'; // Display initialization error message in UI
        }
    }

    function onSuccess(response) {
        const city = response.city.names.en || 'Unknown City';
        fetchWeather(city);
    }

    async function fetchWeather(city) {
        try {
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

            updateDisplay(weatherData, city);
        } catch (error) {
            console.error('Error:', error);
            weatherDisplay.textContent = 'Error fetching weather data'; // Display error message in UI
        }
    }

    function updateDisplay(weatherData, city) {
        const weather = weatherData.current_weather.weathercode;
        const temperature = weatherData.current_weather.temperature;
        let emoji = getWeatherEmoji(weather);

        weatherDisplay.textContent = `${emoji} ${temperature}°C`;
        weatherDisplay.title = "Weather in " + city + ": " + temperature + "°C and the wind is blowing at " + weatherData.current_weather.windspeed + " km/h.";
    }

    function getWeatherEmoji(weatherCode) {
        let emoji;
        switch (weatherCode) {
            case 0:
                emoji = '☀️';
                break; // Clear sky
            case 1:
                emoji = '🌤️';
                break; // Mainly clear
            case 2:
                emoji = '⛅';
                break; // Partly cloudy
            case 3:
                emoji = '☁️';
                break; // Overcast
            case 45:
                emoji = '🌫️';
                break; // Fog and depositing rime fog
            case 48:
                emoji = '🌫️';
                break; // Fog and depositing rime fog
            case 51:
                emoji = '🌧️';
                break; // Drizzle: Light intensity
            case 53:
                emoji = '🌧️';
                break; // Drizzle: Moderate intensity
            case 55:
                emoji = '🌧️';
                break; // Drizzle: Dense intensity
            case 56:
                emoji = '🧊🌧️';
                break; // Freezing Drizzle: Light intensity
            case 57:
                emoji = '🧊🌧️';
                break; // Freezing Drizzle: Dense intensity
            case 61:
                emoji = '🌧️';
                break; // Rain: Slight intensity
            case 63:
                emoji = '🌧️';
                break; // Rain: Moderate intensity
            case 65:
                emoji = '🌧️';
                break; // Rain: Heavy intensity
            case 66:
                emoji = '🧊🌧️';
                break; // Freezing Rain: Light intensity
            case 67:
                emoji = '🧊🌧️';
                break; // Freezing Rain: Heavy intensity
            case 71:
                emoji = '❄️';
                break; // Snow fall: Slight intensity
            case 73:
                emoji = '❄️';
                break; // Snow fall: Moderate intensity
            case 75:
                emoji = '❄️';
                break; // Snow fall: Heavy intensity
            case 77:
                emoji = '🌨️';
                break; // Snow grains
            case 80:
                emoji = '🌦️';
                break; // Rain showers: Slight intensity
            case 81:
                emoji = '🌦️';
                break; // Rain showers: Moderate intensity
            case 82:
                emoji = '🌦️';
                break; // Rain showers: Violent intensity
            case 85:
                emoji = '🌨️';
                break; // Snow showers: Slight intensity
            case 86:
                emoji = '🌨️';
                break; // Snow showers: Heavy intensity
            case 95:
                emoji = '🌩️';
                break; // Thunderstorm: Slight or moderate
            case 96:
                emoji = '🌩️🧊';
                break; // Thunderstorm with slight hail
            case 99:
                emoji = '🌩️🧊';
                break; // Thunderstorm with heavy hail
            default:
                emoji = ''; // Unknown weather
        }
        return emoji;
    }

    function onError(error) {
        console.error('GeoIP2 Error:', error);
        weatherDisplay.textContent = 'Error retrieving location data'; // Display error message in UI
    }

    // Call updateWeather immediately when the page loads
    updateWeather();

    // Set the interval to update weather every 5 minutes
    setInterval(updateWeather, 300000); // 300000 milliseconds = 5 minutes
});
