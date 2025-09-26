#!/usr/bin/env python3
"""
Análisis detallado de clientes no importados
Investigar por qué 397 clientes no se importaron
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def analyze_missing_clients():
    """Analizar clientes que no se importaron"""
    print("🔍 ANÁLISIS DE CLIENTES NO IMPORTADOS")
    print("=" * 45)
    
    # Cargar datos originales
    source_file = "/Users/enrique/Proyectos/imports/source/cuvet-v2.xlsx"
    df_original = pd.read_excel(source_file, sheet_name='pacientes amos', engine='openpyxl')
    
    # Filtrar solo clientes (PatientType = 0)
    df_clients = df_original[df_original['PatientType'] == 0].copy()
    
    print(f"📊 Clientes originales: {len(df_clients):,}")
    
    # Cargar datos importados
    import_file = "/Users/enrique/Proyectos/imports/source/clients_from_vetpraxis_after_import_v2.csv"
    df_imported = pd.read_csv(import_file, sep=';', quotechar='"', skipinitialspace=True, low_memory=False)
    
    print(f"📊 Clientes importados: {len(df_imported):,}")
    
    # Convertir import_client_id a numérico
    df_imported['import_client_id_numeric'] = pd.to_numeric(df_imported['import_client_id'], errors='coerce')
    
    # Identificar IDs no importados
    original_ids = set(df_clients['PatientId'].dropna())
    imported_ids = set(df_imported['import_client_id_numeric'].dropna())
    
    missing_ids = original_ids - imported_ids
    print(f"🔍 Clientes no importados: {len(missing_ids):,}")
    
    if not missing_ids:
        print("✅ Todos los clientes fueron importados correctamente")
        return
    
    # Analizar los clientes no importados
    df_missing = df_clients[df_clients['PatientId'].isin(missing_ids)].copy()
    
    print(f"\n📋 ANÁLISIS DE CLIENTES NO IMPORTADOS:")
    print("=" * 40)
    
    # Estadísticas básicas
    print(f"📊 Total clientes no importados: {len(df_missing):,}")
    
    # Verificar si tienen campo IsDeleted (aunque no lo encontramos antes)
    if 'IsDeleted' in df_missing.columns:
        deleted_count = df_missing[df_missing['IsDeleted'] == 1].shape[0]
        print(f"🗑️  Clientes eliminados: {deleted_count:,}")
    
    # Analizar fechas de creación
    if 'DateCreated' in df_missing.columns:
        df_missing['DateCreated'] = pd.to_datetime(df_missing['DateCreated'])
        print(f"\n📅 ANÁLISIS DE FECHAS DE CREACIÓN:")
        print(f"   Fecha más antigua: {df_missing['DateCreated'].min()}")
        print(f"   Fecha más reciente: {df_missing['DateCreated'].max()}")
        
        # Distribución por año
        year_counts = df_missing['DateCreated'].dt.year.value_counts().sort_index()
        print(f"   Distribución por año:")
        for year, count in year_counts.items():
            print(f"     {year}: {count:,} clientes")
    
    # Verificar completitud de datos
    print(f"\n📊 COMPLETITUD DE DATOS EN CLIENTES NO IMPORTADOS:")
    key_fields = ['FirstName', 'LastName', 'Email', 'HomePhone', 'MobileOrOtherPhone']
    
    for field in key_fields:
        if field in df_missing.columns:
            non_null_count = df_missing[field].notna().sum()
            non_null_pct = non_null_count / len(df_missing) * 100
            print(f"   📝 {field}: {non_null_count:,} registros ({non_null_pct:.1f}%)")
    
    # Comparar con clientes importados exitosamente
    print(f"\n📊 COMPARACIÓN CON CLIENTES IMPORTADOS:")
    df_imported_successfully = df_clients[df_clients['PatientId'].isin(imported_ids)].copy()
    
    for field in key_fields:
        if field in df_missing.columns and field in df_imported_successfully.columns:
            missing_pct = df_missing[field].notna().sum() / len(df_missing) * 100
            imported_pct = df_imported_successfully[field].notna().sum() / len(df_imported_successfully) * 100
            
            print(f"   {field}:")
            print(f"     No importados: {missing_pct:.1f}%")
            print(f"     Importados: {imported_pct:.1f}%")
            print(f"     Diferencia: {imported_pct - missing_pct:.1f}%")
    
    # Mostrar ejemplos de clientes no importados
    print(f"\n📋 EJEMPLOS DE CLIENTES NO IMPORTADOS (primeros 10):")
    example_fields = ['PatientId', 'FirstName', 'LastName', 'Email', 'DateCreated']
    available_fields = [field for field in example_fields if field in df_missing.columns]
    
    for i in range(min(10, len(df_missing))):
        print(f"\nCliente no importado {i+1}:")
        row = df_missing.iloc[i]
        for field in available_fields:
            value = row[field]
            if pd.isna(value):
                value = "NULL"
            print(f"   {field}: {value}")
    
    # Verificar si hay algún patrón en los IDs no importados
    print(f"\n🔍 ANÁLISIS DE PATRONES EN IDs NO IMPORTADOS:")
    missing_ids_list = sorted(list(missing_ids))
    
    print(f"   ID más bajo no importado: {min(missing_ids_list):,}")
    print(f"   ID más alto no importado: {max(missing_ids_list):,}")
    
    # Verificar si hay rangos consecutivos
    consecutive_ranges = []
    current_range = [missing_ids_list[0]]
    
    for i in range(1, len(missing_ids_list)):
        if missing_ids_list[i] == missing_ids_list[i-1] + 1:
            current_range.append(missing_ids_list[i])
        else:
            if len(current_range) > 1:
                consecutive_ranges.append((current_range[0], current_range[-1]))
            current_range = [missing_ids_list[i]]
    
    if len(current_range) > 1:
        consecutive_ranges.append((current_range[0], current_range[-1]))
    
    if consecutive_ranges:
        print(f"   Rangos consecutivos encontrados: {len(consecutive_ranges)}")
        for start, end in consecutive_ranges[:5]:  # Mostrar primeros 5
            print(f"     {start:,} - {end:,} ({end-start+1} IDs)")
    
    # Generar reporte de clientes no importados
    report_file = "/Users/enrique/Proyectos/imports/missing_clients_analysis.txt"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("REPORTE - CLIENTES NO IMPORTADOS\n")
        f.write("=" * 40 + "\n\n")
        f.write(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write(f"RESUMEN:\n")
        f.write(f"• Total clientes originales: {len(df_clients):,}\n")
        f.write(f"• Total clientes importados: {len(df_imported):,}\n")
        f.write(f"• Clientes no importados: {len(missing_ids):,}\n")
        f.write(f"• Tasa de pérdida: {len(missing_ids)/len(df_clients)*100:.2f}%\n\n")
        
        f.write(f"IDs NO IMPORTADOS:\n")
        f.write("-" * 20 + "\n")
        for id_val in sorted(missing_ids):
            f.write(f"{id_val}\n")
        
        if consecutive_ranges:
            f.write(f"\nRANGOS CONSECUTIVOS:\n")
            f.write("-" * 20 + "\n")
            for start, end in consecutive_ranges:
                f.write(f"{start:,} - {end:,} ({end-start+1} IDs)\n")
    
    print(f"\n✅ Reporte guardado: {report_file}")
    
    return df_missing, missing_ids

def main():
    print("🏥 ANÁLISIS DETALLADO - CLIENTES NO IMPORTADOS")
    print("=" * 50)
    
    try:
        df_missing, missing_ids = analyze_missing_clients()
        
        print(f"\n🎯 CONCLUSIONES:")
        print("=" * 20)
        
        if len(missing_ids) < 500:
            print("✅ La tasa de importación es excelente (>97%)")
            print("🔍 Los clientes no importados requieren investigación individual")
        else:
            print("⚠️  Tasa de pérdida significativa - requiere investigación")
        
        print(f"\n📊 Estadísticas finales:")
        print(f"   • Tasa de importación: {((20656 - len(missing_ids))/20656*100):.2f}%")
        print(f"   • Clientes perdidos: {len(missing_ids):,}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
