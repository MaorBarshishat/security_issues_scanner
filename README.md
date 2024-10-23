# Security Issues Scanner

### Scanner Features
- **OSS Static Tools - SonarQube:** SonarQube is an open-source static analysis tool that identifies code quality issues and security vulnerabilities, providing actionable insights and metrics to improve software quality.
- **Security Analysis:** After scanning, the tool logs the top five security issues identified in the project.
- **Automation:** The entire process is automated using Docker scanner, and python script that anlyze the scan.

## How to Run

### Step 1: Create a Properties File
Create a `sonar-project.properties` file in the directory you wish to scan:

```properties
sonar.projectKey=maorbarshishat_project_key
sonar.projectName=My Project
sonar.projectVersion=2.0
sonar.sources=${pwd}
sonar.language=java,js,py,go
sonar.sourceEncoding=UTF-8
sonar.host.url=https://sonarcloud.io/
sonar.login=82d954c03927143f3b3ee77000e7bf084b2f6a78
sonar.javascript.lcov.reportPaths=lcov.info
sonar.exclusions=**/*.java
sonar.organization=maorbarshishat
```

### Step 2: Run the Scanner using Docker
Run the following command in the directory containing your project and sonar-project.properties file:
```bash
# Start the scanning
docker run --rm --network host -v $(pwd):/usr/src sonarsource/sonar-scanner-cli -Dsonar.projectKey=maorbarshishat_project_key -Dsonar.sources=. -Dsonar.host.url=https://sonarcloud.io/
```

### Step 3: Analyze the scanning results
1. clone the project
2. run the python script
3. see the top_5_vulnerabilities.html
