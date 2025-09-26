#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para organizar los datos de control en hojas separadas
según su estado: todos, eliminados, y limpios
Los datos de control no requieren merge ya que están completos en una sola hoja
"""

import pandas as pd
import os
from datetime import datetime

def organize_datosdecontrol_data(input_file=None, output_dir=None):
    """Organiza los datos de control en hojas separadas por estado"""
    
    # Configurar rutas por defecto si no se proporcionan
    if input_file is None:
        base_path = os.path.dirname(os.path.dirname(__file__))
        input_file = os.path.join(base_path, "backup", "cuvet-v2.xlsx")
    
    if output_dir is None:
        base_path = os.path.dirname(os.path.dirname(__file__))
        output_dir = os.path.join(base_path, "generation")
    
    # Asegurar que el directorio de salida existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Archivo de salida organizado
    output_file = os.path.join(output_dir, "datosdecontrol_organized.xlsx")
    
    print("[DATA] ORGANIZANDO DATOS DE CONTROL EN HOJAS SEPARADAS")
    print("="*60)
    print(f"[DIR] Archivo origen: {os.path.basename(input_file)}")
    
    # Identificar la hoja de datos de control
    try:
        xl = pd.ExcelFile(input_file)
        control_sheet = None
        
        # Buscar hoja por nombre
        for sheet in xl.sheet_names:
            sheet_lower = sheet.lower()
            if any(keyword in sheet_lower for keyword in ['control', 'data', 'generic', 'controldata', 'controldatageneric']):
                control_sheet = sheet
                break
        
        # Si no se encuentra por nombre, buscar por columnas
        if not control_sheet:
            print("[SEARCH] Buscando hoja por contenido de columnas...")
            for sheet_name in xl.sheet_names:
                try:
                    sample_df = pd.read_excel(input_file, sheet_name=sheet_name, nrows=0)
                    columns = [col.lower() for col in sample_df.columns]
                    if any(keyword in ' '.join(columns) for keyword in ['controldatagenericid', 'controldata', 'valuenumber', 'valuestring']):
                        control_sheet = sheet_name
                        print(f"  [OK] Encontrada: {sheet_name}")
                        break
                except:
                    continue
        
        if not control_sheet:
            print("[X] No se encontró hoja de datos de control")
            return
        
        print(f"[LIST] Hoja de datos de control: {control_sheet}")
        
    except Exception as e:
        print(f"[X] Error al identificar hoja: {e}")
        return
    
    # Cargar los datos de control
    df_all = pd.read_excel(input_file, sheet_name=control_sheet)
    
    print(f"[OK] Datos cargados: {df_all.shape[0]} filas, {df_all.shape[1]} columnas")
    print(f"[LIST] Columnas: {list(df_all.columns)}")
    
    # 1. TODOS LOS REGISTROS (datos originales)
    print(f"\n[LIST] HOJA 1 - TODOS LOS REGISTROS:")
    print(f"   - Total registros: {len(df_all):,}")
    
    # 2. ELIMINADOS (IsDeleted = 1)
    print(f"\n[DEL]  HOJA 2 - ELIMINADOS:")
    if 'IsDeleted' in df_all.columns:
        df_deleted = df_all[df_all['IsDeleted'] == 1].copy()
        print(f"   - Registros eliminados: {len(df_deleted):,}")
        
        if len(df_deleted) > 0:
            # Analizar tipos de control eliminados
            if 'Key' in df_deleted.columns:
                deleted_keys = df_deleted['Key'].value_counts().head(5)
                print(f"   - Top tipos de control eliminados:")
                for key_type, count in deleted_keys.items():
                    if pd.notna(key_type):
                        print(f"     * {key_type}: {count} registros")
    else:
        df_deleted = pd.DataFrame()  # DataFrame vacío si no existe IsDeleted
        print(f"   - No se encontró columna IsDeleted")
    
    # 3. DATOS LIMPIOS (sin eliminados)
    print(f"\n[STAR] HOJA 3 - DATOS LIMPIOS:")
    if 'IsDeleted' in df_all.columns:
        df_clean = df_all[df_all['IsDeleted'] == 0].copy()
    else:
        df_clean = df_all.copy()  # Si no existe IsDeleted, todos son limpios
    
    # Aplicar limpieza adicional
    text_fields = ['Key', 'ValueString', 'Unit', 'UnitSystem']
    for field in text_fields:
        if field in df_clean.columns:
            df_clean[field] = df_clean[field].astype(str).str.strip()
            df_clean[field] = df_clean[field].replace('nan', pd.NA)
    
    # Ordenar por paciente y fecha
    sort_columns = []
    if 'PatientId' in df_clean.columns:
        sort_columns.append('PatientId')
    if 'DataDate' in df_clean.columns:
        sort_columns.append('DataDate')
    if 'Key' in df_clean.columns:
        sort_columns.append('Key')
    
    if sort_columns:
        df_clean = df_clean.sort_values(sort_columns, ascending=True)
    
    print(f"   - Registros limpios: {len(df_clean):,}")
    
    if 'PatientId' in df_clean.columns:
        print(f"   - Pacientes únicos: {df_clean['PatientId'].nunique():,}")
    
    if 'Key' in df_clean.columns:
        print(f"   - Tipos de control únicos: {df_clean['Key'].nunique():,}")
    
    if 'DataDate' in df_clean.columns and len(df_clean) > 0:
        try:
            date_series = pd.to_datetime(df_clean['DataDate'])
            valid_dates = date_series.notna()
            if valid_dates.sum() > 0:
                date_min = date_series[valid_dates].min()
                date_max = date_series[valid_dates].max()
                print(f"   - Rango de fechas: {date_min.strftime('%Y-%m-%d')} a {date_max.strftime('%Y-%m-%d')}")
        except:
            print(f"   - Error al procesar fechas")
    
    # VERIFICACIÓN DE TOTALES
    print(f"\n[SEARCH] VERIFICACIÓN DE TOTALES:")
    print(f"   - Total original: {len(df_all):,}")
    print(f"   - Eliminados: {len(df_deleted):,}")
    print(f"   - Limpios: {len(df_clean):,}")
    
    # Verificar suma
    expected_total = len(df_deleted) + len(df_clean)
    if 'IsDeleted' in df_all.columns and expected_total == len(df_all):
        print(f"   [OK] Verificación correcta: {len(df_deleted)} + {len(df_clean)} = {len(df_all)}")
    else:
        print(f"   [WARN]  Sin columna IsDeleted o discrepancia en totales")
    
    # ANÁLISIS DE TIPOS DE CONTROL EN DATOS LIMPIOS
    if len(df_clean) > 0 and 'Key' in df_clean.columns:
        print(f"\n[TOP] TOP 10 TIPOS DE CONTROL EN DATOS LIMPIOS:")
        top_clean = df_clean['Key'].value_counts().head(10)
        for i, (key_type, count) in enumerate(top_clean.items(), 1):
            if pd.notna(key_type):
                print(f"   {i}. {key_type}: {count:,} registros")
    
    # ANÁLISIS DE VALORES
    if len(df_clean) > 0:
        print(f"\n[SAVE] ANÁLISIS DE VALORES EN DATOS LIMPIOS:")
        
        if 'ValueNumber' in df_clean.columns:
            numeric_count = df_clean['ValueNumber'].notna().sum()
            print(f"   - Valores numéricos: {numeric_count:,}")
            
        if 'ValueString' in df_clean.columns:
            string_count = df_clean['ValueString'].notna().sum()
            print(f"   - Valores de texto: {string_count:,}")
        
        # Distribución por tipo de valor
        if 'ValueNumber' in df_clean.columns and 'ValueString' in df_clean.columns:
            both_count = (df_clean['ValueNumber'].notna() & df_clean['ValueString'].notna()).sum()
            only_numeric = (df_clean['ValueNumber'].notna() & df_clean['ValueString'].isna()).sum()
            only_string = (df_clean['ValueNumber'].isna() & df_clean['ValueString'].notna()).sum()
            neither = (df_clean['ValueNumber'].isna() & df_clean['ValueString'].isna()).sum()
            
            print(f"   - Solo numérico: {only_numeric:,}")
            print(f"   - Solo texto: {only_string:,}")
            print(f"   - Ambos valores: {both_count:,}")
            print(f"   - Sin valores: {neither:,}")
    
    # GUARDAR ARCHIVO ORGANIZADO
    print(f"\n[SAVE] Guardando archivo organizado...")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        
        # Hoja 1: Todos los registros
        df_all.to_excel(writer, sheet_name='01_Todos_Registros', index=False)
        
        # Hoja 2: Eliminados
        df_deleted.to_excel(writer, sheet_name='02_Eliminados', index=False)
        
        # Hoja 3: Datos limpios
        df_clean.to_excel(writer, sheet_name='03_Datos_Limpios', index=False)
        
        # Hoja 4: Resumen estadístico
        stats_data = {
            'Categoría': [
                'Total registros',
                'Registros eliminados',
                'Registros limpios',
                'Pacientes únicos (limpios)',
                'Tipos de control únicos (limpios)',
                'Valores numéricos (limpios)',
                'Valores de texto (limpios)',
                'Fecha procesamiento'
            ],
            'Cantidad': [
                len(df_all),
                len(df_deleted),
                len(df_clean),
                df_clean['PatientId'].nunique() if 'PatientId' in df_clean.columns and len(df_clean) > 0 else 0,
                df_clean['Key'].nunique() if 'Key' in df_clean.columns and len(df_clean) > 0 else 0,
                df_clean['ValueNumber'].notna().sum() if 'ValueNumber' in df_clean.columns and len(df_clean) > 0 else 0,
                df_clean['ValueString'].notna().sum() if 'ValueString' in df_clean.columns and len(df_clean) > 0 else 0,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='04_Resumen_Estadistico', index=False)
        
        # Hoja 5: Top tipos de control
        if len(df_clean) > 0 and 'Key' in df_clean.columns:
            top_df = df_clean['Key'].value_counts().head(20).reset_index()
            top_df.columns = ['Tipo_Control', 'Cantidad']
            top_df.to_excel(writer, sheet_name='05_Top_Tipos_Control', index=False)
        
        # Hoja 6: Análisis por paciente (top pacientes con más controles)
        if len(df_clean) > 0 and 'PatientId' in df_clean.columns:
            patient_stats = df_clean.groupby('PatientId').agg({
                'ControlDataGenericId': 'count' if 'ControlDataGenericId' in df_clean.columns else 'size',
                'Key': 'nunique' if 'Key' in df_clean.columns else lambda x: 0,
                'DataDate': ['min', 'max'] if 'DataDate' in df_clean.columns else lambda x: None
            }).reset_index()
            
            # Aplanar columnas multinivel si es necesario
            if isinstance(patient_stats.columns, pd.MultiIndex):
                patient_stats.columns = ['PatientId', 'Total_Controles', 'Tipos_Control_Unicos', 'Fecha_Min', 'Fecha_Max']
            else:
                patient_stats.columns = ['PatientId', 'Total_Controles', 'Tipos_Control_Unicos']
            
            # Ordenar por total de controles y tomar top 100
            patient_stats = patient_stats.sort_values('Total_Controles', ascending=False).head(100)
            patient_stats.to_excel(writer, sheet_name='06_Top_Pacientes', index=False)
    
    print(f"[OK] Archivo guardado: {os.path.basename(output_file)}")
    print(f"\n[DATA] RESUMEN FINAL:")
    print(f"   [LIST] Hoja 1: Todos los registros ({len(df_all):,})")
    print(f"   [DEL]  Hoja 2: Eliminados ({len(df_deleted):,})")
    print(f"   [STAR] Hoja 3: Datos limpios ({len(df_clean):,})")
    print(f"   [STATS] Hoja 4: Resumen estadístico")
    print(f"   [TOP] Hoja 5: Top tipos de control")
    print(f"   [USERS] Hoja 6: Top pacientes")
    
    print(f"\n[DONE] ORGANIZACIÓN COMPLETADA")
    print(f"[DIR] Archivo: {output_file}")
    
    return {
        'all': df_all,
        'deleted': df_deleted,
        'clean': df_clean
    }

def main():
    """Función principal"""
    import sys
    
    print("[>>] ORGANIZANDO DATOS DE CONTROL")
    
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
        result = organize_datosdecontrol_data(input_file, output_dir)
        print(f"\n[OK] Proceso completado exitosamente")
        print(f"[DATA] Datos organizados en hojas separadas para mejor análisis")
    except Exception as e:
        print(f"[X] Error durante la organización: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()