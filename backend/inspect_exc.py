from app.services.gemini_service import generate_answer
try:
    generate_answer('List skills mentioned', [{'document_id':'doc1','chunk_index':0,'text':'This document mentions Python and SQL.'}])
except Exception as e:
    print('EXC STR:\n', str(e))
    print('\nEXC REPR:\n', repr(e))
    print('\nEXC ARGS:\n', e.args)
    import traceback
    traceback.print_exc()
