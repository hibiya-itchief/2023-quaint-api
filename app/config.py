from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URI = "mysql://quaint:password@localhost/quaint-app"
    TEST_DATABASE_URI = "mysql://quaint:password@localhost/quaint-app-test"
settings= Settings()