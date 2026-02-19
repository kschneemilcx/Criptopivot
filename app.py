"""
Versión optimizada para Render.com
NO requiere input() interactivo
Servidor HTTP siempre activo
"""
import os
os.environ['MPLBACKEND'] = 'Agg'

import sys
import time
import threading
import http.server
import socketserver

# Import todo del bot principal
sys.path.insert(0, os.path.dirname(__file__))
from crypto_pivot_v4_5_hybrid import (
    analyze_asset_full,
    educational_content,
    build_dashboard_hybrid,
    CONFIG,
    success,
    info,
    warn,
    err
)

# Puerto para Render
PORT = int(os.environ.get("PORT", 10000))

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    """Handler HTTP con logging mejorado y sin cache"""
    
    def log_message(self, format, *args):
        info(f"{self.address_string()} - {format % args}")
    
    def end_headers(self):
        # Agregar headers anti-cache
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()
    
    def do_GET(self):
        # Redirect root to dashboard
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/dashboard.html')
            self.end_headers()
            return
        
        return http.server.SimpleHTTPRequestHandler.do_GET(self)


def generate_dashboard():
    """Genera el dashboard una vez"""
    try:
        info("🔄 Generando dashboard...")
        
        # Analizar BTC
        info("📊 Analizando BTC...")
        btc_data = analyze_asset_full("BTC")
        
        # Analizar ETH
        info("📊 Analizando ETH...")
        eth_data = analyze_asset_full("ETH")
        
        # Contenido educativo
        edu = educational_content()
        
        # Construir dashboard
        info("🎨 Construyendo dashboard HTML...")
        build_dashboard_hybrid(btc_data, eth_data, edu, CONFIG["OUTPUT_DIR"])
        
        success(f"✅ Dashboard actualizado - BTC: {btc_data['geometric_bias']} ({btc_data['synthesis']['score']}/4⭐)")
        
        if btc_data.get('context_alert', {}).get('has_alert'):
            warn(f"⚠ Alerta activa: {btc_data['context_alert']['alert_type']}")
        
    except Exception as e:
        err(f"❌ Error generando dashboard: {str(e)}")
        import traceback
        traceback.print_exc()


def regenerate_loop():
    """Loop infinito que regenera el dashboard cada hora"""
    # Loop cada hora (primera generación ya se hizo en main)
    while True:
        try:
            info(f"⏰ Esperando 60 minutos para próxima actualización...")
            time.sleep(3600)  # 60 minutos
            generate_dashboard()
        except Exception as e:
            err(f"Error en loop de regeneración: {str(e)}")
            time.sleep(300)  # 5 minutos antes de reintentar


