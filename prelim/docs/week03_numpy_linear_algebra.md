# Week 3: NumPy Matrix Operations and Linear Algebra

**CPE15 - Programming for Data Science**

---

## Concepts Covered

| # | Concept | Module |
|---|---------|--------|
| 1 | Array creation and shapes | numpy |
| 2 | Elementwise vs matrix multiplication | numpy |
| 3 | Transpose | numpy.linalg |
| 4 | Determinant | numpy.linalg |
| 5 | Rank | numpy.linalg |
| 6 | Condition number | numpy.linalg |
| 7 | Inverse and identity check | numpy.linalg |
| 8 | Solving linear systems | numpy.linalg |
| 9 | Residual verification | numpy |
| 10 | Eigenvalues and eigenvectors | numpy.linalg |
| 11 | Explained variance share | numpy |
| 12 | Vectorization vs loops | numpy |

---

## 1. Array Creation and Shapes

```python
import numpy as np

A = np.array([[1.0, 2.0], [3.0, 4.0]])
B = np.array([[2.0, 0.0], [1.0, 2.0]])

print("Shape of A:", A.shape)  # (2, 2)
print("Shape of B:", B.shape)  # (2, 2)
```

**Common constructors:**

| Function | Purpose |
|----------|---------|
| `np.array([[...], ...])` | from a nested list |
| `np.eye(n)` | n x n identity matrix |
| `np.diag([d1, d2])` | diagonal matrix from a list |
| `np.zeros((m, n))` | all zeros |
| `np.ones((m, n))` | all ones |

---

## 2. Elementwise vs Matrix Multiplication

These are fundamentally different operations.

```python
A = np.array([[1.0, 2.0], [3.0, 4.0]])
B = np.array([[2.0, 0.0], [1.0, 2.0]])

# Elementwise -- same-position multiplication
print("A * B:", A * B, sep="\n")
# [[2. 0.]
#  [3. 8.]]

# Matrix product -- row-by-column dot products
print("A @ B:", A @ B, sep="\n")
# [[ 4.  4.]
#  [10.  8.]]
```

### Shape rule

For `A @ B`: if `A` is `(m, n)` and `B` is `(n, p)`, result is `(m, p)`. Inner dimensions must match.

```python
# (2, 3) @ (3, 1) = (2, 1)
design = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
weights = np.array([[0.5], [1.0], [-0.5]])
scores = design @ weights

print("Shapes:", design.shape, "@", weights.shape, "=", scores.shape)
print("Scores:", scores.ravel())
# [1. 3.5]
```

### Dot product of a row and column

```python
print("Dot product:", A[0] @ B[:, 0])  # 4.0
```

---

## 3. Transpose

The transpose swaps rows and columns. It changes shape but not values.

```python
matrix = np.array([[1, 2, 3], [4, 5, 6]])
print("original shape:", matrix.shape)     # (2, 3)
print("transpose shape:", matrix.T.shape)  # (3, 2)
print(matrix.T)
# [[1 4]
#  [2 5]
#  [3 6]]
```

**Syntax:** `matrix.T` or `np.transpose(matrix)`

---

## 4. Determinant

The determinant indicates singularity. Zero = no unique inverse.

```python
nonsingular = np.array([[2.0, 0.0], [0.0, 3.0]])
singular = np.array([[1.0, 2.0], [2.0, 4.0]])

print("det nonsingular:", np.linalg.det(nonsingular))  # 6.0
print("det singular:", np.linalg.det(singular))         # 0.0
```

**Syntax:** `np.linalg.det(matrix)`

A nonzero determinant alone does not guarantee a trustworthy numerical result -- check the condition number too.

---

## 5. Rank

Rank counts linearly independent rows or columns.

```python
full_rank = np.array([[1.0, 0.0], [0.0, 1.0]])
low_rank = np.array([[1.0, 2.0], [2.0, 4.0]])

print("full rank:", np.linalg.matrix_rank(full_rank))    # 2
print("low rank:", np.linalg.matrix_rank(low_rank))      # 1
```

**Syntax:** `np.linalg.matrix_rank(matrix)`

Rank < n for an n x n matrix means the rows/columns are linearly dependent.

---

## 6. Condition Number

Estimates worst-case amplification of input error. Larger = more sensitive.

```python
stable = np.eye(2)
sensitive = np.array([[1.0, 1.0], [1.0, 1.000001]])

print("identity condition:", np.linalg.cond(stable))             # 1.0
print("sensitive condition:", f"{np.linalg.cond(sensitive):.2e}")  # 4.00e+05
```

**Syntax:** `np.linalg.cond(matrix)`

| Condition number | Interpretation |
|------------------|----------------|
| ~1 | perfectly conditioned (identity) |
| 10-100 | moderately sensitive |
| >1000 | potentially unreliable solve |

---

## 7. Inverse and Identity Verification

```python
M = np.array([[4.0, 1.0], [2.0, 3.0]])
M_inv = np.linalg.inv(M)
identity_check = M @ M_inv

print("Inverse:", np.round(M_inv, 3), sep="\n")
print("M @ inv(M):", np.round(identity_check, 10), sep="\n")
assert np.allclose(identity_check, np.eye(2))
```

**Syntax:**
- `np.linalg.inv(A)` -- compute inverse
- `np.allclose(A, B)` -- compare within floating tolerance
- `np.eye(n)` -- identity matrix

