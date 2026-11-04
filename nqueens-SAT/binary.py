import math
from pysat.solvers import Solver


def var(i, j, n):
    return (i - 1) * n + j


def AMO_binary(x, start_var):
    clauses = []
    n = len(x)

    if n <= 1:
        return clauses, start_var

    k = math.ceil(math.log2(n))
    
    bits = []
    for i in range(start_var, start_var + k):
        bits.append(i)

    for i in range(n):
        binary = format(i, f"0{k}b")

        for j in range(k):
            if binary[j] == '1':
                clauses.append([-x[i], bits[j]])
            else:
                clauses.append([-x[i], -bits[j]])
        
    return clauses, start_var + k

def exactly_one(x, next_var):
    clauses = [x[:]]

    if len(x) >= 2:
        new_clauses, next_var = AMO_binary(x, next_var)
        clauses += new_clauses

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
            new_clauses, next_var = AMO_binary(x, next_var)
            clauses += new_clauses

    # Duong cheo phu: i + j = k
    for k in range(2, 2 * n + 1):
        x = []
        for i in range(1, n + 1):
            for j in range(1, n + 1):
                if i + j == k:
                    x.append(var(i, j, n))

        if len(x) >= 2:
            new_clauses, next_var = AMO_binary(x, next_var)
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