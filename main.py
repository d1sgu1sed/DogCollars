from fastapi import FastAPI
import uvicorn
from fastapi.routing import APIRouter

from api.handlers.dog_router import dog_router
from api.handlers.user_router import user_router
from api.handlers.task_router import task_router
from api.handlers.login_router import login_router

#####################
# блок с API ROUTES #
#####################

app = FastAPI(title="MobileDogs_K_and_S")

main_api_router = APIRouter() # главный router

main_api_router.include_router(user_router, prefix="/user", tags=["user"])
main_api_router.include_router(dog_router, prefix="/dog", tags=["dog"])
main_api_router.include_router(login_router, prefix="/login", tags=["login"])
main_api_router.include_router(task_router, prefix="/task", tags=["task"])
app.include_router(main_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)