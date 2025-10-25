import importlib.util
import sys, types, io, traceback, re
import pytest

NOTEBOOK_PATH = "notebooks/Taller_1.ipynb"
MODULE_NAME = "notebook_module"

import nbformat
from nbconvert import PythonExporter

def load_notebook_as_module(nb_path):
    exporter = PythonExporter()
    source, _ = exporter.from_filename(nb_path)
    spec = importlib.util.spec_from_loader(MODULE_NAME, loader=None)
    module = importlib.util.module_from_spec(spec)
    exec(source, module.__dict__)
    sys.modules[MODULE_NAME] = module
    return module

@pytest.fixture(scope="session")
def nb_module():
    try:
        return load_notebook_as_module(NOTEBOOK_PATH)
    except Exception as e:
        pytest.fail(f"No se pudo cargar el notebook: {e}\n{traceback.format_exc()}")

class Score:
    total = 0
    achieved = 0
    @classmethod
    def add(cls, points, ok):
        cls.total += points
        if ok: cls.achieved += points
    @classmethod
    def percent(cls):
        return round(100*cls.achieved/cls.total,2) if cls.total else 0

def test_estructura_basica(nb_module):
    puntos = 25
    try:
        assert hasattr(nb_module, "Dispositivo")
        assert hasattr(nb_module, "Habito")
        assert hasattr(nb_module, "Medicion")
        assert hasattr(nb_module, "Hipotesis")
        assert hasattr(nb_module, "Accion")
        assert hasattr(nb_module, "SistemaEnergia")
        assert hasattr(nb_module, "declarar_base")
        ok = True
    except AssertionError:
        ok = False
    Score.add(puntos, ok)
    print(f"Etapa 1 (Estructura): {'OK' if ok else 'FALLA'} -> {puntos if ok else 0}/{puntos}")

def test_reglas_salience(nb_module):
    puntos = 20
    ok = False
    try:
        import inspect
        # Recuperar el texto de la clase completa, o de las reglas declaradas
        src = inspect.getsource(nb_module.SistemaEnergia)
        ok = "@Rule" in src and "salience=" in src
    except Exception:
        try:
            # Fallback: buscar atributos de tipo Rule en la clase
            rules = [a for a in dir(nb_module.SistemaEnergia) if not a.startswith("__")]
            ok = len(rules) >= 4  # debe tener al menos 4 reglas
        except Exception:
            ok = False
    Score.add(puntos, ok)
    print(f"Etapa 2 (Reglas/Salience): {'OK' if ok else 'FALLA'} -> {puntos if ok else 0}/{puntos}")

def test_ejecucion(nb_module):
    puntos = 20
    ok = False
    try:
        e = nb_module.SistemaEnergia()
        e.reset()
        nb_module.declarar_base(e)
        e.run()
        ok = True
    except Exception as ex:
        print("Error de ejecución:", ex)
        ok = False
    Score.add(puntos, ok)
    print(f"Etapa 3 (Ejecución): {'OK' if ok else 'FALLA'} -> {puntos if ok else 0}/{puntos}")

def test_inferencia(nb_module):
    puntos = 25
    ok = False
    try:
        res = nb_module.RESULTADOS
        assert "A" in res and "B" in res and "C" in res
        motivos = [h.get("motivo","") for h in res["A"]["hipotesis"]]                 + [h.get("motivo","") for h in res["B"]["hipotesis"]]                 + [h.get("motivo","") for h in res["C"]["hipotesis"]]
        motivos_lw = [str(m).lower().strip() for m in motivos]
        ok = any("clima" in m for m in motivos_lw)              and any("iluminacion" in m for m in motivos_lw)              and any("normalizado" in m for m in motivos_lw)
    except Exception as ex:
        print("Error de inferencia:", ex)
        ok = False
    Score.add(puntos, ok)
    print(f"Etapa 4 (Inferencia): {'OK' if ok else 'FALLA'} -> {puntos if ok else 0}/{puntos}")

def test_trazabilidad(nb_module, capsys):
    puntos = 10
    ok = False
    try:
        e = nb_module.SistemaEnergia()
        e.reset()
        nb_module.declarar_base(e)
        e.declare(nb_module.Medicion(dispositivo='aire_acondicionado', kwh_periodo=9.8, periodo='dia'))
        e.run()
        salida = capsys.readouterr().out
        ok = "ACTIVADA" in salida or "activada" in salida.lower()
    except Exception as ex:
        print("Error trazabilidad:", ex)
        ok = False
    Score.add(puntos, ok)
    print(f"Etapa 5 (Trazabilidad): {'OK' if ok else 'FALLA'} -> {puntos if ok else 0}/{puntos}")

def test_reporte_final():
    print("\n=== RESUMEN FINAL ===")
    print(f"Puntaje total: {Score.achieved}/{Score.total} -> {Score.percent()}%")
    assert Score.percent() >= 60, "Calificación insuficiente (<60%)"
