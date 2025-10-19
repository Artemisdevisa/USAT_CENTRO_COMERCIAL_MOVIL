# models/localizacion.py
import json
from conexionBD import Conexion

class Localizacion:
    def listar_departamentos(self):
        con = cur = None
        try:
            con = Conexion().open
            cur = con.cursor()
            cur.execute("SELECT fn_departamento_listar_departamentos() AS data;")
            fila = cur.fetchone()
            data = fila.get("data") if isinstance(fila, dict) else (fila[0] if fila else None)
            if isinstance(data, str):
                data = json.loads(data or "[]")
            return True, data or [], "OK"
        except Exception as e:
            return False, None, f"Error al listar departamentos: {e}"
        finally:
            try:
                if cur: cur.close()
                if con: con.close()
            except:
                pass
            
    def listar_provincias_por_departamento(self, id_dep: int):
        con = cur = None
        try:
            con = Conexion().open
            cur = con.cursor()
            cur.execute(
                "SELECT fn_provincia_listar_provincia_por_departamento(%s) AS data;",
                (id_dep,)
            )
            fila = cur.fetchone()
            data = fila.get("data") if isinstance(fila, dict) else (fila[0] if fila else None)
            if isinstance(data, str):
                data = json.loads(data or "[]")
            return True, data or [], "OK"
        except Exception as e:
            return False, None, f"Error al listar provincias: {e}"
        finally:
            try:
                if cur: cur.close()
                if con: con.close()
            except:
                pass

    def listar_distritos_por_provincia(self, id_prov: int):
        con = cur = None
        try:
            con = Conexion().open
            cur = con.cursor()
            cur.execute(
                "SELECT fn_distrito_listar_distritos_por_provincia(%s) AS data;",
                (id_prov,)
            )
            fila = cur.fetchone()
            data = fila.get("data") if isinstance(fila, dict) else (fila[0] if fila else None)
            if isinstance(data, str):
                data = json.loads(data or "[]")
            return True, data or [], "OK"
        except Exception as e:
            return False, None, f"Error al listar distritos: {e}"
        finally:
            try:
                if cur: cur.close()
                if con: con.close()
            except:
                pass
