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

// Instantiate new modal
const modal = new tingle.modal({
    footer: false,
    closeMethods: ['button'],
    closeLabel: "Close"
});

// Set content
modal.setContent('<form id="dtmfForm" class="flex flex-col mt-4">' +
    '<div class="flex">' +
    '<input required id="dtmf" class="js-kioskboard-input flex-grow p-4 bg-gray-100 border border-gray-300 ' +
    'rounded-l-md focus:outline-none focus:ring focus:ring-blue-500 mb-4" data-kioskboard-type="keyboard"' +
    'data-kioskboard-placement="bottom" data-kioskboard-specialcharacters="false" placeholder="DTMF tone">' +
    '<button type="submit" class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-4 px-4 rounded-l-none ' +
    'rounded-r-md mb-4 active:bg-blue-800 active:scale-95 active:ring-4 active:ring-blue-800">' +
    'Send</button>' +
    '</div>' +
    '</form>');

// Add event listener to form submission
document.getElementById('dtmfForm').addEventListener('submit', function (event) {
    event.preventDefault();
    const dtmfValue = document.getElementById('dtmf').value;
    if (dtmfValue) {
        sendDTMF(dtmfValue);
        document.getElementById('dtmf').value = '';
    }
});
