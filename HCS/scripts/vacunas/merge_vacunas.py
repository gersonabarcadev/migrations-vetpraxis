#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simple para hacer MERGE entre vacunas y pacientevacuna
"""

import pandas as pd
import os

def merge_vacunas(input_file=None, output_dir=None):
    """Une las hojas vacunas y pacientevacuna"""
    
    # Configurar rutas por defecto si no se proporcionan
    if input_file is None:
        base_path = os.path.dirname(os.path.dirname(__file__))
        input_file = os.path.join(base_path, "backup", "analisis_veterinry.xlsx")
    
    if output_dir is None:
        base_path = os.path.dirname(os.path.dirname(__file__))
        output_dir = os.path.join(base_path, "generation")
    
    # Asegurar que el directorio de salida existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Archivo de salida
    output_file = os.path.join(output_dir, "vacunas_merged.xlsx")
    
    print("[PROC] Cargando datos...")
    
    # Cargar ambas hojas
    pacientevacuna = pd.read_excel(input_file, sheet_name='pacientevacuna')
    vacunas = pd.read_excel(input_file, sheet_name='vacunas')
    
    print(f"[OK] Datos cargados:")
    print(f"   - pacientevacuna: {pacientevacuna.shape[0]} filas, {pacientevacuna.shape[1]} columnas")
    print(f"   - vacunas: {vacunas.shape[0]} filas, {vacunas.shape[1]} columnas")
    
    print("\n[LINK] Realizando MERGE...")
    
    # Hacer el merge usando VaccineId
    merged_df = pacientevacuna.merge(
        vacunas, 
        on='VaccineId', 
        how='left',
        suffixes=('', '_vaccine')
    )
    
    print(f"[OK] Merge completado: {merged_df.shape[0]} filas, {merged_df.shape[1]} columnas")
    
    # Verificar que el merge fue exitoso
    missing_vaccines = merged_df['Name'].isna().sum()
    if missing_vaccines > 0:
        print(f"[WARN]  {missing_vaccines} registros no encontraron vacuna correspondiente")
    else:
        print("[OK] Todos los registros tienen vacuna correspondiente")
    
    print(f"\n[SAVE] Guardando en: {output_file}")
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Guardar en Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Hoja principal con datos unidos
        merged_df.to_excel(writer, sheet_name='Vacunas_Merged', index=False)
        
        # También guardar las hojas originales para referencia
        pacientevacuna.to_excel(writer, sheet_name='Original_PacienteVacuna', index=False)
        vacunas.to_excel(writer, sheet_name='Original_Vacunas', index=False)
    
    print("[OK] Archivo guardado exitosamente")
    
    # Mostrar información del resultado
    print(f"\n[DATA] RESULTADO FINAL:")
    print(f"   - Total de registros: {len(merged_df):,}")
    print(f"   - Total de columnas: {len(merged_df.columns)}")
    print(f"   - Columnas principales:")
    
    key_columns = ['PatientVaccineId', 'PatientId', 'VaccineId', 'Name', 'DataDate', 'DateExpires']
    for col in key_columns:
        if col in merged_df.columns:
            print(f"     [CHECK] {col}")
    
    print(f"\n[DONE] PROCESO COMPLETADO")
    print(f"[DIR] Archivo: {output_file}")
    
    return merged_df

def main():
    """Función principal"""
    import sys
    
    print("[>>] INICIANDO MERGE DE VACUNAS")
    
    # Verificar argumentos
    if len(sys.argv) >= 4:
        source_file = sys.argv[1]
        client_name = sys.argv[2]
        generation_dir = sys.argv[3]
        
        print(f"[DIR] Archivo fuente: {source_file}")
        print(f"[USER] Cliente: {client_name}")
        print(f"[FOLDER] Directorio generation: {generation_dir}")
        
        input_file = source_file
        output_dir = generation_dir
    else:
        print("[WARN]  Usando modo compatibilidad - rutas por defecto")
        input_file = None
        output_dir = None
    
    try:
        merged_df = merge_vacunas(input_file, output_dir)
        if merged_df is not None:
            print("\n[OK] MERGE COMPLETADO EXITOSAMENTE")
        else:
            print("\n[X] NO SE PUDO COMPLETAR EL MERGE")
    except Exception as e:
        print(f"[X] Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()