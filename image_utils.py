from typing import Tuple
from rich.align import Align
from rich.color_triplet import ColorTriplet
from rich.console import Console
from rich.panel import Panel
from rich.terminal_theme import TerminalTheme
import pynvim
from rich.text import Text
from cairosvg import svg2png
import nest_asyncio

# constant that defines the custom font for rendering panels
CODE_FORMAT = """\
<svg class="rich-terminal" viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg"> <style>

    @font-face {{
        font-family: "JetBrainsMono";
        src: local("JetBrainsMono-Medium");
                url("fonts/JetBrainsMono-Medium.ttf") format("ttf");
        font-style: normal;
        font-weight: 400;
    }}
     @font-face {{
        font-family: "JetBrainsMono";
        src: local("JetBrainsMono-Bold"),
                url("fonts/JetBrainsMono-Bold.ttf") format("ttf");
        font-style: bold;
        font-weight: 700;
    }}

    .{unique_id}-matrix {{
        font-family: JetBrainsMono, monospace;
        font-size: {char_height}px;
        line-height: {line_height}px;
        font-variant-east-asian: full-width;
    }}

    .{unique_id}-title {{
        font-size: 18px;
        font-weight: bold;
        font-family: JetBrainsMono;
    }}

    {styles}
    </style>

    <defs>
    <clipPath id="{unique_id}-clip-terminal">
      <rect x="0" y="0" width="{terminal_width}" height="{terminal_height}" />
    </clipPath>
    {lines}
    </defs>

    {chrome}
    <g transform="translate({terminal_x}, {terminal_y})" clip-path="url(#{unique_id}-clip-terminal)">
    {backgrounds}
    <g class="{unique_id}-matrix">
    {matrix}
    </g>
    </g>
</svg>
"""


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ColorTracker(metaclass=Singleton):
    def __init__(self) -> None:
        self.terminal_theme = TerminalTheme(
            (255, 255, 255),
            (0, 0, 0),
            [
                (0, 0, 0),
                (128, 0, 0),
                (0, 128, 0),
                (128, 128, 0),
                (0, 0, 128),
                (128, 0, 128),
                (0, 128, 128),
                (192, 192, 192),
            ],
            [
                (128, 128, 128),
                (255, 0, 0),
                (0, 255, 0),
                (255, 255, 0),
                (0, 0, 255),
                (255, 0, 255),
                (0, 255, 255),
                (255, 255, 255),
            ],
        )
        self.update_colors()

    def update_colors(self) -> None:
        self.text_color, _ = self.get_highlight_colors("Label")
        self.border_color, self.background_color = self.get_highlight_colors(
            "TelescopeBorder"
        )
        # update the terminal theme to match the rendered text
        self.terminal_theme.foreground_color = ColorTriplet(
            *[int(self.border_color[i : i + 2], 16) for i in (0, 2, 4)]
        )
        self.terminal_theme.background_color = ColorTriplet(
            *[int(self.background_color[i : i + 2], 16) for i in (0, 2, 4)]
        )

    # return the foreground and background colors for a highlight group
    def get_highlight_colors(self, highlight_name: str) -> Tuple[str, str]:
        nest_asyncio.apply()
        nvim = pynvim.attach(
            "child", argv=["/usr/bin/env", "nvim", "--embed", "--headless"]
        )
        group = nvim.api.get_hl_by_name(highlight_name, True)

        foreground = group.get("foreground")
        background = group.get("background")
        if not foreground:
            # fall back to the Keyword highlight group if this one is not found for some reason
            group = nvim.api.get_hl_by_name("Keyword", True)
            foreground = group.get("foreground")
        if not background:
            # fall back to the Normal highlight group
            group = nvim.api.get_hl_by_name("Normal", True)
            background = group.get("background")

        # if this is still no good fall back to static colors
        if not foreground:
            foreground = int(0xD85F28)
        if not background:
            background = int(0x18181B)

        nvim.close()
        return (hex(foreground)[2:].zfill(6), hex(background)[2:].zfill(6))

    def create_panel(
        self, text: str, colors: Tuple[str, str, str], height: int
    ) -> Panel:
        return Panel(
            Align.center(
                Text(text, style=f"bold #{colors[0]} on #{colors[2]}"),
                vertical="middle",
            ),
            style=f"#{colors[1]} on #{colors[2]}",
            border_style=f"#{colors[1]} on #{colors[2]}",
            width=max(20, len(str(text)) + 15),
            height=height,
        )

    def save_png(self, panel: Panel, title: str, filename: str, width: int):
        console = Console(record=True, width=width)
        console.print(panel)
        svg = console.export_svg(
            title=title,
            code_format=CODE_FORMAT,
            font_aspect_ratio=0.60,
            theme=self.terminal_theme,
        )
        svg2png(bytestring=svg, write_to=f"resources/{filename}")

    def update_image(self, before: str, after: str, title: str) -> None:
        text = f"{before}: {after}"
        self.save_png(
            panel=self.create_panel(
                text, (self.text_color, self.border_color, self.background_color), 3
            ),
            title=title,
            width=max(20, len(text) + 15),
            filename=f"{title}.png",
        )

    def update_notification_image(self, text: str, title: str) -> None:
        self.save_png(
            panel=self.create_panel(
                text, (self.text_color, self.border_color, self.background_color), 3
            ),
            title=title,
            width=max(20, len(text) + 15),
            filename=f"notification.png",
        )
