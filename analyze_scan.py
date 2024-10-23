import json
import requests
import yaml
import html2text
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Constants
TOKEN = os.getenv("TOKEN")
PROJECT_KEY = os.getenv("KEY")
API_BASE_URL = "http://localhost:9000/api"
VULNERABILITIES_LIMIT = 5  # Limit for the number of vulnerabilities to fetch

HEADERS = {
    'Authorization': f'Bearer {TOKEN}',
}

# Keys to exclude when processing vulnerabilities
EXCLUDED_KEYS = {
    'flows', 'messageFormattings', 'key', 'project',
    'status', 'author', 'creationDate', 'updateDate'
}


def send_request(url):
    """
    Send a GET request to the SonarQube server and return the response text.
    Args:url (str): The URL to send the request to.
    Returns:str: Response text if the request is successful; empty string otherwise.
    """
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()  # Raise an error for bad responses
        return response.text

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request error occurred: {req_err}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return ""  # Return an empty string on failure


def fetch_vulnerabilities():
    """
    Fetch the top five vulnerabilities from the SonarQube API.
    Returns:list: A list of dictionaries representing the vulnerabilities.
    """
    url = f"{API_BASE_URL}/hotspots/search?inNewCodePeriod=false&onlyMine=false&p=1&project={PROJECT_KEY}&ps=500&status=TO_REVIEW"
    results = send_request(url)

    if results:
        vulnerabilities = json.loads(results).get('hotspots', [])[:VULNERABILITIES_LIMIT]       # fetch top 5 vulnerabilities
        return [{k: v for k, v in vuln.items() if k not in EXCLUDED_KEYS} for vuln in vulnerabilities]      # delete unnecessary keys from vulnerabilities by EXCLUDED_KEYS arr

    return []  # Return an empty list if no results


def fetch_vulnerability_description(rule_key):
    """
    Fetch the description of a vulnerability by its rule key.
    Args:rule_key (str): The rule key for the vulnerability.
    Returns: list: List of description sections for the rule.
    """
    url = f"{API_BASE_URL}/rules/show?key=javascript%3A{rule_key}"
    results = send_request(url)

    return json.loads(results).get('rule', {}).get('descriptionSections',
                                                   []) if results else []  # Return empty list if no results


def format_description(description_sections):
    """
    Format the description sections for better readability.
    Args:description_sections (list): The sections to format.
    Returns:list: Formatted description sections.
    """
    return [
        {section['key'].replace("_", " "): html2text.html2text(section['content']).replace("\n\n", '\n')}
        for section in description_sections
    ]


def process_vulnerabilities(vulnerabilities):
    """
    Process and format the top vulnerabilities.
    Args:vulnerabilities (list): List of vulnerabilities to process.
    Returns:list: Processed vulnerabilities with descriptions.
    """
    processed_vulnerabilities = []

    for vulnerability in vulnerabilities:  # Process each vulnerability
        try:
            rule_key = vulnerability['ruleKey'].split(":")[1]  # Extract rule key
            description_sections = fetch_vulnerability_description(rule_key)
            vulnerability['descriptionSections'] = format_description(description_sections)
            processed_vulnerabilities.append(vulnerability)  # Append the processed vulnerability

        except Exception as e:
            print(f"An error occurred while processing vulnerability '{vulnerability.get('ruleKey')}': {e}")

    return processed_vulnerabilities  # Return all processed vulnerabilities


def save_vulnerabilities_to_file(vulnerabilities, filename='output.txt'):
    """
    Save the processed vulnerabilities to a file in YAML format.
    Args:vulnerabilities (list): List of top 5 vulnerabilities to present.
        filename (str): The name of the file to save to.
    """
    try:
        with open(filename, 'w') as file:
            for count, vulnerability in enumerate(vulnerabilities, start=1):
                file.write(f"--------------------------- Vulnerability number {count} ---------------------------\n\n")
                yaml.dump(vulnerability, file, default_flow_style=False, sort_keys=False)

    except IOError as io_err:
        print(f"Error writing to file '{filename}': {io_err}")
        raise  # Re-raise the exception to notify the calling code of the failure


def main():
    """
    Main function to orchestrate the fetching, processing, and saving of vulnerabilities.
    """
    try:
        vulnerabilities = fetch_vulnerabilities()

        if vulnerabilities:
            processed_vulnerabilities = process_vulnerabilities(vulnerabilities)
            save_vulnerabilities_to_file(processed_vulnerabilities)

    except Exception as e:
        print(f"An error occurred in the main function: {e}")


if __name__ == "__main__":
    main()
