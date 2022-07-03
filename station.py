import csv


def stops_coord(f_name):
  """Генератор возвращающий по очереди информацию о автобусных остановках"""
  with open(f_name, 'r', encoding='utf-8') as f:
      reader = csv.DictReader(f)
      for row in reader:
        yield row
