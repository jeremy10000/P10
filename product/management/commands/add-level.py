from django.core.management.base import BaseCommand, CommandError
from product.models import Category, Product, Level
from django.db import IntegrityError


# Show messages
STDOUT = True


class Command(BaseCommand):
    """
        usage : add-level -l <level>
        ex : add-level -l "low"

    """

    help = 'Insert level in the database.'

    def add_arguments(self, parser):
        """ new argument """

        parser.add_argument("-l", "--level", type=str)

    def handle(self, *args, **options):
        """ main """

        if not isinstance(options["level"], str):
            raise TypeError("Entrez une chaine de caractère.")

        if options["level"]:
            self.level = options["level"]
            self.insert_levels_in_db()
        else:
            raise TypeError("Usage : add-level -l \"Very High\"")

    def insert_levels_in_db(self):
        """ insert level """

        try:
            data = Level(name=self.level)
            data.save()
            if STDOUT:
                self.stdout.write(self.style.SUCCESS(
                    'Level : "%s", Insertion OK' % self.level)
                )
        except IntegrityError:
            if STDOUT:
                self.stdout.write(self.style.WARNING(
                    'Level : "%s", Insertion FAIL (IntegrityError)'
                    % self.level))
