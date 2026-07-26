import inspect
import importlib
import traceback
from app.config import settings

print('cwd OK')
print('GEMINI_KEY set?', bool(settings.GEMINI_API_KEY))
try:
    genai = importlib.import_module('google.genai')
    print('google.genai loaded')
    print('Client sig:', inspect.signature(genai.Client))
    try:
        genai.Client(api_key=settings.GEMINI_API_KEY)
        print('Client created ok')
    except Exception as e:
        print('Client error:', type(e).__name__, e)
        traceback.print_exc()
except Exception as e:
    print('Import error:', type(e).__name__, e)
    traceback.print_exc()
