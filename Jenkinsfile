pipeline {
    agent any

    triggers {
        githubPush()
    }

    environment {
        VENV_DIR      = '.venv'
        // WEBEX_TOKEN   = credentials('Webex_Token')      // Secret text = bot OR personal token
        // WEBEX_ROOM_ID = credentials('Webex_room_Id')    // Secret text = roomId
        WEBEX_TOKEN   = 'Zjc4MjMwMWYtZWZhMS00OTY0LTkzYjgtOGMzYWNlMjgzMTUzNGEyMGQxYzYtYTZi_P0A1_13494cac-24b4-4f89-8247-193cc92a7636'    
        WEBEX_ROOM_ID = 'Y2lzY29zcGFyazovL3VybjpURUFNOnVzLXdlc3QtMl9yL1JPT00vZmUxOGQ0NjAtYzA0Mi0xMWYwLWExMTEtM2RmZDJiNjVhNjZj'
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
                    # Detect python executable (python3 preferred, fallback to python)
                    if command -v python3 >/dev/null 2>&1; then PY=python3; 
                    elif command -v python >/dev/null 2>&1; then PY=python; 
                    else echo "Python not found on agent"; exit 127; fi

                    "$PY" -m venv ${VENV_DIR}
                    . ${VENV_DIR}/bin/activate
                    "$PY" -m pip install --upgrade pip
                    "$PY" -m pip install -r requirements.txt
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
