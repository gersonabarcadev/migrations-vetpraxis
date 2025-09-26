#!/usr/bin/env python3
"""
Análisis detallado de pestañas vacunas y pacientevacuna
Para crear sistema de importación con formato específico
"""

import pandas as pd
import numpy as np
from datetime import datetime
import os

def analyze_vacunas_tables():
    print("🩹 ANÁLISIS DETALLADO - PESTAÑAS VACUNAS")
    print("=" * 60)
    
    new_file = "/Users/enrique/Proyectos/imports/source/cuvet-v2.xlsx"
    
    if not os.path.exists(new_file):
        print(f"❌ Archivo no encontrado: {new_file}")
        return
    
    try:
        # Leer ambas pestañas
        print("📖 Cargando pestañas...")
        df_vacunas = pd.read_excel(new_file, sheet_name='vacunas', engine='openpyxl')
        df_pacientevacuna = pd.read_excel(new_file, sheet_name='pacientevacuna', engine='openpyxl')
        
        print(f"✅ vacunas: {len(df_vacunas):,} registros")
        print(f"✅ pacientevacuna: {len(df_pacientevacuna):,} registros")
        print()
        
        # ANÁLISIS TABLA VACUNAS
        print("🔍 ANÁLISIS TABLA 'vacunas' (catálogo)")
        print("-" * 50)
        print(f"📊 Dimensiones: {df_vacunas.shape}")
        print("📋 Columnas:")
        for i, col in enumerate(df_vacunas.columns, 1):
            print(f"   {i}. {col}")
        
        print(f"\n📅 Rangos de fechas:")
        if 'DataDate' in df_vacunas.columns:
            df_vacunas['DataDate'] = pd.to_datetime(df_vacunas['DataDate'], errors='coerce')
            print(f"   DataDate: {df_vacunas['DataDate'].min()} a {df_vacunas['DataDate'].max()}")
        
        print(f"\n🆔 VaccineId (clave):")
        vaccine_ids = df_vacunas['VaccineId'].nunique()
        print(f"   Vacunas únicas: {vaccine_ids}")
        print(f"   Rango IDs: {df_vacunas['VaccineId'].min()} - {df_vacunas['VaccineId'].max()}")
        
        print(f"\n💊 Nombres de vacunas (muestra):")
        sample_names = df_vacunas['Name'].dropna().unique()[:10]
        for name in sample_names:
            print(f"   • {name}")
        
        if 'Description' in df_vacunas.columns:
            descriptions_count = df_vacunas['Description'].notna().sum()
            print(f"\n📝 Descripciones: {descriptions_count}/{len(df_vacunas)} tienen descripción")
        
        # ANÁLISIS TABLA PACIENTEVACUNA
        print(f"\n\n🔍 ANÁLISIS TABLA 'pacientevacuna' (aplicaciones)")
        print("-" * 50)
        print(f"📊 Dimensiones: {df_pacientevacuna.shape}")
        print("📋 Columnas:")
        for i, col in enumerate(df_pacientevacuna.columns, 1):
            print(f"   {i}. {col}")
        
        # Análisis de IsDeleted
        if 'IsDeleted' in df_pacientevacuna.columns:
            deleted_count = df_pacientevacuna['IsDeleted'].sum()
            active_count = len(df_pacientevacuna) - deleted_count
            print(f"\n🗑️  Estado de registros:")
            print(f"   Activos: {active_count:,}")
            print(f"   Eliminados: {deleted_count:,}")
            print(f"   Tasa eliminación: {(deleted_count/len(df_pacientevacuna)*100):.1f}%")
        
        # Filtrar solo activos para análisis
        df_active = df_pacientevacuna[df_pacientevacuna['IsDeleted'] == 0] if 'IsDeleted' in df_pacientevacuna.columns else df_pacientevacuna
        print(f"\n📊 Analizando {len(df_active):,} registros activos...")
        
        print(f"\n📅 Rangos de fechas (registros activos):")
        if 'DataDate' in df_active.columns:
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
        
        print(f"\n💉 VaccineId:")
        vaccine_used_count = df_active['VaccineId'].nunique()
        print(f"   Vacunas aplicadas: {vaccine_used_count} tipos diferentes")
        print(f"   Rango IDs: {df_active['VaccineId'].min()} - {df_active['VaccineId'].max()}")
        
        # Top vacunas más aplicadas
        top_vaccines = df_active['VaccineId'].value_counts().head(10)
        print(f"\n🏆 Top 10 vacunas más aplicadas:")
        for vaccine_id, count in top_vaccines.items():
            vaccine_name = df_vacunas[df_vacunas['VaccineId'] == vaccine_id]['Name'].iloc[0] if len(df_vacunas[df_vacunas['VaccineId'] == vaccine_id]) > 0 else "Desconocida"
            print(f"   {vaccine_id}: {count:,} aplicaciones - {vaccine_name}")
        
        # Análisis de notas
        if 'Note' in df_active.columns:
            notes_count = df_active['Note'].notna().sum()
            print(f"\n📝 Notas:")
            print(f"   Registros con notas: {notes_count}/{len(df_active)} ({(notes_count/len(df_active)*100):.1f}%)")
            
            if notes_count > 0:
                sample_notes = df_active[df_active['Note'].notna()]['Note'].head(5)
                print(f"   Ejemplos de notas:")
                for i, note in enumerate(sample_notes, 1):
                    note_preview = str(note)[:80] + "..." if len(str(note)) > 80 else str(note)
                    print(f"      {i}. {note_preview}")
        
        # ANÁLISIS DE RELACIÓN ENTRE TABLAS
        print(f"\n\n🔗 ANÁLISIS DE RELACIÓN ENTRE TABLAS")
        print("-" * 50)
        
        # Verificar integridad referencial
        vaccines_in_catalog = set(df_vacunas['VaccineId'].unique())
        vaccines_applied = set(df_active['VaccineId'].unique())
        
        missing_in_catalog = vaccines_applied - vaccines_in_catalog
        unused_in_catalog = vaccines_in_catalog - vaccines_applied
        
        print(f"✅ Vacunas en catálogo: {len(vaccines_in_catalog)}")
        print(f"✅ Vacunas aplicadas: {len(vaccines_applied)}")
        print(f"🔗 Relación exitosa: {len(vaccines_applied - missing_in_catalog)}/{len(vaccines_applied)}")
        
        if missing_in_catalog:
            print(f"⚠️  Vacunas aplicadas sin catálogo: {len(missing_in_catalog)}")
            print(f"   IDs faltantes: {sorted(list(missing_in_catalog))[:10]}")
        
        if unused_in_catalog:
            print(f"📦 Vacunas en catálogo sin uso: {len(unused_in_catalog)}")
        
        # ANÁLISIS PARA IMPORTACIÓN
        print(f"\n\n📋 ESTRUCTURA PARA IMPORTACIÓN")
        print("-" * 50)
        
        print("🎯 Mapeo de campos:")
        print("   A. clinic_record_import_id => Generado (PatientId + DataDate)")
        print("   B. PatientId => pacientevacuna.PatientId")
        print("   C. DataDate => pacientevacuna.DataDate")
        print("   D. Razón => 'Vacuna' (fijo)")
        print("   E. Tratamiento => vacunas.Name (via VaccineId)")
        print("   F. Cantidad => 1 (fijo)")
        print("   G. Notas => pacientevacuna.Note")
        
        # Verificar combinaciones PatientId + DataDate
        df_active['date_only'] = df_active['DataDate'].dt.date
        combinations = df_active.groupby(['PatientId', 'date_only']).size()
        
        print(f"\n📊 Análisis de agrupación por paciente/fecha:")
        print(f"   Total aplicaciones activas: {len(df_active):,}")
        print(f"   Combinaciones únicas (PatientId + Fecha): {len(combinations):,}")
        print(f"   Promedio vacunas por visita: {len(df_active)/len(combinations):.2f}")
        
        # Distribución de vacunas por visita
        visit_distribution = combinations.value_counts().sort_index()
        print(f"\n📈 Distribución de vacunas por visita:")
        for vacunas_por_visita, visitas in visit_distribution.head(10).items():
            print(f"   {vacunas_por_visita} vacuna(s): {visitas:,} visitas")
        
        if len(visit_distribution) > 10:
            print(f"   ... y {len(visit_distribution) - 10} más")
        
        # Casos con múltiples vacunas en misma fecha
        multiple_vaccines = combinations[combinations > 1]
        if len(multiple_vaccines) > 0:
            print(f"\n⚠️  Visitas con múltiples vacunas: {len(multiple_vaccines):,}")
            print(f"   Máximo vacunas en una visita: {multiple_vaccines.max()}")
            
            # Ejemplos
            print(f"   Ejemplos de visitas múltiples:")
            sample_multiple = multiple_vaccines.head(5)
            for (patient_id, date), count in sample_multiple.items():
                vaccines_that_day = df_active[(df_active['PatientId'] == patient_id) & 
                                            (df_active['date_only'] == date)]['VaccineId'].tolist()
                vaccine_names = []
                for vid in vaccines_that_day:
                    name = df_vacunas[df_vacunas['VaccineId'] == vid]['Name'].iloc[0] if len(df_vacunas[df_vacunas['VaccineId'] == vid]) > 0 else f"ID:{vid}"
                    vaccine_names.append(name)
                print(f"      Paciente {patient_id}, {date}: {count} vacunas")
                print(f"         {', '.join(vaccine_names[:3])}")
        
        print(f"\n✅ Análisis completado. Listo para generar template de importación.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_vacunas_tables()
