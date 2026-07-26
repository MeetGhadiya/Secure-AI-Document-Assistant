from app.services.gemini_service import generate_answer

ctx = [{'document_id':'doc1','chunk_index':0,'text':'This document mentions Python and SQL.'}]
print('Calling generate_answer...')
print(generate_answer('List skills mentioned', ctx))
