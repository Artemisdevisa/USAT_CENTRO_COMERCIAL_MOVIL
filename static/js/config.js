// static/js/config.js
console.log('🔧 Iniciando carga de CONFIG...');

const detectarApiUrl = () => {
    const hostname = window.location.hostname;
    
    if (hostname === 'localhost' || hostname === '127.0.0.1') {
        return 'http://127.0.0.1:3007';
    }
    
    if (hostname.startsWith('192.168.') || hostname.startsWith('10.')) {
        return `http://${hostname}:3007`;
    }
    
    return 'https://api.tudominio.com';
};

window.CONFIG = {
    API_URL: detectarApiUrl()
};

console.log('✅ CONFIG cargado:', window.CONFIG.API_URL);