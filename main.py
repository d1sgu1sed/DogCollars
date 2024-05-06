import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRouter

import settings
from api.handlers import user_router

#############################
# блок с API ROUTES
#############################

app = FastAPI(title="MobileDogs_K_and_S")
main_api_router = APIRouter() # главный router

main_api_router.include_router(user_router, prefix="/user", tags=["user"])
app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)