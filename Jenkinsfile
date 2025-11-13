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
                    // Try to locate .env without failing the whole build if absent.
                    def candidatePaths = [ '.env', "${env.WORKSPACE}/.env", '/var/jenkins_home/.env' ]
                    def envPath = candidatePaths.find { fileExists(it) }

                    if (!envPath) {
                        echo 'WARNING: .env file not found. Webex notifications will be skipped.'
                        // Mark a description hint and exit stage early
                        currentBuild.description = ((currentBuild.description ?: '') + ' | no .env -> skip notify').trim()
                        return
                    }
                    echo "Loading secrets from ${envPath}";
                    def dotenv = readFile(envPath)
                    def vars = [:]
                    dotenv.readLines().each { line ->
                        def trimmed = line.trim()
                        if (trimmed && !trimmed.startsWith('#') && trimmed.contains('=')) {
                            def parts = trimmed.split('=', 2)
                            vars[parts[0].trim()] = parts[1].trim()
                        }
                    }
                    def missingKeys = []
                    if (!vars['WEBEX_TOKEN']) missingKeys << 'WEBEX_TOKEN'
                    if (!vars['WEBEX_ROOM_ID']) missingKeys << 'WEBEX_ROOM_ID'
                    if (missingKeys) {
                        echo "WARNING: Missing keys in .env: ${missingKeys.join(', ')}. Skipping notifications.";
                        currentBuild.description = ((currentBuild.description ?: '') + ' | incomplete .env').trim()
                        return
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
                    echo 'Webex notification skipped: secrets not loaded (no or incomplete .env).'
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
