import re
import requests
import json
import os


class HamRadioAPI:
    def __init__(self, cache_file='callsign_cache.json'):
        self.cache_file = cache_file
        self.cache = self.load_cache()

    def load_cache(self):
        """
        Load the cache from a JSON file. If the file does not exist, return an empty dictionary.
        """
        if os.path.exists(self.cache_file):
            with open(self.cache_file, 'r') as file:
                return json.load(file)
        return {}

    def save_cache(self):
        """
        Save the current cache to a JSON file.
        """
        with open(self.cache_file, 'w') as file:
            json.dump(self.cache, file, indent=4)

    def normalize_callsign(self, callsign):
        """
        Normalize the callsign by removing any suffixes and converting to uppercase.
        """
        base_callsign = re.sub(r'-.*$', '', callsign).upper()  # Remove suffix after '-' and convert to upper case
        return base_callsign

    def is_valid_callsign(self, callsign):
        """
        Validate the base part of a callsign using a regular expression pattern.
        """
        base_callsign = self.normalize_callsign(callsign)
        pattern = r"^[A-Z0-9]{1,2}[0-9][A-Z0-9]{1,3}$"
        return re.match(pattern, base_callsign) is not None

    def get_ham_details(self, callsign):
        """
        Retrieve the first name of the HAM operator from the API, using cached results to avoid repeated requests.
        """
        base_callsign = self.normalize_callsign(callsign)

        # Validate the callsign
        if not self.is_valid_callsign(callsign):
            return {"error": "Invalid HAM callsign"}

        # Use cached data if available
        if base_callsign in self.cache:
            return {"name": self.cache[base_callsign]}  # Return the cached first name

        # Make the API request if the callsign is not cached
        try:
            response = requests.get(f"https://ham.brainic.ro/?callsign={base_callsign}")
            response.raise_for_status()  # Raises an HTTPError for bad responses
            data = response.json()
            fname = data.get("fname", "Not available")  # Get the first name or default to "Not available"
            self.cache[base_callsign] = fname  # Cache only the first name
            self.save_cache()  # Save the updated cache
            return {"name": fname}
        except requests.RequestException as e:
            return {"error": f"API request failed: {str(e)}"}
