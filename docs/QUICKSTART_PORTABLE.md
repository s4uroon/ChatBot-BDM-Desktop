# 🚀 Guide Rapide - Version Portable Windows

Guide ultra-rapide pour créer et distribuer la version portable de ChatBot BDM Desktop.

## ⚡ En 3 étapes

### 1️⃣ Installer les dépendances

```bash
pip install -r requirements.txt
pip install -r build_scripts/requirements-build.txt
```

### 2️⃣ Compiler

**Windows** : Double-cliquez sur `build_scripts/build_portable.bat`

ou

**PowerShell** : Clic droit sur `build_scripts/build_portable.ps1` → Exécuter

ou

**Ligne de commande** :

```bash
pyinstaller ChatBot_BDM_Desktop.spec
```

### 3️⃣ Tester

```bash
cd "dist\ChatBot BDM Desktop"
"ChatBot BDM Desktop.exe"
```

---

## 📦 Distribuer

1. Compressez `dist\ChatBot BDM Desktop\` en ZIP
2. Partagez le ZIP
3. Les utilisateurs extraient et lancent l'exe

---

## ✅ Checklist avant distribution

- [ ] L'exe se lance sans erreur
- [ ] Les données (logs/exports) sont stockées dans `data/` à côté de l'exe (créé automatiquement)
- [ ] Le déplacement du dossier fonctionne
- [ ] Testé sur Windows 10 et 11
- [ ] README.txt présent et à jour
- [ ] Taille du package raisonnable (~150-200 Mo)

---

## 🔍 Vérification rapide

```bash
# Voir la structure
tree "dist\ChatBot BDM Desktop" /F

# Lancer en mode debug
"dist\ChatBot BDM Desktop\ChatBot BDM Desktop.exe" --debug

# Vérifier les données
dir "dist\ChatBot BDM Desktop\data"
```

---

## 📖 Documentation complète

Pour plus de détails, consultez **docs/BUILD_PORTABLE.md**

---

**Temps estimé** : 5-10 minutes (première fois), 2 minutes (builds suivants)
