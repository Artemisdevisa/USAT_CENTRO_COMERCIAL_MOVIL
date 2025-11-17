// static/js/mapa_sucursal.js

class MapaSucursal {
    constructor() {
        this.map = null;
        this.marker = null;
        this.latitud = null;
        this.longitud = null;
        this.centroPeruDefecto = [-9.19, -75.0152]; // Centro de Perú
    }

    inicializar(contenedorId = 'mapa') {
        // Inicializar mapa centrado en Perú
        this.map = L.map(contenedorId).setView(this.centroPeruDefecto, 6);

        // Capa de OpenStreetMap
        L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }).addTo(this.map);

        // Evento de clic en el mapa
        this.map.on('click', (e) => this.seleccionarUbicacion(e));

        // Forzar recarga del mapa
        setTimeout(() => this.map.invalidateSize(), 100);
    }

    seleccionarUbicacion(evento) {
        const { lat, lng } = evento.latlng;
        
        this.latitud = lat;
        this.longitud = lng;

        // Eliminar marcador anterior
        if (this.marker) {
            this.map.removeLayer(this.marker);
        }

        // Agregar nuevo marcador
        this.marker = L.marker([lat, lng], {
            draggable: true
        }).addTo(this.map);

        // Actualizar inputs ocultos
        document.getElementById('latitud').value = lat.toFixed(8);
        document.getElementById('longitud').value = lng.toFixed(8);

        // Obtener ubicación inversa (Nominatim)
        this.obtenerDireccionReversa(lat, lng);

        // Evento cuando se arrastra el marcador
        this.marker.on('dragend', (e) => {
            const pos = e.target.getLatLng();
            this.latitud = pos.lat;
            this.longitud = pos.lng;
            document.getElementById('latitud').value = pos.lat.toFixed(8);
            document.getElementById('longitud').value = pos.lng.toFixed(8);
            this.obtenerDireccionReversa(pos.lat, pos.lng);
        });
    }

    async obtenerDireccionReversa(lat, lng) {
        try {
            const response = await fetch(
                `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}&zoom=18&addressdetails=1`
            );
            const data = await response.json();

            if (data && data.address) {
                const { state, province, city, county, suburb, road } = data.address;
                
                // Construir dirección sugerida
                let direccionSugerida = '';
                if (road) direccionSugerida += road;
                if (suburb) direccionSugerida += (direccionSugerida ? ', ' : '') + suburb;
                
                if (direccionSugerida) {
                    document.getElementById('direccion').value = direccionSugerida;
                }

                // Intentar seleccionar ubicación en los selectores
                this.autoSeleccionarUbicacion(state, province, city || county);
            }
        } catch (error) {
            console.error('Error al obtener dirección:', error);
        }
    }

    async autoSeleccionarUbicacion(departamento, provincia, distrito) {
        // Implementar lógica de autoselección si es necesario
        console.log('Ubicación detectada:', { departamento, provincia, distrito });
    }

    centrarEnCoordenadas(lat, lng) {
        if (!this.map) return;
        
        this.latitud = lat;
        this.longitud = lng;

        this.map.setView([lat, lng], 15);

        if (this.marker) {
            this.map.removeLayer(this.marker);
        }

        this.marker = L.marker([lat, lng], {
            draggable: true
        }).addTo(this.map);

        document.getElementById('latitud').value = lat.toFixed(8);
        document.getElementById('longitud').value = lng.toFixed(8);

        this.marker.on('dragend', (e) => {
            const pos = e.target.getLatLng();
            this.latitud = pos.lat;
            this.longitud = pos.lng;
            document.getElementById('latitud').value = pos.lat.toFixed(8);
            document.getElementById('longitud').value = pos.lng.toFixed(8);
            this.obtenerDireccionReversa(pos.lat, pos.lng);
        });
    }

    limpiar() {
        if (this.marker) {
            this.map.removeLayer(this.marker);
            this.marker = null;
        }
        this.latitud = null;
        this.longitud = null;
        document.getElementById('latitud').value = '';
        document.getElementById('longitud').value = '';
        this.map.setView(this.centroPeruDefecto, 6);
    }

    obtenerCoordenadas() {
        return {
            latitud: this.latitud,
            longitud: this.longitud
        };
    }
}

// Instancia global
const mapaSucursal = new MapaSucursal();