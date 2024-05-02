import csv
import math
import copy
import pandas


def get_data_deprecated(filepath):
    file = open(file=filepath, mode="r", encoding="utf-8-sig")
    file_data = []

    initial_row = True
    id_index = None
    reader = csv.reader(file, delimiter=";")
    for row in reader:
        if initial_row:
            for value in row:
                if value.lower() == "id":
                    id_index = row.index(value)
            initial_row = False
        else:
            if id_index is not None:
                row.pop(id_index)
            file_data.append(row)

    file.close()

    return file_data


# Читает таблицу и приводит в формат списка без стобца ID
def get_samples(filepath):
    excel_data = pandas.read_excel(filepath)
    data = pandas.DataFrame(excel_data).drop('ID', axis=1)
    return data.values.tolist()


# Разделение вещественных чисел на группы округляя их до round_to знаков после запятой
def segregate_floats(table, round_to):
    min_max = []
    table_copy = copy.deepcopy(table)

    for i in range(0, len(table[0])):
        #Если строка то не сегрегируем
        if isinstance(table[0][i], str):
            continue

        min = table[0][i]
        max = table[0][i]
        for j in range(0, len(table)):
            if min > table[j][i]:
                min = table[j][i]
            if max < table[j][i]:
                max = table[j][i]

        min_max.append((i, min, max))

    for values in min_max:
        index = values[0]

        for i in range(0, len(table)):
            table_copy[i][index] = f"{round(table[i][index], round_to)}"
    return table_copy
