import hashlib

import util


class ValueRule:
    def __init__(self, attribute_value, most_common_result, encounters, total_encounters):
        self.attribute_value = attribute_value
        self.most_common_result = most_common_result
        self.encounters = encounters
        self.total_encounters = total_encounters

    def __str__(self):
        return f"[attribute_value={self.attribute_value}, most_common_result={self.most_common_result}, " \
               f"encounters={self.encounters}, total_encounters={self.total_encounters}]"


class AttributeRules:
    def __init__(self, attribute_rules):
        self.rules = attribute_rules
        encounters = 0
        total_encounters = 0

        for rule in attribute_rules:
            encounters += rule.encounters
            total_encounters += rule.total_encounters

        accuracy = encounters/total_encounters
        self.accuracy = accuracy

    def get_prediction(self, value):
        for rule in self.rules:
            if rule.attribute_value == value:
                return rule.most_common_result

    def __str__(self):
        return f"Attribute {str(hashlib.md5(str(self.rules).encode(encoding='utf-8-sig')).hexdigest())[:3]}" \
               f", accuracy {self.accuracy}"


class OneRule:
    def __init__(self, learning_sample):
        sample_len = len(learning_sample[0])
        sample_size = len(learning_sample)
        attribute_rules = []
        for i in range(0, sample_len-1):
            attribute_values = []
            result_values = []
            for j in range(0, sample_size):
                attribute_values.append(learning_sample[j][i])
                result_values.append(learning_sample[j][sample_len-1])

            attribute_set = set(attribute_values)
            result_set = set(result_values)
            rules = []
            for attribute in attribute_set:
                total_encounters = attribute_values.count(attribute)
                encounters_dict = {}
                for item in result_set:
                    encounters_dict[item] = 0

                for k in range(0, sample_size):
                    if learning_sample[k][i] != attribute:
                        continue
                    encounters_dict[learning_sample[k][sample_len-1]] += 1

                most_common_result = None
                encounters_count = 0
                for item in encounters_dict:
                    if encounters_dict[item] >= encounters_count:
                        encounters_count = encounters_dict[item]
                        most_common_result = item

                rules.append(ValueRule(attribute, most_common_result, encounters_count, total_encounters))
            attribute_rules.append(AttributeRules(rules))

        self.attribute_rules = attribute_rules
        most_accurate_rule = self.attribute_rules[0]
        for attribute_rule in self.attribute_rules:
            if attribute_rule.accuracy > most_accurate_rule.accuracy:
                most_accurate_rule = attribute_rule
        self.most_accurate_rule = most_accurate_rule

    def get_prediction(self, values):
        if values is None:
            raise ValueError
        if not isinstance(values, list):
            raise ValueError
        if len(values) != len(self.attribute_rules):
            raise ValueError

        return self.most_accurate_rule.get_prediction(values[self.attribute_rules.index(self.most_accurate_rule)])


def main():
    learning_sample = util.get_samples("AppleQualityDataset_Learning.xlsx")
    test_sample = util.get_samples("AppleQualityDataset_Test.xlsx")

    round_to = 1
    segregated_learning_sample = util.segregate_floats(learning_sample, round_to)
    segregated_test_sample = util.segregate_floats(test_sample, round_to)

    one_rule = OneRule(segregated_learning_sample)

    """
    
    total_count = 0
    success_count = 0
    # Расчет ошибки
    for sample in segregated_test_sample:
        total_count += 1
        expected_result = sample[-1]
        prediction = one_rule.get_prediction(sample[:-1])
        if expected_result == prediction:
            success_count += 1

    print(f"Success rate: {int((success_count / total_count) * 100)}%")
    """

if __name__ == '__main__':
    main()









