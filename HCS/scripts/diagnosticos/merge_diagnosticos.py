#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para hacer MERGE entre diagnosticos y pacientediagnosticos
Adaptado del script de merge de procedimientos
"""

import pandas as pd
import os

def merge_diagnosticos(input_file=None, output_dir=None):
    """Une las hojas diagnosticos y pacientediagnosticos"""
    
    # Si no se proporcionan parámetros, usar valores por defecto (compatibilidad hacia atrás)
    if input_file is None:
        base_path = os.path.dirname(os.path.dirname(__file__))
        input_file = os.path.join(base_path, "backup", "analisis_veterinry.xlsx")
    
    if output_dir is None:
        base_path = os.path.dirname(os.path.dirname(__file__))
        output_dir = os.path.join(base_path, "generation")
    
    # Asegurar que el directorio de salida existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Archivo de salida
    output_file = os.path.join(output_dir, "diagnosticos_merged.xlsx")
    
    print("[PROC] Cargando datos...")
    
    # Primero verificar qué hojas están disponibles
    xl = pd.ExcelFile(input_file)
    print(f"[LIST] Hojas disponibles: {xl.sheet_names}")
    
    # Buscar las hojas correctas
    diagnosticos_sheet = None
    pacientediagnosticos_sheet = None
    
    for sheet in xl.sheet_names:
        sheet_lower = sheet.lower()
        if 'diagnostico' in sheet_lower and 'paciente' not in sheet_lower:
            diagnosticos_sheet = sheet
        elif ('paciente' in sheet_lower and 'diagnostico' in sheet_lower) or 'patientdiagnostic' in sheet_lower:
            pacientediagnosticos_sheet = sheet
    
    if not diagnosticos_sheet or not pacientediagnosticos_sheet:
        print("[X] No se encontraron las hojas necesarias")
        print(f"   - Hoja diagnosticos: {diagnosticos_sheet}")
        print(f"   - Hoja pacientediagnosticos: {pacientediagnosticos_sheet}")
        return None
    
    print(f"[OK] Hojas encontradas:")
    print(f"   - Diagnósticos: {diagnosticos_sheet}")
    print(f"   - Paciente Diagnósticos: {pacientediagnosticos_sheet}")
    
    # Cargar ambas hojas
    pacientediagnosticos = pd.read_excel(input_file, sheet_name=pacientediagnosticos_sheet)
    diagnosticos = pd.read_excel(input_file, sheet_name=diagnosticos_sheet)
    
    print(f"[OK] Datos cargados:")
    print(f"   - pacientediagnosticos: {pacientediagnosticos.shape[0]} filas, {pacientediagnosticos.shape[1]} columnas")
    print(f"   - diagnosticos: {diagnosticos.shape[0]} filas, {diagnosticos.shape[1]} columnas")
    
    # Identificar las columnas de ID
    diagnostic_id_col = identify_diagnostic_id_column(diagnosticos, 'diagnosticos')
    patient_diagnostic_id_col = identify_diagnostic_id_column(pacientediagnosticos, 'pacientediagnosticos')
    
    if not diagnostic_id_col or not patient_diagnostic_id_col:
        print("[X] No se pudieron identificar las columnas de ID necesarias")
        return None
    
    print(f"\n[LINK] Realizando MERGE...")
    print(f"   - Columna ID diagnósticos: {diagnostic_id_col}")
    print(f"   - Columna ID paciente-diagnósticos: {patient_diagnostic_id_col}")
    
    # Hacer el merge usando DiagnosticId
    merged_df = pacientediagnosticos.merge(
        diagnosticos, 
        left_on=patient_diagnostic_id_col,
        right_on=diagnostic_id_col,
        how='left',
        suffixes=('', '_diagnostico')
    )
    
    print(f"[OK] Merge completado: {merged_df.shape[0]} filas, {merged_df.shape[1]} columnas")
    
    # Verificar que el merge fue exitoso
    if diagnostic_id_col + '_diagnostico' in merged_df.columns:
        missing_diagnostics = merged_df[diagnostic_id_col + '_diagnostico'].isna().sum()
    else:
        # Si no hay sufijo, buscar una columna que indique datos del diagnóstico
        diag_indicator_cols = [col for col in merged_df.columns if any(word in col.lower() for word in ['name', 'nombre', 'description', 'descripcion']) and col in diagnosticos.columns]
        if diag_indicator_cols:
            missing_diagnostics = merged_df[diag_indicator_cols[0]].isna().sum()
        else:
            missing_diagnostics = 0
    
    if missing_diagnostics > 0:
        print(f"[WARN]  {missing_diagnostics} registros no encontraron diagnóstico correspondiente")
    else:
        print("[OK] Todos los registros tienen diagnóstico correspondiente")
    
    return save_merged_data(merged_df, pacientediagnosticos, diagnosticos, output_file)

def identify_diagnostic_id_column(df, sheet_type):
    """Identifica la columna de DiagnosticId según el tipo de hoja"""
    
    # Buscar columnas que contengan 'diagnosticid'
    diagnostic_cols = [col for col in df.columns if 'diagnosticid' in str(col).lower()]
    
    if sheet_type == 'diagnosticos':
        # Para diagnosticos, buscamos DiagnosticId (sin Patient)
        for col in diagnostic_cols:
            if 'patient' not in str(col).lower():
                return col
    else:
        # Para pacientediagnosticos, puede ser PatientDiagnosticId o DiagnosticId
        # Preferimos DiagnosticId para hacer el match
        for col in diagnostic_cols:
            if 'patient' not in str(col).lower():  # DiagnosticId
                return col
        # Si no encontramos DiagnosticId, usar PatientDiagnosticId
        for col in diagnostic_cols:
            if 'patient' in str(col).lower():
                return col
    
    print(f"[X] No se encontró columna DiagnosticId en {sheet_type}")
    print(f"   Columnas disponibles con 'diagnostic': {diagnostic_cols}")
    return None

def save_merged_data(merged_df, pacientediagnosticos, diagnosticos, output_file):
    """Guarda los datos combinados en Excel"""
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print(f"\n[SAVE] Guardando en: {output_file}")
    
    # Guardar en Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Hoja principal con datos unidos
        merged_df.to_excel(writer, sheet_name='Diagnosticos_Merged', index=False)
        
        # También guardar las hojas originales para referencia
        pacientediagnosticos.to_excel(writer, sheet_name='Original_PacienteDiagnosticos', index=False)
        diagnosticos.to_excel(writer, sheet_name='Original_Diagnosticos', index=False)
    
    print("[OK] Archivo guardado exitosamente")
    
    # Mostrar información del resultado
    print(f"\n[DATA] RESULTADO FINAL:")
    print(f"   - Total de registros: {len(merged_df):,}")
    print(f"   - Total de columnas: {len(merged_df.columns)}")
    
    # Mostrar algunas columnas clave si existen
    key_columns = ['PatientDiagnosticId', 'DiagnosticId', 'PatientId', 'DataDate']
    found_columns = []
    for col in key_columns:
        matching_cols = [c for c in merged_df.columns if col.lower() in c.lower()]
        if matching_cols:
            found_columns.extend(matching_cols[:1])  # Solo tomar la primera coincidencia
    
    if found_columns:
        print(f"   - Columnas principales encontradas:")
        for col in found_columns[:5]:  # Mostrar máximo 5
            print(f"     [CHECK] {col}")
    
    # Estadísticas de calidad del merge
    total_records = len(merged_df)
    records_with_diagnostic_info = 0
    
    # Buscar columnas que indiquen información del diagnóstico
    diagnostic_info_cols = [col for col in merged_df.columns if any(word in col.lower() for word in ['name', 'description', 'nombre', 'descripcion']) and col not in ['Note']]
    
    if diagnostic_info_cols:
        # Contar registros que tienen información del diagnóstico
        records_with_diagnostic_info = merged_df[diagnostic_info_cols[0]].notna().sum()
        match_percentage = (records_with_diagnostic_info / total_records) * 100
        
        print(f"\n[STATS] ESTADÍSTICAS DE CALIDAD:")
        print(f"   - Registros con match exitoso: {records_with_diagnostic_info:,} ({match_percentage:.1f}%)")
        print(f"   - Registros sin diagnóstico: {total_records - records_with_diagnostic_info:,} ({100 - match_percentage:.1f}%)")
    
    print(f"\n[DONE] PROCESO COMPLETADO")
    print(f"[DIR] Archivo: {output_file}")
    
    return merged_df

def main():
    """Función principal"""
    import sys
    
    print("[>>] INICIANDO MERGE DE DIAGNÓSTICOS")
    
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
        merged_df = merge_diagnosticos(input_file, output_dir)
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