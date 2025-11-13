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

        success {
            script {

                def message = "Build SUCCESS - Job: ${env.JOB_NAME} #${env.BUILD_NUMBER} - Console: ${env.BUILD_URL}console"

                // OPTIONAL DEBUG - REMOVE ONCE IT WORKS
                echo "DEBUG: TOKEN LENGTH = ${env.WEBEX_TOKEN?.length()}"
                echo "DEBUG: ROOMID LENGTH = ${env.WEBEX_ROOM_ID?.length()}"

                httpRequest(
                    httpMode: 'POST',
                    url: 'https://webexapis.com/v1/messages',
                    customHeaders: [
                        [name: 'Authorization', value: "Bearer ${env.WEBEX_TOKEN}"],
                        [name: 'Content-Type', value: 'application/json']
                    ],
                    requestBody: """
                    {
                        "roomId": "${env.WEBEX_ROOM_ID}",
                        "text": "${message}"
                    }
                    """
                )
            }
        }

        failure {
            script {

                def message = "Build FAILED - Job: ${env.JOB_NAME} #${env.BUILD_NUMBER} - Console: ${env.BUILD_URL}console"

                httpRequest(
                    httpMode: 'POST',
                    url: 'https://webexapis.com/v1/messages',
                    customHeaders: [
                        [name: 'Authorization', value: "Bearer ${env.WEBEX_TOKEN}"],
                        [name: 'Content-Type', value: 'application/json']
                    ],
                    requestBody: """
                    {
                        "roomId": "${env.WEBEX_ROOM_ID}",
                        "text": "${message}"
                    }
                    """
                )
            }
        }
    }
}
