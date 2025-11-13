pipeline {
    agent any

    triggers {
        // GitHub webhook will hit /github-webhook/
        githubPush()
    }

    environment {
        VENV_DIR      = '.venv'
        WEBEX_TOKEN   = credentials('The_Bot_Access_Token')
        WEBEX_ROOM_ID = credentials('Webex_room_Id')
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
                def message = """**Build SUCCESS**
Job: ${env.JOB_NAME} #${env.BUILD_NUMBER}
Branch: ${env.BRANCH_NAME ?: 'n/a'}
Console: ${env.BUILD_URL}console
"""

                httpRequest(
                    httpMode: 'POST',
                    url: 'https://webexapis.com/v1/messages',
                    customHeaders: [[name: 'Authorization', value: "Bearer ${WEBEX_TOKEN}"]],
                    contentType: 'APPLICATION_JSON',
                    requestBody: groovy.json.JsonOutput.toJson([
                        roomId  : WEBEX_ROOM_ID,
                        markdown: message
                    ])
                )
            }
        }

        failure {
            script {
                def message = """**Build FAILED**
Job: ${env.JOB_NAME} #${env.BUILD_NUMBER}
Branch: ${env.BRANCH_NAME ?: 'n/a'}
Console: ${env.BUILD_URL}console
"""

                httpRequest(
                    httpMode: 'POST',
                    url: 'https://webexapis.com/v1/messages',
                    customHeaders: [[name: 'Authorization', value: "Bearer ${WEBEX_TOKEN}"]],
                    contentType: 'APPLICATION_JSON',
                    requestBody: groovy.json.JsonOutput.toJson([
                        roomId  : WEBEX_ROOM_ID,
                        markdown: message
                    ])
                )
            }
        }
    }
}
