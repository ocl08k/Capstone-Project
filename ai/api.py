import json
from fastapi import FastAPI, Query, Request
from fastapi.responses import StreamingResponse
from main import answer_streaming

app = FastAPI()


async def event_generator(request: Request, character: str):
    async for model_response, reference_text, is_answer in answer_streaming(character=character, batch=3):
        if await request.is_disconnected():
            break
        if is_answer:
            yield f"data: {json.dumps({'type': 'answer', 'response': model_response, 'reference_text': reference_text})}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'report', 'response': model_response, 'reference_text': reference_text})}\n\n"


@app.get("/trigger/")
async def trigger_process(request: Request,
                          turn: str = Query(..., description="The message to send to the model")):
    headers = {
        "Content-Type": "text/event-stream",
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
    }
    return StreamingResponse(event_generator(request, turn), media_type="text/event-stream", headers=headers)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8001)
