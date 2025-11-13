pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        VENV_DIR      = '.venv'
        WEBEX_TOKEN   = credentials('Webex_Token')      // Secret text = bot OR personal token
        WEBEX_ROOM_ID = credentials('Webex_room_Id')    // Secret text = roomId
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
                // Only attempt Webex notify if both credentials are present
                def token = env.WEBEX_TOKEN?.trim()
                def roomId = env.WEBEX_ROOM_ID?.trim()
                if (!token || !roomId) {
                    echo 'Webex notification skipped: missing WEBEX_TOKEN or WEBEX_ROOM_ID credentials.'
                    return
                }

                def status = currentBuild.currentResult ?: 'UNKNOWN'
                def message = "Job: ${env.JOB_NAME} #${env.BUILD_NUMBER} | Branch: ${env.BRANCH_NAME ?: 'n/a'} | Result: ${status} | Console: ${env.BUILD_URL}console"

                // Send message; don't fail the build if the API rejects (e.g., 401)
                try {
                    httpRequest(
                        httpMode: 'POST',
                        url: 'https://webexapis.com/v1/messages',
                        customHeaders: [[name: 'Authorization', value: "Bearer ${token}"]],
                        contentType: 'APPLICATION_JSON',
                        validResponseCodes: '200:299',
                        requestBody: groovy.json.JsonOutput.toJson([
                            roomId  : roomId,
                            markdown: "**Build ${status}**\n${message}"
                        ])
                    )
                } catch (e) {
                    echo "Webex notification failed (non-fatal): ${e.message}"
                }
            }
        }
    }
}
