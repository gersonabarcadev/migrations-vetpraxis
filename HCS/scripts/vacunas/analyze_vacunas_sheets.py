#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de las hojas de vacunas y pacientevacuna
"""

import pandas as pd
import os

def analyze_excel_sheets(file_path):
    """Analiza las hojas de un archivo Excel"""
    print(f"\n{'='*60}")
    print(f"ANALIZANDO ARCHIVO: {file_path}")
    print(f"{'='*60}")
    
    try:
        # Leer todas las hojas del archivo
        xl = pd.ExcelFile(file_path)
        print(f"\nHojas disponibles: {xl.sheet_names}")
        
        # Buscar hojas relacionadas con vacunas
        vacunas_sheets = [sheet for sheet in xl.sheet_names if 'vacuna' in sheet.lower()]
        
        if not vacunas_sheets:
            print("[X] No se encontraron hojas relacionadas con vacunas")
            return
        
        print(f"\nHojas de vacunas encontradas: {vacunas_sheets}")
        
        for sheet_name in vacunas_sheets:
            print(f"\n{'-'*50}")
            print(f"ANALIZANDO HOJA: {sheet_name}")
            print(f"{'-'*50}")
            
            # Leer la hoja
            df = pd.read_excel(file_path, sheet_name=sheet_name)
            
            # Información básica
            print(f"[DATA] Dimensiones: {df.shape[0]} filas x {df.shape[1]} columnas")
            print(f"[LIST] Columnas: {list(df.columns)}")
            
            # Mostrar las primeras filas
            print(f"\n[SEARCH] Primeras 5 filas:")
            print(df.head().to_string())
            
            # Verificar valores únicos en columnas clave
            if 'patientvaccineid' in df.columns:
                unique_ids = df['patientvaccineid'].nunique()
                total_rows = len(df)
                duplicates = total_rows - unique_ids
                print(f"\n[KEY] PatientVaccineID:")
                print(f"   - Valores únicos: {unique_ids}")
                print(f"   - Total de filas: {total_rows}")
                print(f"   - Duplicados: {duplicates}")
                
                if duplicates > 0:
                    print(f"   [WARN]  ADVERTENCIA: Hay {duplicates} IDs duplicados")
                    duplicated_ids = df[df['patientvaccineid'].duplicated(keep=False)]['patientvaccineid'].unique()
                    print(f"   IDs duplicados: {duplicated_ids[:10]}...")  # Mostrar solo los primeros 10
            
            # Verificar nulos
            print(f"\n❓ Valores nulos por columna:")
            null_counts = df.isnull().sum()
            for col, null_count in null_counts.items():
                if null_count > 0:
                    percentage = (null_count / len(df)) * 100
                    print(f"   - {col}: {null_count} ({percentage:.1f}%)")
            
            # Si hay columnas de fecha, analizarlas
            date_columns = [col for col in df.columns if any(keyword in col.lower() for keyword in ['date', 'fecha', 'time', 'created', 'updated'])]
            if date_columns:
                print(f"\n[DATE] Columnas de fecha encontradas: {date_columns}")
                for date_col in date_columns:
                    try:
                        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                        min_date = df[date_col].min()
                        max_date = df[date_col].max()
                        print(f"   - {date_col}: desde {min_date} hasta {max_date}")
                    except:
                        print(f"   - {date_col}: Error al convertir a fecha")
            
            print(f"\n[STATS] Estadísticas descriptivas (columnas numéricas):")
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                print(df[numeric_cols].describe())
            else:
                print("   No hay columnas numéricas")
        
    except Exception as e:
        print(f"[X] Error al analizar {file_path}: {str(e)}")

def main():
    """Función principal"""
    import sys
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) >= 4:
        source_file = sys.argv[1]
        client_name = sys.argv[2]
        generation_dir = sys.argv[3]
        
        print(f"[DIR] Archivo fuente: {source_file}")
        print(f"[USER] Cliente: {client_name}")
        print(f"[FOLDER] Directorio generation: {generation_dir}")
        
        file_path = source_file
    else:
        # Ruta por defecto (para compatibilidad)
        base_path = "/Users/vetpraxis/Downloads/migrations/veterinary/HCS/Vacuna/NS_HURON_AZUL_LOS_OLIVOS"
        file_path = os.path.join(base_path, "backup", "analisis_veterinry.xlsx")
    
    if not os.path.exists(file_path):
        print(f"[X] No se encontró el archivo: {file_path}")
        return
    
    print("[>>] INICIANDO ANÁLISIS DE VACUNAS")
    analyze_excel_sheets(file_path)
    print("\n[OK] ANÁLISIS COMPLETADO")

if __name__ == "__main__":
    main()