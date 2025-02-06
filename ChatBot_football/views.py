from django.shortcuts import render, redirect
import os
from dotenv import load_dotenv
from django.http import JsonResponse
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
from django.views.decorators.csrf import csrf_protect

load_dotenv()

ai_endpoint = os.getenv('AI_SERVICE_ENDPOINT')
ai_key = os.getenv('AI_SERVICE_KEY')
ai_project_name = os.getenv('QA_PROJECT_NAME')
ai_deployment_name = os.getenv('QA_DEPLOYMENT_NAME')

credential = AzureKeyCredential(ai_key)
ai_client = QuestionAnsweringClient(endpoint=ai_endpoint, credential=credential)

history = []

@csrf_protect
def home(request):
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
                    project_name=ai_project_name,
                    deployment_name=ai_deployment_name
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