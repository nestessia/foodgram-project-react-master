
import csv

from django.core.management import BaseCommand

from recipes.models import Tag


class Command(BaseCommand):
    help = 'Заполнение данных в модель Tag из csv.'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str, help='Путь к файлу')

    def handle(self, *args, **options):
        file_path = 'data/tags.csv'
        try:
            with open(file_path, 'r', encoding='utf-8') as csv_file:
                reader = csv.reader(csv_file)
                self.stdout.write('Заполнение началось')
                for name, color, slug in reader:
                    Tag.objects.create(
                        name=name,
                        color=color,
                        slug=slug
                    )
                self.stdout.write('Заполнение завершено.')
        except FileNotFoundError as e:
            self.stdout.write(f'Ошибка: {e}')
        except Exception as e:
            self.stdout.write(f'Ошибка: {e}')
