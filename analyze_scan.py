import requests
from requests.exceptions import HTTPError, Timeout, RequestException

from jinja2 import Template
from dotenv import load_dotenv
import os

# Load environment variables from the .env file. It includes the key and token to access SonarCloud
# In real deployment enviroment a more secured solution should be provided
load_dotenv()

API_BASE_URL = "https://sonarcloud.io/api"
OUTPUT_FILE = "top_5_vulnerabilities.html"

# Keys to exclude from the vulnerability data
EXCLUDED_VULNERABILITY_KEYS = [
    'flows', 'messageFormattings', 'project',
    'status', 'author', 'creationDate', 'updateDate'
]
# keys to include in 'description section' key
INCLUDES_DESCRIPTION_KEYS = [
    'riskDescription', 'vulnerabilityDescription', 'fixRecommendations'
]

# Limit for the number of vulnerabilities to fetch
TOP_VULNERABILITIES_LIMIT = 5


class Sonarfetcher():
    def __init__(self, token: str,
                 project_key: str,
                 excluded_vulnerability_keys: list[str],
                 included_description_keys: list[str],
                 top_vulnerabilities_limit: int = TOP_VULNERABILITIES_LIMIT) -> None:
        self.__api_base_url = API_BASE_URL
        self.__token = token
        self.__project_key = project_key
        self.__excluded_vulnerability_keys = excluded_vulnerability_keys
        self.__included_description_keys = included_description_keys
        self.__top_vulnerabilities_limit = top_vulnerabilities_limit

    def __send_http_request(self, url: str) -> any:
        """Send a GET request and return the response JSON."""
        headers = {'Authorization': f'Bearer {self.__token}'}

        # send http rew with right exceptions handling
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            if response.headers.get('Content-Type') == 'application/json':
                return response.json()
            else:
                raise "Unexpected response content"
        except HTTPError as http_err:
            print(f"HTTP error occurred: {http_err}")
        except Timeout:
            print(f"Timeout error occurred for URL: {url}")
        except RequestException as req_err:
            print(f"An error occurred: {req_err}")
        except Exception as err:
            print(f"{type(err)}: An unexpected error occurred: {err}")
        return None

    def __fetch_all_vulnerabilities(self) -> list[dict]:
        """Fetch top vulnerabilities from the SonarQube API."""
        url = (f"{self.__api_base_url}/hotspots/search?projectKey="
               f"{self.__project_key}&p=1&ps="
               f"{self.__top_vulnerabilities_limit}&sinceLeakPeriod=false&status=TO_REVIEW")
        results = self.__send_http_request(url)
        if results is None:
            return []

        # fetch hotspots from results
        try:
            vulnerabilities = results['hotspots']
        except KeyError as e:
            print(f"Key error: The key '{e}' was not found.\nFailed fetch vulnerabilities")
            return []

        # Filter out excluded keys from vulnerabilities
        return [
            {k: v for k, v in vuln.items() if k not in self.__excluded_vulnerability_keys}
            for vuln in vulnerabilities
        ]

    def __fetch_vulnerability_description(self, rule_key: str) -> dict:
        """Fetch the description of a vulnerability by its rule key."""
        url = f"{self.__api_base_url}/hotspots/show?hotspot={rule_key}"
        result: dict = self.__send_http_request(url)
        if result is None:
            return {}

        try:
            # access the description dict
            description: dict = result['rule']

            # return the important fields from the description dict
            return {k: v for k, v in description.items() if k in self.__included_description_keys}
        except KeyError as e:
            print(f"Key error: The key '{e}' was not found.\nFailed to access description vulnerability")
            return {}
        except Exception as e:
            print(f"{type(e)}: failed to access description vulnerability: {e}")
            return {}

    def __process_vulnerabilities(self, vulnerabilities: list[dict]) -> list[dict]:
        """Process vulnerabilities to include their descriptions."""
        for vuln in vulnerabilities:
            try:
                # get description per each vulnerability and append it into the processed array
                vulnerability_description = self.__fetch_vulnerability_description(vuln['key'])
                if vulnerability_description:
                    vuln['description sections'] = vulnerability_description  # append description sections
            except KeyError as e:
                print(f"Key error: The key '{e}' was not found.\nFailed processing vulnerability")
                return []
            except Exception as e:
                print(f"{type(e)}: failed processing vulnerability: {e}")
                return []
        return vulnerabilities

    def get_vulnerabilities(self) -> list[dict]:
        vulnerabilities = self.__fetch_all_vulnerabilities()
        if vulnerabilities:
            return self.__process_vulnerabilities(vulnerabilities)
        return []


def save_vulnerabilities_to_file(vulnerabilities, filename=OUTPUT_FILE):
    """Save the processed vulnerabilities to an HTML file."""

    # html template for output file
    template = Template("""
            <ol style="  line-height: 1.8;">
                {% for key, value in data.items() %}<li>
                   <strong>{{ key }}:</strong> 
                   {% if value is mapping %}
                       <ul>
                           {% for sub_key, sub_value in value.items() %}
                               <li><strong>{{ sub_key }}:</strong> {{ sub_value }}</li>
                           {% endfor %}
                       </ul>
                   {% else %}
                       {{ value }}
                   {% endif %}
               </li>
           {% endfor %}
           </ol>
       """)

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
    token = os.getenv("TOKEN")
    project_key = os.getenv("KEY")
    sonar_fetcher = Sonarfetcher(token,
                                 project_key,
                                 EXCLUDED_VULNERABILITY_KEYS,
                                 INCLUDES_DESCRIPTION_KEYS,
                                 TOP_VULNERABILITIES_LIMIT)
    sonar_vulnerabilities = sonar_fetcher.get_vulnerabilities()
    if sonar_vulnerabilities:
        save_vulnerabilities_to_file(sonar_vulnerabilities)
    else:
        print("No vulnerabilities found or getting error in the middle")


if __name__ == "__main__":
    main()
