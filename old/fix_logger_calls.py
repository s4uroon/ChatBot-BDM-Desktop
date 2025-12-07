"""
fix_logger_calls.py
===================
Script pour détecter et corriger automatiquement tous les appels
aux méthodes personnalisées du logger qui n'existent pas
"""

import os
import re

# Mapping des méthodes personnalisées vers les méthodes standard
LOGGER_FIXES = {
    r'\.log_error\(': '.error(',
    r'\.log_config\(': '.debug(',
    r'\.log_api_request\(': '.debug(',
    r'\.log_api_chunk\(': '.debug(',
    r'\.log_api_complete\(': '.debug(',
    r'\.log_code_block_detected\(': '.debug(',
    r'\.log_database_operation\(': '.debug(',
    r'\.log_export\(': '.info(',
}

def scan_file(filepath):
    """Scan un fichier pour détecter les appels problématiques."""
    problems = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
        
        for line_num, line in enumerate(lines, 1):
            for old_pattern in LOGGER_FIXES.keys():
                if re.search(old_pattern, line):
                    problems.append({
                        'file': filepath,
                        'line': line_num,
                        'content': line.strip(),
                        'pattern': old_pattern
                    })
    
    except Exception as e:
        print(f"Erreur lecture {filepath}: {e}")
    
    return problems

def fix_file(filepath):
    """Corrige automatiquement un fichier."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Appliquer toutes les corrections
        for old_pattern, new_method in LOGGER_FIXES.items():
            content = re.sub(old_pattern, new_method, content)
        
        # Si des changements ont été faits
        if content != original_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
    
    except Exception as e:
        print(f"Erreur correction {filepath}: {e}")
        return False
    
    return False

def scan_directory(directory):
    """Scan récursivement tous les fichiers Python."""
    all_problems = []
    
    for root, dirs, files in os.walk(directory):
        # Ignorer venv
        if 'venv' in root or 'myenv' in root or '__pycache__' in root:
            continue
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                problems = scan_file(filepath)
                if problems:
                    all_problems.extend(problems)
    
    return all_problems

def main():
    """Fonction principale."""
    print("=" * 70)
    print("  CORRECTION AUTOMATIQUE DES APPELS LOGGER")
    print("=" * 70)
    print()
    
    # Scan
    print("[1/2] Scan des fichiers Python...")
    problems = scan_directory('.')
    
    if not problems:
        print("✅ Aucun problème détecté !")
        return
    
    # Afficher les problèmes trouvés
    print(f"\n⚠️  {len(problems)} appel(s) problématique(s) détecté(s):\n")
    
    files_with_problems = {}
    for problem in problems:
        filepath = problem['file']
        if filepath not in files_with_problems:
            files_with_problems[filepath] = []
        files_with_problems[filepath].append(problem)
    
    for filepath, file_problems in files_with_problems.items():
        print(f"📄 {filepath} ({len(file_problems)} problème(s))")
        for p in file_problems[:3]:  # Afficher max 3 exemples
            print(f"   Ligne {p['line']}: {p['content'][:80]}")
        if len(file_problems) > 3:
            print(f"   ... et {len(file_problems) - 3} autre(s)")
        print()
    
    # Demander confirmation
    print(f"Voulez-vous corriger automatiquement ces {len(files_with_problems)} fichier(s) ?")
    choice = input("Tapez 'oui' pour continuer: ").strip().lower()
    
    if choice != 'oui':
        print("❌ Opération annulée")
        return
    
    # Correction
    print("\n[2/2] Correction des fichiers...")
    fixed_count = 0
    
    for filepath in files_with_problems.keys():
        if fix_file(filepath):
            print(f"✅ Corrigé: {filepath}")
            fixed_count += 1
        else:
            print(f"⚠️  Aucun changement: {filepath}")
    
    print()
    print("=" * 70)
    print(f"✅ TERMINÉ: {fixed_count} fichier(s) corrigé(s)")
    print("=" * 70)
    print()
    print("Vous pouvez maintenant relancer l'application:")
    print("  python main.py")

if __name__ == '__main__':
    main()
