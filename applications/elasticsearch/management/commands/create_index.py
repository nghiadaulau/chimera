"""
Create a search index
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    """Run the management command."""

    help = "Create a new search index using the relevant mapping file."
    description = "Create search index"

    def handle(self):
        """Create new search index."""

        return True
