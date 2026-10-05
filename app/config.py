from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    debug: bool = True

    # Gemini
    gemini_api_key: str = ""
    gemini_flash_model: str = "gemini-2.5-flash"
    gemini_pro_model: str = "gemini-2.5-pro"

    # Image generation
    # huggingface = hosted inference
    # local = local Diffusers
    # placeholder = development/testing only
    image_provider: str = "huggingface"

    hf_token: str = ""
    hf_image_model: str = "black-forest-labs/FLUX.1-schnell"

    # Local Diffusers
    local_diffusion_model: str = "runwayml/stable-diffusion-v1-5"
    local_device: str = "auto"

    # Comic settings
    panel_count: int = 5

    image_width: int = 768
    image_height: int = 512
    image_steps: int = 4

    output_dir: str = "static"

    max_prompt_length: int = 2000

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def static_dir(self) -> Path:
        return BASE_DIR / self.output_dir

    @property
    def panel_dir(self) -> Path:
        return self.static_dir / "panels"

    @property
    def export_dir(self) -> Path:
        return self.static_dir / "exports"


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

settings.panel_dir.mkdir(parents=True, exist_ok=True)
settings.export_dir.mkdir(parents=True, exist_ok=True)