pipeline {
  agent any

  environment {
    PY = 'python3'
    VENV_DIR = '.venv'
    // Create two Jenkins 'Secret text' credentials:
    //   - webex_bot_token (Bot token from developer.webex.com)
    //   - webex_room_id   (WebEx Space ID)
    WEBEX_TOKEN = credentials('webex_bot_token')
    WEBEX_ROOM_ID = credentials('webex_room_id')
  }

  triggers {
    // Webhook endpoint: https://<your-ngrok-domain>/github-webhook/
    githubPush()
  }

  options { timestamps() }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Setup Python') {
      steps {
        sh '''
          set -e
          if command -v python3 >/dev/null 2>&1; then PY=python3; else PY=python; fi
          $PY -m venv ${VENV_DIR}
          . ${VENV_DIR}/bin/activate
          pip install --upgrade pip
          pip install -r requirements.txt
        '''
      }
    }

    stage('Run unit tests') {
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
        def msg = """**✅ Build SUCCESS**
- Job: ${env.JOB_NAME} #${env.BUILD_NUMBER}
- Branch: ${env.BRANCH_NAME ?: 'n/a'}
- Commit: ${env.GIT_COMMIT ? env.GIT_COMMIT.take(7) : 'n/a'}
- Console: ${env.BUILD_URL}console
"""
        httpRequest acceptType: 'APPLICATION_JSON',
          contentType: 'APPLICATION_JSON',
          httpMode: 'POST',
          customHeaders: [[name: 'Authorization', value: "Bearer ${env.WEBEX_TOKEN}"]],
          requestBody: groovy.json.JsonOutput.toJson([roomId: env.WEBEX_ROOM_ID, markdown: msg]),
          url: 'https://webexapis.com/v1/messages',
          validResponseCodes: '200:299'
      }
    }
    failure {
      script {
        def msg = """**❌ Build FAILED**
- Job: ${env.JOB_NAME} #${env.BUILD_NUMBER}
- Branch: ${env.BRANCH_NAME ?: 'n/a'}
- Console: ${env.BUILD_URL}console
"""
        httpRequest acceptType: 'APPLICATION_JSON',
          contentType: 'APPLICATION_JSON',
          httpMode: 'POST',
          customHeaders: [[name: 'Authorization', value: "Bearer ${env.WEBEX_TOKEN}"]],
          requestBody: groovy.json.JsonOutput.toJson([roomId: ${env.WEBEX_ROOM_ID}, markdown: msg]),
          url: 'https://webexapis.com/v1/messages',
          validResponseCodes: '200:299'
      }
    }
    always { cleanWs() }
  }
}
