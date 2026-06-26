import utils.session
import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from routes.mlb_finalscores import CustomJSONResponse
from fastapi.middleware.cors import CORSMiddleware
from routes import (
    nba_predictions, 
    nba_injuries,
    mlb_modelpredictions,
    mlb_adjustedpredictions,
    mlb_finalscores  
)

app = FastAPI(default_response_class=CustomJSONResponse)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(nba_predictions.router, tags=["NBA Predictions"])
app.include_router(nba_injuries.router, tags=["NBA Predictions"])
app.include_router(mlb_modelpredictions.router, tags=["MLB Predictions"])
app.include_router(mlb_adjustedpredictions.router, tags=["MLB Predictions"])
app.include_router(mlb_finalscores.router, tags=["MLB Predictions"]) 

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8080, reload=True)