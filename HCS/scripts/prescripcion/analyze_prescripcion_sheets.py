#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de las hojas de prescripciones
Script para analizar la estructura de datos de prescripciones en cuvet-v2.xlsx
Campos esperados: PrescriptionId, Notes, DataDate, TenantIdCreated, PatientId, UserIdCreated, IsDeleted, 
AppointmentId, PrescriptionMedicationId, MedicationId, RequestedUsage, AmountToBuy, ProductId, 
ProductQuantity, Name, Description, ForPatientType, IsStock, SourceUrl
"""

import pandas as pd
import os

def analyze_excel_sheets(file_path):
    """Analiza las hojas de un archivo Excel buscando datos de prescripciones"""
    print(f"\n{'='*60}")
    print(f"ANALIZANDO ARCHIVO: {file_path}")
    print(f"{'='*60}")
    
    try:
        # Leer todas las hojas del archivo
        xl = pd.ExcelFile(file_path)
        print(f"\nHojas disponibles: {xl.sheet_names}")
        
        # Buscar hojas relacionadas con prescripciones
        prescription_sheets = []
        for sheet in xl.sheet_names:
            sheet_lower = sheet.lower()
            if any(keyword in sheet_lower for keyword in ['prescription', 'prescripcion', 'receta', 'medicamento']):
                prescription_sheets.append(sheet)
        
        if not prescription_sheets:
            print("[X] No se encontraron hojas relacionadas con prescripciones")
            # Buscar por contenido si no se encuentran por nombre
            print("\n[SEARCH] Buscando hojas por contenido de columnas...")
            for sheet_name in xl.sheet_names:
                try:
                    sample_df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=0)
                    columns = [col.lower() for col in sample_df.columns]
                    if any(keyword in ' '.join(columns) for keyword in ['prescriptionid', 'prescriptionmedicationid', 'requestedusage', 'amounttobuy']):
                        prescription_sheets.append(sheet_name)
                        print(f"  [OK] Encontrada por contenido: {sheet_name}")
                except:
                    continue
        
        if not prescription_sheets:
            print("[X] No se encontraron hojas con datos de prescripciones")
            return
        
        print(f"\nHojas de prescripciones encontradas: {prescription_sheets}")
        
        for sheet_name in prescription_sheets:
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
            
            # Análisis específico de prescripciones
            analyze_prescription_sheet(df, sheet_name)
            
    except Exception as e:
        print(f"[X] Error al analizar el archivo: {e}")

def analyze_prescription_sheet(df, sheet_name):
    """Análisis específico para hoja de prescripciones"""
    print(f"\n[MED] ANÁLISIS ESPECÍFICO - PRESCRIPCIONES")
    
    # Campos esperados según la especificación
    expected_fields = [
        'PrescriptionId', 'Notes', 'DataDate', 'TenantIdCreated', 'PatientId', 
        'UserIdCreated', 'IsDeleted', 'AppointmentId', 'PrescriptionMedicationId', 
        'MedicationId', 'RequestedUsage', 'AmountToBuy', 'ProductId', 'ProductQuantity', 
        'Name', 'Description', 'ForPatientType', 'IsStock', 'SourceUrl'
    ]
    
    # Verificar campos esperados
    print(f"\n[SEARCH] VERIFICACIÓN DE CAMPOS ESPERADOS:")
    found_fields = {}
    missing_fields = []
    
    for expected_field in expected_fields:
        # Buscar campo exacto o similar
        matching_cols = [col for col in df.columns if expected_field.lower() in col.lower()]
        if matching_cols:
            found_fields[expected_field] = matching_cols[0]
            print(f"   [OK] {expected_field} -> {matching_cols[0]}")
        else:
            missing_fields.append(expected_field)
            print(f"   [X] {expected_field} -> NO ENCONTRADO")
    
    print(f"\n[STATS] RESUMEN DE CAMPOS:")
    print(f"   - Campos encontrados: {len(found_fields)}/{len(expected_fields)}")
    print(f"   - Campos faltantes: {missing_fields}")
    
    # Análisis del campo ID principal (PrescriptionMedicationId)
    if 'PrescriptionMedicationId' in found_fields:
        id_col = found_fields['PrescriptionMedicationId']
        print(f"\n[KEY] ANÁLISIS DEL CAMPO ID PRINCIPAL ({id_col}):")
        unique_ids = df[id_col].nunique()
        total_rows = len(df)
        duplicates = total_rows - unique_ids
        null_count = df[id_col].isnull().sum()
        
        print(f"   - IDs únicos: {unique_ids:,}")
        print(f"   - Total filas: {total_rows:,}")
        print(f"   - Duplicados: {duplicates:,}")
        print(f"   - Valores nulos: {null_count:,}")
    else:
        print(f"\n[X] NO SE ENCONTRÓ CAMPO PrescriptionMedicationId")
    
    # Análisis del campo PatientId
    if 'PatientId' in found_fields:
        patient_col = found_fields['PatientId']
        print(f"\n[PET] ANÁLISIS DE PACIENTES ({patient_col}):")
        unique_patients = df[patient_col].nunique()
        null_patients = df[patient_col].isnull().sum()
        
        print(f"   - Pacientes únicos: {unique_patients:,}")
        print(f"   - Valores nulos: {null_patients:,}")
        
        if unique_patients > 0:
            # Mostrar algunos pacientes de ejemplo
            sample_patients = df[patient_col].dropna().unique()[:5]
            print(f"   - Ejemplos de PatientId: {list(sample_patients)}")
    else:
        print(f"\n[X] NO SE ENCONTRÓ CAMPO PatientId")
    
    # Análisis de medicamentos (Name)
    if 'Name' in found_fields:
        name_col = found_fields['Name']
        print(f"\n[MED] ANÁLISIS DE MEDICAMENTOS ({name_col}):")
        
        unique_meds = df[name_col].nunique()
        null_meds = df[name_col].isnull().sum()
        print(f"   - Medicamentos únicos: {unique_meds:,}")
        print(f"   - Valores nulos: {null_meds:,}")
        
        if unique_meds > 0:
            top_meds = df[name_col].value_counts().head(10)
            print(f"   - Top 10 medicamentos:")
            for med, count in top_meds.items():
                if pd.notna(med):
                    print(f"     * {med}: {count:,} prescripciones")
    else:
        print(f"\n[X] NO SE ENCONTRÓ CAMPO Name (medicamentos)")
    
    # Análisis de cantidades y uso
    print(f"\n[BOX] ANÁLISIS DE CANTIDADES Y USO:")
    
    if 'AmountToBuy' in found_fields:
        amount_col = found_fields['AmountToBuy']
        amount_values = df[amount_col].notna().sum()
        print(f"   - AmountToBuy: {amount_values:,} valores")
        if amount_values > 0:
            try:
                numeric_amounts = pd.to_numeric(df[amount_col], errors='coerce')
                valid_amounts = numeric_amounts.notna().sum()
                if valid_amounts > 0:
                    stats = numeric_amounts.describe()
                    print(f"     Min: {stats['min']}, Max: {stats['max']}, Promedio: {stats['mean']:.2f}")
            except:
                print(f"     Valores no numéricos encontrados")
    
    if 'RequestedUsage' in found_fields:
        usage_col = found_fields['RequestedUsage']
        usage_values = df[usage_col].notna().sum()
        print(f"   - RequestedUsage: {usage_values:,} valores")
        if usage_values > 0:
            avg_length = df[usage_col].astype(str).str.len().mean()
            print(f"     Longitud promedio: {avg_length:.1f} caracteres")
    
    if 'Description' in found_fields:
        desc_col = found_fields['Description']
        desc_values = df[desc_col].notna().sum()
        print(f"   - Description: {desc_values:,} valores")
        if desc_values > 0:
            avg_length = df[desc_col].astype(str).str.len().mean()
            print(f"     Longitud promedio: {avg_length:.1f} caracteres")
    
    # Análisis de fechas
    if 'DataDate' in found_fields:
        date_col = found_fields['DataDate']
        print(f"\n[DATE] ANÁLISIS DE FECHAS ({date_col}):")
        
        try:
            date_series = pd.to_datetime(df[date_col])
            valid_dates = date_series.notna().sum()
            print(f"   - Fechas válidas: {valid_dates:,}")
            
            if valid_dates > 0:
                min_date = date_series.min()
                max_date = date_series.max()
                print(f"   - Rango: {min_date.strftime('%Y-%m-%d')} a {max_date.strftime('%Y-%m-%d')}")
                
                # Distribución por año
                years = date_series.dt.year.value_counts().sort_index()
                print(f"   - Distribución por año:")
                for year, count in years.head(5).items():
                    print(f"     * {year}: {count:,} registros")
        except:
            print(f"   [X] Error al procesar fechas")
    
    # Análisis de eliminados
    if 'IsDeleted' in found_fields:
        deleted_col = found_fields['IsDeleted']
        print(f"\n[DEL]  ANÁLISIS DE ELIMINADOS ({deleted_col}):")
        
        deleted_count = (df[deleted_col] == 1).sum()
        active_count = (df[deleted_col] == 0).sum()
        
        print(f"   - Registros activos: {active_count:,}")
        print(f"   - Registros eliminados: {deleted_count:,}")
        print(f"   - Porcentaje eliminados: {(deleted_count/len(df)*100):.1f}%")
    
    # Análisis de notas existentes
    if 'Notes' in found_fields:
        notes_col = found_fields['Notes']
        print(f"\n[NOTE] ANÁLISIS DE NOTAS EXISTENTES ({notes_col}):")
        
        notes_count = df[notes_col].notna().sum()
        print(f"   - Registros con notas: {notes_count:,}")
        if notes_count > 0:
            avg_length = df[notes_col].astype(str).str.len().mean()
            print(f"   - Longitud promedio: {avg_length:.1f} caracteres")
    
    # Información de tipos de datos
    print(f"\n[STATS] TIPOS DE DATOS:")
    for i, col in enumerate(df.columns):
        if i >= 15:  # Limitar para no saturar
            break
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        print(f"   - {col}: {dtype} (nulos: {null_count:,})")

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
        file_path = os.path.join(base_path, "backup", "cuvet-v2.xlsx")
        
        print(f"[WARN]  Usando modo compatibilidad - archivo por defecto")
    
    if not os.path.exists(file_path):
        print(f"[X] No se encontró el archivo: {file_path}")
        return
    
    print("[>>] INICIANDO ANÁLISIS DE PRESCRIPCIONES")
    analyze_excel_sheets(file_path)
    print("\n[OK] ANÁLISIS COMPLETADO")

if __name__ == "__main__":
    main()