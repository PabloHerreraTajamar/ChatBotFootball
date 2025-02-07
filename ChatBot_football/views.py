from django.shortcuts import render
from django.http import JsonResponse
from azure.core.credentials import AzureKeyCredential
from azure.ai.language.questionanswering import QuestionAnsweringClient
from django.views.decorators.csrf import csrf_exempt
from ChatBotfootball.settings import *

@csrf_exempt
def home(request):
    credential = AzureKeyCredential(AI_KEY)
    ai_client = QuestionAnsweringClient(endpoint=AI_ENDPOINT, credential=credential)

    # Eliminar historial al recargar la página
    if 'history' in request.session:
        del request.session['history']  # Borramos el historial de la sesión

    # Inicializar historial en la sesión si no existe
    if 'history' not in request.session:
        request.session['history'] = []

    if request.method == 'POST':
        if 'reset' in request.POST:
            # Resetear el historial
            request.session['history'] = []
            return JsonResponse({'status': 'success', 'history': []})  # Respuesta JSON para resetear

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
                    request.session['history'].append({"question": user_question, "answer": assistant_reply})
                else:
                    request.session['history'].append({"question": user_question, "answer": "No encontré una respuesta a esa pregunta."})

            except Exception as ex:
                request.session['history'].append({"question": user_question, "answer": f"Se produjo un error: {str(ex)}"})

            # Guardar la sesión después de modificar el historial
            request.session.modified = True

            # Devolver la respuesta en formato JSON
            return JsonResponse({
                'question': user_question,
                'answer': assistant_reply,
                'history': request.session['history']
            })

    # Renderizar la página para la primera carga o cuando no sea una solicitud AJAX
    return render(request, 'ChatBot_football/index.html', {
        'history': request.session.get('history', []),
    })
