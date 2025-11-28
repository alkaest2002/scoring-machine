import marimo

__generated_with = "0.18.1"
app = marimo.App(width="full", auto_download=["html"])


@app.cell
def _():
    import sys  
    from pathlib import Path

    parent_dir = str(Path().resolve())
    sys.path.insert(0, parent_dir)
    print(parent_dir)
    return (Path,)


@app.cell
def _(Path):
    import json
    import pandas as pd

    from lib.utils import create_normative_table
    from lib.test_specs import TestSpecs

    TEST_PATH = Path("./lib/tests/core")

    data_norms = pd.DataFrame({
        "scale": ["wb","pro","fun","risk", "tot_risk", "tot","wb","pro","fun","risk", "tot_risk", "tot"],
        "norms_id": ["ita_comm_m","ita_comm_m","ita_comm_m","ita_comm_m","ita_comm_m","ita_comm_m","ita_comm_f","ita_comm_f","ita_comm_f","ita_comm_f","ita_comm_f","ita_comm_f"],
        "mean": [.98, .84, 1.04, .16, .95, .81, 1.26, .99, 1.01, .11, 1.03, .87],
        "ds": [.69, .60, .56, .42, .55, .50, .85, .65, .51, .33, .56, .49]
    })

    with open(TEST_PATH / f"{TEST_PATH.name}_specs.json", "r") as fin:
        test_specs = TestSpecs(json.loads(fin.read()))

    norms = create_normative_table(test_specs, data_norms)
    norms.head(6)
    return TEST_PATH, norms


@app.cell
def _(TEST_PATH, norms):
    # available signs ꜜ ꜛ ◦
    c1 = norms["std"].between(0, 30, inclusive="left")
    c2 = norms["std"].between(30, 40, inclusive="left")
    c3 = norms["std"].between(60, 70, inclusive="left")
    c4 = norms["std"].between(70, 500, inclusive="left")

    norms.loc[c1, "std_interpretation"] = "ꜜꜜ"
    norms.loc[c2, "std_interpretation"] = "ꜜ"
    norms.loc[c3, "std_interpretation"] = "ꜛ"
    norms.loc[c4, "std_interpretation"] = "ꜛꜛ"


    norms.to_csv(TEST_PATH / f"{TEST_PATH.name}_norms.csv", index=False)
    norms
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
