import json

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.common.management.commands.translate import translate_to_latin
from apps.common.models import Country, Region, District, Neighborhood
from core.settings.base import BASE_DIR


class Command(BaseCommand):
    help = "Import regions from a JSON file"

    @transaction.atomic
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.HTTP_NOT_MODIFIED(
                "Import data... wait...",
            )
        )

        with open(BASE_DIR / "apps/common/management/commands/data.json", "r", encoding='utf-8') as json_file:

            data = json.load(json_file)

            country, created = Country.objects.get_or_create(name="O'zbekiston")

            for item in data:

                if item['model'] == 'common.region':

                    Region.objects.get_or_create(
                        country_id=country.id,
                        name=translate_to_latin(item['fields']['title']),
                    )

                elif item['model'] == 'common.district':

                    print(item['fields']['title'])
                    region = Region.objects.get(id=item['fields']['region'])
                    District.objects.get_or_create(
                        region_id=region.id,
                        name=translate_to_latin(item['fields']['title'])
                    )

                elif item['model'] == 'common.neighborhood':

                    district = District.objects.get(id=item['fields']['district'])
                    Neighborhood.objects.get_or_create(
                        district_id=district.id,
                        name=translate_to_latin(item['fields']['title'])
                    )

        self.stdout.write(self.style.SUCCESS("data successfully imported"))
