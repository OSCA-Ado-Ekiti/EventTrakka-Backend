import secrets
from pathlib import Path, PosixPath

import aiofiles
import jinja2
from aiofiles.os import remove
from playwright.async_api import async_playwright


class PDFGenerator:
    """Generates PDF files from HTML web pages"""

    def __init__(self, template: str | Path):
        self.file_name: str | None = None
        environment = jinja2.Environment()
        if isinstance(template, Path) or isinstance(template, PosixPath):
            template = self._load_template(template)
        self.template_engine = environment.from_string(template)

    async def generate(self, context: dict) -> bytes | None:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()
            await self._render_page(context)
            await page.goto(f"file:///eventtrakka-backend/{self.file_name}")
            pdf_bytes = await page.pdf()
            await browser.close()
            await self._cleanup()
        return pdf_bytes

    async def _render_page(self, context: dict):
        self.file_name = secrets.token_urlsafe(32) + ".html"
        html_content = self.template_engine.render(context)
        async with aiofiles.open(self.file_name, "w") as f:
            await f.write(html_content)

    def _load_template(self, template: Path) -> str:
        """loads a template string from the provided path"""
        content = ""
        with template.open("r") as f:
            content = f.read()
        return content

    async def _cleanup(self):
        await remove(self.file_name)
