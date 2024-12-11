import os
import pandas as pd
from pydantic import BaseModel, computed_field

from database import DatabaseHandler


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


def generate_solution(req: Request, request_id: int):
    packages = pd.DataFrame(req.packages)
    ulds = pd.DataFrame(req.ulds)

    pck_path = f"./data/{request_id}/packages.csv"
    uld_path = f"./data/{request_id}/ulds.csv"
    pack_path = f"./data/{request_id}/solution.csv"

    # Create a new directory and sstore the dataframes
    os.makedirs(f"./data/{request_id}")
    packages.to_csv(pck_path, index=False)
    ulds.to_csv(uld_path, index=False)

    # Execute the script to generate the solution
    os.system(f"python ./scripts/generate.py {pck_path} {uld_path} {pack_path}")

    res = pd.read_csv(pack_path).to_dict(orient="records")
    with DatabaseHandler() as db:
        db.update_request_result(request_id, res)

    return res