**Prefer `solve` over `inv`** when the goal is solving `Ax = b`. Direct solving is faster and more numerically stable.

---

## 8. Solving Linear Systems

`np.linalg.solve(A, b)` finds `x` in `Ax = b` without explicitly computing `A^-1`.

### Nodal-voltage example

```python
conductance = np.array([
    [0.30, -0.10],
    [-0.10, 0.25],
])
current = np.array([1.2, 0.5])

voltage = np.linalg.solve(conductance, current)
print("Node voltages (V):", np.round(voltage, 4))
# Node voltages (V): [5.3846 4.1538]
```

### Handling singular systems

```python
singular = np.array([[1.0, 2.0], [2.0, 4.0]])
try:
    np.linalg.solve(singular, np.array([3.0, 6.0]))
except np.linalg.LinAlgError as e:
    print(f"Cannot solve: {e}")
```

---

## 9. Residual Verification

Always substitute the solution back and check the residual `Ax - b`.

```python
residual = conductance @ voltage - current
print("Residual:", residual)
print("Max absolute residual:", np.abs(residual).max())
print("Close to zero:", np.allclose(residual, 0))
assert np.allclose(residual, 0)
```

| Residual | Meaning |
|----------|---------|
| ~0 (floating point) | numerical solution satisfies the equations |
| large | something is wrong (singular, ill-conditioned, or wrong) |

A near-zero residual confirms the equations were solved, but does not validate the model or coefficients.

---

## 10. Eigenvalues and Eigenvectors

For a square matrix `A`, an eigenvector `v` and eigenvalue `lambda` satisfy:

```
A @ v = lambda * v
```

### Computing eigenpairs

```python
covariance = np.array([[4.0, 1.8], [1.8, 1.5]])

eigenvalues, eigenvectors = np.linalg.eigh(covariance)

# Sort descending
order = np.argsort(eigenvalues)[::-1]
eigenvalues = eigenvalues[order]
eigenvectors = eigenvectors[:, order]

print("Eigenvalues:", np.round(eigenvalues, 4))
print("Eigenvectors (by column):\n", np.round(eigenvectors, 4))
print("Explained share:", np.round(eigenvalues / eigenvalues.sum(), 4))
```

### Verifying an eigenpair

```python
v = eigenvectors[:, 0]
lam = eigenvalues[0]

left = covariance @ v
right = lam * v

print("A @ v:", np.round(left, 6))
print("lambda * v:", np.round(right, 6))
assert np.allclose(left, right)
```

### Functions

| Function | Use case |
|----------|----------|
| `np.linalg.eig(A)` | general square matrices |
| `np.linalg.eigh(A)` | real symmetric / Hermitian (returns real eigenvalues) |
| `np.linalg.eigvalsh(A)` | eigenvalues only for symmetric matrices |

**Note:** Eigenvector signs are not unique (`v` and `-v` represent the same direction).

---

## 11. Explained Variance Share

For a covariance matrix, dividing eigenvalues by their sum gives the variance fraction per direction.

```python
cov = np.array([[4.0, 0.0], [0.0, 1.0]])
vals = np.linalg.eigvalsh(cov)[::-1]
share = vals / vals.sum()

print("eigenvalues:", vals)          # [4. 1.]
print("variance shares:", share)     # [0.8 0.2]
```

This is the foundation of PCA (principal component analysis).

---

## 12. Vectorization vs Loops

Vectorized operations run in optimized C under the hood and are much faster than Python loops.

```python
import time

np.random.seed(15)
n = 200_000
a = np.random.rand(n)
b = np.random.rand(n)

# Loop
def looped_sum():
    total = np.empty(n)
    for i in range(n):
        total[i] = a[i] + b[i]
    return total

# Vectorized
def vectorized_sum():
    return a + b

# Confirm same result
assert np.allclose(looped_sum(), vectorized_sum())

# Benchmark
loop_times = []
vec_times = []
for _ in range(5):
    t0 = time.perf_counter(); looped_sum(); loop_times.append(time.perf_counter() - t0)
    t0 = time.perf_counter(); vectorized_sum(); vec_times.append(time.perf_counter() - t0)

loop_median = sorted(loop_times)[len(loop_times) // 2]
vec_median = sorted(vec_times)[len(vec_times) // 2]
print(f"Loop:   {loop_median:.5f} s")
print(f"Vector: {vec_median:.5f} s")
print(f"Speedup: {loop_median / vec_median:.1f}x")
```

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Using `*` instead of `@` for matrix multiply | `@` composes row-to-column relationships |
| Wrong multiplication order | `A @ B != B @ A` in general |
| Computing `inv(A) @ b` to solve | Use `np.linalg.solve(A, b)` instead |
| No residual check after solve | Always compute `A @ x - b` |
| Trusting condition number without context | Report it with units and required precision |

---

## Key Takeaways

1. **`@` for matrix multiply, `*` for elementwise** -- different operations, different shape rules
2. **Check shapes first** -- inner dimensions must match for `@`
3. **`solve(A, b)` over `inv(A) @ b`** -- faster and more stable
4. **Always verify the residual** -- `A @ x - b` should be near zero
5. **Condition number > determinant** -- tells you if the solve is trustworthy
6. **Eigenpairs satisfy `Av = lambda * v`** -- verify with `np.allclose`
7. **Vectorize over loops** -- orders of magnitude faster for large arrays
