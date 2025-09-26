#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de las hojas de procedimientos y pacienteprocedimientos
Basado en el script de análisis de vacunas
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
        
        # Buscar hojas relacionadas con procedimientos
        procedimientos_sheets = [sheet for sheet in xl.sheet_names if 'procedimientos' in sheet.lower()]
        
        if not procedimientos_sheets:
            print("[X] No se encontraron hojas relacionadas con procedimientos")
            return
        
        print(f"\nHojas de procedimientos encontradas: {procedimientos_sheets}")
        
        for sheet_name in procedimientos_sheets:
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
            
            # Análisis específico según el tipo de hoja
            if 'procedimientos' in sheet_name.lower() and 'paciente' not in sheet_name.lower():
                analyze_procedimientos_sheet(df, sheet_name)
            elif 'pacienteprocedimientos' in sheet_name.lower() or ('paciente' in sheet_name.lower() and 'procedimientos' in sheet_name.lower()):
                analyze_pacienteprocedimientos_sheet(df, sheet_name)
            
    except Exception as e:
        print(f"[X] Error al analizar el archivo: {e}")

def analyze_procedimientos_sheet(df, sheet_name):
    """Análisis específico para hoja de procedimientos"""
    print(f"\n🔬 ANÁLISIS ESPECÍFICO - PROCEDIMIENTOS")
    
    # Buscar columna de ID (InterventionId)
    id_columns = [col for col in df.columns if 'interventionid' in col.lower()]
    if id_columns:
        id_col = id_columns[0]
        print(f"[OK] Columna de ID encontrada: {id_col}")
        unique_ids = df[id_col].nunique()
        total_rows = len(df)
        duplicates = total_rows - unique_ids
        print(f"   - IDs únicos: {unique_ids}")
        print(f"   - Total filas: {total_rows}")
        print(f"   - Duplicados: {duplicates}")
        
        # Verificar valores nulos
        null_count = df[id_col].isnull().sum()
        print(f"   - Valores nulos en ID: {null_count}")
    else:
        print("[X] No se encontró columna InterventionId")
    
    # Buscar campos comunes
    common_fields = ['nombre', 'name', 'description', 'descripcion', 'tipo', 'type', 'precio', 'price', 'cost', 'costo']
    found_fields = []
    for field in common_fields:
        matching_cols = [col for col in df.columns if field in col.lower()]
        if matching_cols:
            found_fields.extend(matching_cols)
    
    if found_fields:
        print(f"[OK] Campos comunes encontrados: {found_fields}")
    
    # Información de tipos de datos
    print(f"\n[STATS] Tipos de datos:")
    for col in df.columns[:10]:  # Limitar a 10 columnas para no saturar
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        print(f"   - {col}: {dtype} (nulos: {null_count})")

def analyze_pacienteprocedimientos_sheet(df, sheet_name):
    """Análisis específico para hoja de pacienteprocedimientos"""
    print(f"\n🏥 ANÁLISIS ESPECÍFICO - PACIENTE PROCEDIMIENTOS")
    
    # Buscar columnas de ID
    patient_id_columns = [col for col in df.columns if 'patientinterventionid' in col.lower()]
    intervention_id_columns = [col for col in df.columns if 'interventionid' in col.lower() and 'patient' not in col.lower()]
    
    if patient_id_columns:
        patient_id_col = patient_id_columns[0]
        print(f"[OK] Columna de ID de paciente-procedimientos encontrada: {patient_id_col}")
        unique_patient_ids = df[patient_id_col].nunique()
        total_rows = len(df)
        print(f"   - IDs únicos de paciente-procedimientos: {unique_patient_ids}")
        print(f"   - Total filas: {total_rows}")
        
        # Verificar valores nulos
        null_count = df[patient_id_col].isnull().sum()
        print(f"   - Valores nulos en PatientInterventionId: {null_count}")
    else:
        print("[X] No se encontró columna PatientInterventionId")
    
    if intervention_id_columns:
        intervention_id_col = intervention_id_columns[0]
        print(f"[OK] Columna de ID de procedimientos encontrada: {intervention_id_col}")
        unique_intervention_ids = df[intervention_id_col].nunique()
        print(f"   - IDs únicos de procedimientos: {unique_intervention_ids}")
        
        # Verificar valores nulos
        null_count = df[intervention_id_col].isnull().sum()
        print(f"   - Valores nulos en InterventionId: {null_count}")
    else:
        print("[X] No se encontró columna InterventionId")
    
    # Buscar campos de fecha
    date_fields = [col for col in df.columns if any(word in col.lower() for word in ['date', 'fecha', 'timestamp', 'time'])]
    if date_fields:
        print(f"[OK] Campos de fecha encontrados: {date_fields}")
    
    # Buscar campos de paciente
    patient_fields = [col for col in df.columns if any(word in col.lower() for word in ['patient', 'paciente', 'pet', 'mascota'])]
    if patient_fields:
        print(f"[OK] Campos de paciente encontrados: {patient_fields}")
    
    # Información de tipos de datos
    print(f"\n[STATS] Tipos de datos:")
    for col in df.columns[:10]:  # Limitar a 10 columnas para no saturar
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        print(f"   - {col}: {dtype} (nulos: {null_count})")

def main():
    """Función principal"""
    import sys
    
    # Verificar argumentos de línea de comandos
    if len(sys.argv) != 4:
        print("Uso: python analyze_procedimientos_sheets.py <archivo_fuente> <cliente> <directorio_generation>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    cliente = sys.argv[2]
    generation_dir = sys.argv[3]
    
    if not os.path.exists(file_path):
        print(f"[X] No se encontró el archivo: {file_path}")
        return
    
    print("[>>] INICIANDO ANÁLISIS DE PROCEDIMIENTOS")
    print(f"[DIR] Archivo fuente: {file_path}")
    print(f"[USER] Cliente: {cliente}")
    print(f"[FOLDER] Directorio generation: {generation_dir}")
    
    analyze_excel_sheets(file_path)
    print("\n[OK] ANÁLISIS COMPLETADO")

if __name__ == "__main__":
    main()