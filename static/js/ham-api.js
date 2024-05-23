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
 * # Created on 5/16/24, 8:44 PM
 * #
 * # Author: Silviu Stroe
 */

async function fetchName(callsign) {
    try {
        const response = await fetch(`/api/get-name/${callsign}`);
        const data = await response.json();
        return data.name;  // Ensure this key matches what your Flask API returns
    } catch (error) {
        console.error('Error fetching name for callsign:', callsign, error);
        throw error;  // Re-throw the error to handle it in the caller
    }
}

async function getGroupName(number) {
    try {
        const response = await fetch(`/api/get-group-name/${number}`);
        if (response.status === 200) {
            const data = await response.json();
            return data.name;
        } else if (response.status === 404) {
            return null;
        }
    } catch (error) {
        console.error('Error fetching group name for number:', number, error);
        throw error;
    }
}