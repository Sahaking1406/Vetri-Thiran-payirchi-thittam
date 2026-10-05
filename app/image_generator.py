import hashlib
import re
import time
from pathlib import Path

from PIL import (
    Image,
    ImageDraw,
    ImageFont,
)

from .config import settings


NEGATIVE_PROMPT = (
    "text, words, letters, captions, speech bubbles, "
    "watermark, logo, signature, blurry, low quality, "
    "duplicate characters, extra limbs, malformed hands"
)


def _safe_name(
    text: str,
    index: int,
) -> str:

    slug = re.sub(
        r"[^a-zA-Z0-9]+",
        "-",
        text,
    ).strip("-").lower()

    digest = hashlib.sha1(
        text.encode("utf-8")
    ).hexdigest()[:10]

    return (
        f"panel-{index}-"
        f"{slug[:40]}-"
        f"{digest}.png"
    )


def _placeholder(
    prompt: str,
    output_path: Path,
    panel_number: int,
) -> None:

    image = Image.new(
        "RGB",
        (
            settings.image_width,
            settings.image_height,
        ),
        "white",
    )

    draw = ImageDraw.Draw(
        image
    )

    font = ImageFont.load_default()

    draw.text(
        (40, 40),
        f"COMICCRAFT PANEL {panel_number}",
        fill="black",
        font=font,
    )

    draw.text(
        (40, 90),
        "Image generation fallback",
        fill="black",
        font=font,
    )

    draw.text(
        (40, 140),
        prompt[:220],
        fill="black",
        font=font,
    )

    image.save(
        output_path
    )


def _generate_huggingface(
    prompt: str,
) -> Image.Image:

    if not settings.hf_token:

        raise RuntimeError(
            "HF_TOKEN is missing."
        )

    from huggingface_hub import (
        InferenceClient
    )

    client = InferenceClient(
        api_key=settings.hf_token,
        provider="auto",
    )

    image = client.text_to_image(
        prompt=prompt,
        model=settings.hf_image_model,
        negative_prompt=NEGATIVE_PROMPT,
        width=settings.image_width,
        height=settings.image_height,
        num_inference_steps=settings.image_steps,
    )

    return image


def generate_image(
    prompt: str,
    panel_number: int,
) -> str:

    filename = _safe_name(
        prompt,
        panel_number,
    )

    output_path = (
        settings.panel_dir / filename
    )

    provider = (
        settings.image_provider
        .lower()
        .strip()
    )

    try:

        if provider == "huggingface":

            image = _generate_huggingface(
                prompt
            )

            image.save(
                output_path
            )

        elif provider == "placeholder":

            _placeholder(
                prompt,
                output_path,
                panel_number,
            )

        elif provider == "local":

            from .image_generator_local import (
                generate_local_image,
            )

            image = generate_local_image(
                prompt
            )

            image.save(
                output_path
            )

        else:

            raise RuntimeError(
                "Unknown IMAGE_PROVIDER."
            )

        return (
            f"/static/panels/{filename}"
        )

    except Exception as exc:

        print(
            f"[ComicCraft] Image generation failed "
            f"for panel {panel_number}: {exc}"
        )

        print(
            f"[ComicCraft] Using fallback image "
            f"for panel {panel_number}."
        )

        _placeholder(
            prompt,
            output_path,
            panel_number,
        )

        return (
            f"/static/panels/{filename}"
        )