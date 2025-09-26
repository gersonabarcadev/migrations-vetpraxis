#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para transformar apuntes al formato de importación
Mapeo de campos:
- NoteId -> ID ATENCION
- PatientId -> ID MASCOTA  
- DataDate -> FECHA
- NoteText -> NOTAS
"""

import pandas as pd
import os
import sys
import re
from datetime import datetime

def clean_text_for_excel(text):
    """
    Limpia texto para evitar problemas de corrupción en Excel.
    Elimina caracteres de control, emojis y otros caracteres problemáticos.
    """
    if pd.isna(text) or text == '':
        return text
    
    # Convertir a string si no lo es
    text = str(text)
    
    # Eliminar TODOS los caracteres de control (excepto space, tab, newline)
    text = re.sub(r'[\x00-\x1f\x7f-\x9f]', ' ', text)
    
    # Eliminar emojis y símbolos Unicode problemáticos
    text = re.sub(r'[\U0001F600-\U0001F64F]', '', text)  # emoticons
    text = re.sub(r'[\U0001F300-\U0001F5FF]', '', text)  # symbols & pictographs
    text = re.sub(r'[\U0001F680-\U0001F6FF]', '', text)  # transport & map symbols
    text = re.sub(r'[\U0001F1E0-\U0001F1FF]', '', text)  # flags
    text = re.sub(r'[\U00002600-\U000026FF]', '', text)  # miscellaneous symbols
    text = re.sub(r'[\U00002700-\U000027BF]', '', text)  # dingbats
    
    # Eliminar caracteres que pueden causar problemas en XML/Excel
    text = re.sub(r'[<>&"\']', '', text)  # caracteres XML problemáticos
    text = re.sub(r'[\u200B-\u200F\u2028-\u202F\u205F-\u206F]', '', text)  # espacios Unicode
    
    # Solo mantener caracteres ASCII básicos + tildes y ñ españolas
    text = re.sub(r'[^\x20-\x7E\u00C0-\u00FF\u0100-\u017F]', '', text)
    
    # Eliminar caracteres que pueden interpretarse como fórmulas
    text = re.sub(r'^[=+\-@]', '', text)  # quitar = + - @ al inicio
    
    # Limpiar espacios múltiples y caracteres problemáticos
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Limitar longitud para evitar problemas (Excel tiene límites por celda)
    if len(text) > 32767:  # límite de Excel por celda
        text = text[:32767]
    
    return text

# Configurar UTF-8 para Windows
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

def transform_to_import(input_file=None, output_dir=None):
    """
    Transforma los datos de apuntes al formato de importación NOTAS
    """
    
    # Configurar rutas por defecto si no se proporcionan
    if input_file is None:
        source_file = "../generation/apuntes_organized.xlsx"
    else:
        source_file = input_file
    
    if output_dir is None:
        output_dir = "../generation"
    
    # Crear directorio de salida si no existe
    os.makedirs(output_dir, exist_ok=True)
    
    output_file = os.path.join(output_dir, f"apuntes_import_transformed.xlsx")
    
    print("=" * 80)
    print("TRANSFORMACIÓN DE APUNTES A FORMATO DE IMPORTACIÓN")
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
        # Si tenemos archivo Excel con hojas, buscar la hoja de apuntes
        if source_file.endswith('.xlsx'):
            # Intentar leer directamente de la hoja apuntes
            try:
                source_df = pd.read_excel(source_file, sheet_name='apuntes')
                add_to_report("[OK] Cargando datos desde hoja 'apuntes'")
            except:
                # Si no existe, intentar cargar el archivo completo
                xl = pd.ExcelFile(source_file)
                if 'apuntes' in xl.sheet_names:
                    source_df = pd.read_excel(source_file, sheet_name='apuntes')
                    add_to_report("[OK] Cargando datos desde hoja 'apuntes'")
                else:
                    # Buscar hoja que contenga datos de notas
                    found_sheet = None
                    for sheet in xl.sheet_names:
                        if any(keyword in sheet.lower() for keyword in ['apuntes', 'nota', 'note']):
                            found_sheet = sheet
                            break
                    
                    if found_sheet:
                        source_df = pd.read_excel(source_file, sheet_name=found_sheet)
                        add_to_report(f"[OK] Cargando datos desde hoja '{found_sheet}'")
                    else:
                        add_to_report("[X] No se encontró hoja de apuntes en el archivo")
                        return None
        else:
            add_to_report(f"[X] Formato de archivo no soportado: {source_file}")
            return None
        
        add_to_report("1. CARGANDO DATOS ORIGEN")
        add_to_report("-" * 40)
        add_to_report(f"Registros cargados: {len(source_df):,}")
        add_to_report(f"Columnas origen: {list(source_df.columns)}")
        add_to_report("")
        
        add_to_report("2. APLICANDO FILTROS Y VALIDACIONES")
        add_to_report("-" * 40)
        
        # Registros originales
        total_original = len(source_df)
        add_to_report(f"Registros originales: {total_original:,}")
        
        # Filtrar registros eliminados si existe la columna
        if 'IsDeleted' in source_df.columns:
            before_filter = len(source_df)
            source_df = source_df[source_df['IsDeleted'] == 0]
            after_filter = len(source_df)
            removed = before_filter - after_filter
            if removed > 0:
                add_to_report(f"  - Removidos {removed:,} registros eliminados")
        
        # Filtrar registros con datos requeridos
        required_fields = ['NoteId', 'PatientId', 'DataDate']
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
        
        # Verificar duplicados por NoteId
        if 'NoteId' in source_df.columns:
            duplicates = source_df['NoteId'].duplicated().sum()
            if duplicates > 0:
                add_to_report(f"  [WARN]  Se encontraron {duplicates} duplicados por NoteId")
                source_df = source_df.drop_duplicates(subset=['NoteId'], keep='first')
                add_to_report(f"  - Registros después de eliminar duplicados: {len(source_df):,}")
        
        add_to_report("")
        
        add_to_report("3. APLICANDO TRANSFORMACIONES")
        add_to_report("-" * 40)
        
        # Crear el DataFrame transformado
        df_transformed = pd.DataFrame()
        
        # Mapear columnas según especificación del formato NOTAS
        add_to_report("Aplicando mapeo para formato NOTAS:")
        
        # 1. ID ATENCION <- NoteId
        df_transformed['ID ATENCION'] = source_df['NoteId'] if 'NoteId' in source_df.columns else None
        add_to_report("  - NoteId -> ID ATENCION")
        
        # 2. ID MASCOTA <- PatientId
        df_transformed['ID MASCOTA'] = source_df['PatientId'] if 'PatientId' in source_df.columns else None
        add_to_report("  - PatientId -> ID MASCOTA")
        
        # 3. FECHA <- DataDate
        df_transformed['FECHA'] = pd.to_datetime(source_df['DataDate']) if 'DataDate' in source_df.columns else None
        add_to_report("  - DataDate -> FECHA")
        
        # 4. NOTAS <- NoteText (directamente, ya que es texto libre)
        if 'NoteText' in source_df.columns:
            # Mapear las columnas restantes
            df_transformed['NOTAS'] = source_df['NoteText'].fillna('Apunte sin contenido').apply(clean_text_for_excel)
        else:
            df_transformed['NOTAS'] = 'Apunte sin texto disponible'
        add_to_report("  - NoteText -> NOTAS")
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
        
        add_to_report("6. GUARDANDO RESULTADO EN MÚLTIPLES HOJAS")
        add_to_report("-" * 40)
        
        # Limpiar todo el DataFrame antes de escribir
        for col in df_transformed.columns:
            if df_transformed[col].dtype == 'object':
                df_transformed[col] = df_transformed[col].apply(clean_text_for_excel)
        
        # Crear el archivo Excel con múltiples hojas
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            
            # Hoja principal: datos listos para importar
            df_final = df_transformed.drop('nota_length', axis=1, errors='ignore')
            df_final.to_excel(writer, sheet_name='datos_limpios', index=False)
            
            # Hoja de mapeo de campos
            mapeo_data = {
                'Campo_Origen': [
                    'NoteId',
                    'PatientId', 
                    'DataDate',
                    'NoteText'
                ],
                'Campo_Destino': [
                    'ID ATENCION',
                    'ID MASCOTA',
                    'FECHA', 
                    'NOTAS'
                ],
                'Descripcion': [
                    'ID único del apunte',
                    'ID del paciente/mascota',
                    'Fecha del apunte',
                    'Texto completo del apunte'
                ],
                'Formato': [
                    'Entero',
                    'Entero',
                    'YYYY-MM-DD',
                    'Texto libre'
                ]
            }
            mapeo_df = pd.DataFrame(mapeo_data)
            mapeo_df.to_excel(writer, sheet_name='mapeo_campos', index=False)
            
            # Estadísticas de transformación
            stats_data = {
                'Concepto': [
                    'Registros originales',
                    'Registros transformados',
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
        add_to_report(f"  - mapeo_campos: documentación del mapeo de campos")
        add_to_report(f"  - estadisticas: métricas de la transformación")
        
        add_to_report("")
        add_to_report("7. RESUMEN DE TRANSFORMACIÓN")
        add_to_report("-" * 40)
        add_to_report(f"Registros originales: {total_original:,}")
        add_to_report(f"Registros procesados: {len(df_transformed):,}")
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
            add_to_report(f"  NOTAS: {str(row['NOTAS'])[:100]}{'...' if len(str(row['NOTAS'])) > 100 else ''}")
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
    
    print("[>>] TRANSFORMANDO APUNTES AL FORMATO NOTAS")
    
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
        result = transform_to_import(input_file, output_dir)
        if result is not None:
            output_file = os.path.join(output_dir or "../generation", "apuntes_import_transformed.xlsx")
            if validate_output(output_file):
                print(f"\n[OK] Transformación completada exitosamente")
                print(f"[DIR] Archivo listo para importación: {os.path.basename(output_file)}")
    except Exception as e:
        print(f"[X] Error durante la transformación: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()