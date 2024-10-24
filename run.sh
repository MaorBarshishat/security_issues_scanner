#!/usr/bin/env bash

workdir=/tmp/work

function exit_command {
  echo "exiting... $1"
  rm -rf $workdir 2> /dev/null
  exit 0
}

if [ $# -ne 1 ]
then 
  exit_command "Please provide github repository link"
fi

# step 1: installing requirements
echo "Installing Python requirements..."
pip install -r requirements.txt

# step 2: clone repository and update properties localy
echo "Cloning the Git repository..."
rm -rf $workdir 2> /dev/null
mkdir $workdir
pushd $workdir
if ! git clone $1 .
then
  exit_command "failed to git clone"
fi

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


# step 3: run the sonar scanner docker to scan the code
echo "Running SonarScanner..."
docker run --name sonarscaner --rm --network host -v $(pwd):/usr/src sonarsource/sonar-scanner-cli \
  -Dsonar.projectKey=maorbarshishat_project_key \
  -Dsonar.sources=. \
  -Dsonar.host.url=https://sonarcloud.io/

# waiting until docker completes
docker wait sonarscaner 2> /dev/null

# return to home dir and clear the working directory
popd
rm -rf $workdir

# Step 4: Run the Python script to create a top 5 report
echo "Running the Python script..."
python3 analyze_scan.py

# Step 5: open the vulnerabilities file
open top_5_vulnerabilities.html

exit_command "done, output is at $(pwd)/top_5_vulnerabilities.html"
