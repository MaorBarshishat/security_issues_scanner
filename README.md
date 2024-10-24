# Security Issues Scanner

### Scanner Features
- **OSS Static Tools - SonarQube:** SonarQube is an open-source static analysis tool that identifies code quality issues and security vulnerabilities, providing actionable insights and metrics to improve software quality.
- **Security Analysis:** After scanning, the tool logs the top five security issues identified in the project.
- **Automation:** The entire process is automated using Docker scanner, and python script that anlyze the scan.

## How to Run

### Step 1: Scan The Diractory

write this in your bash
```bash
 Step 1: Create the sonar-project.properties file
cat <<EOL > sonar-project.properties
sonar.projectKey=maorbarshishat_project_key
sonar.projectName=My Project
sonar.projectVersion=2.0
sonar.sources=$(pwd)
sonar.language=java,js,py,go
sonar.sourceEncoding=UTF-8
sonar.host.url=https://sonarcloud.io/
sonar.login=a638b1d8e907795410a757a0da834ceccc3053b0
sonar.javascript.lcov.reportPaths=lcov.info
sonar.exclusions=**/*.java
sonar.organization=maorbarshishat
EOL

echo "Created sonar-project.properties file."

# Step 2: Run SonarScanner using Docker
echo "Running SonarScanner..."
docker run --rm --network host -v $(pwd):/usr/src sonarsource/sonar-scanner-cli \
  -Dsonar.projectKey=maorbarshishat_project_key \
  -Dsonar.sources=. \
  -Dsonar.host.url=https://sonarcloud.io/
```


### Step 2: Analyze The Scanning Results
```bash
# Step 1: Clone the Git repository one directory above the current directory
echo "Cloning the Git repository..."
cd ..
git clone https://github.com/MaorBarshishat/security_issues_scanner.git
cd security_issues_scanner

# Step 2: Install the requirements for the Python script
echo "Installing Python requirements..."
pip install -r requirements.txt

# Step 3: Run the Python script
echo "Running the Python script..."
python3 analyze_scan.py
```
