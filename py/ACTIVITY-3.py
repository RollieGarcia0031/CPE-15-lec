import numpy as np

# Declare the conductance as 3x3 matrix and an injected_current_array with 3 columns
conductance_matrix = np.array([
    [ 0.50, -0.20, -0.10],
    [-0.20,  0.45, -0.15],
    [-0.10, -0.15,  0.35],
])

injected_current = np.array([2.0, 1.2, 0.8])

# calculate determinant, rank, and condition
determinant = np.linalg.det(conductance_matrix)
rank = np.linalg.matrix_rank(conductance_matrix)
condition_num = np.linalg.cond(conductance_matrix)

# find the volate on each nodes
node_volatages = np.linalg.solve(conductance_matrix, injected_current)

# verify values using substituion
residual = conductance_matrix @ node_volatages - injected_current
abs_max_residual = float(np.abs(residual).max())

print("residual: ", residual)

assert np.allclose(residual, 0)

report = {
    "Diagnosis": {
        "Determinant" : float(determinant),
        "Rank" : int(rank),
        "Condition" : float(np.round(condition_num, 2)),
    },
    "Node voltages" : np.round(node_volatages, 2).tolist(),
    "Absolute Maximum Residual": abs_max_residual
}

report