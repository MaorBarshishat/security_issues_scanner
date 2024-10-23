import requests
from jinja2 import Template
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Constants for API interaction
TOKEN = os.getenv("TOKEN")
PROJECT_KEY = os.getenv("KEY")
API_BASE_URL = "https://sonarcloud.io/api"
HEADERS = {'Authorization': f'Bearer {TOKEN}'}

# Keys to exclude from the vulnerability data
EXCLUDED_KEYS = {
    'flows', 'messageFormattings', 'project',
    'status', 'author', 'creationDate', 'updateDate'
}

# Limit for the number of vulnerabilities to fetch
VULNERABILITIES_LIMIT = 5


def send_request(url):
    """Send a GET request and return the response JSON."""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return {}


def fetch_vulnerabilities():
    """Fetch top vulnerabilities from the SonarQube API."""
    url = f"{API_BASE_URL}/hotspots/search?projectKey={PROJECT_KEY}&p=1&ps=500&sinceLeakPeriod=false&status=TO_REVIEW"
    results = send_request(url)
    vulnerabilities = results.get('hotspots', [])[:VULNERABILITIES_LIMIT]

    # Filter out excluded keys from vulnerabilities
    return [
        {k: v for k, v in vuln.items() if k not in EXCLUDED_KEYS}
        for vuln in vulnerabilities
    ]


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
            vuln['description sections'] = fetch_vulnerability_description(vuln['key'])     # get description
            processed.append(vuln)
        except Exception as e:
            print(f"Error processing '{vuln.get('ruleKey')}': {e}")
    return processed


def save_vulnerabilities_to_file(vulnerabilities, filename='top_5_vulnerabilities.html'):
    """Save the processed vulnerabilities to an HTML file."""
    template = Template("<ul>{% for key, value in data.items() %}<li>{{ key }}: {{ value }}</li>{% endfor %}</ul>")     # template for html file structure of each vulnerability
    
    # write to html file in chunks
    try:
        with open(filename, 'w') as file:
            for count, vuln in enumerate(vulnerabilities, 1):
                html_content = template.render(data=vuln)
                file.write(f"<h2>--- Vulnerability {count} ---</h2><br>" + html_content.replace("\\n",
                                                                                                "<br>") + "<br><br><br>")
    except IOError as e:
        print(f"File write error: {e}")


def main():
    """Main function to orchestrate fetching, processing, and saving vulnerabilities."""
    vulnerabilities = fetch_vulnerabilities()
    if vulnerabilities:
        processed_vulnerabilities = process_vulnerabilities(vulnerabilities)
        save_vulnerabilities_to_file(processed_vulnerabilities)
        print("Output saved in top_5_vulnerabilities.html")


if __name__ == "__main__":
    main()
