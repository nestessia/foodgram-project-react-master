
import csv

from django.core.management import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Заполнение данных в модель Ingredient из csv.'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Путь к файлу')

    def handle(self, *args, **options):
        try:
            file_path = 'data/ingredients.csv'
            with open(file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                self.stdout.write('Заполнение началось')
                for name, measurement_unit in reader:
                    Ingredient.objects.create(
                        name=name,
                        measurement_unit=measurement_unit
                    )
            self.stdout.write('Заполнение завершено.')
        except FileNotFoundError as e:
            self.stdout.write(f'Ошибка: {e}')
        except Exception as e:
            self.stdout.write(f'Ошибка: {e}')
