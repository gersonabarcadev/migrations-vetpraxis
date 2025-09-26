#!/usr/bin/env python3
"""
Análisis detallado de pestañas procedimientos y pacienteprocedimientos
Para crear sistema de importación con formato específico
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def analyze_procedimientos_tables():
    print("🏥 ANÁLISIS DETALLADO - PESTAÑAS PROCEDIMIENTOS")
    print("=" * 60)
    
    new_file = "/Users/enrique/Proyectos/imports/source/cuvet-v2.xlsx"
    
    if not os.path.exists(new_file):
        print(f"❌ Archivo no encontrado: {new_file}")
        return
    
    try:
        # Leer ambas pestañas
        print("📖 Cargando pestañas...")
        df_procedimientos = pd.read_excel(new_file, sheet_name='procedimientos', engine='openpyxl')
        df_pacienteprocedimientos = pd.read_excel(new_file, sheet_name='pacienteprocedimientos', engine='openpyxl')
        
        print(f"✅ procedimientos: {len(df_procedimientos):,} registros")
        print(f"✅ pacienteprocedimientos: {len(df_pacienteprocedimientos):,} registros")
        print()
        
        # ANÁLISIS TABLA PROCEDIMIENTOS
        print("🔍 ANÁLISIS TABLA 'procedimientos' (catálogo)")
        print("-" * 50)
        print(f"📊 Dimensiones: {df_procedimientos.shape}")
        print("📋 Columnas:")
        for i, col in enumerate(df_procedimientos.columns, 1):
            print(f"   {i}. {col}")
        
        print(f"\n📅 Rangos de fechas:")
        if 'DataDate' in df_procedimientos.columns:
            df_procedimientos['DataDate'] = pd.to_datetime(df_procedimientos['DataDate'], errors='coerce')
            print(f"   DataDate: {df_procedimientos['DataDate'].min()} a {df_procedimientos['DataDate'].max()}")
        
        print(f"\n🆔 InterventionId (clave):")
        intervention_ids = df_procedimientos['InterventionId'].nunique()
        print(f"   Procedimientos únicos: {intervention_ids}")
        print(f"   Rango IDs: {df_procedimientos['InterventionId'].min()} - {df_procedimientos['InterventionId'].max()}")
        
        print(f"\n🏥 Nombres de procedimientos (muestra):")
        sample_names = df_procedimientos['Name'].dropna().unique()[:15]
        for name in sample_names:
            print(f"   • {name}")
        
        if 'Description' in df_procedimientos.columns:
            descriptions_count = df_procedimientos['Description'].notna().sum()
            print(f"\n📝 Descripciones: {descriptions_count}/{len(df_procedimientos)} tienen descripción")
            
            if descriptions_count > 0:
                print(f"   Ejemplos de descripciones:")
                sample_desc = df_procedimientos[df_procedimientos['Description'].notna()]['Description'].head(5)
                for i, desc in enumerate(sample_desc, 1):
                    desc_preview = str(desc)[:80] + "..." if len(str(desc)) > 80 else str(desc)
                    print(f"      {i}. {desc_preview}")
        
        # Análisis de categorías si existe
        if 'ExpirationDays' in df_procedimientos.columns:
            expiration_stats = df_procedimientos['ExpirationDays'].value_counts().head(10)
            print(f"\n⏰ Días de expiración más comunes:")
            for days, count in expiration_stats.items():
                print(f"   {days} días: {count} procedimientos")
        
        # ANÁLISIS TABLA PACIENTEPROCEDIMIENTOS
        print(f"\n\n🔍 ANÁLISIS TABLA 'pacienteprocedimientos' (aplicaciones)")
        print("-" * 50)
        print(f"📊 Dimensiones: {df_pacienteprocedimientos.shape}")
        print("📋 Columnas:")
        for i, col in enumerate(df_pacienteprocedimientos.columns, 1):
            print(f"   {i}. {col}")
        
        # Análisis de IsDeleted
        if 'IsDeleted' in df_pacienteprocedimientos.columns:
            deleted_count = df_pacienteprocedimientos['IsDeleted'].sum()
            active_count = len(df_pacienteprocedimientos) - deleted_count
            print(f"\n🗑️  Estado de registros:")
            print(f"   Activos: {active_count:,}")
            print(f"   Eliminados: {deleted_count:,}")
            print(f"   Tasa eliminación: {(deleted_count/len(df_pacienteprocedimientos)*100):.1f}%")
        
        # Filtrar solo activos para análisis
        df_active = df_pacienteprocedimientos[df_pacienteprocedimientos['IsDeleted'] == 0] if 'IsDeleted' in df_pacienteprocedimientos.columns else df_pacienteprocedimientos
        print(f"\n📊 Analizando {len(df_active):,} registros activos...")
        
        print(f"\n📅 Rangos de fechas (registros activos):")
        if 'DataDate' in df_active.columns:
            df_active = df_active.copy()
            df_active['DataDate'] = pd.to_datetime(df_active['DataDate'], errors='coerce')
            print(f"   DataDate: {df_active['DataDate'].min()} a {df_active['DataDate'].max()}")
        
        if 'DateExpires' in df_active.columns:
            df_active['DateExpires'] = pd.to_datetime(df_active['DateExpires'], errors='coerce')
            expires_valid = df_active['DateExpires'].dropna()
            if len(expires_valid) > 0:
                print(f"   DateExpires: {expires_valid.min()} a {expires_valid.max()}")
                print(f"   Registros con vencimiento: {len(expires_valid)}/{len(df_active)}")
        
        print(f"\n🆔 PatientId:")
        patient_count = df_active['PatientId'].nunique()
        print(f"   Pacientes únicos: {patient_count:,}")
        print(f"   Rango IDs: {df_active['PatientId'].min()} - {df_active['PatientId'].max()}")
        
        print(f"\n🏥 InterventionId:")
        intervention_used_count = df_active['InterventionId'].nunique()
        print(f"   Procedimientos aplicados: {intervention_used_count} tipos diferentes")
        print(f"   Rango IDs: {df_active['InterventionId'].min()} - {df_active['InterventionId'].max()}")
        
        # Top procedimientos más aplicados
        top_procedures = df_active['InterventionId'].value_counts().head(15)
        print(f"\n🏆 Top 15 procedimientos más aplicados:")
        for intervention_id, count in top_procedures.items():
            procedure_name = df_procedimientos[df_procedimientos['InterventionId'] == intervention_id]['Name'].iloc[0] if len(df_procedimientos[df_procedimientos['InterventionId'] == intervention_id]) > 0 else "Desconocido"
            print(f"   {intervention_id}: {count:,} aplicaciones - {procedure_name}")
        
        # Análisis de notas
        if 'Note' in df_active.columns:
            notes_count = df_active['Note'].notna().sum()
            print(f"\n📝 Notas:")
            print(f"   Registros con notas: {notes_count}/{len(df_active)} ({(notes_count/len(df_active)*100):.1f}%)")
            
            if notes_count > 0:
                sample_notes = df_active[df_active['Note'].notna()]['Note'].head(5)
                print(f"   Ejemplos de notas:")
                for i, note in enumerate(sample_notes, 1):
                    note_preview = str(note)[:100] + "..." if len(str(note)) > 100 else str(note)
                    print(f"      {i}. {note_preview}")
        
        # ANÁLISIS DE RELACIÓN ENTRE TABLAS
        print(f"\n\n🔗 ANÁLISIS DE RELACIÓN ENTRE TABLAS")
        print("-" * 50)
        
        # Verificar integridad referencial
        procedures_in_catalog = set(df_procedimientos['InterventionId'].unique())
        procedures_applied = set(df_active['InterventionId'].unique())
        
        missing_in_catalog = procedures_applied - procedures_in_catalog
        unused_in_catalog = procedures_in_catalog - procedures_applied
        
        print(f"✅ Procedimientos en catálogo: {len(procedures_in_catalog)}")
        print(f"✅ Procedimientos aplicados: {len(procedures_applied)}")
        print(f"🔗 Relación exitosa: {len(procedures_applied - missing_in_catalog)}/{len(procedures_applied)}")
        
        if missing_in_catalog:
            print(f"⚠️  Procedimientos aplicados sin catálogo: {len(missing_in_catalog)}")
            print(f"   IDs faltantes: {sorted(list(missing_in_catalog))[:10]}")
        
        if unused_in_catalog:
            print(f"📦 Procedimientos en catálogo sin uso: {len(unused_in_catalog)}")
            print(f"   Porcentaje sin uso: {len(unused_in_catalog)/len(procedures_in_catalog)*100:.1f}%")
        
        # ANÁLISIS PARA IMPORTACIÓN
        print(f"\n\n📋 ESTRUCTURA PARA IMPORTACIÓN")
        print("-" * 50)
        
        print("🎯 Mapeo de campos propuesto:")
        print("   A. clinic_record_import_id => Generado (PatientId + DataDate)")
        print("   B. PatientId => pacienteprocedimientos.PatientId")
        print("   C. DataDate => pacienteprocedimientos.DataDate")
        print("   D. Razón => 'Procedimiento' (fijo)")
        print("   E. Tratamiento => procedimientos.Name (via InterventionId)")
        print("   F. Cantidad => 1 (fijo)")
        print("   G. Notas => pacienteprocedimientos.Note")
        
        # Verificar combinaciones PatientId + DataDate
        df_active['date_only'] = df_active['DataDate'].dt.date
        combinations = df_active.groupby(['PatientId', 'date_only']).size()
        
        print(f"\n📊 Análisis de agrupación por paciente/fecha:")
        print(f"   Total aplicaciones activas: {len(df_active):,}")
        print(f"   Combinaciones únicas (PatientId + Fecha): {len(combinations):,}")
        print(f"   Promedio procedimientos por visita: {len(df_active)/len(combinations):.2f}")
        
        # Distribución de procedimientos por visita
        visit_distribution = combinations.value_counts().sort_index()
        print(f"\n📈 Distribución de procedimientos por visita:")
        for procedimientos_por_visita, visitas in visit_distribution.head(10).items():
            print(f"   {procedimientos_por_visita} procedimiento(s): {visitas:,} visitas")
        
        if len(visit_distribution) > 10:
            print(f"   ... y {len(visit_distribution) - 10} más")
        
        # Casos con múltiples procedimientos en misma fecha
        multiple_procedures = combinations[combinations > 1]
        if len(multiple_procedures) > 0:
            print(f"\n⚠️  Visitas con múltiples procedimientos: {len(multiple_procedures):,}")
            print(f"   Máximo procedimientos en una visita: {multiple_procedures.max()}")
            
            # Ejemplos
            print(f"   Ejemplos de visitas múltiples:")
            sample_multiple = multiple_procedures.head(5)
            for (patient_id, date), count in sample_multiple.items():
                procedures_that_day = df_active[(df_active['PatientId'] == patient_id) & 
                                              (df_active['date_only'] == date)]['InterventionId'].tolist()
                procedure_names = []
                for iid in procedures_that_day:
                    name = df_procedimientos[df_procedimientos['InterventionId'] == iid]['Name'].iloc[0] if len(df_procedimientos[df_procedimientos['InterventionId'] == iid]) > 0 else f"ID:{iid}"
                    procedure_names.append(name)
                print(f"      Paciente {patient_id}, {date}: {count} procedimientos")
                print(f"         {', '.join(procedure_names[:3])}")
                if len(procedure_names) > 3:
                    print(f"         ... y {len(procedure_names) - 3} más")
        
        # Análisis temporal
        print(f"\n📅 ANÁLISIS TEMPORAL:")
        year_counts = df_active['DataDate'].dt.year.value_counts().sort_index()
        print(f"   Distribución por año:")
        for year, count in year_counts.items():
            print(f"      {year}: {count:,} procedimientos")
        
        print(f"\n✅ Análisis completado. Listo para generar template de importación.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_procedimientos_tables()
