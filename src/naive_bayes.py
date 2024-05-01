from src import util


class ResultValue:
    def __init__(self, value, encounters, training_data_size):
        self.value = value
        self.encounters = encounters
        self.training_data_size = training_data_size

    def get_probability(self):
        return self.encounters / self.training_data_size


class ValueRule:
    def __init__(self, attribute_value, result_value, encounters, result_encounters):
        self.attribute_value = attribute_value
        self.result_value = result_value
        self.encounters = encounters
        self.result_encounters = result_encounters

    def get_probability(self, alpha, uniques):
        return (self.encounters + alpha) / (self.result_encounters + alpha * uniques)

    def __str__(self):
        return f"[attribute_value={self.attribute_value}, result_value={self.result_value}, " \
               f"encounters={self.encounters}, result_encounters={self.result_encounters}, " \
               f"probability={self.get_probability()}]"


class AttributeRules:
    def __init__(self, value_rules):
        self.value_rules = value_rules

    def __str__(self):
        return "\n".join([str(rule) for rule in self.value_rules])

    def get_result_encounters(self, result):
        for value_rule in self.value_rules:
            if value_rule.result_value == result:
                return value_rule.result_encounters

        return 1

    def get_probability(self, value, result, alpha):
        for rule in self.value_rules:
            if rule.attribute_value == value and rule.result_value == result:
                return rule.get_probability(alpha, len(self.value_rules))
        return alpha / (len(self.value_rules) * alpha + self.get_result_encounters(result))


class NaiveBayes:
    def __init__(self, learning_sample, alpha=1):
        self.sample_len = len(learning_sample[0])
        self.sample_size = len(learning_sample)
        self.alpha = alpha

        values = [learning_sample[i][self.sample_len - 1] for i in range(0, self.sample_size)]
        result_values_set = set(values)

        result_values = []
        for result_value in result_values_set:
            result_values.append(ResultValue(result_value, values.count(result_value), self.sample_size))

        self.result_values = result_values

        attribute_rules = []
        # По столбцам
        for i in range(0, self.sample_len - 1):
            value_rules = []
            for result_value in result_values_set:
                # По строкам
                attribute_values = [learning_sample[j][i] for j in range(0, self.sample_size)]
                attribute_values_set = set(attribute_values)

                for attribute_value in attribute_values_set:
                    encounters = 1
                    result_encounters = len(attribute_values_set)
                    for j in range(0, self.sample_size):
                        if learning_sample[j][self.sample_len - 1] != result_value:
                            continue
                        result_encounters += 1

                        if learning_sample[j][i] == attribute_value:
                            encounters += 1
                    value_rules.append(ValueRule(attribute_value, result_value, encounters, result_encounters))
            attribute_rules.append(AttributeRules(value_rules))

        self.attribute_rules = attribute_rules

    def get_prediction(self, values):
        if values is None:
            raise ValueError
        if not isinstance(values, list):
            raise ValueError
        if len(values) != len(self.attribute_rules):
            raise ValueError

        predictions = []
        for result_value in self.result_values:
            probability = result_value.get_probability()
            for i in range(0, len(values)):
                probability *= self.attribute_rules[i].get_probability(values[i], result_value.value, self.alpha)

            predictions.append([result_value.value, probability])

        max_probability = -1
        max_probability_value = None
        summ = 0
        for item in predictions:
            if max_probability < item[1]:
                max_probability = item[1]
                max_probability_value = item[0]
            summ += item[1]

        # Возвращается наиболее вероятное значение и вероятность данного значения
        return max_probability_value, max_probability/summ


def main():
    #Выборка для обучения
    learning_sample = util.get_samples("AppleQualityDataset_Learning.xlsx")
    #Выборка для тестирования
    test_sample = util.get_samples("AppleQualityDataset_Test.xlsx")

    #Для сегрегации происходит округлениее до round_to цифр после запятой
    round_to = 0
    segregated_learning_sample = util.segregate_floats(learning_sample, round_to)
    segregated_test_sample = util.segregate_floats(test_sample, round_to)

    bayes = NaiveBayes(segregated_learning_sample)

    total_count = 0
    success_count = 0
    # Расчет ошибки
    for sample in segregated_test_sample:
        total_count += 1
        expected_result = sample[-1]
        prediction = bayes.get_prediction(sample[:-1])
        if expected_result == prediction[0]:
            success_count += 1

    print(f"Success rate: {int((success_count / total_count) * 100)}%")


if __name__ == '__main__':
    main()


