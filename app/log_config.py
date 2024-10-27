from pydantic import BaseModel, Field, computed_field


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str | None = Field(default=None)
    LOG_FORMAT: str = Field(default="%(levelprefix)s | %(asctime)s | %(message)s")
    LOG_LEVEL: str = Field(default="INFO")
    LOGGERS: dict | None = Field(default=None)

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False

    @computed_field()
    def loggers(self) -> dict:
        return (
            self.LOGGERS
            if self.LOGGERS is not None
            else {
                self.LOGGER_NAME: {"handlers": ["default"], "level": self.LOG_LEVEL},
            }
        )

    @computed_field()
    def formatters(self) -> dict:
        return {
            "default": {
                "()": "uvicorn.logging.DefaultFormatter",
                "fmt": self.LOG_FORMAT,
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        }

    @computed_field()
    def handlers(self) -> dict:
        return {
            "default": {
                "formatter": "default",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stderr",
            },
        }
