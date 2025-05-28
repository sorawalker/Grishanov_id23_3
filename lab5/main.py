from fastapi import FastAPI
from fastapi.security import HTTPBearer
from app.api.endpoints import router
from app.websocket.endpoints import router as websocket_router
from app.db.database import engine
from app.models.user import Base
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI()

security = HTTPBearer()

app.include_router(router)
app.include_router(websocket_router, prefix="/websocket", tags=["websocket"])

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)
