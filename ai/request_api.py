import asyncio
import json
import aiohttp


async def stream_response():
    url = "http://127.0.0.1:8001/trigger/"
    headers = {"Accept": "text/event-stream"}
    params = {"turn": action}
    # music
    # teddybear
    # garden
    # dolphin
    # animal

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            async for line in response.content:
                if line:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith('data:'):
                        data = json.loads(decoded_line[5:].strip())
                        label = data["type"]
                        response_text = data["response"].replace("“", "").replace("”", "")
                        reference_text = data["reference_text"]
                        if "answer" in label:
                            print(f"type:{label}\nreference_text':{reference_text}\nresponse:{response_text}\n")
                        else:
                            print(f"type:{label}\nresponse:{response_text}\n")


if __name__ == "__main__":
    action = input("Please select the person you want to talk to:")
    asyncio.run(stream_response())
