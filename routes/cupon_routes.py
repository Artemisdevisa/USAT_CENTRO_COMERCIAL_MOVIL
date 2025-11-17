from flask import Blueprint, jsonify
from models.cupon import Cupon

ws_cupon = Blueprint('ws_cupon', __name__)

@ws_cupon.route('/cupones/listar-por-sucursal/<int:id_sucursal>', methods=['GET'])
def listar_por_sucursal(id_sucursal):
    """Listar cupones activos de una sucursal"""
    try:
        print(f"📥 Listando cupones para sucursal: {id_sucursal}")
        cupones = Cupon.listar_por_sucursal(id_sucursal)
        
        print(f"✅ Cupones encontrados: {len(cupones) if cupones else 0}")
        
        return jsonify({
            'status': True,
            'data': cupones
        }), 200
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': False,
            'data': [],
            'message': f'Error: {str(e)}'
        }), 500