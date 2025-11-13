pipeline {
    agent any

    triggers {
        // GitHub webhook will hit /github-webhook/
        githubPush()
    }

    environment {
        VENV_DIR      = '.venv'
        // These IDs must match your Jenkins credentials exactly
        WEBEX_TOKEN   = credentials('Webex_Token')
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
                    customHeaders: [[name: 'Authorization', value: "Bearer ${env.WEBEX_TOKEN}"]],
                    contentType: 'APPLICATION_JSON',
                    requestBody: groovy.json.JsonOutput.toJson([
                        roomId  : env.WEBEX_ROOM_ID,
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
                    customHeaders: [[name: 'Authorization', value: "Bearer ${env.WEBEX_TOKEN}"]],
                    contentType: 'APPLICATION_JSON',
                    requestBody: groovy.json.JsonOutput.toJson([
                        roomId  : env.WEBEX_ROOM_ID,
                        markdown: message
                    ])
                )
            }
        }
    }
}
