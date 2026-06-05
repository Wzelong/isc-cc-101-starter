from fastapi import FastAPI

from app.api import chart, notes, terminology

app = FastAPI(title="Larkspur EMR")
app.include_router(chart.router)
app.include_router(notes.router)
app.include_router(terminology.router)
