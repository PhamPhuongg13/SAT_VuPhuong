
from pysat.solvers import Solver


def AMO_sequential_counter(x, start_var):
    clauses = []
    n = len(x)

    if n <= 1:
        return clauses

    s = list(range(start_var, start_var + n - 1))

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

def build_L(var_info, nodes):
    L = {node: [] for node in nodes}

    for var, (node, pe, cycle, iteration) in var_info.items():
        L[node].append(var)

    return L


# C1: Exactly-One Constraint
def encode_C1(L, next_var):
    clauses = []

    for variables in L.values():
        new_clauses, next_var = exactly_one(
            variables, next_var
        )
        clauses += new_clauses

    return clauses, next_var


# C2: Resource Constraint
def encode_C2(L, var_info, II, nodes):
    clauses = []

    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            u = nodes[i]
            v = nodes[j]

            for var1 in L[u]:
                _, pe1, t1, _ = var_info[var1]

                for var2 in L[v]:
                    _, pe2, t2, _ = var_info[var2]

                    if pe1 == pe2 and t1 % II == t2 % II:
                        clauses.append([-var1, -var2])

    return clauses



# Dependency Constraint
# t(v) + d * II >= t(u) + latency(u)
def encode_dependency(L, var_info, edges, latency, II):
    clauses = []

    for u, v, d in edges:
        for var1 in L[u]:
            _, _, t1, _ = var_info[var1]

            for var2 in L[v]:
                _, _, t2, _ = var_info[var2]

                if t2 + d * II < t1 + latency[u]:
                    clauses.append([-var1, -var2])

    return clauses


def solve_mapping(clauses, var_info):
    with Solver(name="glucose3", bootstrap_with=clauses) as solver:
        if not solver.solve():
            print("\nUNSAT - Khong ton tai mapping hop le!")
            return None

        print("\nSAT - Tim thay mapping hop le!")

        model = solver.get_model()

        selected_vars = [
            v for v in model
            if v > 0 and v in var_info
        ]

        mapping = {}

        for v in sorted(selected_vars):
            node, pe, cycle, iteration = var_info[v]
            mapping[node] = (pe, cycle, iteration)

        return mapping


if __name__ == "__main__":
    II = 3

    # DFG
    nodes = ["a", "b", "c"]

    # ID -> (node, PE, cycle, iteration)
    var_info = {
        1: ("a", 0, 1, 0),
        2: ("a", 1, 1, 0),
        3: ("a", 0, 2, 0),
        4: ("b", 0, 4, 0),
        5: ("b", 1, 2, 0),
        6: ("c", 0, 7, 0),
    }

    # sinh L(các ứng viên của từng node)
    L = build_L(var_info, nodes)

    # (node nguồn, node đích, iteration distance)
    edges = [
        ("a", "b", 0),
        ("b", "c", 1)
    ]

    latency = {
        "a": 1,
        "b": 2,
        "c": 1
    }

    next_var = max(var_info, default=0) + 1

    # C1: Exactly-One
    clauses_C1, next_var = encode_C1(L, next_var)

    # C2: Resource
    clauses_C2 = encode_C2(L, var_info, II, nodes)

    # Dependency
    clauses_dep = encode_dependency(
        L, var_info, edges, latency, II
    )

    # Ghép CNF
    clauses = clauses_C1 + clauses_C2 + clauses_dep

    print("L:", L)
    print("C1 clauses:", len(clauses_C1))
    print("C2 clauses:", len(clauses_C2))
    print("Dependency clauses:", len(clauses_dep))
    print("Total clauses:", len(clauses))
    print("Next variable:", next_var)

    # Chạy SAT Solver
    mapping = solve_mapping(clauses, var_info)

    if mapping is not None:
        print("\nMapping result:")

        for node, (pe, cycle, iteration) in mapping.items():
            print(
                f"Node {node} -> "
                f"PE {pe}, "
                f"Cycle {cycle}, "
                f"Iteration {iteration}, "
                f"Modulo slot {cycle % II}"
            )
