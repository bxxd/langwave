from bs4 import BeautifulSoup, NavigableString
import re
import os
import logging
from types import SimpleNamespace

log = logging.getLogger(__name__)


def file_exists(file_path):
    return os.path.isfile(file_path)


def clean_text(text):
    # return text
    # print(f"clean_text: `{text}`")
    text = text.strip().replace("\n", " ").replace("\t", " ").replace("\r", " ")
    text = " ".join(text.split())
    return text


def get_elements(element):
    if not element:
        log.error(f"element is None")
        return []
    if isinstance(element, NavigableString):
        return []
    texts = []
    for child in element.children:
        s = SimpleNamespace()
        if child.name == "table":
            table = child
            rows = table.find_all("tr")
            table_text = ""
            for row in rows:
                cols = row.find_all("td")
                row_text = ""
                cols = [
                    clean_text(col.text)
                    for col in cols
                    if col.text.strip() not in ["", "$"]
                ]
                if len("".join(cols)):
                    row_text = " | ".join(cols)
                if row_text:
                    table_text += row_text + " "  # add a newline after each row
            s.text = f"{table_text}\n"
            s.type = "table"
            # print(f"s type: `{s.type}` text: `{s.text}`")
            texts.append(s)
        elif child.name == "span":
            s.text = f"{clean_text(child.text)}"
            s.type = "span"
            style = child.get("style", "")
            weight = 0
            if "font-weight" in style:
                weight = int(style.split("font-weight:")[1].split(";")[0])
                if weight > 400:
                    s.type = "h2"
            # print(f"span style: `{style}` child: `{child}`")
            # print(f"s type: `{s.type}` text: `{s.text}` weight: `{weight}`")
            texts.append(s)
        else:
            texts.extend(get_elements(child))
    return texts


def get_sections(file_path):
    if not file_path:
        raise ValueError("file_path is required")
    if not "htm" in file_path:
        file_path = f"docs/filings/{file_path}.htm"
    log.info(f"Reading {file_path}")

    with open(file_path, "rb") as f:
        html = f.read().decode("ISO-8859-1")

    # Parse HTML using BeautifulSoup
    soup = BeautifulSoup(html, "html.parser")

    body = soup.find("body")
    if not body:
        log.warning("No body found, using div")
        body = soup.find("div")

    sections = get_elements(body)

    start = False

    part = ""
    span_found = False

    complete_sections = []

    cnt = 0

    toc = 0

    def add_section(text, cnt):
        nonlocal complete_sections, start
        section = SimpleNamespace()
        section.text = text
        section.cnt = cnt

        complete_sections.append(section)
        if not start:
            lowered = text.lower()
            if (
                "financial" in lowered
                and "balance" in lowered
                and "sheets" in lowered
                and ("table of contents" not in lowered and "index" not in lowered)
            ):
                start = True
                print(f"Found start")
                complete_sections = [section]

    for s in sections[:]:
        text = s.text
        if len(text) <= 3:
            continue

        lowered = text.lower()
        if lowered.startswith("table of contents"):
            print(f"Found table of contents: `{text}` {toc}")
            if toc >= 2:
                continue

            toc += 1
        elif text.startswith(
            "The accompanying notes are an integral part of these unaudited condensed consolidated financial statements"
        ):
            continue

        # print(f"{s.type}: `{text}`")

        if s.type == "h2":
            if (
                "item 6" in lowered and "exhibits" in lowered
            ) or "signatures" in lowered:
                log.info(f"Found end: `{text}`")
                break
            if part and span_found:
                cnt += 1
                log.info(f"creating section {cnt}")
                add_section(part, cnt)
                section = None
                # print(f"section: `{section.text}`")
                part = f"*{text}*"
                span_found = False

            if part:
                part = f"{part} *{text}*"
            else:
                part = f"*{text}*"

        elif s.type in ["span", "table"]:
            span_found = True
            if part:
                part = f"{part} {text}"
            else:
                part = text

    if part:
        add_section(part, cnt)

    return complete_sections


async def main(args):
    sections = get_sections(args.filing)
    for s in sections:
        print(f"### section {s.cnt}:\n`{s.text}`")
    log.info(f"have {len(sections)} sections")


import argparse, asyncio


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--filing", "-f", help="filing document", required=True)
    parser.add_argument("--debug", "-d", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args))
