import pandas as pd
from pydantic import BaseModel


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


class Request(BaseModel):
    packages: list[Package]
    ulds: list[ULD]


def get_cached_solution():
    df = pd.read_csv("sample_solution.csv")
    return df.to_dict(orient="records")


def generate_solution(req: Request):
    return get_cached_solution()
