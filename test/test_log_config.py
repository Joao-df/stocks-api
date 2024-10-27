from app.log_config import LogConfig


class TestLogConfig:
    def test_default_initialization(self) -> None:
        config = LogConfig()
        assert config.LOGGER_NAME is None
        assert config.LOG_FORMAT == "%(levelprefix)s | %(asctime)s | %(message)s"
        assert config.LOG_LEVEL == "INFO"
        assert config.version == 1
        assert config.disable_existing_loggers is False

    def test_custom_logger_name(self) -> None:
        custom_name = "customLogger"
        config = LogConfig(LOGGER_NAME=custom_name)
        assert config.loggers[custom_name]["handlers"] == ["default"]
        assert config.loggers[custom_name]["level"] == "INFO"

    def test_log_format_application(self) -> None:
        config = LogConfig()
        formatter = config.formatters["default"]["fmt"]
        assert formatter == "%(levelprefix)s | %(asctime)s | %(message)s"

    def test_log_level_setting(self) -> None:
        config = LogConfig(LOG_LEVEL="DEBUG")
        assert config.loggers[None]["level"] == "DEBUG"

    def test_empty_loggers_dict_behavior(self) -> None:
        config = LogConfig(LOGGERS={})
        assert len(config.loggers) == 0
