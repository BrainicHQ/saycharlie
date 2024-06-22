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
 * # Created on 6/22/24, 11:01 AM
 * #
 * # Author: Silviu Stroe
 */
document.addEventListener('DOMContentLoaded', function () {
    let peakLevelRX = -30; // Initialize peak level for RX
    let peakLevelTX = -30; // Initialize peak level for TX
    let lastUpdateRX = Date.now(); // Track last update time for RX
    let lastUpdateTX = Date.now(); // Track last update time for TX

    const volumeLevelRX = document.getElementById('volumeLevelRX');
    const peakLevelBarRX = document.getElementById('peakLevelRX');
    const volumeLevelTX = document.getElementById('volumeLevelTX');
    const peakLevelBarTX = document.getElementById('peakLevelTX');
    const minDb = -30;
    const maxDb = 3;

    function updateLevels() {
        const now = Date.now();

        // Update peak level decay for RX
        if (now - lastUpdateRX > 100) {
            peakLevelRX -= 0.5;
            peakLevelRX = Math.max(peakLevelRX, minDb);
            lastUpdateRX = now;
        }
        let peakPercentageRX = ((peakLevelRX - minDb) / (maxDb - minDb)) * 100;
        peakPercentageRX = Math.max(0, Math.min(peakPercentageRX, 100));
        peakLevelBarRX.style.left = `${peakPercentageRX.toFixed(2)}%`;

        // Update peak level decay for TX
        if (now - lastUpdateTX > 100) {
            peakLevelTX -= 0.5;
            peakLevelTX = Math.max(peakLevelTX, minDb);
            lastUpdateTX = now;
        }
        let peakPercentageTX = ((peakLevelTX - minDb) / (maxDb - minDb)) * 100;
        peakPercentageTX = Math.max(0, Math.min(peakPercentageTX, 100));
        peakLevelBarTX.style.left = `${peakPercentageTX.toFixed(2)}%`;

        // Call this function again on the next animation frame
        requestAnimationFrame(updateLevels);
    }

    function getColorForLevel(dB) {
        if (dB <= -60) {
            return 'Black'; // Below audible threshold
        } else if (dB <= -18) {
            return 'Green'; // Safe levels, low to moderate signal, background noise
        } else if (dB <= -6) {
            return 'Yellow'; // Optimal recording levels, loud but not too loud
        } else {
            return 'Red'; // Close to clipping, high risk of distortion
        }
    }

    socket.on('audio_level_rx', function (data) {
        updateLevel(data, volumeLevelRX, peakLevelBarRX, 'RX');
    });

    socket.on('audio_level_tx', function (data) {
        updateLevel(data, volumeLevelTX, peakLevelBarTX, 'TX');
    });

    function updateLevel(data, volumeLevel, peakLevelBar, type) {
        const level = parseFloat(data.level);
        let percentage = ((level - minDb) / (maxDb - minDb)) * 100;
        percentage = Math.max(0, Math.min(percentage, 100));
        volumeLevel.style.width = `${percentage.toFixed(2)}%`;
        volumeLevel.style.backgroundColor = getColorForLevel(level);

        if (type === 'RX') {
            if (level > peakLevelRX || Date.now() - lastUpdateRX > 200) {
                peakLevelRX = level;
                lastUpdateRX = Date.now();
            }
        } else if (type === 'TX') {
            if (level > peakLevelTX || Date.now() - lastUpdateTX > 200) {
                peakLevelTX = level;
                lastUpdateTX = Date.now();
            }
        }

        let peakPercentage = ((eval(`peakLevel${type}`) - minDb) / (maxDb - minDb)) * 100;
        peakPercentage = Math.max(0, Math.min(peakPercentage, 100));
        peakLevelBar.style.left = `${peakPercentage.toFixed(2)}%`;
    }

    // Start the animation frame for peak level decay
    requestAnimationFrame(updateLevels);
});