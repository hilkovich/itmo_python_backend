import json
import uvicorn


async def app(scope, receive, send):
    if scope["type"] == "http" and scope["method"] == "GET":
        if scope["path"].startswith("/factorial"):
            await get_factorial(scope, send)
        elif scope["path"].startswith("/fibonacci"):
            await get_fibonacci(scope, send)
        elif scope["path"].startswith("/mean"):
            await get_mean(receive, send)
        else:
            await send_answer(send)
    else:
        await send_answer(send)


async def send_answer(
    send,
    status_code: int = 404,
    content_type: bytes = b"text/plain",
    body: bytes = b"404 Not Found",
):
    await send(
        {
            "type": "http.response.start",
            "status": status_code,
            "headers": [(b"content-type", content_type)],
        }
    )
    await send(
        {
            "type": "http.response.body",
            "body": body,
        }
    )


def factorial(n: int) -> int:
    if n in [0, 1]:
        return 1
    else:
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result


def fibonacci(n: int) -> int:
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)


async def get_factorial(scope, send):
    query_str = scope["query_string"].decode("utf-8")
    n = query_str.lstrip("n=")

    try:
        n = int(n)
    except ValueError:
        await send_answer(
            send,
            status_code=422,
            body=b"422 Unprocessable Entity",
        )
        return

    if n < 0:
        await send_answer(send, status_code=400, body=b"400 Bad Request")
        return

    result = json.dumps({"result": factorial(n)}).encode("utf-8")
    await send_answer(
        send, status_code=200, content_type=b"application/json", body=result
    )


async def get_fibonacci(scope, send):
    n = scope["path"].lstrip("/fibonacci/")

    try:
        n = int(n)
    except ValueError:
        await send_answer(
            send,
            status_code=422,
            body=b"422 Unprocessable Entity",
        )
        return

    if n < 0:
        await send_answer(send, status_code=400, body=b"400 Bad Request")
        return

    result = json.dumps({"result": fibonacci(n)}).encode("utf-8")
    await send_answer(
        send, status_code=200, content_type=b"application/json", body=result
    )


async def get_mean(receive, send):
    request = await receive()
    body = request["body"]
    if len(body) == 0:
        await send_answer(
            send,
            status_code=422,
            body=b"422 Unprocessable Entity",
        )
        return

    n = json.loads(body)

    if isinstance(n, list):
        if not n:
            await send_answer(
                send,
                status_code=400,
                body=b"400 Bad Request",
            )
            return
        elif not all(isinstance(n, (float, int)) for n in n):
            await send_answer(
                send,
                status_code=404,
                body=b"404 Not Found",
            )
            return
        else:
            mean_result = sum(n) / len(n)
            result = json.dumps({"result": mean_result}).encode("utf-8")
            await send_answer(
                send, status_code=200, content_type=b"application/json", body=result
            )
    else:
        await send_answer(
            send,
            status_code=404,
            body=b"404 Not Found",
        )


if __name__ == "__main__":
    uvicorn.run("hw_1:app", host="127.0.0.1", port=8000, reload=True)
