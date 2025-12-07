"""
test_pyqt.py
============
Script de diagnostic complet pour PyQt6 sur Windows
"""

import sys
import os
import platform
import subprocess


def print_header(title):
    """Affiche un en-tête formaté."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def check_python():
    """Vérifie la version de Python."""
    print_header("1. VÉRIFICATION PYTHON")
    
    version = sys.version_info
    print(f"✓ Version Python : {version.major}.{version.minor}.{version.micro}")
    print(f"✓ Architecture  : {platform.architecture()[0]}")
    print(f"✓ Plateforme    : {platform.system()} {platform.release()}")
    print(f"✓ Exécutable    : {sys.executable}")
    
    # Vérifier version minimale
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("\n⚠️  ATTENTION: Python 3.8+ requis pour PyQt6")
        return False
    
    return True


def check_pip():
    """Vérifie pip et liste les packages Qt."""
    print_header("2. VÉRIFICATION PIP & PACKAGES")
    
    try:
        import pip
        print(f"✓ Pip installé : {pip.__version__}")
    except ImportError:
        print("❌ Pip non trouvé")
        return False
    
    # Liste des packages installés
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "list"],
            capture_output=True,
            text=True
        )
        
        print("\nPackages Qt installés:")
        qt_packages = ['PyQt6', 'PyQt5', 'PySide6', 'PySide2']
        found_any = False
        
        for line in result.stdout.split('\n'):
            for pkg in qt_packages:
                if pkg.lower() in line.lower():
                    print(f"  {line}")
                    found_any = True
        
        if not found_any:
            print("  ❌ Aucun package Qt trouvé")
            return False
        
    except Exception as e:
        print(f"❌ Erreur lors de la vérification des packages: {e}")
        return False
    
    return True


def check_pyqt6_import():
    """Teste l'import de PyQt6."""
    print_header("3. TEST IMPORT PyQt6")
    
    # Test QtCore
    try:
        from PyQt6 import QtCore
        print("✅ PyQt6.QtCore importé avec succès")
        print(f"   Version Qt    : {QtCore.qVersion()}")
        print(f"   Version PyQt  : {QtCore.PYQT_VERSION_STR}")
    except ImportError as e:
        print(f"❌ Erreur import PyQt6.QtCore:")
        print(f"   {str(e)}")
        print("\n💡 Solution: Installer Visual C++ Redistributables")
        print("   Lien: https://aka.ms/vs/17/release/vc_redist.x64.exe")
        return False
    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        return False
    
    # Test QtWidgets
    try:
        from PyQt6.QtWidgets import QApplication
        print("✅ PyQt6.QtWidgets importé avec succès")
    except ImportError as e:
        print(f"❌ Erreur import PyQt6.QtWidgets:")
        print(f"   {str(e)}")
        return False
    
    # Test QtWebEngineWidgets
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        print("✅ PyQt6.QtWebEngineWidgets importé avec succès")
    except ImportError as e:
        print(f"❌ Erreur import PyQt6.QtWebEngineWidgets:")
        print(f"   {str(e)}")
        print("\n💡 Solution: Installer PyQt6-WebEngine")
        print("   pip install PyQt6-WebEngine==6.6.0")
        return False
    
    return True


def check_qapplication():
    """Teste la création d'une QApplication."""
    print_header("4. TEST CRÉATION QApplication")
    
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication([])
        print("✅ QApplication créée avec succès")
        print(f"   Nom application: {app.applicationName()}")
        return True
    except Exception as e:
        print(f"❌ Erreur création QApplication:")
        print(f"   {str(e)}")
        return False


def check_dll_path():
    """Vérifie le chemin des DLLs Qt."""
    print_header("5. VÉRIFICATION CHEMINS DLL")
    
    try:
        import PyQt6
        pyqt_path = os.path.dirname(PyQt6.__file__)
        qt_bin_path = os.path.join(pyqt_path, 'Qt6', 'bin')
        
        print(f"✓ Chemin PyQt6: {pyqt_path}")
        print(f"✓ Chemin Qt bin: {qt_bin_path}")
        
        if os.path.exists(qt_bin_path):
            dll_files = [f for f in os.listdir(qt_bin_path) if f.endswith('.dll')]
            print(f"\n✓ {len(dll_files)} DLL(s) trouvée(s):")
            
            critical_dlls = ['Qt6Core.dll', 'Qt6Gui.dll', 'Qt6Widgets.dll']
            for dll in critical_dlls:
                if dll in dll_files:
                    print(f"  ✅ {dll}")
                else:
                    print(f"  ❌ {dll} MANQUANT")
                    return False
            
            return True
        else:
            print(f"\n❌ Répertoire Qt bin introuvable: {qt_bin_path}")
            return False
            
    except Exception as e:
        print(f"❌ Erreur: {e}")
        return False


