pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        VENV_DIR = '.venv'
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python Environment') {
            steps {
                sh '''
                    set -e
                    python3 -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Unit Tests') {
            steps {
                sh '''
                    set -e
                    . ${VENV_DIR}/bin/activate
                    pytest -q --maxfail=1 --disable-warnings
                '''
            }
        }
    }

    post {
        always {
            script {
                // ⚠️ TEMP FOR ASSIGNMENT DEMO ONLY
                // 1) Put your bot token here (NO "Bearer ", just the token)
                // 2) Put your roomId here (Y2lzY29z... string)
                def token  = 'Zjc4MjMwMWYtZWZhMS00OTY0LTkzYjgtOGMzYWNlMjgzMTUzNGEyMGQxYzYtYTZi_P0A1_13494cac-24b4-4f89-8247-193cc92a7636'
                def roomId = 'Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vZmUxOGQ0NjAtYzA0Mi0xMWYwLWExMTEtM2RmZDJiNjVhNjZj'

                def status  = currentBuild.currentResult ?: 'UNKNOWN'
                def message = "Job: ${env.JOB_NAME} #${env.BUILD_NUMBER} | Branch: ${env.BRANCH_NAME ?: 'n/a'} | Result: ${status} | Console: ${env.BUILD_URL}console"

                try {
                    httpRequest(
                        httpMode: 'POST',
                        url: 'https://webexapis.com/v1/messages',
                        customHeaders: [
                            [name: 'Authorization', value: "Bearer ${token}"],
                            [name: 'Content-Type',  value: 'application/json']
                        ],
                        contentType: 'APPLICATION_JSON',
                        validResponseCodes: '200:299',
                        requestBody: groovy.json.JsonOutput.toJson([
                            roomId  : roomId,
                            text    : "Build ${status} - ${message}"
                        ])
                    )
                } catch (e) {
                    echo "Webex notification failed (non-fatal): ${e.message}"
                }
            }
        }
    }
}
