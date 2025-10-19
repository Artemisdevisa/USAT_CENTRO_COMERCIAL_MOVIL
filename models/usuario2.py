# models/usuario2.py
import json
from conexionBD import Conexion

class Usuario2:
    def registrar_cliente(
        self,
        nombres: str,
        apellidos: str,
        tipo_doc: int,
        documento: str,
        fecha_nacimiento: str,  # 'YYYY-MM-DD'
        telefono: str,
        id_dist: int,
        direccion: str,
        nomusuario: str,
        email: str,
        password: str,
        img_logo: str | None = None
    ):
        con = cur = None
        try:
            con = Conexion().open
            cur = con.cursor()
            cur.execute(
                """
                SELECT fn_usuario_registrar_cliente(
                    %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                ) AS data;
                """,
                (
                    nombres, apellidos, tipo_doc, documento, fecha_nacimiento,
                    telefono, id_dist, direccion, nomusuario, email, password, img_logo
                )
            )
            row = cur.fetchone()
            # Confirmar la transacción porque la función hace INSERTs
            con.commit()

            data = row["data"] if isinstance(row, dict) else (row[0] if row else None)
            # Si viene como texto, parsear a objeto
            if isinstance(data, str):
                data = json.loads(data)

            # Esperamos un JSON de la forma {status, message, data:{...}}
            if isinstance(data, dict) and data.get("status") is True:
                return True, data, 200
            else:
                # Si la función devolvió error, propagamos su mensaje
                msg = (data or {}).get("message", "Error desconocido")
                return False, {"status": False, "data": None, "message": msg}, 400

        except Exception as e:
            # Rollback ante cualquier error
            try:
                if con:
                    con.rollback()
            except:
                pass
            return False, {"status": False, "data": None, "message": str(e)}, 500
        finally:
            try:
                if cur: cur.close()
                if con: con.close()
            except:
                pass
