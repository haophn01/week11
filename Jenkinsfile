pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        VENV_DIR      = '.venv'
        // Env var names (left) can be anything, but credentials('...') MUST match Jenkins IDs
        WEBEX_TOKEN   = credentials('WEBEX_TOKEN')       // Jenkins credential ID
        WEBEX_ROOM_ID = credentials('WEBEX_ROOM_ID')     // Jenkins credential ID
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
                // Read from env.* (these are populated by environment { ... } above)
                def token = env.WEBEX_TOKEN?.trim()
                def roomId = env.WEBEX_ROOM_ID?.trim()

                if (!token || !roomId) {
                    echo 'Webex notification skipped: missing WEBEX_TOKEN or WEBEX_ROOM_ID.'
                    echo "DEBUG token len: ${token?.length()}"
                    echo "DEBUG roomId len: ${roomId?.length()}"
                    return
                }

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
