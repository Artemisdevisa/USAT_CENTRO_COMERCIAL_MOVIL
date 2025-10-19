import json
from conexionBD import Conexion

class TipoDocumento:
    def listar_tipo_documento(self):
        con = cur = None
        try:
            con = Conexion().open
            cur = con.cursor()
            cur.execute("SELECT fn_tipo_documento_listar() AS data;")
            fila = cur.fetchone()
            data = fila.get("data") if isinstance(fila, dict) else (fila[0] if fila else None)
            if isinstance(data, str):
                data = json.loads(data or "[]")
            return True, data or [], "OK"
        except Exception as e:
            return False, None, f"Error al listar los tipos de documentos: {e}"
        finally:
            try:
                if cur: cur.close()
                if con: con.close()
            except:
                pass