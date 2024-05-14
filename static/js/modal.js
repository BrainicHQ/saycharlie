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
    'rounded-r-md mb-4">Send</button>' +
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
