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

        stage('Load .env Secrets') {
            steps {
                script {
                    if (!fileExists('.env')) {
                        error 'Missing .env file in workspace. Provide it (not committed) on the agent before running.'
                    }
                    def dotenv = readFile('.env')
                    def vars = [:]
                    dotenv.readLines().each { line ->
                        def trimmed = line.trim()
                        if (trimmed && !trimmed.startsWith('#') && trimmed.contains('=')) {
                            def parts = trimmed.split('=', 2)
                            vars[parts[0].trim()] = parts[1].trim()
                        }
                    }
                    if (!vars['WEBEX_TOKEN'] || !vars['WEBEX_ROOM_ID']) {
                        error 'WEBEX_TOKEN or WEBEX_ROOM_ID missing in .env file.'
                    }
                    // Export into environment for later stages/post
                    env.WEBEX_TOKEN   = vars['WEBEX_TOKEN']
                    env.WEBEX_ROOM_ID = vars['WEBEX_ROOM_ID']
                    echo 'Loaded WEBEX_TOKEN and WEBEX_ROOM_ID from .env'
                }
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
                def token  = env.WEBEX_TOKEN
                def roomId = env.WEBEX_ROOM_ID

                if (!token || !roomId) {
                    echo 'Webex notification skipped: secrets not loaded.'
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
