from datetime import datetime
from pathlib import Path
import re
import unicodedata

from fpdf import FPDF


from .config import settings
from .schemas import ComicLayoutPanel


def _absolute_image_path(
    panel: ComicLayoutPanel,
) -> Path:

    return (
        settings.static_dir
        / panel.image_path
    )


def _clean_text(
    text: str,
) -> str:

    if not text:
        return ""

    # Convert problematic Unicode punctuation
    # into PDF-safe equivalents.
    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2212": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "\u200b": "",
        "\u200c": "",
        "\u200d": "",
        "\ufeff": "",
        "\t": " ",
    }

    for old, new in replacements.items():
        text = text.replace(
            old,
            new,
        )

    # Normalize Unicode.
    text = unicodedata.normalize(
        "NFKD",
        text,
    )

    # Remove unsupported characters for
    # the built-in Helvetica font.
    text = (
        text
        .encode(
            "latin-1",
            errors="replace",
        )
        .decode("latin-1")
    )

    # Remove repeated spaces.
    text = re.sub(
        r"[ ]{2,}",
        " ",
        text,
    )

    return text.strip()


def _safe_multicell(
    pdf: FPDF,
    text: str,
    height: float,
    align: str = "L",
) -> None:

    cleaned = _clean_text(
        text
    )

    if not cleaned:
        return

    pdf.multi_cell(
        w=0,
        h=height,
        text=cleaned,
        align=align,
        wrapmode="CHAR",
        new_x="LMARGIN",
        new_y="NEXT",
    )


def save_pdf(
    title: str,
    layout: list[ComicLayoutPanel],
) -> str:

    timestamp = datetime.now().strftime(
        "%Y%m%d-%H%M%S-%f"
    )

    filename = (
        f"comiccraft-{timestamp}.pdf"
    )

    output_path = (
        settings.export_dir
        / filename
    )

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4",
    )

    pdf.set_margins(
        left=15,
        top=15,
        right=15,
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=18,
    )

    # Small horizontal padding prevents
    # edge-space problems.
    pdf.c_margin = 1

    for panel in layout:

        pdf.add_page()

        # =====================================
        # PANEL TITLE
        # =====================================

        pdf.set_font(
            "Helvetica",
            "B",
            18,
        )

        _safe_multicell(
            pdf,
            f"Panel {panel.panel_number}: {panel.title}",
            9,
            "C",
        )

        pdf.ln(3)

        # =====================================
        # IMAGE
        # =====================================

        image_path = (
            _absolute_image_path(
                panel
            )
        )

        if image_path.exists():

            pdf.image(
                str(image_path),
                x=15,
                y=38,
                w=180,
            )

            pdf.set_y(143)

        else:

            pdf.set_y(40)

            pdf.set_font(
                "Helvetica",
                "I",
                10,
            )

            _safe_multicell(
                pdf,
                "Image unavailable.",
                6,
                "C",
            )

        # =====================================
        # SCENE DESCRIPTION
        # =====================================

        pdf.set_font(
            "Helvetica",
            "I",
            10,
        )

        _safe_multicell(
            pdf,
            panel.scene_description,
            5.5,
        )

        pdf.ln(2)

        # =====================================
        # CAPTION
        # =====================================

        pdf.set_font(
            "Helvetica",
            "B",
            10.5,
        )

        _safe_multicell(
            pdf,
            f"Caption: {panel.caption}",
            5.5,
        )

        pdf.ln(1)

        # =====================================
        # NARRATION
        # =====================================

        pdf.set_font(
            "Helvetica",
            "",
            10.5,
        )

        _safe_multicell(
            pdf,
            f"Narration: {panel.narration}",
            5.5,
        )

        # =====================================
        # DIALOGUE
        # =====================================

        if panel.dialogue:

            pdf.ln(2)

            pdf.set_font(
                "Helvetica",
                "B",
                10.5,
            )

            _safe_multicell(
                pdf,
                "Dialogue:",
                5.5,
            )

            pdf.set_font(
                "Helvetica",
                "",
                10.5,
            )

            _safe_multicell(
                pdf,
                f'"{panel.dialogue}"',
                5.5,
            )

        # =====================================
        # FOOTER
        # =====================================

        pdf.set_y(
            -12
        )

        pdf.set_font(
            "Helvetica",
            "",
            7,
        )

        pdf.cell(
            0,
            5,
            "Created with ComicCraft",
            align="C",
        )

    pdf.output(
        str(output_path)
    )

    return (
        f"/static/exports/{filename}"
    )