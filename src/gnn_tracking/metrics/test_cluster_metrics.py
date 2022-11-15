from __future__ import annotations

import dataclasses

import numpy as np
import pytest
from pytest import approx

from gnn_tracking.metrics.cluster_metrics import custom_metrics


@dataclasses.dataclass
class ClusterMetricTestCase:
    def __init__(
        self,
        *,
        truth: list[float],
        predicted: list[float],
        pts: None | list[float] = None,
        reconstructable: None | list[bool] = None,
        pt_thld=-1.0,
        **kwargs,
    ):
        self.truth = np.array(truth)
        self.predicted = np.array(predicted)
        self.expected = kwargs
        if pts is None:
            self.pts = np.zeros_like(self.predicted)
        else:
            self.pts = np.array(pts)
        if reconstructable is None:
            self.reconstructable = np.full_like(self.predicted, True)
        else:
            self.reconstructable = np.array(reconstructable)
        self.pt_thld = pt_thld

    def run(self):
        metrics = custom_metrics(
            truth=self.truth,
            predicted=self.predicted,
            pts=self.pts,
            pt_thlds=[self.pt_thld],
            reconstructable=self.reconstructable,
        )
        assert metrics[self.pt_thld] == approx(self.expected, nan_ok=True)


test_cases = [
    ClusterMetricTestCase(
        truth=[],
        predicted=[],
        n_particles=0,
        n_clusters=0,
        perfect=float("nan"),
        lhc=float("nan"),
        double_majority=float("nan"),
    ),
    # Nan because of having only noise from DBSCAN
    ClusterMetricTestCase(
        truth=[1, 2],
        predicted=[-1, -1],
        n_particles=2,
        n_clusters=0,
        perfect=0,
        lhc=float("nan"),
        double_majority=0,
    ),
    ClusterMetricTestCase(
        truth=[0],
        predicted=[0],
        pt_thld=1.0,
        n_particles=0,
        n_clusters=0,
        perfect=float("nan"),
        lhc=float("nan"),
        double_majority=float("nan"),
    ),
    ClusterMetricTestCase(
        truth=[0],
        predicted=[1],
        n_particles=1,
        n_clusters=1,
        perfect=1.0,
        lhc=1.0,
        double_majority=1.0,
    ),
    ClusterMetricTestCase(
        truth=[0, 0, 0, 0],
        predicted=[1, -1, -1, -1],
        n_particles=1,
        n_clusters=1,
        perfect=0.0,
        lhc=1.0,
        double_majority=0.0,
    ),
    ClusterMetricTestCase(
        truth=[0],
        predicted=[0],
        n_particles=1,
        n_clusters=1,
        perfect=1.0,
        lhc=1.0,
        double_majority=1.0,
    ),
    ClusterMetricTestCase(
        truth=[0, 1],
        predicted=[1, 0],
        n_particles=2,
        n_clusters=2,
        perfect=1.0,
        lhc=1.0,
        double_majority=1.0,
    ),
    ClusterMetricTestCase(
        truth=[0, 0],
        predicted=[1, 0],
        n_particles=1,
        n_clusters=2,
        perfect=0.0,
        lhc=2.0 / 2.0,
        double_majority=0.0,
    ),
    ClusterMetricTestCase(
        truth=[1, 0],
        predicted=[0, 0],
        n_particles=2,
        n_clusters=1,
        perfect=0.0,
        lhc=0.0,
        double_majority=0.0,
    ),
    ClusterMetricTestCase(
        truth=[0, 0, 0, 0, 1],
        predicted=[0, 0, 0, 0, 0],
        n_particles=2,
        n_clusters=1,
        perfect=0,
        lhc=1 / 1,
        double_majority=1 / 2,
    ),
    ClusterMetricTestCase(
        truth=[0, 0, 0, 0, 0],
        predicted=[0, 0, 0, 0, 1],
        n_particles=1,
        n_clusters=2,
        perfect=0,
        lhc=2 / 2,
        double_majority=1 / 1,
    ),
    ClusterMetricTestCase(
        # fmt: off
        truth=[
            0, 0, 0, 0, 0, 0,  # lhc, dm
            1, 1, 1, 1, 1, 5,  # lhc, dm
            0, 1, 1, 2,  # x
            0, 1, 2, 3,  # x
            4, 4,  # perfect, lhc, dm
            5  # lhc
        ],
        predicted=[
            0, 0, 0, 0, 0, 0,
            1, 1, 1, 1, 1, 1,
            2, 2, 2, 2,
            3, 3, 3, 3,
            4, 4,
            5,
        ],
        # fmt: on
        n_particles=6,
        n_clusters=6,
        perfect=1 / 6,
        lhc=4 / 6,
        double_majority=3 / 6,
    ),
    # same thing as the last, except with pt thresholds masking some particles
    ClusterMetricTestCase(
        # fmt: off
        truth=[
            0, 0, 0, 0, 0, 0,  # lhc, dm  (masked)
            1, 1, 1, 1, 1, 5,  # lhc, dm
            0, 1, 1, 2,  # x
            0, 1, 2, 3,  # x
            4, 4,  # perfect, lhc, dm  (masked)
            5  # lhc
        ],
        # We mask PIDS 0 and 4.
        pts=[
            0, 0, 0, 0, 0, 0,
            1, 1, 1, 1, 1, 1,
            0, 1, 1, 1,
            0, 1, 1, 1,
            0, 0,
            1,
        ],
        predicted=[
            0, 0, 0, 0, 0, 0,  # (masked)
            1, 1, 1, 1, 1, 1,
            2, 2, 2, 2,
            3, 3, 3, 3,
            4, 4,  # (masked)
            5,
        ],
        # fmt: on
        pt_thld=0.5,
        n_particles=4,
        n_clusters=4,
        perfect=0 / 4,
        lhc=2 / 4,
        double_majority=1 / 4,
    ),
    # same thing as the last, except with pt thresholds and reconstructability
    # masking some particles
    ClusterMetricTestCase(
        # fmt: off
        truth=[
            0, 0, 0, 0, 0, 0,  # lhc, dm  (pt-masked)
            1, 1, 1, 1, 1, 5,  # lhc, dm (reco-masked)
            0, 1, 1, 2,  # x
            0, 1, 2, 3,  # x
            4, 4,  # perfect, lhc, dm  (pt-masked)
            5  # lhc
        ],
        # We mask PIDS 0 and 4.
        pts=[
            0, 0, 0, 0, 0, 0,
            1, 1, 1, 1, 1, 1,
            0, 1, 1, 1,
            0, 1, 1, 1,
            0, 0,
            1,
        ],
        # Everything reconstructable except PID 1
        reconstructable=[
            True, True, True, True, True, True,
            False, False, False, False, False, True,
            True, False, False, True,
            True, False, True, True,
            True, True,
            True,
        ],
        predicted=[
            0, 0, 0, 0, 0, 0,  # (pt-masked)
            1, 1, 1, 1, 1, 1,
            2, 2, 2, 2,
            3, 3, 3, 3,
            4, 4,  # (pt-masked)
            5,
        ],
        # fmt: on
        pt_thld=0.5,
        n_particles=4,
        n_clusters=4,
        perfect=0 / 3,
        lhc=1 / 4,
        double_majority=0 / 3,
    ),
]


@pytest.mark.parametrize("test_case", test_cases)
def test_custom_metrics(test_case):
    test_case.run()
