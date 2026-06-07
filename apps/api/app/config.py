from functools import cached_property

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    output_dir: str = "/app/outputs"
    cors_origins: str = "http://localhost:5173"
    mock_pipeline: bool = True
    ytdlp_audio_format: str = "bestaudio/best"
    ffmpeg_bin: str = "ffmpeg"
    musescore_bin: str = "mscore"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @cached_property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


settings = Settings()
