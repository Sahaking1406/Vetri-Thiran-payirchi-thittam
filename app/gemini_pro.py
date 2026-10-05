from .config import settings
from .schemas import (
    ComicOutline,
    ComicStory,
    PanelStory,
)


def _fallback_story(
    outline: ComicOutline,
    character_name: str,
) -> ComicStory:

    panels = []

    captions = [
        "A new adventure begins.",
        "Something unexpected appears.",
        "The danger is getting closer.",
        "Everything depends on this moment.",
        "The journey reaches its end.",
    ]

    narrations = [
        f"{character_name} steps forward with courage.",
        f"{character_name} carefully investigates the mysterious discovery.",
        f"{character_name} prepares to face the growing danger.",
        f"{character_name} gives everything to overcome the challenge.",
        f"{character_name} smiles, knowing the adventure changed everything.",
    ]

    dialogues = [
        f"{character_name}: I have to find out what is happening.",
        f"{character_name}: This clue must mean something.",
        f"{character_name}: I cannot give up now.",
        f"{character_name}: This ends here!",
        f"{character_name}: I will never forget this journey.",
    ]

    for index, panel in enumerate(
        outline.panels
    ):

        panels.append(
            PanelStory(
                panel_number=panel.panel_number,
                title=panel.title,
                scene_description=panel.scene_description,
                image_prompt=panel.image_prompt,
                caption=captions[index % len(captions)],
                narration=narrations[index % len(narrations)],
                dialogue=dialogues[index % len(dialogues)],
            )
        )

    return ComicStory(
        panels=panels
    )


def generate_story(
    outline: ComicOutline,
    character_name: str,
    tone: str,
) -> ComicStory:

    try:

        from google.genai import types
        from google import genai

        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        client = genai.Client(
            api_key=settings.gemini_api_key
        )

        prompt = f"""
Turn this comic outline into polished comic writing.

Main character:
{character_name}

Tone:
{tone}

Outline:
{outline.model_dump_json(indent=2)}

Requirements:
- Preserve all 5 panels.
- Keep the protagonist consistent.
- Generate a caption.
- Generate narration.
- Generate natural dialogue.
- Keep the storyline coherent.
- Make panel 5 feel like a satisfying conclusion.

Return only valid JSON.
"""

        response = client.models.generate_content(
            model=settings.gemini_pro_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ComicStory,
                temperature=0.9,
            ),
        )

        if getattr(response, "parsed", None):
            story = response.parsed
        elif response.text:
            story = ComicStory.model_validate_json(
                response.text
            )
        else:
            raise RuntimeError(
                "Gemini returned an empty story."
            )

        if len(story.panels) != len(
            outline.panels
        ):
            raise RuntimeError(
                "Story panel count mismatch."
            )

        return story

    except Exception as exc:

        print(
            f"[ComicCraft] Gemini story unavailable: {exc}"
        )

        print(
            "[ComicCraft] Using local story fallback."
        )

        return _fallback_story(
            outline,
            character_name,
        )