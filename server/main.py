from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse, Response
from api.daily_router import router as daily_router
from utils.logger_config import logger

app = FastAPI()

app.include_router(daily_router, prefix="/daily_principle")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 422异常处理
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    try:
        # 获取请求的body
        body = await request.body()
        # 打印请求参数和错误信息
        logger.error(f"422 Validation Error! Path: {request.url.path}")
        logger.error(f"Request body: {body.decode('utf-8')}")
        logger.error(f"Validation details: {exc.errors()}")
    except Exception as e:
        logger.error(f"Failed to log request body: {e}")

    # 自定义返回内容
    return JSONResponse(
        status_code=422,
        content={
            "error_code": 422,
            "message": "Validation Error",
            "details": exc.errors()
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error_code": exc.status_code,
            "message": exc.detail,
        },
    )


# 全局请求／响应日志中间件
@app.middleware("http")
async def log_request_response(request: Request, call_next):
    # 1. 读取并记录请求体
    body_bytes = await request.body()
    body_str = body_bytes.decode('utf-8') if body_bytes else "<empty>"
    logger.info(f">>> REQUEST {request.method} {request.url.path} → Body: {body_str}")

    # 2. 执行下一个处理器，获取 Response
    response: Response = await call_next(request)

    # 3. 读取并记录响应体
    #    注意：Response.body_iterator 是异步生成，所以我们需要把它“吃”下来
    resp_body = b""
    async for chunk in response.body_iterator:
        resp_body += chunk

    # 4. 打日志
    # text = resp_body.decode('utf-8', errors='replace')
    # logger.info(f"<<< RESPONSE {request.method} {request.url.path} ← "
    #              f"Status: {response.status_code} Body: {Bodytext}")

    # 5. 因为我们已经消费了 body_iterator，需要用新的 Response 重建返回值
    new_response = Response(
        content=resp_body,
        status_code=response.status_code,
        headers=dict(response.headers),
        media_type=response.media_type
    )
    return new_response

@app.get("/")
async def root():
    return {"message": "Hello World"}

