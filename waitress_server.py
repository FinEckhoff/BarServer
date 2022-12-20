from waitress import serve
import BarServer
serve(BarServer.app, host='0.0.0.0', port=6969)
