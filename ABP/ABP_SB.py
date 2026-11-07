from pysat.solvers import Solver

def var(i, l, n):
    """
    x_i^l = True nếu đỉnh i nhận nhãn l.
    i: 1 -> n
    l: 1 -> n
    """
    return (i - 1) * n + l

def AMO_sequential_counter(x, start_var):
    clauses = []
    n = len(x)

    if n <= 1:
        return clauses

    s = []
    for i in range(start_var, start_var + n - 1):
        s.append(i)

    clauses.append([-x[0], s[0]])

    for i in range(1, n - 1):
        clauses.append([-x[i], s[i]])
        clauses.append([-s[i - 1], s[i]])
        clauses.append([-s[i - 1], -x[i]])

    clauses.append([-s[-1], -x[-1]])

    return clauses


def exactly_one(x, next_var):
    clauses = [x[:]]

    if len(x) >= 2:
        clauses += AMO_sequential_counter(x, next_var)
        next_var += len(x) - 1

    return clauses, next_var

def encode_LABELS(n, next_var):
    clauses = []

    for i in range(1, n + 1):
        x = [var(i, l, n) for l in range(1, n + 1)]
        new_clauses, next_var = exactly_one(x, next_var)
        clauses += new_clauses

    return clauses, next_var

def encode_VERTICES(n, next_var):
    clauses = []

    for l in range(1, n + 1):
        x = [var(i, l, n) for i in range(1, n + 1)]
        new_clauses, next_var = exactly_one(x, next_var)
        clauses += new_clauses

    return clauses, next_var

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

# SCAMO
def build_SCL(x, w, next_var):
    clauses = []
    R = {}

    groups = []
    for i in range(0, len(x), w):
        groups.append(x[i:i + w])
    m = len(groups)

    for i in range(m):
        block = groups[i]
        start = i * w + 1
        end = start + len(block) - 1

        # AMO xuoi
        new_clauses, prefix, next_var = AMZ_block(block, next_var)

        clauses += new_clauses
        for j in range(len(prefix)):
            R[start, start + j] = prefix[j]

        shared_var = prefix[-1]

        # AMZ nguoc -> dung chung bien phu cuoi
        new_clauses, suffix, next_var = AMZ_block(block[::-1], next_var, last_var=shared_var)

        clauses += new_clauses
        for j in range(len(suffix)):
            R[end - j, end] = suffix[j]

    return clauses, R, next_var

def encode_OBJ_k(n, edges, k, next_var):
    clauses = []

    R = {}
    w = k + 1

    for u in range(1, n + 1):
        x = [var(u, l, n) for l in range(1, n + 1)]

        new_clauses, new_R, next_var = build_SCL(x, w, next_var)

        clauses += new_clauses
        R[u] = new_R

    for u, v in edges:
        R_u, R_v = R[u], R[v]

        for l in range(1, n - k + 1):
            block_id = (l - 1) // w
            block_end = min((block_id + 1) * w, n)

            if l + k <= block_end: # Cửa sổ nằm trong block
                window_u = [R_u[l, l + k]]
                window_v = [R_v[l, l + k]]
            else: # Cửa sổ là 2 block giao nhau
                window_u = [R_u[l, block_end], R_u[block_end + 1, l + k]]                
                window_v = [R_v[l, block_end], R_v[block_end + 1, l + k]]

            for a in window_u:
                for b in window_v:
                    clauses.append([-a, -b])

    return clauses, next_var

def symmetry_breaking(n, edges):
    clauses = []
    deg = [0] * (n + 1)

    for u, v in edges:
        deg[u] += 1
        deg[v] += 1

    maxi = 0
    pos = 0

    for i, x in enumerate(deg):
        if x > maxi:
            maxi = x
            pos = i

    lim = (n + 1) // 2

    for l in range(lim + 1, n + 1):
        clauses.append([-var(pos, l, n)])

    return clauses




# =====================================================
#                       SOLVE(K)
# =====================================================

def solve_k(n, edges, k):
    clauses = []

    next_var = n * n + 1

    # LABELS ^ VERTICES ^ OBJ-k
    new_clauses, next_var = encode_LABELS(n, next_var)
    clauses += new_clauses

    new_clauses, next_var = encode_VERTICES(n, next_var)
    clauses += new_clauses

    new_clauses, next_var = encode_OBJ_k(n, edges, k, next_var)
    clauses += new_clauses

    # Symmetry Breaking
    clauses += symmetry_breaking(n, edges)

    with Solver(name="glucose3") as solver:
        solver.append_formula(clauses)

        if solver.solve():
            model = solver.get_model()

            positive = set(x for x in model if x > 0)
            labels = {}

            for i in range(1, n + 1):
                for l in range(1, n + 1):
                    if var(i, l, n) in positive:
                        labels[i] = l
                        break
            return True, labels
        return False, None


# =====================================================
#                   Linear Search
# =====================================================

def linear_search(n, edges):
    best = 0
    best_model = None

    for k in range(0, n):
        oki, new_model = solve_k(n, edges, k)

        if oki:
            best = k + 1
            best_model = new_model
        else:
            break

    return best, best_model


# =====================================================
#                         Main
# =====================================================

if __name__ == "__main__":

    n = 5

    edges = [
        (1, 2),
        (2, 3),
        (3, 4),
        (4, 5),
    ]

    best, labels = linear_search(n, edges)

    print("Anti-bandwidth =", best)
    print("labels =", labels)
    
    if labels is not None:
        for u, l in labels.items():
            print(f"Đỉnh {u} nhận nhãn {l}")