def check_vcredist():
    """Vérifie si Visual C++ Redistributables sont installés."""
    print_header("6. VÉRIFICATION VISUAL C++ REDISTRIBUTABLES")
    
    # Vérifier dans le registre Windows
    if platform.system() == 'Windows':
        try:
            import winreg
            
            vc_versions = []
            registry_paths = [
                r"SOFTWARE\Microsoft\VisualStudio\14.0\VC\Runtimes\x64",
                r"SOFTWARE\WOW6432Node\Microsoft\VisualStudio\14.0\VC\Runtimes\x64",
            ]
            
            for path in registry_paths:
                try:
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path)
                    version, _ = winreg.QueryValueEx(key, "Version")
                    vc_versions.append(version)
                    winreg.CloseKey(key)
                except:
                    continue
            
            if vc_versions:
                print(f"✅ Visual C++ Redistributables détecté(s):")
                for v in vc_versions:
                    print(f"   Version: {v}")
                return True
            else:
                print("❌ Visual C++ Redistributables non détecté")
                print("\n💡 Solution:")
                print("   1. Télécharger: https://aka.ms/vs/17/release/vc_redist.x64.exe")
                print("   2. Installer en tant qu'administrateur")
                print("   3. Redémarrer l'ordinateur")
                return False
                
        except ImportError:
            print("⚠️  Module winreg non disponible, impossible de vérifier")
            return True
    else:
        print("ℹ️  Test Windows uniquement, ignoré sur cette plateforme")
        return True


def print_summary(results):
    """Affiche le résumé des tests."""
    print_header("RÉSUMÉ DES TESTS")
    
    all_passed = all(results.values())
    
    for test_name, passed in results.items():
        status = "✅ PASSÉ" if passed else "❌ ÉCHEC"
        print(f"{status}  {test_name}")
    
    print("\n" + "=" * 60)
    
    if all_passed:
        print("\n🎉 TOUS LES TESTS SONT PASSÉS !")
        print("\nVotre environnement PyQt6 est correctement configuré.")
        print("Vous pouvez lancer l'application: python main.py")
    else:
        print("\n⚠️  CERTAINS TESTS ONT ÉCHOUÉ")
        print("\nConsultez WINDOWS_FIX.md pour les solutions détaillées.")
        print("\nSolution rapide (90% des cas):")
        print("  1. Installer Visual C++ Redistributables")
        print("     https://aka.ms/vs/17/release/vc_redist.x64.exe")
        print("  2. Redémarrer l'ordinateur")
        print("  3. Réinstaller PyQt6:")
        print("     pip uninstall PyQt6 PyQt6-WebEngine -y")
        print("     pip install PyQt6==6.6.1 PyQt6-WebEngine==6.6.0")
    
    print("\n" + "=" * 60)


def main():
    """Fonction principale."""
    print("\n" + "=" * 60)
    print("  DIAGNOSTIC PyQt6 - Chatbot Desktop")
    print("=" * 60)
    
    results = {}
    
    # Exécution des tests
    results["Python"] = check_python()
    results["Pip & Packages"] = check_pip()
    results["Import PyQt6"] = check_pyqt6_import()
    
    # Tests supplémentaires seulement si PyQt6 s'importe
    if results["Import PyQt6"]:
        results["QApplication"] = check_qapplication()
        results["Chemins DLL"] = check_dll_path()
    
    results["Visual C++ Redistributables"] = check_vcredist()
    
    # Résumé
    print_summary(results)
    
    # Code de sortie
    return 0 if all(results.values()) else 1


if __name__ == '__main__':
    exit_code = main()
    
    # Pause pour Windows (si lancé en double-clic)
    if platform.system() == 'Windows':
        input("\nAppuyez sur Entrée pour quitter...")
    
    sys.exit(exit_code)
