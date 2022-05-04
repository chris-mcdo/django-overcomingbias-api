import os
from dataclasses import dataclass
from typing import Optional, Union

import pandadoc
from django.template.loader import render_to_string


def get_supported_writers():
    # Available pandoc output formats
    available_writers = pandadoc.call_pandoc(["--list-output-formats"]).splitlines()
    supported_writers = [
        Writer
        for Writer in CONFIGURED_WRITERS
        if Writer.pandoc_name in available_writers
    ]

    return supported_writers


def get_export_template(item):
    pandoc_template_format = ".html"
    opts = item._meta
    return f"{opts.app_label}/export/{opts.model_name}{pandoc_template_format}"


def render_item(item):
    """Render a ContentItem using a template."""
    export_template = get_export_template(item)

    return render_to_string(export_template, {"item": item})


def render_sequence(items):
    return "\n".join([render_item(item) for item in items])


def export_sequence(sequence, writer):
    # Metadata
    # metadata_template = f"{sequence._meta.app_label}/export/metadata.md"
    # metadata = render_to_string(metadata_template, {"sequence": sequence})

    items = sequence.items.select_subclasses()

    sequence_html = render_sequence(items)

    return writer.convert(input_format="html", input_text=sequence_html)


@dataclass
class PandocWriter:
    """Base class for representing pandoc config options."""

    output_file: Optional[Union[str, bytes, os.PathLike]] = None
    file_suffix: Optional[str] = None
    standalone: bool = True
    template: Optional[str] = None
    binary: bool = False

    @property
    def options(self):
        # Initialise option list
        _options = []

        # Output format
        _options.extend(["-t", self.pandoc_name])

        # Document template
        if self.template:
            _options.extend(["--template", self.template])
        elif self.standalone:
            _options.append("-s")

        # Output channel
        if self.output_file:
            _options.extend(["-o", self.output_file])
        elif self.binary:
            _options.extend(["-o", "-"])

        return _options

    def __str__(self):
        return self.pandoc_name

    def convert(self, input_format, input_text):
        options = ["-f", input_format] + self.options
        decode = not self.binary
        return pandadoc.call_pandoc(
            options=options, input_text=input_text, decode=decode
        )

    def set_output_file(self, path_without_extension):
        self.output_file = f"{path_without_extension}{self.file_suffix}"


@dataclass
class BinaryPandocWriter(PandocWriter):
    binary: bool = True


@dataclass
class TextPandocWriter(PandocWriter):
    binary: bool = False


@dataclass
class PDFPandocWriter(BinaryPandocWriter):
    pandoc_name = "pdf"
    mime_type = "application/pdf"
    file_suffix: Optional[str] = ".pdf"


@dataclass
class MarkdownPandocWriter(TextPandocWriter):
    pandoc_name = "markdown"
    mime_type = "text/markdown"
    file_suffix: Optional[str] = ".md"


@dataclass
class EPUBPandocWriter(BinaryPandocWriter):
    pandoc_name = "epub"
    mime_type = "application/epub+zip"
    file_suffix: Optional[str] = ".epub"


CONFIGURED_WRITERS = [PDFPandocWriter, MarkdownPandocWriter, EPUBPandocWriter]
