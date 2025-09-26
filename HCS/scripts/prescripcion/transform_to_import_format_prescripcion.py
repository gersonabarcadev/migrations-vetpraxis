#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para transformar prescripciones al formato de importación
Las prescripciones se transformarán usando el formato NOTAS para facilitar la importación

Mapeo de campos propuesto:
- PrescriptionMedicationId -> ID ATENCION
- PatientId -> ID MASCOTA  
- DataDate -> FECHA
- Name + AmountToBuy + RequestedUsage + Description -> NOTAS (formato simplificado)
"""

import pandas as pd
import os
from datetime import datetime

def transform_to_import(input_file=None, output_dir=None):
    """
    Transforma los datos de prescripciones al formato de importación NOTAS
    """
    
    # Configurar rutas por defecto si no se proporcionan
    if input_file is None:
        source_file = "../generation/prescripcion_organized.xlsx"
    else:
        # Si se proporciona input_file, buscar el archivo organized en el output_dir
        if output_dir and os.path.exists(os.path.join(output_dir, "prescripcion_organized.xlsx")):
            source_file = os.path.join(output_dir, "prescripcion_organized.xlsx")
        else:
            source_file = input_file
    
    if output_dir is None:
        output_dir = "../generation"
    
    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"prescripcion_import_transformed.xlsx")
    
    print("=" * 80)
    print("TRANSFORMACIÓN DE PRESCRIPCIONES A FORMATO DE IMPORTACIÓN NOTAS")
    print("=" * 80)
    print(f"Archivo origen: {source_file}")
    print(f"Archivo destino: {output_file}")
    print(f"Fecha de procesamiento: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Lista para reporte en consola
    report_lines = []
    
    def add_to_report(message):
        print(message)
        report_lines.append(message)
    
    try:
        # Verificar que existe el archivo origen
        if not os.path.exists(source_file):
            raise FileNotFoundError(f"No se encontró el archivo: {source_file}")
        
        add_to_report("1. CARGANDO DATOS ORIGEN")
        add_to_report("-" * 40)
        
        # Cargar datos limpios del archivo organizado
        source_df = pd.read_excel(source_file, sheet_name='03_Datos_Limpios')
        add_to_report(f"Registros cargados: {len(source_df):,}")
        add_to_report(f"Columnas origen: {list(source_df.columns)}")
        add_to_report("")
        
        add_to_report("2. APLICANDO FILTROS Y VALIDACIONES")
        add_to_report("-" * 40)
        
        # Registros originales
        total_original = len(source_df)
        add_to_report(f"Registros originales: {total_original:,}")
        
        # Filtrar registros con datos requeridos
        # Debe tener PrescriptionMedicationId, PatientId y DataDate
        required_fields = ['PrescriptionMedicationId', 'PatientId', 'DataDate']
        initial_count = len(source_df)
        
        for field in required_fields:
            if field in source_df.columns:
                before_count = len(source_df)
                source_df = source_df[source_df[field].notna()]
                after_count = len(source_df)
                removed = before_count - after_count
                if removed > 0:
                    add_to_report(f"  - Removidos {removed:,} registros sin {field}")
            else:
                add_to_report(f"  [X] Campo requerido {field} no encontrado")
        
        add_to_report(f"Registros válidos después de filtros: {len(source_df):,}")
        
        # Verificar duplicados por PrescriptionMedicationId
        if 'PrescriptionMedicationId' in source_df.columns:
            duplicates = source_df['PrescriptionMedicationId'].duplicated().sum()
            if duplicates > 0:
                add_to_report(f"  [WARN]  Se encontraron {duplicates} duplicados por PrescriptionMedicationId")
                source_df = source_df.drop_duplicates(subset=['PrescriptionMedicationId'], keep='first')
                add_to_report(f"  - Registros después de eliminar duplicados: {len(source_df):,}")
        
        add_to_report("")
        
        add_to_report("3. APLICANDO TRANSFORMACIONES")
        add_to_report("-" * 40)
        
        # Crear el DataFrame transformado
        df_transformed = pd.DataFrame()
        
        # Mapear columnas según especificación del formato NOTAS
        add_to_report("Aplicando mapeo para formato NOTAS:")
        
        # 1. ID ATENCION <- PrescriptionMedicationId
        df_transformed['ID ATENCION'] = source_df['PrescriptionMedicationId'] if 'PrescriptionMedicationId' in source_df.columns else None
        add_to_report("  - PrescriptionMedicationId -> ID ATENCION")
        
        # 2. ID MASCOTA <- PatientId
        df_transformed['ID MASCOTA'] = source_df['PatientId'] if 'PatientId' in source_df.columns else None
        add_to_report("  - PatientId -> ID MASCOTA")
        
        # 3. FECHA <- DataDate
        df_transformed['FECHA'] = pd.to_datetime(source_df['DataDate']) if 'DataDate' in source_df.columns else None
        add_to_report("  - DataDate -> FECHA")
        
        # 4. NOTAS <- Name + AmountToBuy + RequestedUsage + Description (formato limpio)
        def combine_prescription_data(row):
            """Combina los campos de prescripción en formato limpio y directo"""
            parts = []
            
            # Parte 1: Nombre del medicamento + cantidad (formato: MEDICAMENTO CANTIDAD)
            name_with_amount = ""
            if pd.notna(row.get('Name', '')):
                name_clean = str(row['Name']).strip().upper()
                if name_clean and name_clean.lower() != 'nan':
                    name_with_amount = name_clean
                    
                    # Agregar cantidad directamente después del nombre si existe
                    if pd.notna(row.get('AmountToBuy', '')):
                        amount = str(row['AmountToBuy']).strip()
                        if amount and amount.lower() != 'nan':
                            name_with_amount += f" {amount}"
            
            if name_with_amount:
                parts.append(name_with_amount)
            
            # Parte 2: Descripción (información técnica del medicamento)
            if pd.notna(row.get('Description', '')):
                desc = str(row['Description']).strip()
                if desc and desc.lower() != 'nan':
                    # Limpiar y formatear descripción
                    desc_clean = desc.replace('  ', ' ').strip()
                    # Limitar longitud para mantener legibilidad
                    if len(desc_clean) > 60:
                        desc_clean = desc_clean[:57] + "..."
                    # Convertir a mayúsculas solo la primera letra de cada palabra importante
                    desc_formatted = desc_clean.title()
                    parts.append(desc_formatted)
            
            # Parte 3: Uso/Instrucciones (costo, frecuencia, etc.)
            if pd.notna(row.get('RequestedUsage', '')):
                usage = str(row['RequestedUsage']).strip()
                if usage and usage.lower() != 'nan':
                    # Mantener formato original para costos y instrucciones
                    usage_clean = usage.replace('  ', ' ').strip()
                    # Limitar longitud
                    if len(usage_clean) > 50:
                        usage_clean = usage_clean[:47] + "..."
                    parts.append(usage_clean)
            
            # Si no hay información, crear nota por defecto
            if not parts:
                parts.append("PRESCRIPCIÓN SIN DETALLES")
            
            return " | ".join(parts)
        
        df_transformed['NOTAS'] = source_df.apply(combine_prescription_data, axis=1)
        add_to_report("  - Name + AmountToBuy + RequestedUsage + Description -> NOTAS (formato simplificado)")
        add_to_report("")
        
        add_to_report("4. VALIDACIONES FINALES")
        add_to_report("-" * 40)
        
        # Verificar rangos de fechas
        if 'FECHA' in df_transformed.columns and df_transformed['FECHA'].notna().sum() > 0:
            fecha_min = df_transformed['FECHA'].min()
            fecha_max = df_transformed['FECHA'].max()
            add_to_report(f"Rango de fechas: {fecha_min.strftime('%Y-%m-%d')} a {fecha_max.strftime('%Y-%m-%d')}")
        
        # Verificar IDs únicos
        id_atencion_unicos = df_transformed['ID ATENCION'].nunique()
        id_mascota_unicos = df_transformed['ID MASCOTA'].nunique()
        add_to_report(f"ID ATENCION únicos: {id_atencion_unicos:,}")
        add_to_report(f"ID MASCOTA únicos: {id_mascota_unicos:,}")
        
        # Verificar notas vacías
        notas_vacias = (df_transformed['NOTAS'].str.strip() == '').sum()
        add_to_report(f"Registros con notas vacías: {notas_vacias}")
        
        # Estadísticas de longitud de notas
        df_transformed['nota_length'] = df_transformed['NOTAS'].str.len()
        add_to_report(f"Longitud promedio de notas: {df_transformed['nota_length'].mean():.0f} caracteres")
        add_to_report(f"Longitud mínima: {df_transformed['nota_length'].min()}")
        add_to_report(f"Longitud máxima: {df_transformed['nota_length'].max()}")
        
        add_to_report("")
        
        add_to_report("5. ESTADÍSTICAS POR AÑO")
        add_to_report("-" * 40)
        
        # Distribución por año
        if 'FECHA' in df_transformed.columns and df_transformed['FECHA'].notna().sum() > 0:
            df_transformed['año'] = df_transformed['FECHA'].dt.year
            year_counts = df_transformed['año'].value_counts().sort_index()
            
            add_to_report("Distribución por año:")
            for year, count in year_counts.items():
                percentage = (count / len(df_transformed)) * 100
                add_to_report(f"  - {year}: {count:,} registros ({percentage:.1f}%)")
            
            # Quitar columna temporal
            df_transformed = df_transformed.drop('año', axis=1)
        else:
            add_to_report("No se pudieron procesar fechas para estadísticas anuales")
        
        add_to_report("")
        
        add_to_report("6. ANÁLISIS POR MEDICAMENTOS")
        add_to_report("-" * 40)
        
        # Extraer medicamentos de las notas para análisis
        if 'Name' in source_df.columns:
            med_types = source_df['Name'].value_counts().head(10)
            add_to_report("Top 10 medicamentos transformados:")
            for med_name, count in med_types.items():
                if pd.notna(med_name):
                    percentage = (count / len(df_transformed)) * 100
                    add_to_report(f"  - {med_name}: {count:,} prescripciones ({percentage:.1f}%)")
        
        add_to_report("")
        
        add_to_report("7. PREPARANDO DATOS EXCLUIDOS")
        add_to_report("-" * 40)
        
        # Registros excluidos (si los hay)
        df_excluded = pd.DataFrame()
        
        # Si existe archivo organizado, obtener eliminados
        try:
            df_excluded = pd.read_excel(source_file, sheet_name='02_Eliminados')
            add_to_report(f"Registros excluidos (eliminados): {len(df_excluded):,}")
        except:
            add_to_report("No se encontraron registros excluidos")
        
        add_to_report("")
        
        add_to_report("8. GUARDANDO RESULTADO EN MÚLTIPLES HOJAS")
        add_to_report("-" * 40)
        
        # Crear el archivo Excel con múltiples hojas
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            
            # Hoja principal: datos listos para importar
            df_final = df_transformed.drop('nota_length', axis=1, errors='ignore')
            df_final.to_excel(writer, sheet_name='datos_limpios', index=False)
            
            # Hoja de excluidos si existe
            if len(df_excluded) > 0:
                df_excluded.to_excel(writer, sheet_name='datos_excluidos', index=False)
            
            # Hoja de mapeo de campos
            mapeo_data = {
                'Campo_Origen': [
                    'PrescriptionMedicationId',
                    'PatientId', 
                    'DataDate',
                    'Name + AmountToBuy + RequestedUsage + Description'
                ],
                'Campo_Destino': [
                    'ID ATENCION',
                    'ID MASCOTA',
                    'FECHA', 
                    'NOTAS'
                ],
                'Descripcion': [
                    'ID único de la prescripción',
                    'ID del paciente/mascota',
                    'Fecha de la prescripción',
                    'Información de medicamento y uso'
                ],
                'Formato_Nota': [
                    'N/A',
                    'N/A', 
                    'YYYY-MM-DD',
                    '[MEDICAMENTO CANTIDAD] | [Descripción técnica] | [Instrucciones/Costo]'
                ]
            }
            mapeo_df = pd.DataFrame(mapeo_data)
            mapeo_df.to_excel(writer, sheet_name='mapeo_campos', index=False)
            
            # Estadísticas de transformación
            stats_data = {
                'Concepto': [
                    'Registros originales (limpios)',
                    'Registros transformados',
                    'Registros excluidos',
                    'ID ATENCION únicos',
                    'ID MASCOTA únicos', 
                    'Longitud promedio notas',
                    'Fecha procesamiento',
                    'Rango fechas (inicio)',
                    'Rango fechas (fin)'
                ],
                'Valor': [
                    total_original,
                    len(df_transformed),
                    len(df_excluded),
                    id_atencion_unicos,
                    id_mascota_unicos,
                    f"{df_transformed['nota_length'].mean():.0f} chars" if 'nota_length' in df_transformed.columns else 'N/A',
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    df_transformed['FECHA'].min().strftime('%Y-%m-%d') if df_transformed['FECHA'].notna().sum() > 0 else 'N/A',
                    df_transformed['FECHA'].max().strftime('%Y-%m-%d') if df_transformed['FECHA'].notna().sum() > 0 else 'N/A'
                ]
            }
            stats_df = pd.DataFrame(stats_data)
            stats_df.to_excel(writer, sheet_name='estadisticas', index=False)
        
        add_to_report(f"Archivo Excel guardado: {output_file}")
        add_to_report(f"Estructura del archivo:")
        add_to_report(f"  - datos_limpios: {len(df_transformed):,} registros (listos para importar)")
        if len(df_excluded) > 0:
            add_to_report(f"  - datos_excluidos: {len(df_excluded):,} registros")
        add_to_report(f"  - mapeo_campos: documentación del mapeo de campos")
        add_to_report(f"  - estadisticas: métricas de la transformación")
        
        add_to_report("")
        add_to_report("9. RESUMEN DE TRANSFORMACIÓN")
        add_to_report("-" * 40)
        add_to_report(f"Registros originales: {total_original:,}")
        add_to_report(f"Registros procesados: {len(df_transformed):,}")
        add_to_report(f"Registros excluidos: {len(df_excluded):,}")
        add_to_report(f"Tasa de éxito: {(len(df_transformed)/total_original)*100:.1f}%")
        
        # Mostrar muestra de datos transformados
        add_to_report("")
        add_to_report("MUESTRA DE DATOS TRANSFORMADOS:")
        add_to_report("-" * 40)
        for i, row in df_transformed.head(3).iterrows():
            add_to_report(f"Registro {i+1}:")
            add_to_report(f"  ID ATENCION: {row['ID ATENCION']}")
            add_to_report(f"  ID MASCOTA: {row['ID MASCOTA']}")
            add_to_report(f"  FECHA: {row['FECHA'].strftime('%Y-%m-%d') if pd.notna(row['FECHA']) else 'N/A'}")
            add_to_report(f"  NOTAS: {row['NOTAS'][:100]}{'...' if len(str(row['NOTAS'])) > 100 else ''}")
            add_to_report("")
            
        return df_transformed
        
    except Exception as e:
        add_to_report(f"ERROR: {str(e)}")
        import traceback
        add_to_report(traceback.format_exc())
        return

def validate_output(output_file):
    """
    Valida que el archivo de salida sea correcto
    """
    if not output_file or not os.path.exists(output_file):
        print(f"ERROR: El archivo de salida no existe: {output_file}")
        return False
        
    try:
        # Verificar estructura del archivo
        xl = pd.ExcelFile(output_file)
        required_sheets = ['datos_limpios', 'mapeo_campos', 'estadisticas']
        
        for sheet in required_sheets:
            if sheet not in xl.sheet_names:
                print(f"ERROR: Falta la hoja {sheet}")
                return False
        
        # Verificar datos limpios
        df_clean = pd.read_excel(output_file, sheet_name='datos_limpios')
        required_columns = ['ID ATENCION', 'ID MASCOTA', 'FECHA', 'NOTAS']
        
        for col in required_columns:
            if col not in df_clean.columns:
                print(f"ERROR: Falta la columna {col}")
                return False
        
        print(f"[OK] Validación exitosa: {len(df_clean)} registros listos para importar")
        return True
        
    except Exception as e:
        print(f"ERROR en validación: {e}")
        return False

def main():
    """Función principal"""
    import sys
    
    print("[>>] TRANSFORMANDO PRESCRIPCIONES AL FORMATO NOTAS")
    
    # Verificar argumentos
    if len(sys.argv) >= 4:
        source_file = sys.argv[1]
        client_name = sys.argv[2]
        generation_dir = sys.argv[3]
        
        print(f"[DIR] Archivo fuente original: {source_file}")
        print(f"[USER] Cliente: {client_name}")
        print(f"[FOLDER] Directorio generation: {generation_dir}")
        
        input_file = source_file  # Para buscar el organized
        output_dir = generation_dir
    else:
        print("[WARN]  Usando modo compatibilidad - rutas por defecto")
        input_file = None
        output_dir = None
    
    try:
        result = transform_to_import(input_file, output_dir)
        if result is not None:
            output_file = os.path.join(output_dir or "../generation", "prescripcion_import_transformed.xlsx")
            if validate_output(output_file):
                print(f"\n[OK] Transformación completada exitosamente")
                print(f"[DIR] Archivo listo para importación: {os.path.basename(output_file)}")
    except Exception as e:
        print(f"[X] Error durante la transformación: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()