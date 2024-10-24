# Security Issues Scanner

* **OSS Static tools:**
  - **SonarCloud:** is a tool used to scan code to identify vulnerabilities, bugs and code smells. I used the community edition.
  - **SonarScanner:** is the scanner to use when there is no specific scanner for your build system. I used a docker so that way we can clone any repository and scan it locally.

* **Enviroment tools:**
  - **Client App:** I wrote a small python3 based client application that accesses the SonarCloud via REST APIs in order to fetch top 5 vulnerabilities, and write them to a file using html format.
  - **bash script** I have created a bash script to automate the process of installing, cloning, scanning and fetching results.

* **The process**:
1. The bash program clones the input git repository into a /tmp/work folder.
2. A properties file is created on that folder to configure the sonar parameters.
3. Running the sonarscanner docker that will perform the scan locally and send the results to SonarCloud.
4. Executing the python3 client application to access SonarCloud and fetch the 5 top results, and then formatting to a nice html format.

* **Requirements:**
It is assume to have the following on your local machine:
- docker
- python3
- pip

* **How to run:**
The following will apply the code analysis on https://github.com/FudanSELab/train-ticket.git
```bash
git clone https://github.com/MaorBarshishat/security_issues_scanner.git
cd security_issues_scanner
chmod +x run.sh
./run.sh https://github.com/FudanSELab/train-ticket.git
```
In case having permissions issues on your local machine it is possible to run it using sudo
