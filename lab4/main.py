from fastapi import FastAPI
from fastapi.security import HTTPBearer
from app.api.endpoints import router
from app.db.database import engine
from app.models.user import Base
from dotenv import load_dotenv

load_dotenv()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="TSP API",
    description="API for Traveling Salesman Problem with user authentication",
    version="1.0.0"
)

# Add security scheme for Swagger
security = HTTPBearer()

app.include_router(router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=3000)
