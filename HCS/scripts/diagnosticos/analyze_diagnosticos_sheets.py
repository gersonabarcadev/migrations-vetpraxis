#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de las hojas de diagnosticos y pacientediagnosticos
Adaptado del script de análisis de procedimientos para diagnósticos
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
        
        # Buscar hojas relacionadas con diagnosticos
        diagnosticos_sheets = [sheet for sheet in xl.sheet_names if 'diagnostic' in sheet.lower()]
        
        if not diagnosticos_sheets:
            print("[X] No se encontraron hojas relacionadas con diagnósticos")
            return
        
        print(f"\nHojas de diagnósticos encontradas: {diagnosticos_sheets}")
        
        for sheet_name in diagnosticos_sheets:
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
            if 'diagnostic' in sheet_name.lower() and 'patient' not in sheet_name.lower():
                analyze_diagnosticos_sheet(df, sheet_name)
            elif 'patientdiagnostic' in sheet_name.lower() or ('patient' in sheet_name.lower() and 'diagnostic' in sheet_name.lower()):
                analyze_pacientediagnosticos_sheet(df, sheet_name)
            
    except Exception as e:
        print(f"[X] Error al analizar el archivo: {e}")

def analyze_diagnosticos_sheet(df, sheet_name):
    """Análisis específico para hoja de diagnosticos"""
    print(f"\n🔬 ANÁLISIS ESPECÍFICO - DIAGNÓSTICOS")
    
    # Buscar columna de ID (DiagnosticId)
    id_columns = [col for col in df.columns if 'diagnosticid' in col.lower()]
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
        print("[X] No se encontró columna DiagnosticId")
    
    # Buscar campos comunes
    common_fields = ['nombre', 'name', 'description', 'descripcion', 'tipo', 'type', 'diagnostico', 'diagnostic']
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

def analyze_pacientediagnosticos_sheet(df, sheet_name):
    """Análisis específico para hoja de pacientediagnosticos"""
    print(f"\n🏥 ANÁLISIS ESPECÍFICO - PACIENTE DIAGNÓSTICOS")
    
    # Buscar columnas de ID
    patient_diagnostic_id_columns = [col for col in df.columns if 'patientdiagnosticid' in col.lower()]
    diagnostic_id_columns = [col for col in df.columns if 'diagnosticid' in col.lower() and 'patient' not in col.lower()]
    
    if patient_diagnostic_id_columns:
        patient_diagnostic_id_col = patient_diagnostic_id_columns[0]
        print(f"[OK] Columna de ID de paciente-diagnósticos encontrada: {patient_diagnostic_id_col}")
        unique_patient_diagnostic_ids = df[patient_diagnostic_id_col].nunique()
        total_rows = len(df)
        print(f"   - IDs únicos de paciente-diagnósticos: {unique_patient_diagnostic_ids}")
        print(f"   - Total filas: {total_rows}")
        
        # Verificar valores nulos
        null_count = df[patient_diagnostic_id_col].isnull().sum()
        print(f"   - Valores nulos en PatientDiagnosticId: {null_count}")
    else:
        print("[X] No se encontró columna PatientDiagnosticId")
    
    if diagnostic_id_columns:
        diagnostic_id_col = diagnostic_id_columns[0]
        print(f"[OK] Columna de ID de diagnósticos encontrada: {diagnostic_id_col}")
        unique_diagnostic_ids = df[diagnostic_id_col].nunique()
        print(f"   - IDs únicos de diagnósticos: {unique_diagnostic_ids}")
        
        # Verificar valores nulos
        null_count = df[diagnostic_id_col].isnull().sum()
        print(f"   - Valores nulos en DiagnosticId: {null_count}")
    else:
        print("[X] No se encontró columna DiagnosticId")
    
    # Buscar campos de fecha
    date_fields = [col for col in df.columns if any(word in col.lower() for word in ['date', 'fecha', 'timestamp', 'time'])]
    if date_fields:
        print(f"[OK] Campos de fecha encontrados: {date_fields}")
    
    # Buscar campos de paciente
    patient_fields = [col for col in df.columns if any(word in col.lower() for word in ['patient', 'paciente', 'pet', 'mascota'])]
    if patient_fields:
        print(f"[OK] Campos de paciente encontrados: {patient_fields}")
    
    # Buscar campos de peso y temperatura
    peso_temp_fields = [col for col in df.columns if any(word in col.lower() for word in ['peso', 'weight', 'temp', 'temperatura', 'temperature'])]
    if peso_temp_fields:
        print(f"[OK] Campos de peso/temperatura encontrados: {peso_temp_fields}")
        
        # Analizar contenido de estos campos
        for field in peso_temp_fields:
            non_null_count = df[field].notna().sum()
            if non_null_count > 0:
                print(f"   - {field}: {non_null_count} valores no nulos")
                # Mostrar algunos valores de ejemplo
                sample_values = df[field].dropna().head(3).tolist()
                print(f"     Ejemplos: {sample_values}")
    
    # Información de tipos de datos
    print(f"\n[STATS] Tipos de datos:")
    for col in df.columns[:15]:  # Mostrar más columnas para diagnósticos
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        print(f"   - {col}: {dtype} (nulos: {null_count})")

def main():
    """Función principal"""
    import sys
    
    # Verificar si se pasaron argumentos
    if len(sys.argv) >= 4:
        # Argumentos: script_name, source_file, client_name, generation_dir
        source_file = sys.argv[1]
        client_name = sys.argv[2] 
        generation_dir = sys.argv[3]
        
        print(f"[DIR] Archivo fuente: {source_file}")
        print(f"[USER] Cliente: {client_name}")
        print(f"[FOLDER] Directorio generation: {generation_dir}")
        
        file_path = source_file
    else:
        # Modo compatibilidad hacia atrás
        base_path = os.path.dirname(os.path.dirname(__file__))
        file_path = os.path.join(base_path, "backup", "analisis_veterinry.xlsx")
        
        print(f"[WARN]  Usando modo compatibilidad - archivo por defecto")
    
    if not os.path.exists(file_path):
        print(f"[X] No se encontró el archivo: {file_path}")
        return
    
    print("[>>] INICIANDO ANÁLISIS DE DIAGNÓSTICOS")
    analyze_excel_sheets(file_path)
    print("\n[OK] ANÁLISIS COMPLETADO")

if __name__ == "__main__":
    main()