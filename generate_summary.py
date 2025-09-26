#!/usr/bin/env python3
"""
Resumen conciso de todas las pestañas con formato solicitado:
- Pestaña
- Cantidad de registros  
- Rango de fechas
- Diferencia con archivo original
"""

import pandas as pd
from datetime import datetime
import os

def generate_summary_report():
    print("📊 RESUMEN EJECUTIVO - ANÁLISIS CUVET-V2.XLSX")
    print("=" * 80)
    
    new_file = "/Users/enrique/Proyectos/imports/source/cuvet-v2.xlsx"
    original_file = "/Users/enrique/Proyectos/imports/source/cuvet.xlsx"
    
    # Verificar archivos
    if not os.path.exists(new_file):
        print(f"❌ Archivo no encontrado: {new_file}")
        return
    
    has_original = os.path.exists(original_file)
    
    try:
        # Leer información de ambos archivos
        new_sheets = pd.ExcelFile(new_file).sheet_names
        
        if has_original:
            original_sheets = pd.ExcelFile(original_file).sheet_names
            original_counts = {}
            
            # Obtener conteos del archivo original
            for sheet_name in original_sheets:
                try:
                    df_orig = pd.read_excel(original_file, sheet_name=sheet_name, engine='openpyxl')
                    original_counts[sheet_name] = len(df_orig)
                except:
                    original_counts[sheet_name] = 0
        else:
            original_sheets = []
            original_counts = {}
        
        # Clasificar pestañas
        nuevas_pestanas = [sheet for sheet in new_sheets if sheet not in original_sheets]
        
        print(f"Pestaña".ljust(25) + 
              f"Registros".ljust(12) + 
              f"Rango de Fechas".ljust(45) + 
              f"Diferencia con Original")
        print("-" * 105)
        
        # Procesar cada pestaña
        for sheet_name in new_sheets:
            try:
                df = pd.read_excel(new_file, sheet_name=sheet_name, engine='openpyxl')
                registros = len(df)
                
                # Buscar rango de fechas
                date_columns = []
                for col in df.columns:
                    if any(keyword in col.lower() for keyword in ['date', 'fecha', 'modified', 'created']):
                        # Excluir columnas que claramente no son fechas reales
                        if not any(exclude in col.lower() for exclude in ['userid', 'tenantid']):
                            date_columns.append(col)
                
                rango_fechas = "Sin fechas"
                if date_columns:
                    fechas_validas = []
                    for date_col in date_columns:
                        try:
                            df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
                            valid_dates = df[date_col].dropna()
                            if len(valid_dates) > 0:
                                fechas_validas.extend(valid_dates)
                        except:
                            continue
                    
                    if fechas_validas:
                        fecha_min = min(fechas_validas)
                        fecha_max = max(fechas_validas)
                        
                        # Formatear fechas de manera compacta
                        if fecha_min.year == fecha_max.year:
                            if fecha_min.month == fecha_max.month:
                                rango_fechas = f"{fecha_min.strftime('%d')}-{fecha_max.strftime('%d %b %Y')}"
                            else:
                                rango_fechas = f"{fecha_min.strftime('%b')}-{fecha_max.strftime('%b %Y')}"
                        else:
                            rango_fechas = f"{fecha_min.strftime('%Y')}-{fecha_max.strftime('%Y')}"
                        
                        # Si es muy reciente, mostrar fecha completa
                        if fecha_max.year == 2025 and fecha_max.month >= 9:
                            rango_fechas = f"{fecha_min.strftime('%Y')} a {fecha_max.strftime('%d %b %Y')}"
                
                # Determinar diferencia con original
                if sheet_name in nuevas_pestanas:
                    diferencia = "🆕 NUEVA PESTAÑA"
                elif sheet_name in original_counts:
                    diff = registros - original_counts[sheet_name]
                    if diff == 0:
                        diferencia = "✅ Sin cambios"
                    elif diff > 0:
                        diferencia = f"📈 +{diff:,} registros"
                    else:
                        diferencia = f"📉 {diff:,} registros"
                else:
                    diferencia = "❓ No comparado"
                
                # Formatear salida
                print(f"{sheet_name[:24].ljust(25)}" + 
                      f"{registros:,}".ljust(12) + 
                      f"{rango_fechas[:44].ljust(45)}" + 
                      f"{diferencia}")
                
            except Exception as e:
                print(f"{sheet_name[:24].ljust(25)}" + 
                      f"ERROR".ljust(12) + 
                      f"Error al procesar".ljust(45) + 
                      f"❌ {str(e)[:30]}")
        
        # Resumen final
        total_registros = sum([len(pd.read_excel(new_file, sheet_name=s, engine='openpyxl')) 
                              for s in new_sheets])
        
        print("-" * 105)
        print(f"📊 TOTALES:")
        print(f"   Pestañas: {len(new_sheets)} ({len(nuevas_pestanas)} nuevas)")
        print(f"   Registros: {total_registros:,} total")
        
        if nuevas_pestanas:
            registros_nuevos = sum([len(pd.read_excel(new_file, sheet_name=s, engine='openpyxl')) 
                                   for s in nuevas_pestanas])
            print(f"   Nuevos registros: {registros_nuevos:,}")
        
        print(f"   Fecha de análisis: {datetime.now().strftime('%d %b %Y %H:%M')}")
        
    except Exception as e:
        print(f"❌ Error general: {e}")

if __name__ == "__main__":
    generate_summary_report()
