#!/usr/bin/env python3
"""
Análisis comparativo de la importación de clientes
Compara datos originales (cuvet-v2.xlsx - pacientes amos) con datos importados (clients_from_vetpraxis_after_import.json.csv)
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def analyze_original_clients():
    """Analizar datos originales de clientes desde cuvet-v2.xlsx"""
    print("📊 ANALIZANDO DATOS ORIGINALES DE CLIENTES")
    print("=" * 50)
    
    source_file = "/Users/enrique/Proyectos/imports/source/cuvet-v2.xlsx"
    
    if not os.path.exists(source_file):
        print(f"❌ Archivo no encontrado: {source_file}")
        return None
    
    try:
        # Cargar pestaña "pacientes amos"
        df_original = pd.read_excel(source_file, sheet_name='pacientes amos', engine='openpyxl')
        
        print(f"📋 Total registros en 'pacientes amos': {len(df_original):,}")
        
        # Mostrar columnas disponibles
        print(f"\n📂 Columnas disponibles ({len(df_original.columns)}):")
        for i, col in enumerate(df_original.columns, 1):
            print(f"   {i:2d}. {col}")
        
        # Verificar columna PatientType
        if 'PatientType' in df_original.columns:
            print(f"\n🔍 Distribución por PatientType:")
            patient_type_counts = df_original['PatientType'].value_counts().sort_index()
            for ptype, count in patient_type_counts.items():
                type_desc = "Cliente" if ptype == 0 else "Mascota" if ptype == 1 else "Desconocido"
                print(f"   {ptype} ({type_desc}): {count:,} registros")
            
            # Filtrar solo clientes (PatientType = 0)
            df_clients = df_original[df_original['PatientType'] == 0].copy()
            print(f"\n👥 Clientes filtrados: {len(df_clients):,}")
            
        else:
            print("⚠️  No se encontró columna 'PatientType'")
            print("Columnas disponibles:", list(df_original.columns))
            return None
        
        # Verificar registros eliminados
        if 'IsDeleted' in df_clients.columns:
            deleted_clients = df_clients[df_clients['IsDeleted'] == 1]
            active_clients = df_clients[df_clients['IsDeleted'] == 0]
            
            print(f"\n🗑️  Estado de clientes:")
            print(f"   Eliminados (IsDeleted=1): {len(deleted_clients):,}")
            print(f"   Activos (IsDeleted=0): {len(active_clients):,}")
            
            # Usar solo clientes activos
            df_clients_active = active_clients.copy()
        else:
            print("⚠️  No se encontró columna 'IsDeleted'")
            df_clients_active = df_clients.copy()
        
        print(f"📊 Clientes activos para análisis: {len(df_clients_active):,}")
        
        # Análizar campos clave de clientes
        print(f"\n🔍 ANÁLISIS DE CAMPOS CLAVE DE CLIENTES:")
        
        # ID del cliente
        if 'PatientId' in df_clients_active.columns:
            unique_ids = df_clients_active['PatientId'].nunique()
            print(f"🆔 IDs únicos de clientes: {unique_ids:,}")
        
        # Nombres
        name_fields = ['FirstName', 'LastName', 'Name']
        for field in name_fields:
            if field in df_clients_active.columns:
                non_null = df_clients_active[field].notna().sum()
                print(f"📝 {field}: {non_null:,} registros con datos ({non_null/len(df_clients_active)*100:.1f}%)")
        
        # Email
        if 'Email' in df_clients_active.columns:
            emails_with_data = df_clients_active['Email'].notna().sum()
            unique_emails = df_clients_active['Email'].nunique()
            print(f"📧 Email: {emails_with_data:,} con datos, {unique_emails:,} únicos")
        
        # Teléfonos
        phone_fields = ['Phone', 'CellPhone', 'HomePhone']
        for field in phone_fields:
            if field in df_clients_active.columns:
                phones_with_data = df_clients_active[field].notna().sum()
                print(f"📞 {field}: {phones_with_data:,} registros con datos")
        
        # Fecha de creación
        if 'CreatedAt' in df_clients_active.columns:
            df_clients_active['CreatedAt'] = pd.to_datetime(df_clients_active['CreatedAt'])
            print(f"📅 Rango de fechas de creación:")
            print(f"   Desde: {df_clients_active['CreatedAt'].min()}")
            print(f"   Hasta: {df_clients_active['CreatedAt'].max()}")
        
        # Mostrar ejemplos
        print(f"\n📋 EJEMPLOS DE CLIENTES (primeros 3):")
        key_columns = ['PatientId', 'FirstName', 'LastName', 'Email', 'Phone']
        available_columns = [col for col in key_columns if col in df_clients_active.columns]
        
        for i in range(min(3, len(df_clients_active))):
            print(f"\nCliente {i+1}:")
            row = df_clients_active.iloc[i]
            for col in available_columns:
                value = row[col]
                if pd.isna(value):
                    value = "NULL"
                print(f"   {col}: {value}")
        
        return df_clients_active
        
    except Exception as e:
        print(f"❌ Error analizando datos originales: {e}")
        import traceback
        traceback.print_exc()
        return None

def analyze_imported_clients():
    """Analizar datos importados de clientes desde CSV"""
    print(f"\n📊 ANALIZANDO DATOS IMPORTADOS DE CLIENTES")
    print("=" * 50)
    
    import_file = "/Users/enrique/Proyectos/imports/source/clients_from_vetpraxis_after_import_v2.csv"
    
    if not os.path.exists(import_file):
        print(f"❌ Archivo no encontrado: {import_file}")
        return None
    
    try:
        # Cargar archivo CSV con separador punto y coma y manejo de comillas
        df_imported = pd.read_csv(import_file, sep=';', quotechar='"', skipinitialspace=True)
        
        print(f"📋 Total registros importados: {len(df_imported):,}")
        
        # Mostrar columnas disponibles
        print(f"\n📂 Columnas disponibles ({len(df_imported.columns)}):")
        for i, col in enumerate(df_imported.columns, 1):
            print(f"   {i:2d}. {col}")
        
        # Análisis de campos clave
        print(f"\n🔍 ANÁLISIS DE CAMPOS CLAVE IMPORTADOS:")
        
        # ID
        if 'id' in df_imported.columns:
            unique_ids = df_imported['id'].nunique()
            print(f"🆔 IDs únicos: {unique_ids:,}")
        
        # Nombres
        name_fields = ['first_name', 'last_name', 'name']
        for field in name_fields:
            if field in df_imported.columns:
                non_null = df_imported[field].notna().sum()
                print(f"📝 {field}: {non_null:,} registros con datos ({non_null/len(df_imported)*100:.1f}%)")
        
        # Email
        if 'email' in df_imported.columns:
            emails_with_data = df_imported['email'].notna().sum()
            unique_emails = df_imported['email'].nunique()
            print(f"📧 email: {emails_with_data:,} con datos, {unique_emails:,} únicos")
        
        # Teléfonos
        phone_fields = ['phone', 'mobile_phone', 'home_phone']
        for field in phone_fields:
            if field in df_imported.columns:
                phones_with_data = df_imported[field].notna().sum()
                print(f"📞 {field}: {phones_with_data:,} registros con datos")
        
        # Fechas
        date_fields = ['created_at', 'updated_at']
        for field in date_fields:
            if field in df_imported.columns:
                df_imported[field] = pd.to_datetime(df_imported[field], errors='coerce')
                print(f"📅 Rango {field}:")
                print(f"   Desde: {df_imported[field].min()}")
                print(f"   Hasta: {df_imported[field].max()}")
        
        # Campo import_client_id (para mapear con originales)
        if 'import_client_id' in df_imported.columns:
            import_client_ids = df_imported['import_client_id'].notna().sum()
            unique_import_client_ids = df_imported['import_client_id'].nunique()
            print(f"🔗 import_client_id: {import_client_ids:,} con datos, {unique_import_client_ids:,} únicos")
        
        # Mostrar ejemplos
        print(f"\n📋 EJEMPLOS DE CLIENTES IMPORTADOS (primeros 3):")
        key_columns = ['id', 'import_client_id', 'name', 'last_name', 'email', 'mobile_phone']
        available_columns = [col for col in key_columns if col in df_imported.columns]
        
        for i in range(min(3, len(df_imported))):
            print(f"\nCliente importado {i+1}:")
            row = df_imported.iloc[i]
            for col in available_columns:
                value = row[col]
                if pd.isna(value):
                    value = "NULL"
                print(f"   {col}: {value}")
        
        return df_imported
        
    except Exception as e:
        print(f"❌ Error analizando datos importados: {e}")
        import traceback
        traceback.print_exc()
        return None

def compare_datasets(df_original, df_imported):
    """Comparar datasets originales vs importados"""
    print(f"\n📊 COMPARACIÓN DE DATASETS")
    print("=" * 40)
    
    if df_original is None or df_imported is None:
        print("❌ No se pueden comparar datasets - datos faltantes")
        return
    
    # Estadísticas básicas
    print(f"📊 ESTADÍSTICAS BÁSICAS:")
    print(f"   Clientes originales (activos): {len(df_original):,}")
    print(f"   Clientes importados: {len(df_imported):,}")
    
    if len(df_imported) > 0:
        import_rate = len(df_imported) / len(df_original) * 100
        print(f"   Tasa de importación: {import_rate:.2f}%")
        
        if import_rate < 95:
            print("   ⚠️  Posible pérdida de datos en la importación")
        elif import_rate > 105:
            print("   ⚠️  Posibles duplicados en la importación")
        else:
            print("   ✅ Tasa de importación aceptable")
    
    # Comparar por import_client_id si está disponible
    if 'import_client_id' in df_imported.columns and 'PatientId' in df_original.columns:
        print(f"\n🔗 ANÁLISIS POR IMPORT_CLIENT_ID:")
        
        # Convertir import_client_id a numérico para comparar
        df_imported['import_client_id_numeric'] = pd.to_numeric(df_imported['import_client_id'], errors='coerce')
        
        original_ids = set(df_original['PatientId'].dropna())
        imported_client_ids = set(df_imported['import_client_id_numeric'].dropna())
        
        print(f"   IDs originales únicos: {len(original_ids):,}")
        print(f"   Import Client IDs únicos: {len(imported_client_ids):,}")
        
        # IDs coincidentes
        matching_ids = original_ids.intersection(imported_client_ids)
        print(f"   IDs coincidentes: {len(matching_ids):,}")
        
        # Calcular tasa de coincidencia
        if len(original_ids) > 0:
            match_rate = len(matching_ids) / len(original_ids) * 100
            print(f"   Tasa de coincidencia: {match_rate:.2f}%")
        
        # IDs faltantes
        missing_ids = original_ids - imported_client_ids
        if missing_ids:
            print(f"   ⚠️  IDs no importados: {len(missing_ids):,}")
            if len(missing_ids) <= 10:
                print(f"      IDs faltantes: {sorted(list(missing_ids))}")
            else:
                print(f"      Primeros 10 IDs faltantes: {sorted(list(missing_ids))[:10]}")
        
        # IDs extras
        extra_ids = imported_client_ids - original_ids
        if extra_ids:
            print(f"   ⚠️  Import Client IDs extras (no en originales): {len(extra_ids):,}")
            if len(extra_ids) <= 10:
                print(f"      IDs extras: {sorted(list(extra_ids))}")
        else:
            print(f"   ✅ No hay IDs extras - mapeo perfecto")
    
    # Comparar campos de datos
    print(f"\n📊 COMPARACIÓN DE CALIDAD DE DATOS:")
    
    field_mappings = [
        ('FirstName', 'name'),
        ('LastName', 'last_name'),
        ('Email', 'email'),
        ('HomePhone', 'home_phone'),
        ('MobileOrOtherPhone', 'mobile_phone')
    ]
    
    for orig_field, import_field in field_mappings:
        if orig_field in df_original.columns and import_field in df_imported.columns:
            orig_non_null = df_original[orig_field].notna().sum()
            import_non_null = df_imported[import_field].notna().sum()
            
            orig_pct = orig_non_null / len(df_original) * 100
            import_pct = import_non_null / len(df_imported) * 100
            
            print(f"   📝 {orig_field} → {import_field}:")
            print(f"      Original: {orig_non_null:,}/{len(df_original):,} ({orig_pct:.1f}%)")
            print(f"      Importado: {import_non_null:,}/{len(df_imported):,} ({import_pct:.1f}%)")
            
            if abs(orig_pct - import_pct) > 5:
                print(f"      ⚠️  Diferencia significativa: {abs(orig_pct - import_pct):.1f}%")

def generate_detailed_report(df_original, df_imported):
    """Generar reporte detallado"""
    print(f"\n📄 GENERANDO REPORTE DETALLADO")
    print("=" * 35)
    
    report_file = "/Users/enrique/Proyectos/imports/client_import_analysis_report.txt"
    
    try:
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("REPORTE DE ANÁLISIS - IMPORTACIÓN DE CLIENTES\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Fecha de análisis: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Resumen ejecutivo
            f.write("RESUMEN EJECUTIVO:\n")
            f.write("-" * 20 + "\n")
            if df_original is not None:
                f.write(f"• Clientes originales (activos): {len(df_original):,}\n")
            if df_imported is not None:
                f.write(f"• Clientes importados: {len(df_imported):,}\n")
            
            if df_original is not None and df_imported is not None:
                import_rate = len(df_imported) / len(df_original) * 100
                f.write(f"• Tasa de importación: {import_rate:.2f}%\n")
                
                status = "EXITOSA" if 95 <= import_rate <= 105 else "CON OBSERVACIONES"
                f.write(f"• Estado de importación: {status}\n")
            
            f.write("\nFUENTES DE DATOS:\n")
            f.write("-" * 20 + "\n")
            f.write("• Original: cuvet-v2.xlsx - pestaña 'pacientes amos' (PatientType=0)\n")
            f.write("• Importado: clients_from_vetpraxis_after_import_v2.csv\n")
            
            # Detalles de análisis
            if df_original is not None:
                f.write(f"\nDATOS ORIGINALES:\n")
                f.write("-" * 20 + "\n")
                f.write(f"• Total registros filtrados: {len(df_original):,}\n")
                f.write(f"• Columnas analizadas: {len(df_original.columns)}\n")
                
                if 'PatientId' in df_original.columns:
                    f.write(f"• IDs únicos: {df_original['PatientId'].nunique():,}\n")
                
                key_fields = ['FirstName', 'LastName', 'Email', 'Phone']
                for field in key_fields:
                    if field in df_original.columns:
                        non_null = df_original[field].notna().sum()
                        pct = non_null / len(df_original) * 100
                        f.write(f"• {field}: {non_null:,} registros ({pct:.1f}%)\n")
            
            if df_imported is not None:
                f.write(f"\nDATOS IMPORTADOS:\n")
                f.write("-" * 20 + "\n")
                f.write(f"• Total registros: {len(df_imported):,}\n")
                f.write(f"• Columnas disponibles: {len(df_imported.columns)}\n")
                
                if 'id' in df_imported.columns:
                    f.write(f"• IDs únicos: {df_imported['id'].nunique():,}\n")
                
                if 'import_client_id' in df_imported.columns:
                    import_client_count = df_imported['import_client_id'].notna().sum()
                    f.write(f"• Import Client IDs: {import_client_count:,} registros\n")
                
                key_fields = ['name', 'last_name', 'email', 'mobile_phone']
                for field in key_fields:
                    if field in df_imported.columns:
                        non_null = df_imported[field].notna().sum()
                        pct = non_null / len(df_imported) * 100
                        f.write(f"• {field}: {non_null:,} registros ({pct:.1f}%)\n")
        
        print(f"✅ Reporte guardado: {report_file}")
        
    except Exception as e:
        print(f"❌ Error generando reporte: {e}")

def main():
    print("🏥 ANÁLISIS COMPARATIVO - IMPORTACIÓN DE CLIENTES")
    print("=" * 60)
    
    try:
        # Analizar datos originales
        df_original = analyze_original_clients()
        
        # Analizar datos importados
        df_imported = analyze_imported_clients()
        
        # Comparar datasets
        compare_datasets(df_original, df_imported)
        
        # Generar reporte
        generate_detailed_report(df_original, df_imported)
        
        print(f"\n🎉 ¡ANÁLISIS COMPLETADO!")
        print("📊 Revisa el reporte generado para detalles completos")
        
    except Exception as e:
        print(f"❌ Error durante análisis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
