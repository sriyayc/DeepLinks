import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import Base, engine
from .seed import seed
from .routes import products, users, orders, search, deeplinks, agent, cart, admin, challenges

app = FastAPI(
    title="CyberCart Workshop API",
    description="Backend for the CyberCart deep-link security workshop.",
)

# Vite may be opened through either local hostname during development.
# In hosted deployments (e.g. Railway) set ALLOWED_ORIGINS to a comma-separated
# list of shop frontend origins, e.g. "https://cybercart-frontend.up.railway.app".
# Keep this scoped to the shop frontend; never add the attacker origin here.
_default_origins = "http://localhost:5173,http://127.0.0.1:5173"
_allowed_origins = [
    o.strip()
    for o in os.getenv("ALLOWED_ORIGINS", _default_origins).split(",")
    if o.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
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
app.include_router(cart.router)
app.include_router(admin.router)
app.include_router(challenges.router)


@app.get("/api/health")
def health():
    return {"status": "ok"}
