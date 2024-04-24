// Initialize Kioskboard
KioskBoard.init({
    // Define the keys for DTMF tones
    keysArrayOfObjects: [{"0": "1", "1": "2", "2": "3"}, {"0": "4", "1": "5", "2": "6"}, {
        "0": "7", "1": "8", "2": "9"
    }, {"0": "*", "1": "0", "2": "#"}],

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