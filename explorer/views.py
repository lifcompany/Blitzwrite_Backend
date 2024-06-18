import json
import requests
import xml.etree.ElementTree as ET
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

class QuestionsExplorer:
    def GetQuestions(self, questionType, userInput, countryCode):
        questionResults = []
        searchQuery = questionType + " " + userInput + " "
        googleSearchUrl = f"http://google.com/complete/search?output=toolbar&gl={countryCode}&q={searchQuery}"

        try:
            result = requests.get(googleSearchUrl)
            result.raise_for_status()
            tree = ET.ElementTree(ET.fromstring(result.content))
            root = tree.getroot()
            for suggestion in root.findall('CompleteSuggestion'):
                question = suggestion.find('suggestion').attrib.get('data')
                questionResults.append(question)
        except requests.exceptions.RequestException as e:
            questionResults.append(f"Request failed: {e}")
        except ET.ParseError as e:
            questionResults.append(f"Failed to parse XML: {e}")

        return questionResults

@csrf_exempt
@require_http_methods(["POST"])
def get_questions(request):
    try:
        data = json.loads(request.body)
        keyword = data.get('keyword', '')
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    if not keyword:
        return JsonResponse({"error": "Keyword is required"}, status=400)

    qObj = QuestionsExplorer()
    questions = qObj.GetQuestions("is", keyword, "us")
    return JsonResponse({"questions": questions})
