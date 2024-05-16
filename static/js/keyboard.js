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

// Initialize Kioskboard
KioskBoard.init({
    // Define the keys for DTMF tones
    keysArrayOfObjects: [{"0":"1","1":"2","2":"3","3":"4","4":"5","5":"6"},{"0":"7","1":"8","2":"9","3":"0","4":"*","5":"#"}],

    // Language Code (ISO 639-1) for custom keys (for language support)
    language: 'en',

    // Theme of the keyboard
    theme: 'material',

    // Enable/disable auto-scrolling to input/textarea element
    autoScroll: true,

    // Start with caps lock active or not
    capsLockActive: false,

    // Allow/disallow real/physical keyboard usage
    allowRealKeyboard: true,

    // Allow/disallow mobile keyboard usage
    allowMobileKeyboard: true,

    // CSS animations for opening or closing the keyboard
    cssAnimations: true,

    // CSS animations duration in milliseconds
    cssAnimationsDuration: 360,

    // CSS animations style for opening or closing the keyboard
    cssAnimationsStyle: 'slide',

    // Enable/disable Spacebar functionality on the keyboard
    keysAllowSpacebar: false,

    // Text of the space key (Spacebar)
    keysSpacebarText: 'Space',

    // Font family of the keys
    keysFontFamily: 'sans-serif',

    // Font size of the keys
    keysFontSize: '22px',

    // Font weight of the keys
    keysFontWeight: 'normal',

    // Size of the icon keys
    keysIconSize: '25px',

    // Text of the Enter key (Enter/Return)
    keysEnterText: 'Enter',

    // Callback function of the Enter key
    keysEnterCallback: undefined,

    // Whether Enter key can close and remove the keyboard
    keysEnterCanClose: true,
});

KioskBoard.run('.js-kioskboard-input');