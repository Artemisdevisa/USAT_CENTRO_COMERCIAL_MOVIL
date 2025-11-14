// static/js/utils.js
// ✅ SOLUCIÓN: Construcción dinámica de URLs

function construirUrlImagen(urlRelativa) {
    if (!urlRelativa) return 'https://via.placeholder.com/300x400?text=Sin+Imagen';
    
    // Si ya es URL completa, devolverla tal cual
    if (urlRelativa.startsWith('http://') || urlRelativa.startsWith('https://')) {
        return urlRelativa;
    }
    
    // Construir URL completa con API_URL
    const baseUrl = window.CONFIG?.API_URL || 'http://127.0.0.1:3007';
    
    // Asegurar que la ruta empiece con /
    const ruta = urlRelativa.startsWith('/') ? urlRelativa : '/' + urlRelativa;
    
    return baseUrl + ruta;
}

// Exportar para uso global
window.construirUrlImagen = construirUrlImagen;