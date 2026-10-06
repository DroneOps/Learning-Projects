// Mini app para macOS que lista los nombres de las redes Wi-Fi cercanas.
// macOS (14+) oculta esos nombres a scripts de terminal; solo una app con permiso de
// Localización puede verlos. wifi_tello.py la compila y la abre automáticamente.
// Uso: open -W TelloWiFi.app --args <archivo_salida>
import CoreLocation
import CoreWLAN
import Foundation

let archivoSalida = CommandLine.arguments.dropFirst().first ?? "/dev/stdout"

func terminar(_ redes: [String], _ codigo: Int32) -> Never {
    try? redes.joined(separator: "\n").write(toFile: archivoSalida, atomically: true, encoding: .utf8)
    exit(codigo)
}

class Escaner: NSObject, CLLocationManagerDelegate {
    let gestor = CLLocationManager()

    override init() {
        super.init()
        gestor.delegate = self  // macOS llama a locationManagerDidChangeAuthorization al asignar el delegate
    }

    func locationManagerDidChangeAuthorization(_ gestor: CLLocationManager) {
        switch gestor.authorizationStatus {
        case .notDetermined:
            gestor.requestWhenInUseAuthorization()  // muestra la ventana de permiso
        case .authorizedAlways:
            let redes = (try? CWWiFiClient.shared().interface()?.scanForNetworks(withSSID: nil)) ?? []
            terminar(redes.compactMap { $0.ssid }, 0)
        default:
            terminar([], 2)  // permiso negado
        }
    }
}

let escaner = Escaner()
// Si el usuario no responde la ventana de permiso en 60 s, salimos sin resultados
RunLoop.main.run(until: Date(timeIntervalSinceNow: 60))
terminar([], 3)
