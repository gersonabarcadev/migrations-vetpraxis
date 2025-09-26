#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script mejorado para organizar los datos de vacunas en hojas separadas
según su estado: todos, sin match, eliminados, y limpios
"""

import pandas as pd
import os
from datetime import datetime

def organize_vacunas_data(input_file=None, output_dir=None):
    """Organiza los datos de vacunas en hojas separadas por estado"""
    
    # Configurar rutas por defecto si no se proporcionan
    if input_file is None:
        base_path = os.path.dirname(os.path.dirname(__file__))
        input_file = os.path.join(base_path, "generation", "vacunas_merged.xlsx")
    else:
        # SIEMPRE buscar el archivo merged en el output_dir cuando se ejecuta desde master script
        if output_dir:
            merged_file = os.path.join(output_dir, "vacunas_merged.xlsx")
            if os.path.exists(merged_file):
                input_file = merged_file
                print(f"[OK] Usando archivo merged: {os.path.basename(input_file)}")
            else:
                print(f"[X] ERROR: No se encontró vacunas_merged.xlsx en {output_dir}")
                return None
    
    if output_dir is None:
        base_path = os.path.dirname(os.path.dirname(__file__))
        output_dir = os.path.join(base_path, "generation")
    
    # Asegurar que el directorio de salida existe
    os.makedirs(output_dir, exist_ok=True)
    
    # Archivo de salida organizado
    output_file = os.path.join(output_dir, "vacunas_organized.xlsx")
    
    print("[DATA] ORGANIZANDO DATOS DE VACUNAS EN HOJAS SEPARADAS")
    print("="*60)
    print(f"[DIR] Archivo origen: {os.path.basename(input_file)}")
    
    # Cargar el archivo merged
    df_all = pd.read_excel(input_file, sheet_name='Vacunas_Merged')
    
    print(f"[OK] Datos cargados: {df_all.shape[0]} filas, {df_all.shape[1]} columnas")
    
    # 1. TODOS LOS REGISTROS (base del merge)
    print(f"\n[LIST] HOJA 1 - TODOS LOS REGISTROS:")
    print(f"   - Total registros del merge: {len(df_all):,}")
    
    # 2. SIN MATCH (registros que no encontraron vacuna)
    print(f"\n[X] HOJA 2 - SIN MATCH:")
    # Los que no tienen match son los que no tienen nombre de la vacuna
    df_no_match = df_all[df_all['Name'].isna()].copy()
    print(f"   - Registros sin match: {len(df_no_match):,}")
    
    if len(df_no_match) > 0:
        missing_ids = df_no_match['VaccineId'].unique()
        print(f"   - IDs de vacunas faltantes: {list(missing_ids)}")
        
        # Mostrar detalles de los registros sin match
        for idx, row in df_no_match.iterrows():
            print(f"     * Paciente {row['PatientId']}, VaccineId {row['VaccineId']}, Fecha {row['DataDate'].strftime('%Y-%m-%d')}")
    
    # 3. ELIMINADOS (IsDeleted = 1)
    print(f"\n[DEL]  HOJA 3 - ELIMINADOS:")
    df_deleted = df_all[df_all['IsDeleted'] == 1].copy()
    print(f"   - Registros eliminados: {len(df_deleted):,}")
    
    if len(df_deleted) > 0:
        deleted_vaccines = df_deleted['Name'].value_counts().head(5)
        print(f"   - Top vacunas eliminadas:")
        for vaccine, count in deleted_vaccines.items():
            if pd.notna(vaccine):
                print(f"     * {vaccine}: {count} registros")
    
    # 4. DATOS LIMPIOS (sin eliminados y con match)
    print(f"\n[STAR] HOJA 4 - DATOS LIMPIOS:")
    df_clean = df_all[(df_all['IsDeleted'] == 0) & (df_all['Name'].notna())].copy()
    
    # Aplicar limpieza adicional
    text_fields = ['Name', 'Description', 'Note']
    for field in text_fields:
        if field in df_clean.columns:
            df_clean[field] = df_clean[field].astype(str).str.strip()
            df_clean[field] = df_clean[field].replace('nan', pd.NA)
    
    # Ordenar por paciente y fecha
    df_clean = df_clean.sort_values(['PatientId', 'DataDate'], ascending=[True, True])
    
    print(f"   - Registros limpios: {len(df_clean):,}")
    print(f"   - Pacientes únicos: {df_clean['PatientId'].nunique():,}")
    print(f"   - Vacunas únicas: {df_clean['VaccineId'].nunique():,}")
    
    if len(df_clean) > 0:
        date_min = df_clean['DataDate'].min()
        date_max = df_clean['DataDate'].max()
        print(f"   - Rango de fechas: {date_min.strftime('%Y-%m-%d')} a {date_max.strftime('%Y-%m-%d')}")
    
    # VERIFICACIÓN DE TOTALES
    print(f"\n[SEARCH] VERIFICACIÓN DE TOTALES:")
    total_check = len(df_no_match) + len(df_deleted) + len(df_clean)
    # Nota: puede haber registros que sean tanto eliminados como sin match
    df_deleted_with_match = df_all[(df_all['IsDeleted'] == 1) & (df_all['Name'].notna())]
    overlap = len(df_deleted_with_match)
    
    print(f"   - Total original: {len(df_all):,}")
    print(f"   - Sin match: {len(df_no_match):,}")
    print(f"   - Eliminados (con match): {len(df_deleted):,}")
    print(f"   - Limpios: {len(df_clean):,}")
    print(f"   - Registros eliminados que SÍ tienen match: {overlap}")
    
    # TOP VACUNAS EN DATOS LIMPIOS
    if len(df_clean) > 0 and 'Name' in df_clean.columns:
        print(f"\n[TOP] TOP 5 VACUNAS EN DATOS LIMPIOS:")
        top_clean = df_clean['Name'].value_counts().head(5)
        for i, (vaccine, count) in enumerate(top_clean.items(), 1):
            if pd.notna(vaccine):
                print(f"   {i}. {vaccine}: {count} veces")
    
    # GUARDAR ARCHIVO ORGANIZADO
    print(f"\n[SAVE] Guardando archivo organizado...")
    
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        
        # Hoja 1: Todos los registros
        df_all.to_excel(writer, sheet_name='01_Todos_Registros', index=False)
        
        # Hoja 2: Sin match
        df_no_match.to_excel(writer, sheet_name='02_Sin_Match', index=False)
        
        # Hoja 3: Eliminados
        df_deleted.to_excel(writer, sheet_name='03_Eliminados', index=False)
        
        # Hoja 4: Datos limpios
        df_clean.to_excel(writer, sheet_name='04_Datos_Limpios', index=False)
        
        # Hoja 5: Resumen estadístico
        stats_data = {
            'Categoría': [
                'Total registros (merge)',
                'Registros sin match',
                'Registros eliminados',
                'Registros limpios',
                'Pacientes únicos (limpios)',
                'Vacunas únicas (limpios)',
                'Fecha procesamiento'
            ],
            'Cantidad': [
                len(df_all),
                len(df_no_match),
                len(df_deleted),
                len(df_clean),
                df_clean['PatientId'].nunique() if len(df_clean) > 0 else 0,
                df_clean['VaccineId'].nunique() if len(df_clean) > 0 else 0,
                datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            ]
        }
        stats_df = pd.DataFrame(stats_data)
        stats_df.to_excel(writer, sheet_name='05_Resumen_Estadistico', index=False)
        
        # Hoja 6: Top procedimientos limpios
        if len(df_clean) > 0 and 'Name' in df_clean.columns:
            top_df = df_clean['Name'].value_counts().head(20).reset_index()
            top_df.columns = ['Procedimiento', 'Cantidad']
            top_df.to_excel(writer, sheet_name='06_Top_Procedimientos', index=False)
    
    print(f"[OK] Archivo guardado: {os.path.basename(output_file)}")
    print(f"\n[DATA] RESUMEN FINAL:")
    print(f"   [LIST] Hoja 1: Todos los registros ({len(df_all):,})")
    print(f"   [X] Hoja 2: Sin match ({len(df_no_match):,})")
    print(f"   [DEL]  Hoja 3: Eliminados ({len(df_deleted):,})")
    print(f"   [STAR] Hoja 4: Datos limpios ({len(df_clean):,})")
    print(f"   [STATS] Hoja 5: Resumen estadístico")
    print(f"   [TOP] Hoja 6: Top procedimientos")
    
    print(f"\n[DONE] ORGANIZACIÓN COMPLETADA")
    print(f"[DIR] Archivo: {output_file}")
    
    return {
        'all': df_all,
        'no_match': df_no_match,
        'deleted': df_deleted,
        'clean': df_clean
    }

def main():
    """Función principal"""
    import sys
    
    print("[>>] ORGANIZANDO DATOS DE VACUNAS")
    
    # Verificar argumentos
    if len(sys.argv) >= 4:
        source_file = sys.argv[1]
        client_name = sys.argv[2]
        generation_dir = sys.argv[3]
        
        print(f"[DIR] Archivo fuente original: {source_file}")
        print(f"[USER] Cliente: {client_name}")
        print(f"[FOLDER] Directorio generation: {generation_dir}")
        
        input_file = source_file  # Para buscar el merged
        output_dir = generation_dir
    else:
        print("[WARN]  Usando modo compatibilidad - rutas por defecto")
        input_file = None
        output_dir = None
    
    try:
        result = organize_vacunas_data(input_file, output_dir)
        print(f"\n[OK] Proceso completado exitosamente")
        print(f"[DATA] Datos organizados en hojas separadas para mejor análisis")
    except Exception as e:
        print(f"[X] Error durante la organización: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()