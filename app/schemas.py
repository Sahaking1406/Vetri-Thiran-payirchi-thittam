from typing import List

from pydantic import BaseModel, Field, field_validator


class PromptRequest(BaseModel):
    story_prompt: str = Field(
        min_length=3,
        max_length=2000,
    )

    character_name: str = Field(
        default="Alex",
        min_length=1,
        max_length=80,
    )

    setting: str = Field(
        default="enchanted forest",
        min_length=1,
        max_length=120,
    )

    tone: str = Field(
        default="dramatic",
        min_length=1,
        max_length=50,
    )

    art_style: str = Field(
        default="comic book",
        min_length=1,
        max_length=80,
    )

    @field_validator(
        "story_prompt",
        "character_name",
        "setting",
        "tone",
        "art_style",
    )
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError(
                "Value cannot be empty."
            )

        return value


class PanelOutline(BaseModel):
    panel_number: int = Field(ge=1)
    title: str
    scene_description: str
    image_prompt: str


class ComicOutline(BaseModel):
    panels: List[PanelOutline]


class PanelStory(BaseModel):
    panel_number: int
    title: str
    scene_description: str
    image_prompt: str
    caption: str
    narration: str
    dialogue: str = ""


class ComicStory(BaseModel):
    panels: List[PanelStory]


class ComicLayoutPanel(BaseModel):
    panel_number: int
    title: str

    image_path: str
    image_url: str

    scene_description: str
    caption: str
    narration: str
    dialogue: str = ""


class ComicGenerationResponse(BaseModel):
    title: str
    panels: List[ComicLayoutPanel]
    pdf_url: str