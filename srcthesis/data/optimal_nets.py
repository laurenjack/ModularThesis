optimal_dict = {'sig-or-sm' : ([784, 30, 30, 10], ['sig', 'or', 'sm'], [0.3, (0.3, 0.01), 0.3]),
                'sig-and-sm': ([784, 30, 30, 10], ['sig', 'and', 'sm'], [0.03, (0.1, 0.01), 0.03]),
                'sig-sig-or-sm': ([784, 30, 30, 30, 10], ['sig', 'sig', 'or', 'sm'], [0.03, 0.03, (0.03, 0.01), 0.03]),
                'sig-sig-and-sm': ([784, 30, 30, 30, 10], ['sig', 'sig', 'and', 'sm'], [0.1, 0.1, (0.1, 0.001), 0.1]),
                'sig-or-and-sm': ([784, 30, 30, 30, 10], ['sig', 'or', 'and', 'sm'], [0.1, (0.1, 0.01), (0.1, 0.001), 0.1]),
                'sig-and-or-sm': ([784, 30, 30, 30, 10], ['sig', 'and', 'or', 'sm'], [0.3, (0.3, 0.001), (0.3, 0.001), 0.3]),
                'sig-sig-sig-sm': ([784, 30, 30, 30, 10], ['sig', 'sig', 'sig', 'sm'], [0.1] * 4),
                'sig-sig-sm': ([784, 30, 30, 10], ['sig', 'sig', 'sm'], [0.03] * 3),
                'sig-sm': ([784, 30, 10], ['sig', 'sm'], [0.1] * 2)}

def get_optimal(act_strings):
    return optimal_dict[act_strings]