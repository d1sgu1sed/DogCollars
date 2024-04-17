from envparse import Env

env = Env()

REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default="postgresql+asyncpg://sxannyy:7721@0.0.0.0:5432/mobiledogs"
)