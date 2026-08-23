from fastapi import FastAPI

from app.ai_tutor.router import router

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="Mock CBT AI Tutor",
    version="1.0.0",
)

app.include_router(router)

# # Allow FastAPI CORS for local development
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=[
#         "http://127.0.0.1:5500",
#         "http://localhost:5500",
#         "http://127.0.0.1:8000",
#         "http://localhost:8000",
#     ],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


@app.get("/")
async def root():

    return {
        "success": True,
        "service": "Mock CBT AI Tutor API",
    }
