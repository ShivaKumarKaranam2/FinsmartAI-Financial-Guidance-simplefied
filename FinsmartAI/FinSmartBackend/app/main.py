import time
import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response

from app.core.config import settings
from app.core.logging import setup_logger
from app.api.routers import (
    rag_router,
    finance_router,
    sentiment_router,
    budget_router,
    portfolio_router,
)

logger = setup_logger("finsmart.app")


def create_app() -> FastAPI:
    """Creates and configures a FastAPI application instance."""
    app = FastAPI(
        title=settings.title,
        description=settings.description,
        version=settings.version,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS Configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    from starlette.concurrency import iterate_in_threadpool

    @app.middleware("http")
    async def log_requests_middleware(request: Request, call_next):
        """
        Logs every HTTP request:
          - INPUT: HTTP method, path, query params, and body payload
          - OUTPUT: Status code, duration in ms, and response payload
        """
        start_time = time.time()
        client_host = request.client.host if request.client else "unknown"
        path = request.url.path
        method = request.method
        query_str = str(request.query_params) if request.query_params else ""

        # Capture Request Body (Input)
        body_preview = ""
        content_type = request.headers.get("content-type", "")
        if "multipart/form-data" in content_type:
            body_preview = "<multipart file upload>"
        else:
            try:
                body_bytes = await request.body()
                if body_bytes:
                    body_preview = body_bytes.decode("utf-8", errors="ignore")
                    if len(body_preview) > 300:
                        body_preview = body_preview[:300] + " ... [truncated]"
            except Exception:
                body_preview = "<unreadable body>"

        input_log = f"📥 [HTTP INPUT] {method} {path}"
        if query_str:
            input_log += f" | Query: {query_str}"
        if body_preview:
            input_log += f" | Body: {body_preview}"
        logger.info(input_log)

        try:
            response: Response = await call_next(request)
            duration_ms = round((time.time() - start_time) * 1000, 1)
            status = response.status_code

            # Capture Response Body (Output)
            resp_content_type = response.headers.get("content-type", "")

            # For Server-Sent Events / Streams: do not buffer chunks, return immediately
            if "text/event-stream" in resp_content_type or getattr(response, "is_streaming", False):
                output_log = f"📤 [HTTP OUTPUT] {method} {path} -> {status} ({duration_ms}ms) | Response: <Server-Sent Event Stream>"
                logger.info(output_log)
                response.headers["X-Process-Time-Ms"] = str(duration_ms)
                return response

            output_preview = ""
            if hasattr(response, "body_iterator") and response.body_iterator:
                try:
                    res_body = [section async for section in response.body_iterator]
                    response.body_iterator = iterate_in_threadpool(iter(res_body))
                    raw_bytes = b"".join(res_body)
                    raw_str = raw_bytes.decode("utf-8", errors="ignore")
                    output_preview = raw_str[:300] + (" ... [truncated]" if len(raw_str) > 300 else "")
                except Exception as e_out:
                    output_preview = f"<stream unbuffered: {e_out}>"
            elif hasattr(response, "body") and response.body:
                raw_str = response.body.decode("utf-8", errors="ignore")
                output_preview = raw_str[:300] + (" ... [truncated]" if len(raw_str) > 300 else "")

            output_log = f"📤 [HTTP OUTPUT] {method} {path} -> {status} ({duration_ms}ms) | Response: {output_preview}"
            if status >= 500:
                logger.error(output_log)
            elif status >= 400:
                logger.warning(output_log)
            else:
                logger.info(output_log)

            response.headers["X-Process-Time-Ms"] = str(duration_ms)
            return response

        except Exception as exc:
            duration_ms = round((time.time() - start_time) * 1000, 1)

            logger.error(f"🔥 [HTTP EXCEPTION] {method} {path} ({duration_ms}ms) - {exc}", exc_info=True)
            raise


    # Register API Routers
    app.include_router(rag_router, prefix="/api/rag", tags=["FinRAG (Document QA)"])
    app.include_router(finance_router, prefix="/api/finance_rag", tags=["Personal Finance Assistant"])
    app.include_router(sentiment_router, prefix="/api/sentiment", tags=["Market Sentiment"])
    app.include_router(budget_router, prefix="/api/budget", tags=["Budget Recommendations"])
    app.include_router(portfolio_router, prefix="/api/portfolio", tags=["Investment Advisor"])

    # Root & Health Endpoints
    @app.get("/", tags=["Health"])
    async def root():
        return {
            "service": settings.title,
            "status": "running 🚀",
            "version": settings.version,
            "docs": "/docs",
            "active_llm_model": settings.llm.default_model
        }

    @app.get("/health", tags=["Health"])
    async def health_check():
        return {
            "status": "healthy",
            "version": settings.version,
            "active_llm_model": settings.llm.default_model
        }

    return app


app = create_app()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

