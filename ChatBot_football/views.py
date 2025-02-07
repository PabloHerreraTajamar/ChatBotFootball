from django.shortcuts import render, redirect
import os
from dotenv import load_dotenv
from django.http import JsonResponse
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
from django.views.decorators.csrf import csrf_protect
from ChatBotfootball.settings import *


history = []

@csrf_protect
def home(request):
    credential = AzureKeyCredential(AI_KEY)
    ai_client = QuestionAnsweringClient(endpoint=AI_ENDPOINT, credential=credential)
    global history

    if request.method == 'POST':
        if 'reset' in request.POST:
            history.clear()
            return redirect('home')

        user_question = request.POST.get('question', '').strip()
        
        if user_question:
            try:
                response = ai_client.get_answers(
                    question=user_question,
                    project_name=AI_PROJECT_NAME,
                    deployment_name=AI_DEPLOYMENT_NAME
                )

                if response.answers:
                    answer = response.answers[0].answer
                    assistant_reply = f"{answer}"
                    history.append({"question": user_question, "answer": assistant_reply})
                else:
                    history.append({"question": user_question, "answer": "No encontré una respuesta a esa pregunta."})

            except Exception as ex:
                history.append({"question": user_question, "answer": f"Se produjo un error: {str(ex)}"})

    return render(request, 'ChatBot_football/index.html', {
        'history': history,
    })