a = [1, 2, 3, 4, 5]
b = [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]

for i, indices in enumerate(zip(a, b)):
    (idx, (left, right)) = indices
    print(i, idx, left, right)
