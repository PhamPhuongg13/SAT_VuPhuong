from pysat.solvers import Solver


def var(i, j, n):
    return (i - 1) * n + j

def AMO_pairwise(x):
    clauses = []

    for i in range(len(x)):
        for j in range(i + 1, len(x)):
            clauses.append([-x[i], -x[j]])

    return clauses

def AMO_commander(x, start_var, group_size):
    clauses = []
    n = len(x)
    tmp = start_var

    if n <= group_size:
        clauses = AMO_pairwise(x)
        return clauses, tmp

    groups = []
    for i in range(0, n, group_size):
        groups.append(x[i : i + group_size])

    commanders = []
    for group in groups:
        c = tmp
        tmp += 1

        commanders.append(c)

        clauses += AMO_pairwise(group)
        for xi in group:
            clauses.append([-xi, c])

    if len(commanders) >= 2:
        new_clauses, tmp = AMO_commander(commanders, tmp, group_size)
        clauses += new_clauses
    
    return clauses, tmp


def exactly_one(x, next_var, group_size):
    clauses = [x[:]]  # ALO

    # AMO
    if len(x) >= 2:
        new_clauses, next_var = AMO_commander(x, next_var, group_size)
        clauses += new_clauses

    return clauses, next_var


def solve(n, group_size):
    clauses = []
    next_var = n * n + 1

    # Moi hang co dung 1 quan hau
    for i in range(1, n + 1):
        x = []
        for j in range(1, n + 1):
            x.append(var(i, j, n))

        new_clauses, next_var = exactly_one(x, next_var, group_size)
        clauses += new_clauses
        

    # Moi cot co dung 1 quan hau
    for j in range(1, n + 1):
        x = []
        for i in range(1, n + 1):
            x.append(var(i, j, n))

        new_clauses, next_var = exactly_one(x, next_var, group_size)
        clauses += new_clauses

    # Duong cheo chinh: i - j = k
    for k in range(-(n - 1), n):
        x = []
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if i - j == k:
                    x.append(var(i, j, n))

        if len(x) >= 2:
            new_clauses, next_var = AMO_commander(x, next_var, group_size)
            clauses += new_clauses

    # Duong cheo phu: i + j = k
    for k in range(2, 2 * n + 1):
        x = []
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if i + j == k:
                    x.append(var(i, j, n))

        if len(x) >= 2:
            new_clauses, next_var = AMO_commander(x, next_var, group_size)
            clauses += new_clauses

    return clauses


def print_board(model, n):
    true_vars = set()
    for literal in model:
        if literal > 0:
            true_vars.add(literal)

    for i in range(1, n + 1):
        row = []
        for j in range(1, n + 1):
            variable = var(i, j, n)
            if variable in true_vars:
                row.append("Q")
            else:
                row.append(".")
        print(" ".join(row))


def solve_n_queens(n, group_size = 3):
    clauses = solve(n, group_size)
    count = 0

    with Solver(name="glucose3", bootstrap_with=clauses) as solver:
        while solver.solve():
            model = solver.get_model()
            count += 1

            print(f"Nghiem {count}:")
            print_board(model, n)
            print()

            queen_vars = [
                var(i, j, n)
                for i in range(1, n + 1)
                for j in range(1, n + 1)
                if var(i, j, n) in model
            ]

            solver.add_clause([-x for x in queen_vars])

    print(f"Tong so nghiem: {count}")


if __name__ == "__main__":
    n = 8
    solve_n_queens(n)