import time
import random
import pandas as pd
from pydantic import BaseModel, computed_field
from core.genetic import GeneticSolver
from core.manager import PackageManager


class Package(BaseModel):
    id: str
    length: float
    width: float
    height: float
    weight: float
    cost: float
    priority: bool


class ULD(BaseModel):
    id: str
    length: float
    width: float
    height: float
    weight: float

    @computed_field
    def capacity(self) -> float:
        return self.weight


class Request(BaseModel):
    packages: list[Package]
    ulds: list[ULD]
    mock: bool = True


def get_cached_solution():
    df = pd.read_csv("sample_solution.csv")
    return df.to_dict(orient="records")


def generate_solution(req: Request):
    if req.mock:
        time.sleep(random.uniform(0.2, 1.5))
        return get_cached_solution()

    solver = GeneticSolver(req.packages, req.ulds)
    base_solution = solver.run()

    mng = PackageManager(
        len(req.packages),
        len(req.ulds),
        base_solution.uld_order,
        base_solution.pack_order,
        base_solution.alloted,
    )

    return mng.get_results()