def main():
    """Punto de entrada principal para Render"""
    print("""
╔══════════════════════════════════════════════════════════════════════════╗
║  🔷 CRYPTO PIVOT ANALYZER v4.5 — RENDER DEPLOY                          ║
╚══════════════════════════════════════════════════════════════════════════╝
""")
    
    # Crear directorios
    os.makedirs(CONFIG["OUTPUT_DIR"], exist_ok=True)
    os.makedirs(CONFIG["CACHE_DIR"], exist_ok=True)
    
    # Cambiar a directorio de salida
    os.chdir(CONFIG["OUTPUT_DIR"])
    
    # Crear página de loading temporal
    with open("dashboard.html", "w", encoding="utf-8") as f:
        f.write("""
<!DOCTYPE html>
<html lang='es'>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0">
    <title>Crypto Pivot Analyzer - Cargando</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'IBM Plex Mono', monospace;
            background: linear-gradient(135deg, #0a0e1a 0%, #1a1f35 100%);
            color: #e2e8f0;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            padding: 20px;
        }
        .loading-container {
            text-align: center;
            max-width: 600px;
        }
        .logo {
            font-size: 4rem;
            margin-bottom: 20px;
            animation: pulse 2s ease-in-out infinite;
        }
        @keyframes pulse {
            0%, 100% { opacity: 1; transform: scale(1); }
            50% { opacity: 0.8; transform: scale(1.05); }
        }
        h1 {
            color: #00ff9f;
            font-size: 1.5rem;
            margin-bottom: 10px;
            font-weight: 600;
        }
        .spinner {
            border: 4px solid rgba(0,255,159,0.1);
            border-radius: 50%;
            border-top: 4px solid #00ff9f;
            width: 60px;
            height: 60px;
            animation: spin 1s linear infinite;
            margin: 30px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .status {
            background: rgba(15,22,41,0.8);
            border: 1px solid #1e2d4a;
            border-radius: 10px;
            padding: 20px;
            margin: 20px 0;
            border-left: 4px solid #00ff9f;
        }
        .status-title {
            color: #00ff9f;
            font-size: 0.9rem;
            margin-bottom: 10px;
            font-weight: 600;
        }
        .status-text {
            color: #64748b;
            font-size: 0.85rem;
            line-height: 1.6;
        }
        .progress-bar {
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            height: 8px;
            margin: 15px 0;
            overflow: hidden;
        }
        .progress-fill {
            background: linear-gradient(90deg, #00ff9f, #00d4ff);
            height: 100%;
            width: 0%;
            animation: loading 3s ease-in-out infinite;
        }
        @keyframes loading {
            0% { width: 0%; }
            50% { width: 70%; }
            100% { width: 100%; }
        }
        .countdown {
            color: #ffd60a;
            font-size: 2rem;
            font-weight: 700;
            margin: 20px 0;
        }
        .steps {
            text-align: left;
            margin: 20px 0;
        }
        .step {
            display: flex;
            align-items: center;
            margin: 10px 0;
            font-size: 0.85rem;
            color: #64748b;
        }
        .step-icon {
            color: #00ff9f;
            margin-right: 10px;
            font-size: 1.2rem;
        }
    </style>
</head>
<body>
    <div class='loading-container'>
        <div class='logo'>🔷</div>
        <h1>CRYPTO PIVOT ANALYZER v4.5</h1>
        
        <div class='spinner'></div>
        
        <div class='status'>
            <div class='status-title'>⏳ Generando Dashboard Inicial</div>
            <div class='status-text'>
                Primera vez: descargando 12 meses de datos históricos 4H para BTC y ETH.
                <br>Esto puede tomar 2-4 minutos.
            </div>
            <div class='progress-bar'>
                <div class='progress-fill'></div>
            </div>
        </div>
        
        <div class='countdown' id='countdown'>Recargando en <span id='seconds'>10</span>s</div>
        
        <div class='steps'>
            <div class='step'>
                <span class='step-icon'>✓</span>
                <span>Servidor HTTP iniciado</span>
            </div>
            <div class='step'>
                <span class='step-icon'>⏳</span>
                <span>Descargando datos históricos BTC/ETH...</span>
            </div>
            <div class='step'>
                <span class='step-icon'>⏳</span>
                <span>Calculando TIME/DISTANCE validation...</span>
            </div>
            <div class='step'>
                <span class='step-icon'>⏳</span>
                <span>Generando dashboard HTML...</span>
            </div>
        </div>
        
        <p style='color:#64748b;font-size:0.75rem;margin-top:30px'>
            Esta página se recargará automáticamente cuando el dashboard esté listo.
        </p>
    </div>
    
    <script>
        let seconds = 10;
        const countdownEl = document.getElementById('seconds');
        
        const interval = setInterval(() => {
            seconds--;
            countdownEl.textContent = seconds;
            
            if (seconds <= 0) {
                clearInterval(interval);
                location.reload();
            }
        }, 1000);
    </script>
</body>
</html>
""")
    
    # Crear directorio de salida
    os.makedirs(CONFIG["OUTPUT_DIR"], exist_ok=True)
    
    # Generar dashboard ANTES de iniciar servidor
    info("⏳ Generando dashboard inicial antes de iniciar servidor...")
    generate_dashboard()
    success("✅ Dashboard inicial listo")
    
    # Cambiar al directorio de salida
    os.chdir(CONFIG["OUTPUT_DIR"])
    success(f"📂 Servidor en: {os.getcwd()}")
    
    # Iniciar loop de regeneración en background
    regen_thread = threading.Thread(target=regenerate_loop, daemon=True)
    regen_thread.start()
    
    # Iniciar servidor HTTP
    Handler = DashboardHandler
    
    try:
        with socketserver.TCPServer(("0.0.0.0", PORT), Handler) as httpd:
            success(f"✓ Servidor HTTP iniciado en puerto {PORT}")
            success(f"✓ Dashboard disponible en http://0.0.0.0:{PORT}/dashboard.html")
            info("🔄 Auto-actualización cada 60 minutos")
            warn("⚠ Presiona Ctrl+C para detener")
            
            # Servir indefinidamente
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        warn("\n👋 Servidor detenido por usuario")
    except Exception as e:
        err(f"💥 Error fatal: {str(e)}")
        raise


if __name__ == "__main__":
    main()
