def AMO_block(x, start_var):
    clauses = []
    n = len(x)

    if n <= 1:
        return clauses, x[:], start_var

    R = [x[0]]

    for i in range(1, n):
        R.append(start_var)
        start_var += 1

        clauses.append([-x[i], R[i]])
        clauses.append([-R[i - 1], R[i]])
        clauses.append([x[i], R[i - 1], -R[i]])
        clauses.append([-x[i], -R[i - 1]])

    return clauses, R, start_var


def AMZ_block(x, start_var, last_var=None):
    clauses = []
    n = len(x)

    if n <= 1:
        return clauses, x[:], start_var

    R = [x[0]]

    for i in range(1, n):
        if i == n - 1 and last_var is not None:
            R.append(last_var)
        else:
            R.append(start_var)
            start_var += 1

        clauses.append([-x[i], R[i]])
        clauses.append([-R[i - 1], R[i]])
        clauses.append([x[i], R[i - 1], -R[i]])

    return clauses, R, start_var


def SCL_encoding(x, w, start_var):
    clauses = []
    next_var = start_var
    n = len(x)

    if w == 1:
        return clauses, [], [], next_var

    groups = []

    for i in range(0, n, w):
        groups.append(x[i:i + w])

    m = len(groups)

    prefix_R = [None] * m
    suffix_R = [None] * m

    for i in range(m):

        # Nhom dau -> AMO nguoc
        if i == 0 and m > 1:
            new_clauses, R, next_var = AMO_block(groups[i][::-1], next_var)

            clauses += new_clauses
            suffix_R[i] = R

        # Nhom cuoi -> AMO xuoi
        elif i == m - 1:
            new_clauses, R, next_var = AMO_block(groups[i], next_var)

            clauses += new_clauses
            prefix_R[i] = R

        # Cac nhom giua -> AMO xuoi + AMZ nguoc
        else:
            # AMO xuoi
            new_clauses, R, next_var = AMO_block(groups[i], next_var)

            clauses += new_clauses
            prefix_R[i] = R

            shared_var = R[-1]

            # AMZ nguoc -> dung chung bien phu cuoi
            new_clauses, R, next_var = AMZ_block(groups[i][::-1], next_var, last_var=shared_var)

            clauses += new_clauses
            suffix_R[i] = R

    # Tao connection clauses
    for i in range(m - 1):
        left = suffix_R[i]
        right = prefix_R[i + 1]

        for k in range(1, min(w, len(right) + 1)):
            clauses.append([-left[w - k - 1], -right[k - 1]])

    return clauses, prefix_R, suffix_R, next_var


x = [1, 2, 3, 4, 5, 6, 7, 8, 9]

clauses, prefix_R, suffix_R, next_var = SCL_encoding(x, 3, 10)

print("Clauses:", clauses)
print("Prefix R:", prefix_R)
print("Suffix R:", suffix_R)
print("Next var:", next_var)
print("So clauses:", len(clauses))
print("So bien phu:", next_var - 10)