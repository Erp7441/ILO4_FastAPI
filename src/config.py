from dotenv import load_dotenv
from pydantic.v1 import BaseSettings
import os

if not load_dotenv():
    try:
        IP = os.environ['IP']
        USER_NAME = os.environ['USER_NAME']
        PASSWORD = os.environ['PASSWORD']
    except KeyError as e:
        raise KeyError(f"Environment variable {e} is not set")


class IloSettings(BaseSettings):
    class Config:
        case_sensitive = True

    IP: str
    USER_NAME: str
    PASSWORD: str


ilo_settings = IloSettings()
