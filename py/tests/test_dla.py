import os
import numpy as np
from time import sleep
from dla import run_dla, C, find_D, p5

def test_seeded_determinism():
    np.random.seed(42)
    c1, _ = run_dla(300, 1, 0, p5)

    np.random.seed(42)
    c2, _ = run_dla(300, 1, 0, p5)
    assert c1 == c2

def test_particle_count():
    np.random.seed(1)
    cluster, order = run_dla(300, 1, 0, p5)

    assert len(cluster) >= 300
    assert (0,0) in cluster

def test_no_floaters():
    np.random.seed(67)
    cluster, _ = run_dla(300, 1, 0, p5)

    neighbours = [(1,0),(-1,0),(0,1),(0,-1),(1,1),(-1,1),(1,-1),(-1,-1)]

    for (x, y) in cluster:
        if (x, y) == (0, 0):
            continue
        
        assert any((x+dx, y+dy) in cluster for (dx, dy) in neighbours), \
            f"{(x,y)} is floating."
        
def verify_fractal():
    np.random.seed(670)

    cluster = run_dla(5000, 1, 0, p5)
    D_list = []

    for _ in range(3):
        r, C_r = C(cluster)
        D_list.append(find_D(r, C_r))
    
    assert 1.5 < np.mean(D_list) < 1.9

def matches_golden():
    path = os.path.join(os.path.dirname(__file__), "..", "control.npy")
    if not os.path.exist(path):
        return
    control = np.load(path)
    np.random.seed(153)
    cluster, _ = run_dla(1000, 1, 0, p5)
    current = np.array(sorted(cluster))

    assert np.array_equal(current, control)