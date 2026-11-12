#!/usr/bin/env python3
"""Rebuild six class figures offline from the archived, hashed input snapshots.

Usage: python generar.py --output /absolute/path/to/output
Only Python's standard library is required. No network or shared-repo writes.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path

BASE = Path(__file__).resolve().parent
INPUTS = BASE / "inputs"
BLUE, ORANGE, GRAY = "#2463A6", "#D66B28", "#687787"


def dump(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def rows(name: str, first: int, last: int) -> list[dict]:
    with (INPUTS / name).open(encoding="utf-8", newline="") as stream:
        result = list(csv.DictReader(stream))
    years = [int(row["year"]) for row in result]
    if years != list(range(first, last + 1)):
        raise ValueError(f"Missing, duplicate or unordered years in {name}")
    return result


def numeric(row: dict, key: str) -> float:
    value = float(row[key])
    if not math.isfinite(value):
        raise ValueError(f"Non-finite {key}: {row}")
    return value


def trace(years: list[int], values: list[float], name: str, color: str = BLUE, dash: str = "solid") -> dict:
    if len(years) != len(values) or len(values) < 2 or not all(math.isfinite(v) for v in values):
        raise ValueError("Invalid trace")
    return {"type": "scatter", "mode": "lines", "name": name, "x": years, "y": values,
            "line": {"color": color, "width": 3, "dash": dash}, "connectgaps": False,
            "hovertemplate": "%{x}<br>%{y:.2f}<extra>%{fullData.name}</extra>"}


def layout(title: str, unit: str, note: str, legend: bool = False) -> dict:
    return {"title": {"text": title, "x": 0.02, "xanchor": "left", "font": {"size": 21}},
            "paper_bgcolor": "white", "plot_bgcolor": "white",
            "font": {"family": "Arial, sans-serif", "size": 13, "color": "#243447"},
            "margin": {"l": 85, "r": 35, "t": 85, "b": 105}, "height": 500,
            "xaxis": {"title": {"text": "Año"}, "type": "linear", "tickformat": "d", "showgrid": False},
            "yaxis": {"title": {"text": unit}, "rangemode": "tozero", "gridcolor": "#E5EAF0", "zerolinecolor": "#BBC4CE"},
            "hovermode": "x unified", "showlegend": legend,
            "legend": {"orientation": "h", "x": 0, "y": 1.12},
            "annotations": [{"text": note, "xref": "paper", "yref": "paper", "x": 0, "y": -0.24,
                             "xanchor": "left", "showarrow": False, "align": "left", "font": {"size": 11, "color": GRAY}}]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=BASE, help="Directory for specs, derived CSVs and manifest")
    args = parser.parse_args()
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=True)
    hashes = json.loads((INPUTS / "hashes.json").read_text(encoding="utf-8"))
    for name, expected in hashes.items():
        actual = hashlib.sha256((INPUTS / name).read_bytes()).hexdigest()
        if actual != expected:
            raise ValueError(f"Input hash mismatch: {name}")
    metadata = json.loads((INPUTS / "source_metadata.json").read_text(encoding="utf-8"))
    eia = rows("eia_usa_1970_2019.csv", 1970, 2019)
    pwt = rows("pwt100_usa.csv", 1950, 2019)
    wdi = rows("wdi_usa_1960_2024.csv", 1960, 2024)
    entries = []

    def emit(number: int, title: str, module: str, description: str, formula: str,
             unit: str, source_urls: list[str], source_file: str, vintage: str,
             limitations: list[str], data: list[dict], note: str, table: list[dict]) -> None:
        slug = f"iguzmanvt-{number}"
        years = data[0]["x"]
        spec = {"data": data, "layout": layout(title, unit, note, len(data) > 1), "frames": []}
        dump(out / f"{slug}.json", spec)
        with (out / f"{slug}.csv").open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=list(table[0]), lineterminator="\n")
            writer.writeheader()
            writer.writerows(table)
        entries.append({"identity": f"iguzmanvt:{number}", "slug": slug, "title": title,
                        "module": module, "description": description, "formula": formula,
                        "units": unit, "period": {"start": min(years), "end": max(years), "frequency": "annual"},
                        "country": "USA", "source_urls": source_urls,
                        "source_paths": [f"inputs/{source_file}", "inputs/source_metadata.json"],
                        "source_vintage": vintage, "limitations": limitations,
                        "kind": "reconstructed_from_verified_sources",
                        "inputs_sha256": {f"inputs/{name}": hashes[name] for name in [source_file, "source_metadata.json"]},
                        "spec_path": f"{slug}.json", "derived_csv_path": f"{slug}.csv",
                        "original_chart_recovered": False, "data_points": sum(len(t["x"]) for t in data)})

    years = [int(r["year"]) for r in eia]
    intensity = [numeric(r, "TETGRUS") for r in eia]
    expenditure = [numeric(r, "TEGDSUS") for r in eia]
    if not all(v > 0 for v in intensity) or not all(0 < v < 100 for v in expenditure):
        raise ValueError("Unexpected EIA indicator range")
    eia_urls = [metadata["eia"]["url"], metadata["eia"]["table_pdf_url"],
                "https://www.eia.gov/totalenergy/data/monthly/index.php"]
    eia_vintage = "Monthly Energy Review de octubre de 2026, publicado el 29-10-2026; se selecciona el período 1970–2019."
    eia_limits = ["Reconstrucción temática; no se recuperó el gráfico original de Chart Studio.",
                  "Cobertura: los 50 estados de Estados Unidos y el Distrito de Columbia, verificada en el cuadro 1.7 de EIA.",
                  "Se utilizan datos revisados en octubre de 2026 para 1970–2019; la edición histórica del gráfico original es desconocida."]
    emit(190, "Estados Unidos: intensidad energética", "Energy",
         "Consumo de energía primaria por unidad de PIB real; menor intensidad significa menos energía por dólar de producción.",
         "Serie TETGRUS publicada por EIA: consumo de energía primaria / PIB real en dólares encadenados de 2017, expresado en miles de Btu por dólar.",
         "Miles de Btu por dólar de 2017", eia_urls, "eia_usa_1970_2019.csv", eia_vintage,
         eia_limits + ["La intensidad observada no identifica por separado los efectos causales de la tecnología, la composición sectorial o los precios de la energía."],
         [trace(years, intensity, "Energía primaria / PIB real")],
         "Fuente: EIA, MER octubre 2026. Reconstrucción temática; datos de 1970–2019.",
         [{"year": y, "thousand_btu_per_chained_2017_dollar": v} for y, v in zip(years, intensity)])
    emit(192, "Estados Unidos: gasto energético / PIB", "Energy",
         "Gasto nominal en energía como porcentaje del PIB nominal. Complementa la intensidad física de la gráfica 190.",
         "Serie TEGDSUS publicada por EIA: 100 × gasto nominal en energía / PIB nominal.",
         "Porcentaje del PIB nominal", eia_urls, "eia_usa_1970_2019.csv", eia_vintage,
         eia_limits + ["El gasto incluye impuestos cuando hay datos disponibles. El cociente no estima una elasticidad de producción ni el efecto causal del precio de la energía."],
         [trace(years, expenditure, "Gasto energético / PIB", ORANGE)],
         "Fuente: EIA, MER octubre 2026. Cociente nominal/nominal; reconstrucción temática.",
         [{"year": y, "energy_expenditures_percent_gdp": v} for y, v in zip(years, expenditure)])

    years = [int(r["year"]) for r in pwt]
    labour = [numeric(r, "labsh") for r in pwt]
    emp = [numeric(r, "emp") for r in pwt]
    pop = [numeric(r, "pop") for r in pwt]
    if not all(r["countrycode"] == "USA" for r in pwt) or not all(0 < v < 1 for v in labour):
        raise ValueError("Invalid PWT country or labour shares")
    if not all(0 < e < p for e, p in zip(emp, pop)):
        raise ValueError("Invalid PWT employment/population inputs")
    nonlabour = [100 * (1 - v) for v in labour]
    employment_ratio = [100 * e / p for e, p in zip(emp, pop)]
    pwt_urls = [metadata["pwt"]["official_workbook_url"],
                "https://www.rug.nl/ggdc/docs/pwt100-user-guide-to-data-files.pdf"]
    pwt_vintage = "Penn World Table 10.0, edición corregida de junio de 2021; datos de 1950–2019."
    pwt_limits = ["Reconstrucción con datos verificados; no corresponde a los datos recuperados del gráfico original de Chart Studio.",
                  "PWT 10.0, período histórico 1950–2019; no incluye proyecciones ni observaciones posteriores."]
    emit(198, "Estados Unidos: participación no laboral del PIB", "Slowdown",
         "Complemento contable de la participación de la remuneración laboral en el PIB a precios nacionales corrientes.",
         "100 × (1 − labsh), donde labsh es la participación de la remuneración laboral en el PIB a precios nacionales corrientes.",
         "Porcentaje del PIB", pwt_urls, "pwt100_usa.csv", pwt_vintage,
         pwt_limits + ["Este complemento no es RK/(W+RK), una participación observada del capital en los costos ni una estimación directa de su elasticidad de producción."],
         [trace(years, nonlabour, "100 × (1 − labsh)")],
         "Fuente: PWT 10.0. Complemento de la remuneración laboral en el PIB; no cociente de costos.",
         [{"year": y, "labsh": l, "nonlabour_share_pct_gdp": v} for y, l, v in zip(years, labour, nonlabour)])
    emit(213, "Estados Unidos: ocupados / población total", "Slowdown",
         "Personas ocupadas en relación con toda la población; PWT mide ambas variables en millones de personas.",
         "100 × emp / pop; emp es el número de personas ocupadas y pop la población total. Ambas variables están en millones, por lo que las unidades se cancelan.",
         "Ocupados por cada 100 habitantes", pwt_urls, "pwt100_usa.csv", pwt_vintage,
         pwt_limits + ["El denominador incluye todas las edades. No es la tasa habitual de empleo sobre población en edad de trabajar, la participación laboral ni la proporción de personas de 20–64 años.",
                       "La variación observada no identifica por sí sola un efecto causal de la demografía sobre el crecimiento económico."],
         [trace(years, employment_ratio, "Personas ocupadas / población")],
         "Fuente: PWT 10.0, 1950–2019. Población total como denominador; sin proyecciones.",
         [{"year": y, "emp_millions": e, "pop_millions": p, "employed_per_100_population": v}
          for y, e, p, v in zip(years, emp, pop, employment_ratio)])

    years = [int(r["year"]) for r in wdi]
    births = [numeric(r, "SP.DYN.CBRT.IN") for r in wdi]
    if not all(0 < v < 100 for v in births):
        raise ValueError("Invalid crude birth rate")
    wdi_url = metadata["wdi"]["download"]["url"]
    wdi_vintage = "Banco Mundial, WDI: actualización de la API y consulta del 11-11-2026. La respuesta identifica fuentes de Naciones Unidas y nacionales, pero no precisa la edición de origen de cada observación."
    wdi_limits = ["Reconstrucción de una serie histórica; no se recuperó el gráfico original de Chart Studio.",
                  "Se utiliza la consulta WDI del 11-11-2026; las estimaciones históricas pueden diferir de las disponibles cuando se preparó la clase.",
                  "No incluye proyecciones: todos los años representados pertenecen al período 1960–2024."]
    emit(211, "Estados Unidos: tasa bruta de natalidad", "Slowdown",
         "Nacimientos vivos ocurridos en el año por cada 1.000 habitantes estimados a mitad de año.",
         "Indicador WDI SP.DYN.CBRT.IN: 1.000 × nacimientos vivos del año / población total estimada a mitad de año.",
         "Nacimientos por cada 1.000 habitantes", [wdi_url, "https://data.worldbank.org/indicator/SP.DYN.CBRT.IN?locations=US"],
         "wdi_usa_1960_2024.csv", wdi_vintage,
         wdi_limits + ["La tasa bruta de natalidad no es la tasa global de fecundidad ni el número de hijos por mujer.",
                       "La tendencia descriptiva no demuestra que los cambios en las preferencias familiares la causaran ni cuantifica un efecto causal sobre el crecimiento."],
         [trace(years, births, "Tasa bruta de natalidad")],
         "Fuente: Banco Mundial, WDI. Serie descriptiva; no identifica causas ni efectos sobre el crecimiento.",
         [{"year": y, "live_births_per_1000_population": v} for y, v in zip(years, births)])

    dependency_table = []
    for r in wdi:
        y = int(r["year"])
        total = numeric(r, "SP.POP.TOTL")
        male, female = numeric(r, "SP.POP.TOTL.MA.IN"), numeric(r, "SP.POP.TOTL.FE.IN")
        if abs(male + female - total) > 2:
            raise ValueError(f"Sex totals do not reconcile with total population in {y}")
        teens = male * numeric(r, "SP.POP.1519.MA.5Y") / 100 + female * numeric(r, "SP.POP.1519.FE.5Y") / 100
        young = numeric(r, "SP.POP.0014.TO") + teens
        old = numeric(r, "SP.POP.65UP.TO")
        adults = total - young - old
        if min(young, old, adults) <= 0 or abs(young + adults + old - total) > 0.001:
            raise ValueError(f"Invalid non-overlapping age groups in {y}")
        dependency_table.append({"year": y, "population_total": total, "population_0_19": young,
                                 "population_20_64": adults, "population_65plus": old,
                                 "young_per_100_adults": 100 * young / adults,
                                 "old_per_100_adults": 100 * old / adults,
                                 "total_per_100_adults": 100 * (young + old) / adults})
    data = [trace(years, [r["young_per_100_adults"] for r in dependency_table], "0–19 años / 20–64 años"),
            trace(years, [r["old_per_100_adults"] for r in dependency_table], "65+ años / 20–64 años", ORANGE),
            trace(years, [r["total_per_100_adults"] for r in dependency_table], "Dependencia total", GRAY, "dot")]
    emit(216, "Estados Unidos: dependencia demográfica", "Slowdown",
         "Población de 0–19 y 65 años o más por cada 100 personas de 20–64 años. Los grupos cubren todas las edades y no se solapan.",
         "N15_19 = población masculina × porcentaje masculino de 15–19 / 100 + población femenina × porcentaje femenino de 15–19 / 100; N0_19 = N0_14 + N15_19; N20_64 = población total − N0_19 − N65más. Dependencia joven = 100 × N0_19 / N20_64; dependencia mayor = 100 × N65más / N20_64; dependencia total = suma de ambas.",
         "Personas por cada 100 adultos de 20–64", [wdi_url, "https://data.worldbank.org/indicator/SP.POP.65UP.TO?locations=US",
         "https://databank.worldbank.org/metadataglossary/world-development-indicators/series/SP.POP.1519.MA.5Y"],
         "wdi_usa_1960_2024.csv", wdi_vintage,
         wdi_limits + ["Cambio explícito de convención: 0–19 sustituye al intervalo 0–20 de la clase original para no contar la edad de 20 años en dos grupos.",
                       "Son cocientes de dependencia por edad; no cuentan personas económicamente dependientes ni personas ocupadas.",
                       "La serie histórica no verifica la proyección de clase según la cual la dependencia de mayores se acercaría al 40% en 2030.",
                       "La población de 15–19 años se deriva ponderando los porcentajes específicos de cada sexo por su población correspondiente; las estimaciones pueden tener valores fraccionarios."],
         data, "Grupos sin solapamiento: 0–19, 20–64 y 65+.<br>Se corrige la convención 0–20 de clase. WDI, 1960–2024; sin proyecciones.", dependency_table)
    entries.sort(key=lambda x: int(x["identity"].split(":")[1]))
    dump(out / "manifest.json", {"schema_version": 1, "generator": "generar.py", "offline": True,
                                 "baseline_commit": metadata["source_repo_head"], "entries": entries})
    print(f"Generated {len(entries)} figures and derived CSVs in {out}")


if __name__ == "__main__":
    main()
