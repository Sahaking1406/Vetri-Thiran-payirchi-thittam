from typing import List

from .schemas import (
    ComicLayoutPanel,
    ComicStory,
)


def build_comic_layout(
    story: ComicStory,
    image_paths: List[str],
) -> list[ComicLayoutPanel]:

    if len(story.panels) != len(image_paths):

        raise ValueError(
            "Number of generated images must "
            "match number of story panels."
        )

    layout = []

    for panel, image_url in zip(
        story.panels,
        image_paths,
    ):

        layout.append(

            ComicLayoutPanel(

                panel_number=panel.panel_number,

                title=panel.title,

                image_path=image_url.removeprefix(
                    "/static/"
                ),

                image_url=image_url,

                scene_description=(
                    panel.scene_description
                ),

                caption=panel.caption,

                narration=panel.narration,

                dialogue=panel.dialogue,
            )
        )

    return layout