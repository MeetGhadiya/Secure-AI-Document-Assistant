import importlib
from app.config import settings

genai = importlib.import_module('google.genai')
client = genai.Client(api_key=settings.GEMINI_API_KEY)
print('client type', type(client))
print('has generate_text?', hasattr(client,'generate_text'))
print('has generate?', hasattr(client,'generate'))
print('module has chats?', hasattr(genai,'chats'))
print('module has models?', hasattr(genai,'models'))
print('module has text?', hasattr(genai,'text'))
print('module has client attr?', hasattr(genai,'client'))
print('dir(client) sample:', [n for n in dir(client) if not n.startswith('_')][:50])
