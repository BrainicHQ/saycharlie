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