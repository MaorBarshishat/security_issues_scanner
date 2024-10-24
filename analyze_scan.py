import requests
from jinja2 import Template
from dotenv import load_dotenv
import os

# Load environment variables from the .env file. It includes the key and token to access SonarCloud
# In real deployment enviroment a more secured solution should be provided
load_dotenv()

# Constants for SonarCloud API interaction
PROJECT_KEY = os.getenv("KEY")
API_BASE_URL = "https://sonarcloud.io/api"
HEADERS = {'Authorization': f'Bearer {os.getenv("TOKEN")}'}
OUTPUT_FILE = "top_5_vulnerabilities.html"

# Keys to exclude from the vulnerability data
EXCLUDED_KEYS = {
    'flows', 'messageFormattings', 'project',
    'status', 'author', 'creationDate', 'updateDate'
}

# Limit for the number of vulnerabilities to fetch
TOP_VULNERABILITIES_LIMIT = 5


def send_request(url):
    """Send a GET request and return the response JSON."""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request https {e.response.status_code} - {e.response.text} error")
        raise


def fetch_vulnerabilities():
    """Fetch top vulnerabilities from the SonarQube API."""
    url = f"{API_BASE_URL}/hotspots/search?projectKey={PROJECT_KEY}&p=1&ps={TOP_VULNERABILITIES_LIMIT}&sinceLeakPeriod=false&status=TO_REVIEW"
    results = send_request(url)

    try:
        vulnerabilities = results.get('hotspots', [])

        # Filter out excluded keys from vulnerabilities
        return [
            {k: v for k, v in vuln.items() if k not in EXCLUDED_KEYS}
            for vuln in vulnerabilities
        ]
    except Exception as e:
        print("failed to get vulnerabilities")
        raise

def fetch_vulnerability_description(rule_key):
    """Fetch the description of a vulnerability by its rule key."""
    url = f"{API_BASE_URL}/hotspots/show?hotspot={rule_key}"
    result = send_request(url).get('rule', {})

    return {
        'riskDescription': result.get('riskDescription'),
        'vulnerabilityDescription': result.get('vulnerabilityDescription'),
        'fixRecommendations': result.get('fixRecommendations')
    }


def process_vulnerabilities(vulnerabilities):
    """Process vulnerabilities to include their descriptions."""
    processed = []
    for vuln in vulnerabilities:
        try:
            # get description per each vulnerability and append it into the processed array
            processed.append({'description sections': fetch_vulnerability_description(vuln['key'])})
        except Exception as e:
            print(f"Error processing vulnerability '{vuln.get('ruleKey')}': {e}")
            raise
    return processed


def save_vulnerabilities_to_file(vulnerabilities, filename=OUTPUT_FILE):
    """Save the processed vulnerabilities to an HTML file."""
    template = Template(
        "<ul>{% for key, value in data.items() %}<li>{{ key }}: {{ value }}</li>{% endfor %}</ul>")  # template for html file structure of each vulnerability

    # write to html file in chunks
    try:
        with open(filename, 'w') as file:
            for count, vuln in enumerate(vulnerabilities, 1):
                html_content = template.render(data=vuln)
                file.write(f"<h2>--- Vulnerability {count} ---</h2><br>" + html_content.replace("\\n",
                                                                                                "<br>") + "<br><br><br>")
    except IOError as e:
        print(f"File write error: {e}")
        raise


def main():
    """Main function to orchestrate fetching, processing, and saving vulnerabilities."""
    try:
        vulnerabilities = fetch_vulnerabilities()
        if vulnerabilities:
            processed_vulnerabilities = process_vulnerabilities(vulnerabilities)
            save_vulnerabilities_to_file(processed_vulnerabilities)
            print(f"Output saved in {OUTPUT_FILE}")
        else:
            raise Exception("there is no scanning to analyze...")
    except Exception as e:
        print(f"security issues scanner failed, error is: {e}")


if __name__ == "__main__":
    main()
