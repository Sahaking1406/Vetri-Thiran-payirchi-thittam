from pathlib import Path

from fastapi import (
    APIRouter,
    Form,
    HTTPException,
    Request,
)

from fastapi.responses import (
    FileResponse,
    HTMLResponse,
)

from fastapi.templating import (
    Jinja2Templates,
)

from .config import settings
from .exporters import save_pdf
from .gemini_flash import generate_outline
from .gemini_pro import generate_story
from .image_generator import generate_image
from .layout_builder import build_comic_layout
from .schemas import (
    ComicGenerationResponse,
    PromptRequest,
)


BASE_DIR = (
    Path(__file__)
    .resolve()
    .parent.parent
)

templates = Jinja2Templates(
    directory=str(
        BASE_DIR / "templates"
    )
)

router = APIRouter()


def _validate_prompt_length(
    story_prompt: str,
) -> None:

    if (
        len(story_prompt.strip())
        > settings.max_prompt_length
    ):

        raise HTTPException(
            status_code=422,
            detail=(
                "Story prompt cannot exceed "
                f"{settings.max_prompt_length} "
                "characters."
            ),
        )


def generate_comic(
    request_data: PromptRequest,
):

    # STEP 1
    # Generate five-panel outline.
    outline = generate_outline(
        request_data.story_prompt,
        request_data.character_name,
        request_data.setting,
        request_data.tone,
        request_data.art_style,
    )

    # STEP 2
    # Generate narration/dialogue.
    story = generate_story(
        outline,
        request_data.character_name,
        request_data.tone,
    )

    # STEP 3
    # Generate images.
    image_paths = []

    for panel in story.panels:

        enhanced_prompt = f"""
{panel.image_prompt}

Character continuity:
Main character name: {request_data.character_name}

Setting:
{request_data.setting}

Art direction:
{request_data.art_style}

Important:
- Keep character appearance consistent.
- Keep the visual style consistent.
- Cinematic comic composition.
- High quality.
- Detailed environment.
- Clear subject.
- No text.
- No speech bubbles.
- No captions.
- No watermark.
- No logo.
"""

        image_path = generate_image(
            enhanced_prompt,
            panel.panel_number,
        )

        image_paths.append(
            image_path
        )

    # STEP 4
    # Build final layout.
    layout = build_comic_layout(
        story,
        image_paths,
    )

    # STEP 5
    # Generate PDF.
    title = (
        f"{request_data.character_name}: "
        f"{outline.panels[0].title}"
    )

    pdf_url = save_pdf(
        title,
        layout,
    )

    return (
        title,
        layout,
        pdf_url,
    )


@router.get(
    "/",
    response_class=HTMLResponse,
)
def home(
    request: Request,
):

    return templates.TemplateResponse(
        request,
        "index.html",
        {
            "defaults": {
                "setting": "enchanted forest",
                "tone": "dramatic",
                "art_style": "comic book",
            }
        },
    )


@router.post(
    "/generate",
    response_class=HTMLResponse,
)
def generate_form(
    request: Request,

    story_prompt: str = Form(...),

    character_name: str = Form(...),

    setting: str = Form(...),

    tone: str = Form(...),

    art_style: str = Form(...),
):

    _validate_prompt_length(
        story_prompt
    )

    payload = PromptRequest(
        story_prompt=story_prompt,
        character_name=character_name,
        setting=setting,
        tone=tone,
        art_style=art_style,
    )

    try:

        title, layout, pdf_url = (
            generate_comic(payload)
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "defaults": {
                    "story_prompt": story_prompt,
                    "character_name": character_name,
                    "setting": setting,
                    "tone": tone,
                    "art_style": art_style,
                },
                "error": str(exc),
            },
            status_code=500,
        )

    return templates.TemplateResponse(
        request,
        "comic_preview.html",
        {
            "title": title,
            "layout": layout,
            "pdf_url": pdf_url,
        },
    )


@router.post(
    "/generate-comic/json",
    response_model=ComicGenerationResponse,
)
def generate_json(
    payload: PromptRequest,
):

    _validate_prompt_length(
        payload.story_prompt
    )

    try:

        title, layout, pdf_url = (
            generate_comic(payload)
        )

        return ComicGenerationResponse(
            title=title,
            panels=layout,
            pdf_url=pdf_url,
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=str(exc),
        ) from exc


@router.get(
    "/test-image",
    response_class=HTMLResponse,
)
def test_image(
    request: Request,
    prompt: str = (
        "A brave fox "
        "in an enchanted forest"
    ),
):

    try:

        image_url = generate_image(
            prompt,
            999,
        )

    except Exception as exc:

        return templates.TemplateResponse(
            request,
            "index.html",
            {
                "error": str(exc),
            },
            status_code=500,
        )

    return HTMLResponse(
        f"""
        <!DOCTYPE html>

        <html>

        <head>
            <title>ComicCraft Image Test</title>

            <style>
                body {{
                    font-family: Arial;
                    padding: 40px;
                    background: #f5f5f5;
                }}

                img {{
                    max-width: 900px;
                    width: 100%;
                    border-radius: 15px;
                }}
            </style>
        </head>

        <body>

            <h1>ComicCraft Image Test</h1>

            <p>
                Image generation test successful.
            </p>

            <img
                src="{image_url}"
                alt="Generated test image"
            >

            <p>
                <a href="/">
                    ← Back to ComicCraft
                </a>
            </p>

        </body>

        </html>
        """
    )


@router.get(
    "/download/{filename}"
)
def download_pdf(
    filename: str,
):

    safe_name = Path(
        filename
    ).name

    path = (
        settings.export_dir
        / safe_name
    )

    if not path.exists():

        raise HTTPException(
            status_code=404,
            detail="PDF not found.",
        )

    return FileResponse(
        path,
        media_type="application/pdf",
        filename=safe_name,
    )


@router.get(
    "/export-success",
    response_class=HTMLResponse,
)
def export_success(
    request: Request,
    pdf_path: str = "",
):

    return templates.TemplateResponse(
        request,
        "export_success.html",
        {
            "pdf_path": pdf_path,
        },
    )