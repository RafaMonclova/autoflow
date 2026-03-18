pipeline {
    agent any

    environment {
        PROJECT_NAME = "autoflow"
        ENV_SOURCE_PATH = "/var/lib/jenkins/envs"
    }

    stages {

        stage('Prepare environment') {
            steps {
                echo "📁 Copiando archivo .env para ${PROJECT_NAME}..."
                sh '''
                    # Asegurar que la carpeta de origen existe
                    if [ ! -f "${ENV_SOURCE_PATH}/${PROJECT_NAME}/.env" ]; then
                        echo "❌ ERROR: No se encontró el archivo ${ENV_SOURCE_PATH}/${PROJECT_NAME}/.env"
                        exit 1
                    fi

                    # Copiar el archivo .env al workspace del proyecto
                    cp "${ENV_SOURCE_PATH}/${PROJECT_NAME}/.env" .env
                    echo "✅ Archivo .env copiado en el workspace: $(pwd)/.env"
                '''
            }
        }
        
        stage('Deploy') {
            steps {
                echo "🚀 Ejecutando script de despliegue..."
                sh '''
                chmod +x ./deploy.sh
                ./deploy.sh
                '''
            }
        }
    }

    post {
        success {
            echo "✅ Despliegue completado correctamente"
        }
        failure {
            echo "❌ Falló el despliegue"
        }
    }
}