from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .seed import seed
from .routes import products, users, orders, search, deeplinks, agent

app = FastAPI(
    title="CyberCart Workshop API",
    description="Backend for the CyberCart deep-link security workshop.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)
seed()

app.include_router(products.router)
app.include_router(users.router)
app.include_router(orders.router)
app.include_router(search.router)
app.include_router(deeplinks.router)
app.include_router(agent.router)

@app.get("/api/health")
def health():
    return {"status": "ok"}
