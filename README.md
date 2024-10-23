# Security Issues Scanner

This Telegram bot was created for a technical assessment during an interview. It’s built in Python and is designed to hash `.jpg` and `.jpeg` files sent by users, utilizing the **MD5 algorithm**.

### Scanner Features
- **OSS Static Tools - SonarQube:** SonarQube is an open-source static analysis tool that identifies code quality issues and security vulnerabilities, providing actionable insights and metrics to improve software quality.
- **Security Analysis:** After scanning, the tool logs the top five security issues identified in the project.
- **Automation:** The entire process is automated using Docker.

## How to Run

### Step 1: Create a Properties File
Create a `sonar-project.properties` file in the directory you wish to scan:

```properties
sonar.projectKey=com.companyname.mycoolproject
sonar.projectName=My Cool Project
sonar.projectVersion=2.0
sonar.sources=/home/maor/Desktop/hack_train_ticket/train-ticket
sonar.language=java,js,py,go
sonar.sourceEncoding=UTF-8
sonar.host.url=http://localhost:9000
sonar.login=squ_6d776a666a6b8c781c15cf13fc4179a825719d9e
sonar.javascript.lcov.reportPaths=lcov.info
sonar.exclusions=**/*.java
```

### Step 2: Run the Scanner using Docker
Run the following commands in the directory containing your project:

Wait until the server is up, then access it at http://localhost:9000/. SonarQube provides an intuitive UI where you can monitor the scanning process.
```bash
# Start the SonarQube server
docker run -d --name sonarqube -e SONAR_ES_BOOTSTRAP_CHECKS_DISABLE=true -p 9000:9000 -v sonarqube_data:/opt/sonarqube/data maorbarshishat/sonarqube_server:1.0
```

Next, run this command in the directory you want to scan:
```bash
# Start the scanning
docker run --rm --network host -v $(pwd):/usr/src sonarsource/sonar-scanner-cli -Dsonar.projectKey=com.companyname.mycoolproject -Dsonar.sources=. -Dsonar.host.url=http://localhost:9000
```

After the scanning process completes, analyze the results and store them in output.txt:
```bash
# Start the analysis
docker run --name analyzer analyze_scanning
```
