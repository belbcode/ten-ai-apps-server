from flask import Flask, request, Response
from flask_cors import CORS, cross_origin
from citable import chunk_texts, citable_sequential_chain
import json, math
from utils.async_res import batch
import asyncio

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

loop = asyncio.get_event_loop()


@app.route("/", methods=["GET", "POST"])
@cross_origin()
def echo():
    if request.method == "POST":
        response_body = request.data.decode('utf8').replace("'", '"')
        response_body = json.loads(response_body)
        response_body['echo'] = True

        return response_body
    
@app.route("/cite", methods=['POST'])
@cross_origin()
def cite():
    if request.method == "POST":
        response_body = json.loads(request.data)
        word_count = response_body['wordCount']
        chunks = response_body['chunks']
        chunk_size = math.floor(word_count / chunks)
        text_chunks = chunk_texts(response_body['text'], chunk_size)
        # response = [citable_sequential_chain(chunk)['output'] for chunk in text_chunks]
        # return response
        async def routine(chunk):
            citable_sequential_chain(chunk)
        async def yield_by_chunk(chunks):
            for chunk in chunks:
                try:
                    worker = asyncio.create_task(routine(chunk))
                    worker.add_done_callback(lambda a: print(a.result))
                except(json.decoder.JSONDecodeError):
                    #log this error somewhere
                    continue

        
        loop.run_until_complete(yield_by_chunk(text_chunks))
        return {"happy": ":)"}







# @app.route("/wait", methods=["GET"])
# @cross_origin()
# def while_you_wait():
#     return quips

# def request_method(request : request, method_handler):
#     for method in method_handler:
#         if request.method == method:
#             return method
#     raise NotImplementedError("This route does not support the requested method")

# def generateQuips():
#     global res
#     try:
#         res = json.loads(loading_statements())
#     except(json.JSONDecodeError):
#         LLMParsingError.log_error("not yet implemented")
#         return LLMParsingError("What doth life.?. life.?. life.?.")
#     return res
# quips = generateQuips()