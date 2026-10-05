from .config import settings
from .schemas import ComicOutline, PanelOutline


def _gemini_client():
    from google import genai

    if not settings.gemini_api_key:
        raise RuntimeError("GEMINI_API_KEY is not configured.")

    return genai.Client(
        api_key=settings.gemini_api_key
    )


def _fallback_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> ComicOutline:

    return ComicOutline(
        panels=[
            PanelOutline(
                panel_number=1,
                title="The Beginning",
                scene_description=(
                    f"{character_name} arrives at {setting}, "
                    f"ready to face the mystery described in the story."
                ),
                image_prompt=(
                    f"A cinematic {art_style} illustration of "
                    f"{character_name} entering {setting}, "
                    f"establishing shot, adventurous atmosphere, "
                    f"dramatic lighting, detailed environment, "
                    f"high quality comic composition"
                ),
            ),
            PanelOutline(
                panel_number=2,
                title="The Discovery",
                scene_description=(
                    f"{character_name} discovers an unexpected clue "
                    f"that changes the direction of the adventure."
                ),
                image_prompt=(
                    f"{character_name} discovering a mysterious clue "
                    f"in {setting}, surprised expression, "
                    f"cinematic composition, atmospheric lighting, "
                    f"detailed {art_style} artwork"
                ),
            ),
            PanelOutline(
                panel_number=3,
                title="The Challenge",
                scene_description=(
                    f"A dangerous obstacle appears and "
                    f"{character_name} must decide what to do."
                ),
                image_prompt=(
                    f"{character_name} facing a dangerous challenge "
                    f"in {setting}, dynamic action pose, "
                    f"dramatic perspective, strong lighting, "
                    f"cinematic {art_style} comic scene"
                ),
            ),
            PanelOutline(
                panel_number=4,
                title="The Climax",
                scene_description=(
                    f"{character_name} confronts the main threat "
                    f"and fights to achieve the goal."
                ),
                image_prompt=(
                    f"{character_name} confronting the main threat "
                    f"in {setting}, intense action scene, "
                    f"epic cinematic framing, dramatic lighting, "
                    f"dynamic {art_style} comic illustration"
                ),
            ),
            PanelOutline(
                panel_number=5,
                title="The New Beginning",
                scene_description=(
                    f"After overcoming the challenge, "
                    f"{character_name} finds peace and looks ahead."
                ),
                image_prompt=(
                    f"{character_name} standing triumphantly in "
                    f"{setting} after the adventure, peaceful ending, "
                    f"beautiful lighting, cinematic wide shot, "
                    f"hopeful atmosphere, polished {art_style} artwork"
                ),
            ),
        ]
    )


def generate_outline(
    story_prompt: str,
    character_name: str,
    setting: str,
    tone: str,
    art_style: str,
) -> ComicOutline:

    try:

        from google.genai import types

        client = _gemini_client()

        prompt = f"""
Create a coherent five-panel comic outline.

Story:
{story_prompt}

Main character:
{character_name}

Setting:
{setting}

Tone:
{tone}

Art style:
{art_style}

Requirements:
- Exactly 5 panels.
- Keep the same protagonist.
- Maintain visual continuity.
- Beginning, development, conflict, climax, ending.
- Each panel needs:
  panel_number,
  title,
  scene_description,
  image_prompt.
- Image prompts must describe character, action,
  environment, lighting and composition.
- No text or speech bubbles in image prompts.

Return only valid JSON.
"""

        response = client.models.generate_content(
            model=settings.gemini_flash_model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=ComicOutline,
                temperature=0.8,
            ),
        )

        if getattr(response, "parsed", None):
            outline = response.parsed
        elif response.text:
            outline = ComicOutline.model_validate_json(
                response.text
            )
        else:
            raise RuntimeError(
                "Gemini returned an empty response."
            )

        if len(outline.panels) != settings.panel_count:
            raise RuntimeError(
                "Invalid panel count returned by Gemini."
            )

        return outline

    except Exception as exc:

        print(
            f"[ComicCraft] Gemini outline unavailable: {exc}"
        )

        print(
            "[ComicCraft] Using local story outline fallback."
        )

        return _fallback_outline(
            story_prompt,
            character_name,
            setting,
            tone,
            art_style,
        )