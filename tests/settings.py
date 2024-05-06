from envparse import Env

env = Env()

REAL_DATABASE_URL = env.str(
    "REAL_DATABASE_URL",
    default="postgresql+asyncpg://sxannyy:7721@0.0.0.0:5432/mobiledogs"
)

TEST_DATABASE_URL = env.str(
    "TEST_DATABASE_URL",
    default="postgresql+asyncpg://sxannyy_test:7721test@0.0.0.0:5433/mobiledogs_test"
)