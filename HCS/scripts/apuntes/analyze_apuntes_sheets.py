#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Análisis de las hojas de apuntes/notas
Script para analizar la estructura de datos de apuntes en cuvet-v2.xlsx
Campos esperados: NoteId, NoteText, DataDate, PatientId, TenantId, UserIdCreated, IsDeleted, AppointmentId
"""

import pandas as pd
import os
import sys

# Configurar UTF-8 para Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def analyze_excel_sheets(file_path):
    """Analiza las hojas de un archivo Excel buscando datos de apuntes"""
    print(f"\n{'='*60}")
    print(f"ANALIZANDO ARCHIVO: {file_path}")
    print(f"{'='*60}")
    
    try:
        # Leer todas las hojas del archivo
        xl = pd.ExcelFile(file_path)
        print(f"\nHojas disponibles: {xl.sheet_names}")
        
        # Buscar hojas relacionadas con apuntes/notas
        apuntes_sheets = []
        for sheet in xl.sheet_names:
            sheet_lower = sheet.lower()
            if any(keyword in sheet_lower for keyword in ['apuntes', 'nota', 'note', 'notes']):
                apuntes_sheets.append(sheet)
        
        if not apuntes_sheets:
            print("[X] No se encontraron hojas relacionadas con apuntes")
            # Buscar por contenido si no se encuentran por nombre
            print("\n[SEARCH] Buscando hojas por contenido de columnas...")
            for sheet_name in xl.sheet_names:
                try:
                    sample_df = pd.read_excel(file_path, sheet_name=sheet_name, nrows=0)
                    columns = [col.lower() for col in sample_df.columns]
                    if any(keyword in ' '.join(columns) for keyword in ['noteid', 'notetext', 'note']):
                        apuntes_sheets.append(sheet_name)
                        print(f"  [OK] Encontrada por contenido: {sheet_name}")
                except:
                    continue
        
        if not apuntes_sheets:
            print("[X] No se encontraron hojas con datos de apuntes")
            return
        
        print(f"\nHojas de apuntes encontradas: {apuntes_sheets}")
        
        for sheet_name in apuntes_sheets:
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
            
            # Análisis específico de apuntes
            analyze_apuntes_sheet(df, sheet_name)
            
    except Exception as e:
        print(f"[X] Error al analizar el archivo: {e}")

def analyze_apuntes_sheet(df, sheet_name):
    """Análisis específico para hoja de apuntes"""
    print(f"\n[NOTE] ANÁLISIS ESPECÍFICO - APUNTES")
    
    # Campos esperados según la especificación
    expected_fields = [
        'NoteId', 'NoteText', 'DataDate', 'PatientId', 
        'TenantId', 'UserIdCreated', 'IsDeleted', 'AppointmentId'
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
    
    # Análisis del campo ID principal
    if 'NoteId' in found_fields:
        id_col = found_fields['NoteId']
        print(f"\n[KEY] ANÁLISIS DEL CAMPO ID ({id_col}):")
        unique_ids = df[id_col].nunique()
        total_rows = len(df)
        duplicates = total_rows - unique_ids
        null_count = df[id_col].isnull().sum()
        
        print(f"   - IDs únicos: {unique_ids:,}")
        print(f"   - Total filas: {total_rows:,}")
        print(f"   - Duplicados: {duplicates:,}")
        print(f"   - Valores nulos: {null_count:,}")
    else:
        print(f"\n[X] NO SE ENCONTRÓ CAMPO ID PRINCIPAL")
    
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
    
    # Análisis del campo NoteText
    if 'NoteText' in found_fields:
        text_col = found_fields['NoteText']
        print(f"\n[NOTE] ANÁLISIS DE TEXTO DE APUNTES ({text_col}):")
        
        non_empty = df[text_col].notna().sum()
        avg_length = df[text_col].str.len().mean()
        max_length = df[text_col].str.len().max()
        
        print(f"   - Apuntes con texto: {non_empty:,}")
        print(f"   - Longitud promedio: {avg_length:.1f} caracteres")
        print(f"   - Longitud máxima: {max_length}")
        
        # Ejemplos de textos (primeras palabras)
        sample_texts = df[text_col].dropna().head(5)
        print(f"   - Ejemplos de apuntes:")
        for i, text in enumerate(sample_texts, 1):
            preview = str(text)[:100] + "..." if len(str(text)) > 100 else str(text)
            print(f"     {i}. {preview}")
    else:
        print(f"\n[X] NO SE ENCONTRÓ CAMPO NoteText")
    
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
    
    # Análisis de citas (AppointmentId)
    if 'AppointmentId' in found_fields:
        appt_col = found_fields['AppointmentId']
        print(f"\n[LIST] ANÁLISIS DE CITAS ({appt_col}):")
        
        appt_with_id = df[appt_col].notna().sum()
        appt_unique = df[appt_col].nunique()
        
        print(f"   - Apuntes con ID de cita: {appt_with_id:,}")
        print(f"   - Citas únicas: {appt_unique:,}")
    
    # Información de tipos de datos
    print(f"\n[STATS] TIPOS DE DATOS:")
    for col in df.columns[:10]:  # Limitar para no saturar
        dtype = df[col].dtype
        null_count = df[col].isnull().sum()
        print(f"   - {col}: {dtype} (nulos: {null_count:,})")

def main():
    """Función principal"""
    import sys
    
    print("[>>] INICIANDO ANÁLISIS DE APUNTES")
    
    # Verificar argumentos
    if len(sys.argv) >= 4:
        source_file = sys.argv[1]
        client_name = sys.argv[2]
        generation_dir = sys.argv[3]
        
        print(f"[DIR] Archivo fuente: {source_file}")
        print(f"[USER] Cliente: {client_name}")
        print(f"[FOLDER] Directorio generation: {generation_dir}")
        
        file_path = source_file
    else:
        # Modo compatibilidad hacia atrás
        print(f"[WARN]  Usando modo compatibilidad - archivo por defecto")
        file_path = "cuvet-v2.xlsx"
    
    if not os.path.exists(file_path):
        print(f"[X] No se encontró el archivo: {file_path}")
        return
    
    analyze_excel_sheets(file_path)
    print("\n[OK] ANÁLISIS COMPLETADO")

if __name__ == "__main__":
    main()