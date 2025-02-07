from django.shortcuts import render, redirect
import os
import logging
from dotenv import load_dotenv
from django.http import JsonResponse
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
from django.views.decorators.csrf import csrf_protect
from ChatBotfootball.settings import *

# Configuración de logging
logger = logging.getLogger(__name__)

# Inicialización de historial
history = []

@csrf_protect
def home(request):
    # Declarar la variable global history al inicio de la función
    global history

    # Cargar las variables de entorno (si usas dotenv, asegúrate de tener el archivo .env cargado)
    load_dotenv()

    # Verificar que las variables de entorno esenciales estén definidas
    if not all([AI_KEY, AI_ENDPOINT, AI_PROJECT_NAME, AI_DEPLOYMENT_NAME]):
        logger.error("Faltan variables de entorno: AI_KEY, AI_ENDPOINT, AI_PROJECT_NAME o AI_DEPLOYMENT_NAME.")
        return render(request, 'ChatBot_football/index.html', {
            'history': history,
            'error': 'Faltan configuraciones en el servidor.'
        })

    credential = AzureKeyCredential(AI_KEY)
    ai_client = QuestionAnsweringClient(endpoint=AI_ENDPOINT, credential=credential)

    if request.method == 'POST':
        if 'reset' in request.POST:
            history.clear()
            return redirect('home')

        user_question = request.POST.get('question', '').strip()

        logger.debug(f"Pregunta del usuario: {user_question}")

        if user_question:
            try:
                logger.debug(f"Enviando a la API con los parámetros: Proyecto: {AI_PROJECT_NAME}, Despliegue: {AI_DEPLOYMENT_NAME}")

                # Realizar la consulta a la API de Azure
                response = ai_client.get_answers(
                    question=user_question,
                    project_name=AI_PROJECT_NAME,
                    deployment_name=AI_DEPLOYMENT_NAME
                )

                # Manejo de la respuesta
                if response.answers:
                    answer = response.answers[0].answer
                    assistant_reply = f"{answer}"
                    logger.debug(f"Respuesta de la API: {assistant_reply}")
                    history.append({"question": user_question, "answer": assistant_reply})
                else:
                    logger.warning(f"No se encontró respuesta para la pregunta: {user_question}")
                    history.append({"question": user_question, "answer": "No encontré una respuesta a esa pregunta."})

            except Exception as ex:
                # Log de error en caso de fallo
                logger.error(f"Se produjo un error al consultar la API: {str(ex)}")
                history.append({"question": user_question, "answer": f"Se produjo un error: {str(ex)}"})

    return render(request, 'ChatBot_football/index.html', {
        'history': history,
    })
