#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para reemplazar emojis Unicode por símbolos ASCII en todos los scripts
"""
import os
import glob

# Mapeo de emojis a símbolos ASCII
EMOJI_REPLACEMENTS = {
    '🚀': '[>>]',
    '✅': '[OK]',
    '❌': '[X]',
    '📁': '[DIR]',
    '📄': '[FILE]',
    '👤': '[USER]',
    '📂': '[FOLDER]',
    '🎯': '[>>]',
    '📊': '[DATA]',
    '📋': '[LIST]',
    '🔍': '[SEARCH]',
    '💾': '[SAVE]',
    '📅': '[DATE]',
    '🗑️': '[DEL]',
    '📏': '[UNIT]',
    '📈': '[STATS]',
    '🐾': '[PET]',
    '🔑': '[KEY]',
    '💊': '[MED]',
    '📦': '[BOX]',
    '📝': '[NOTE]',
    '🔧': '[TOOL]',
    '🔄': '[PROC]',
    '⚠️': '[WARN]',
    '🎉': '[DONE]',
    '🏗️': '[BUILD]',
    '🏠': '[HOME]',
    '📍': '[PIN]',
    '🔮': '[MAGIC]',
    '🎊': '[PARTY]',
    '💯': '[100]',
    '📢': '[ANNOUNCE]',
    '🔔': '[BELL]',
    '💡': '[IDEA]',
    '🎲': '[DICE]',
    '🎨': '[ART]',
    '📡': '[SIGNAL]',
    '🖥️': '[PC]',
    '💻': '[LAPTOP]',
    '📱': '[PHONE]',
    '🔗': '[LINK]',
    '✨': '[STAR]',
    '✓': '[CHECK]',
    '🔝': '[TOP]',
    '→': '->',
    '🔒': '[LOCK]',
    '🔓': '[UNLOCK]',
}

def fix_unicode_in_file(file_path):
    """Reemplaza emojis Unicode en un archivo"""
    try:
        # Leer archivo
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        
        # Reemplazar emojis
        for emoji, ascii_symbol in EMOJI_REPLACEMENTS.items():
            content = content.replace(emoji, ascii_symbol)
        
        # Solo escribir si hay cambios
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Contar reemplazos
            changes = sum(1 for emoji in EMOJI_REPLACEMENTS.keys() if emoji in original_content)
            print(f"[OK] {file_path}: {changes} emojis reemplazados")
            return changes
        else:
            print(f"[--] {file_path}: sin cambios")
            return 0
            
    except Exception as e:
        print(f"[X] Error en {file_path}: {e}")
        return 0

def main():
    """Procesa todos los archivos Python en scripts/"""
    
    print("[>>] INICIANDO REEMPLAZO DE EMOJIS UNICODE")
    print("=" * 50)
    
    # Buscar todos los archivos Python en scripts/
    script_files = []
    for root, dirs, files in os.walk('scripts'):
        for file in files:
            if file.endswith('.py'):
                script_files.append(os.path.join(root, file))
    
    print(f"[SEARCH] Encontrados {len(script_files)} archivos Python")
    
    total_changes = 0
    for file_path in script_files:
        changes = fix_unicode_in_file(file_path)
        total_changes += changes
    
    print("=" * 50)
    print(f"[DONE] Procesamiento completado")
    print(f"[STATS] Total archivos: {len(script_files)}")
    print(f"[STATS] Total reemplazos: {total_changes}")
    
    if total_changes > 0:
        print("\n[NOTE] Mapeo de símbolos:")
        for emoji, ascii_symbol in list(EMOJI_REPLACEMENTS.items())[:10]:
            print(f"  {emoji} -> {ascii_symbol}")
        if len(EMOJI_REPLACEMENTS) > 10:
            print(f"  ... y {len(EMOJI_REPLACEMENTS) - 10} más")

if __name__ == "__main__":
    main()