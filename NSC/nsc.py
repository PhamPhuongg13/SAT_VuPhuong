def NSC_ALK(x, k, start_var):
    clauses = []
    n = len(x)

    if k <= 0:
        return [], start_var
    if k > n:
        return [[]], start_var
    if k == 1:
        return [x[:]], start_var
    if k == n:
        return [[xi] for xi in x], start_var

    R = {}
    next_var = start_var

    for i in range(1, n):
        for j in range(1, min(i, k) + 1):
            R[i, j] = next_var
            next_var += 1

    # Formula (1)
    for i in range(1, n):
        clauses.append([-x[i - 1], R[i, 1]])

    # Formula (2)
    for i in range(2, n):
        for j in range(1, min(i - 1, k) + 1):
            clauses.append([-R[i - 1, j], R[i, j]])

    # Formula (3)
    for i in range(1, n - 1):
        for j in range(2, min(i + 1, k) + 1):
            clauses.append([-x[i], -R[i, j - 1], R[i + 1, j]])

    # Formula (4)
    for i in range(1, n - 1):
        for j in range(1, min(i, k) + 1):
            clauses.append([x[i], R[i, j], -R[i + 1, j]])

    # Formula (5)
    for i in range(k):
        clauses.append([x[i], -R[i + 1, i + 1]])

    # Formula (6)
    for i in range(2, n):
        for j in range(2, min(i, k) + 1):
            clauses.append([R[i - 1, j - 1], -R[i, j]])

    # Formula (7)
    clauses.append([R[n - 1, k], x[n - 1]])
    clauses.append([R[n - 1, k], R[n - 1, k - 1]])

    return clauses, next_var


def NSC_AMK(x, k, start_var):
    clauses = []
    n = len(x)

    if k < 0:
        return [[]], start_var
    if k == 0:
        return [[-xi] for xi in x], start_var
    if k >= n:
        return [], start_var

    R = {}
    next_var = start_var

    for i in range(1, n):
        for j in range(1, min(i, k) + 1):
            R[i, j] = next_var
            next_var += 1

    # Formula (1)
    for i in range(1, n):
        clauses.append([-x[i - 1], R[i, 1]])

    # Formula (2)
    for i in range(2, n):
        for j in range(1, min(i - 1, k) + 1):
            clauses.append([-R[i - 1, j], R[i, j]])

    # Formula (3)
    for i in range(1, n - 1):
        for j in range(2, min(i + 1, k) + 1):
            clauses.append([-x[i], -R[i, j - 1], R[i + 1, j]])

    # Formula (8)
    for i in range(k, n):
        clauses.append([-x[i], -R[i, k]])

    return clauses, next_var


def NSC_EK(x, k, start_var):
    clauses = []
    n = len(x)

    if k < 0 or k > n:
        return [[]], start_var
    if k == 0:
        return [[-xi] for xi in x], start_var
    if k == n:
        return [[xi] for xi in x], start_var
    if k == 1:
        clauses.append(x[:])
        for i in range(n):
            for j in range(i + 1, n):
                clauses.append([-x[i], -x[j]])
        return clauses, start_var

    R = {}
    next_var = start_var

    for i in range(1, n):
        for j in range(1, min(i, k) + 1):
            R[i, j] = next_var
            next_var += 1

    # Formula (1)
    for i in range(1, n):
        clauses.append([-x[i - 1], R[i, 1]])

    # Formula (2)
    for i in range(2, n):
        for j in range(1, min(i - 1, k) + 1):
            clauses.append([-R[i - 1, j], R[i, j]])

    # Formula (3)
    for i in range(1, n - 1):
        for j in range(2, min(i + 1, k) + 1):
            clauses.append([-x[i], -R[i, j - 1], R[i + 1, j]])

    # Formula (4)
    for i in range(1, n - 1):
        for j in range(1, min(i, k) + 1):
            clauses.append([x[i], R[i, j], -R[i + 1, j]])

    # Formula (5)
    for i in range(k):
        clauses.append([x[i], -R[i + 1, i + 1]])

    # Formula (6)
    for i in range(2, n):
        for j in range(2, min(i, k) + 1):
            clauses.append([R[i - 1, j - 1], -R[i, j]])

    # Formula (7)
    clauses.append([R[n - 1, k], x[n - 1]])
    clauses.append([R[n - 1, k], R[n - 1, k - 1]])

    # Formula (8)
    for i in range(k, n):
        clauses.append([-x[i], -R[i, k]])

    return clauses, next_var


def NSC_Range(x, u, v, start_var):
    clauses = []
    n = len(x)

    if u > v or u > n or v < 0:
        return [[]], start_var

    u = max(u, 0)
    v = min(v, n)

    if u == 0:
        return NSC_AMK(x, v, start_var)

    if v == n:
        return NSC_ALK(x, u, start_var)

    if u == 1 and v == 1:
        return NSC_EK(x, 1, start_var)

    R = {}
    next_var = start_var

    for i in range(1, n):
        for j in range(1, min(i, v) + 1):
            R[i, j] = next_var
            next_var += 1

    # Formula (1)
    for i in range(1, n):
        clauses.append([-x[i - 1], R[i, 1]])

    # Formula (2) - use v
    for i in range(2, n):
        for j in range(1, min(i - 1, v) + 1):
            clauses.append([-R[i - 1, j], R[i, j]])

    # Formula (3) - use v
    for i in range(1, n - 1):
        for j in range(2, min(i + 1, v) + 1):
            clauses.append([-x[i], -R[i, j - 1], R[i + 1, j]])

    # Formula (4) - use u
    for i in range(1, n - 1):
        for j in range(1, min(i, u) + 1):
            clauses.append([x[i], R[i, j], -R[i + 1, j]])

    # Formula (5) - use u
    for i in range(u):
        clauses.append([x[i], -R[i + 1, i + 1]])

    # Formula (6) - use u
    for i in range(2, n):
        for j in range(2, min(i, u) + 1):
            clauses.append([R[i - 1, j - 1], -R[i, j]])

    # Formula (7) - ALK(u)
    if u == 1:
        clauses.append([R[n - 1, 1], x[n - 1]])
    else:
        clauses.append([R[n - 1, u], x[n - 1]])
        clauses.append([R[n - 1, u], R[n - 1, u - 1]])

    # Formula (8) - AMK(v)
    for i in range(v, n):
        clauses.append([-x[i], -R[i, v]])

    return clauses, next_var

x = [1, 2, 3, 4, 5]
start_var = 6

alk, _ = NSC_ALK(x, 3, start_var)
amk, _ = NSC_AMK(x, 3, start_var)
ek, _ = NSC_EK(x, 3, start_var)
rng, _ = NSC_Range(x, 2, 4, start_var)

print("ALK:", len(alk), "clauses")
print("AMK:", len(amk), "clauses")
print("EK:", len(ek), "clauses")
print("Range:", len(rng), "clauses")

