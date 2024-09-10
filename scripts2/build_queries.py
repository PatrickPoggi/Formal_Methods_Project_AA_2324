'''
This script is meant to buld several queries to be used to verify the following
properties:
    - P1: It is possible for a percentage N% of all civilians to reach a safe state
within time Tscs.
    - P2: A percentage N% of all civilians is always guaranteed to reach a safe
state within time Tscs.

The structures are the following:
    - P1: E<>(global <= Tscs and (rescued_civilians * 100 / CIVILIAN_NUMBER >= N))
    - P2: A<>(global <= Tscs and (rescued_civilians * 100 / CIVILIAN_NUMBER >= N))
'''

queries_file_path = "../../queries.q"
Tscs, N = 0,0
q1_template = "E<>(global <= {Tscs} and (rescued_civilians * 100 / CIVILIAN_NUMBER >= {N}))"
q2_template = "A<>(global <= {Tscs} and (rescued_civilians * 100 / CIVILIAN_NUMBER >= {N}))"

N_values = [45, 50, 55, 60, 65, 70]
Tscs_values = [70, 80, 90, 100]

def build_queries():
    with open(queries_file_path, "w") as f:
        for N in N_values:
            for Tscs in Tscs_values:
                q1 = q1_template.format(Tscs=Tscs, N=N)
                q2 = q2_template.format(Tscs=Tscs, N=N)
                f.write(q1 + "\n")
                f.write(q2 + "\n")

build_queries()