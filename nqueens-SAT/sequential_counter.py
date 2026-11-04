from pysat.solvers import Solver


def var(i, j, n):
    return (i - 1) * n + j


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


def solve(n):
    clauses = []
    next_var = n * n + 1

    # Moi hang co dung 1 quan hau
    for i in range(1, n + 1):
        x = []
        for j in range(1, n + 1):
            x.append(var(i, j, n))

        new_clauses, next_var = exactly_one(x, next_var)
        clauses += new_clauses

    # Moi cot co dung 1 quan hau
    for j in range(1, n + 1):
        x = []
        for i in range(1, n + 1):
            x.append(var(i, j, n))

        new_clauses, next_var = exactly_one(x, next_var)
        clauses += new_clauses

    # Duong cheo chinh: i - j = k
    for k in range(-(n - 1), n):
        x = []
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if i - j == k:
                    x.append(var(i, j, n))

        if len(x) >= 2:
            clauses += AMO_sequential_counter(x, next_var)
            next_var += len(x) - 1

    # Duong cheo phu: i + j = k
    for k in range(2, 2 * n + 1):
        x = []
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if i + j == k:
                    x.append(var(i, j, n))

        if len(x) >= 2:
            clauses += AMO_sequential_counter(x, next_var)
            next_var += len(x) - 1

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


def solve_n_queens(n):
    clauses = solve(n)
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