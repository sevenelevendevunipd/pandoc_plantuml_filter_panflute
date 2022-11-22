#!/usr/bin/env python

import hashlib
import os
import subprocess
import tempfile
from pathlib import Path

from loguru import logger
from panflute import CodeBlock, Doc, Element, Image, Para, Str

PLANTUML_BIN = os.environ.get("PLANTUML_BIN", "plantuml")


def __get_temp_dir() -> Path:
    temp_dir = Path(tempfile.gettempdir()) / "pandoc_plantuml"
    if not temp_dir.exists():
        temp_dir.mkdir()
    return temp_dir


def __get_extension(doc_format: str, default: str, **kwargs: str):
    return kwargs.get(doc_format, default)


def plantuml(elem: Element, doc: Doc):
    """Pandoc filter that does all the magic :D

    Args:
        elem (Element): Pandoc element
        doc (Doc): Pandoc document

    Returns:
        Optional[Element]: Pandoc element iff the current element is a plantuml code block
    """
    if not isinstance(elem, CodeBlock):
        return None
    if "plantuml" not in elem.classes:
        return None
    caption = elem.attributes["caption"]

    filename = __get_temp_dir() / hashlib.sha256(elem.text.encode()).hexdigest()

    ext = __get_extension(doc.format, "svg", docx="png")
    src = filename.with_suffix(".uml")
    dest = filename.with_suffix(f".{ext}")

    if not dest.exists():
        plantuml_source = elem.text
        if not plantuml_source.startswith("@start"):
            plantuml_source = "@startuml\n" + plantuml_source + "\n@enduml\n"
        src.write_text(plantuml_source)

        subprocess.check_call(PLANTUML_BIN.split() + [f"-t{ext}", src])
        logger.info(f"Created image {str(dest.absolute())}")

    return Para(
        Image(
            Str(caption),
            url=str(dest.absolute()),
            identifier=elem.identifier,  # type: ignore
            attributes=elem.attributes,  # type: ignore
            title="fig:",
        )
    )
