import os
from openai import OpenAI

# OpenAI Client Initialization
client = OpenAI(api_key='sk-proj-alFjuPKSX28l2LPbSowIT3BlbkFJEIR82ObAWGWadYBfXJaY')

# Function to extract information from notice text
def extract_information(notice: str):
    prompt = f"""
    Extract the following information from the notice. If the required field 'Address' is missing, skip this notice entirely. 
    If the notice does not contain any useful information, also skip it. Return "N/A" for any field that is not found but has other fields present.

    Follow these instructions to prioritize extraction:

    - Address: Prefer the 'site address' if mentioned; otherwise, extract the 'representative address'.
    - City: Extract the city corresponding to the selected address.
    - State: Extract the state corresponding to the selected address.
    - Zip Code: Extract the zip code corresponding to the selected address. If it's not present, find it using the address, city, and state.
    - Country: Extract the county if mentioned; otherwise, find it using the address.
    - Decedent Name: Extract the full name of the deceased individual.
    - Sale Date: Extract the sale or publication date if available; otherwise, leave it blank.
    - Phone Number: Extract the phone number associated with the representative if present. If multiple phone numbers are listed, choose the one related to the personal representative. Ensure the phone number contains 10 digits; if not present, return "N/A".

    Return the extracted data in JSON format without quotes around values. Use the following keys:
    - Address
    - City
    - State
    - Zip Code
    - Country
    - Decedent Name
    - Sale Date
    - Phone Number

    If the notice is missing essential information like Address, return "skip" instead of the JSON. Ensure the phone number contains 10 digits if not present, return "N/A", and if the zipcode is missing, find it using the address, city, and state.

    Probate Notice:
    {notice}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        
        content = response.choices[0].message.content.strip()
        
        if content.lower() == "skip":
            return None  # Indicate to skip this notice
        
        # Split content by lines to process key-value pairs
        lines = content.split('\n')
        extracted_info = {}
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                # Strip quotes and whitespace from key and value
                extracted_info[key.strip()] = value.strip().replace('"', '').replace("'", "")
                
        return extracted_info
    
    except Exception as e:
        print(f"Error: {e}")
        return {
            "Address": "N/A",
            "City": "N/A",
            "State": "N/A",
            "Zip Code": "N/A",
            "Country": "N/A",
            "Decedent Name": "N/A",
            "Sale Date": "N/A",
            "Phone Number": "N/A"
        }
