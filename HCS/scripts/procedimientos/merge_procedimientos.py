#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para hacer MERGE entre procedimientos y pacienteprocedimientos
Basado en el script de merge de vacunas
"""

import pandas as pd
import os

def merge_procedimientos(input_file=None, output_dir=None):
    """Une las hojas procedimientos y pacienteprocedimientos"""
    
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
    output_file = os.path.join(output_dir, "procedimientos_merged.xlsx")
    
    print("[PROC] Cargando datos...")
    
    # Primero verificar qué hojas están disponibles
    xl = pd.ExcelFile(input_file)
    print(f"[LIST] Hojas disponibles: {xl.sheet_names}")
    
    # Buscar las hojas correctas
    procedimientos_sheet = None
    pacienteprocedimientos_sheet = None
    
    for sheet in xl.sheet_names:
        sheet_lower = sheet.lower()
        if 'procedimiento' in sheet_lower and 'paciente' not in sheet_lower:
            procedimientos_sheet = sheet
        elif ('paciente' in sheet_lower and 'procedimiento' in sheet_lower) or 'patientintervention' in sheet_lower:
            pacienteprocedimientos_sheet = sheet
    
    if not procedimientos_sheet or not pacienteprocedimientos_sheet:
        print("[X] No se encontraron las hojas necesarias")
        print(f"   - Hoja procedimientos: {procedimientos_sheet}")
        print(f"   - Hoja pacienteprocedimientos: {pacienteprocedimientos_sheet}")
        
        # Intentar cargar la primera hoja para ver su estructura
        if xl.sheet_names:
            sample_sheet = xl.sheet_names[0]
            sample_df = pd.read_excel(input_file, sheet_name=sample_sheet)
            print(f"\n[SEARCH] Estructura de la hoja '{sample_sheet}':")
            print(f"   - Dimensiones: {sample_df.shape}")
            print(f"   - Columnas: {list(sample_df.columns)}")
            
            # Buscar patrones en las columnas
            intervention_cols = [col for col in sample_df.columns if 'intervention' in str(col).lower()]
            patient_cols = [col for col in sample_df.columns if 'patient' in str(col).lower()]
            
            if intervention_cols or patient_cols:
                print(f"   - Columnas con 'intervention': {intervention_cols}")
                print(f"   - Columnas con 'patient': {patient_cols}")
                
                # Si encontramos ambos tipos de columnas, probablemente están en la misma hoja
                if intervention_cols and patient_cols:
                    print("\n[IDEA] Parece que los datos están en una sola hoja combinada")
                    return process_combined_sheet(input_file, sample_sheet, output_file, sample_df)
        
        return None
    
    print(f"[OK] Hojas encontradas:")
    print(f"   - Procedimientos: {procedimientos_sheet}")
    print(f"   - Paciente Procedimientos: {pacienteprocedimientos_sheet}")
    
    # Cargar ambas hojas
    pacienteprocedimientos = pd.read_excel(input_file, sheet_name=pacienteprocedimientos_sheet)
    procedimientos = pd.read_excel(input_file, sheet_name=procedimientos_sheet)
    
    print(f"[OK] Datos cargados:")
    print(f"   - pacienteprocedimientos: {pacienteprocedimientos.shape[0]} filas, {pacienteprocedimientos.shape[1]} columnas")
    print(f"   - procedimientos: {procedimientos.shape[0]} filas, {procedimientos.shape[1]} columnas")
    
    # Identificar las columnas de ID
    intervention_id_col = identify_intervention_id_column(procedimientos, 'procedimientos')
    patient_intervention_id_col = identify_intervention_id_column(pacienteprocedimientos, 'pacienteprocedimientos')
    
    if not intervention_id_col or not patient_intervention_id_col:
        print("[X] No se pudieron identificar las columnas de ID necesarias")
        return None
    
    print(f"\n[MERGE] Realizando MERGE...")
    print(f"   - Columna ID procedimientos: {intervention_id_col}")
    print(f"   - Columna ID paciente-procedimientos: {patient_intervention_id_col}")
    
    # Hacer el merge usando InterventionId
    merged_df = pacienteprocedimientos.merge(
        procedimientos, 
        left_on=patient_intervention_id_col,
        right_on=intervention_id_col,
        how='left',
        suffixes=('', '_procedimiento')
    )
    
    print(f"[OK] Merge completado: {merged_df.shape[0]} filas, {merged_df.shape[1]} columnas")
    
    # Verificar que el merge fue exitoso
    if intervention_id_col + '_procedimiento' in merged_df.columns:
        missing_procedures = merged_df[intervention_id_col + '_procedimiento'].isna().sum()
    else:
        # Si no hay sufijo, buscar una columna que indique datos del procedimiento
        proc_indicator_cols = [col for col in merged_df.columns if any(word in col.lower() for word in ['name', 'nombre', 'description', 'descripcion']) and col in procedimientos.columns]
        if proc_indicator_cols:
            missing_procedures = merged_df[proc_indicator_cols[0]].isna().sum()
        else:
            missing_procedures = 0
    
    if missing_procedures > 0:
        print(f"[WARN]  {missing_procedures} registros no encontraron procedimiento correspondiente")
    else:
        print("[OK] Todos los registros tienen procedimiento correspondiente")
    
    return save_merged_data(merged_df, pacienteprocedimientos, procedimientos, output_file)

def process_combined_sheet(input_file, sheet_name, output_file, df):
    """Procesa una hoja que ya tiene los datos combinados"""
    print(f"\n[PROC] Procesando hoja combinada: {sheet_name}")
    
    # Crear directorio de salida si no existe
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print(f"[SAVE] Guardando en: {output_file}")
    
    # Guardar en Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Procedimientos_Combined', index=False)
    
    print("[OK] Archivo guardado exitosamente")
    print(f"\n[DATA] RESULTADO:")
    print(f"   - Total de registros: {len(df):,}")
    print(f"   - Total de columnas: {len(df.columns)}")
    
    return df

def identify_intervention_id_column(df, sheet_type):
    """Identifica la columna de InterventionId según el tipo de hoja"""
    
    # Buscar columnas que contengan 'interventionid'
    intervention_cols = [col for col in df.columns if 'interventionid' in str(col).lower()]
    
    if sheet_type == 'procedimientos':
        # Para procedimientos, buscamos InterventionId (sin Patient)
        for col in intervention_cols:
            if 'patient' not in str(col).lower():
                return col
    else:
        # Para pacienteprocedimientos, puede ser PatientInterventionId o InterventionId
        # Preferimos InterventionId para hacer el match
        for col in intervention_cols:
            if 'patient' not in str(col).lower():  # InterventionId
                return col
        # Si no encontramos InterventionId, usar PatientInterventionId
        for col in intervention_cols:
            if 'patient' in str(col).lower():
                return col
    
    print(f"[X] No se encontró columna InterventionId en {sheet_type}")
    print(f"   Columnas disponibles con 'intervention': {intervention_cols}")
    return None

def save_merged_data(merged_df, pacienteprocedimientos, procedimientos, output_file):
    """Guarda los datos combinados en Excel"""
    
    # Crear directorio si no existe
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    print(f"\n[SAVE] Guardando en: {output_file}")
    
    # Guardar en Excel
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Hoja principal con datos unidos
        merged_df.to_excel(writer, sheet_name='Procedimientos_Merged', index=False)
        
        # También guardar las hojas originales para referencia
        pacienteprocedimientos.to_excel(writer, sheet_name='Original_PacienteProcedimientos', index=False)
        procedimientos.to_excel(writer, sheet_name='Original_Procedimientos', index=False)
    
    print("[OK] Archivo guardado exitosamente")
    
    # Mostrar información del resultado
    print(f"\n[DATA] RESULTADO FINAL:")
    print(f"   - Total de registros: {len(merged_df):,}")
    print(f"   - Total de columnas: {len(merged_df.columns)}")
    
    # Mostrar algunas columnas clave si existen
    key_columns = ['PatientInterventionId', 'InterventionId', 'PatientId', 'DataDate']
    found_columns = []
    for col in key_columns:
        matching_cols = [c for c in merged_df.columns if col.lower() in c.lower()]
        if matching_cols:
            found_columns.extend(matching_cols[:1])  # Solo tomar la primera coincidencia
    
    if found_columns:
        print(f"   - Columnas principales encontradas:")
        for col in found_columns[:5]:  # Mostrar máximo 5
            print(f"     [OK] {col}")
    
    print(f"\n[DONE] PROCESO COMPLETADO")
    print(f"[DIR] Archivo: {output_file}")
    
    return merged_df

def main():
    """Función principal"""
    import sys
    
    print("[>>] INICIANDO MERGE DE PROCEDIMIENTOS")
    
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
        merged_df = merge_procedimientos(input_file, output_dir)
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