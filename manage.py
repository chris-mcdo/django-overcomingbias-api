#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

import django
from django.core.management import call_command, execute_from_command_line


def main():
    """Run administrative tasks."""
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.test_settings")
    django.setup()
    call_command("migrate")
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
