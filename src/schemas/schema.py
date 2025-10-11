import pandera as pa
from pandera import Column, Check

schema_funcionarios = pa.DataFrameSchema(
    {
        "id": Column(int, Check.gt(0), nullable=False),
        "nome": Column(str, nullable=False, checks=[
            Check.str_matches(r"^[A-Za-zÀ-ÿ\s]+$", error="Nome não pode conter números ou caracteres inválidos")
            ]),
        "area": Column(str, Check.str_length(min_value=1), nullable=False),
        "salario": Column(float, Check.gt(0), nullable=False),
        "bonus_percentual": Column(float, Check.in_range(0, 1), nullable=False)
    },
    strict = True,
    coerce = True
)