import pandas as pd
from datetime import datetime
import os
import math

def generate_excel_import_template_apuntes_safe():
    """
    Genera archivos Excel con formato MySQL-safe para concatenación de notas
    Usa separadores explícitos en lugar de saltos de línea
    """
    
    file_path = "/Users/enrique/Proyectos/imports/source/cuvet.xlsx"
    
    # Configuración
    RECORDS_PER_FILE = 10000
    CLINIC_RECORD_ID_START = 1200707  # EDITAR SEGÚN TU BASE DE DATOS
    
    # Opciones de separadores (elige el que prefieras)
    SEPARATOR_OPTIONS = {
        'pipe': ' | ',                    # Opción 1: Pipe con espacios
        'bullet': ' • ',                  # Opción 2: Bullet point
        'marker': '[PÁRRAFO]',           # Opción 3: Marcador explícito
        'html': '<br><br>',              # Opción 4: HTML breaks
        'double_newline': '\n\n'         # Opción 5: Doble salto (original)
    }
    
    # SELECCIONAR SEPARADOR AQUÍ:
    SELECTED_SEPARATOR = 'marker'  # Cambiar por: 'pipe', 'bullet', 'marker', 'html', 'double_newline'
    NOTE_SEPARATOR = SEPARATOR_OPTIONS[SELECTED_SEPARATOR]
    
    print(f"Generando archivos con separador: '{NOTE_SEPARATOR}' ({SELECTED_SEPARATOR})")
    print("Leyendo datos de apuntes...")
    
    # Leer la pestaña de apuntes
    df_apuntes = pd.read_excel(file_path, sheet_name='apuntes')
    
    print(f"Registros totales en apuntes: {len(df_apuntes)}")
    
    # Filtrar registros activos
    df_apuntes_filtered = df_apuntes[df_apuntes['IsDeleted'] == 0].copy()
    print(f"Apuntes activos (IsDeleted=0): {len(df_apuntes_filtered)}")
    
    # Verificar que tenemos PatientId válidos
    df_apuntes_filtered = df_apuntes_filtered[df_apuntes_filtered['PatientId'].notna()].copy()
    print(f"Apuntes con PatientId válido: {len(df_apuntes_filtered)}")
    
    # Crear claves de agrupación usando PatientId original
    df_apuntes_filtered['DataDate'] = pd.to_datetime(df_apuntes_filtered['DataDate'])
    df_apuntes_filtered['date_only'] = df_apuntes_filtered['DataDate'].dt.date
    df_apuntes_filtered['patient_date_key'] = (
        df_apuntes_filtered['PatientId'].astype(str) + '_' + 
        df_apuntes_filtered['date_only'].astype(str)
    )
    
    print(f"Rango de fechas: {df_apuntes_filtered['DataDate'].min()} a {df_apuntes_filtered['DataDate'].max()}")
    
    # === AGRUPAR Y CONCATENAR NOTAS ===
    print(f"\n=== AGRUPANDO NOTAS CON SEPARADOR '{NOTE_SEPARATOR}' ===")
    
    def concatenate_notes_safe(group):
        """Concatena notas con separador MySQL-safe y hora antes de cada párrafo"""
        # Ordenar por fecha (más antigua primero)
        group_sorted = group.sort_values('DataDate')
        
        # Recopilar notas no vacías
        notes_list = []
        for _, row in group_sorted.iterrows():
            note_text = row['NoteText'] if pd.notna(row['NoteText']) else ''
            if note_text.strip():
                # Limpiar la nota individual
                clean_note = str(note_text).strip()
                notes_list.append(clean_note)
        
        # Unir con el separador [PÁRRAFO] que se convertirá a doble salto después
        concatenated_notes = NOTE_SEPARATOR.join(notes_list)
        
        return pd.Series({
            'original_patient_id': group_sorted['PatientId'].iloc[0],
            'earliest_date': group_sorted['DataDate'].min(),
            'latest_date': group_sorted['DataDate'].max(),
            'concatenated_notes': concatenated_notes,
            'note_count': len(notes_list),
            'separator_used': SELECTED_SEPARATOR
        })
    
    # Agrupar por paciente/fecha
    grouped_notes = df_apuntes_filtered.groupby('patient_date_key').apply(concatenate_notes_safe).reset_index()
    
    print(f"Registros únicos después de agrupar: {len(grouped_notes)}")
    print(f"Total notas originales: {len(df_apuntes_filtered)}")
    
    # Estadísticas de concatenación
    multiple_notes = grouped_notes[grouped_notes['note_count'] > 1]
    print(f"Registros con notas concatenadas: {len(multiple_notes)}")
    if len(multiple_notes) > 0:
        max_notes = multiple_notes['note_count'].max()
        avg_notes = multiple_notes['note_count'].mean()
        print(f"Máximo notas concatenadas: {max_notes}")
        print(f"Promedio notas concatenadas: {avg_notes:.1f}")
    
    # === GENERAR IDs ÚNICOS ===
    print(f"\n=== GENERANDO IDs ÚNICOS ===")
    
    grouped_notes = grouped_notes.sort_values('earliest_date').reset_index(drop=True)
    grouped_notes['import_clinic_record_id'] = range(
        CLINIC_RECORD_ID_START, 
        CLINIC_RECORD_ID_START + len(grouped_notes)
    )
    
    print(f"IDs generados desde {CLINIC_RECORD_ID_START} hasta {CLINIC_RECORD_ID_START + len(grouped_notes) - 1}")
    
    # === CREAR ESTRUCTURA PARA EXCEL ===
    print(f"\n=== CREANDO ESTRUCTURA EXCEL ===")
    
    excel_data = []
    for _, row in grouped_notes.iterrows():
        excel_data.append({
            'A': row['import_clinic_record_id'],
            'B': int(row['original_patient_id']),
            'C': row['earliest_date'].strftime('%Y-%m-%d %H:%M:%S'),
            'D': row['concatenated_notes']
        })
    
    df_excel = pd.DataFrame(excel_data)
    
    # === DIVIDIR EN ARCHIVOS ===
    print(f"\n=== DIVIDIENDO EN ARCHIVOS DE {RECORDS_PER_FILE} REGISTROS ===")
    
    # Crear directorio de salida si no existe
    output_dir = "/Users/enrique/Proyectos/imports/generated_files/notes"
    os.makedirs(output_dir, exist_ok=True)
    
    total_records = len(df_excel)
    total_files = math.ceil(total_records / RECORDS_PER_FILE)
    
    print(f"Total registros: {total_records}")
    print(f"Archivos a generar: {total_files}")
    print(f"Directorio de salida: {output_dir}")
    
    generated_files = []
    
    for file_num in range(total_files):
        start_idx = file_num * RECORDS_PER_FILE
        end_idx = min((file_num + 1) * RECORDS_PER_FILE, total_records)
        
        chunk_data = df_excel.iloc[start_idx:end_idx].copy()
        
        # Nombre descriptivo del archivo
        output_file = f"{output_dir}/import_apuntes_{SELECTED_SEPARATOR}_{file_num + 1:03d}.xlsx"
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # Hoja principal
            chunk_data.to_excel(writer, sheet_name='import_data', index=False)
            
            # Hoja de información
            info_data = {
                'Campo': ['A', 'B', 'C', 'D'],
                'Descripcion': [
                    'import_clinic_record_id',
                    'patient_id_original', 
                    'created_at',
                    'notas'
                ],
                'Detalle': [
                    f'IDs únicos del {chunk_data["A"].min()} al {chunk_data["A"].max()}',
                    'PatientId original del sistema de origen',
                    'Fecha más antigua del grupo',
                    f'Notas concatenadas. Separador entre párrafos: {NOTE_SEPARATOR}'
                ]
            }
            
            df_info = pd.DataFrame(info_data)
            df_info.to_excel(writer, sheet_name='info', index=False)
            
            # Hoja de resumen
            summary_data = {
                'Descripcion': [
                    'Archivo numero',
                    'Separador usado',
                    'Registros en este archivo',
                    'Rango de registros',
                    'ID inicial',
                    'ID final',
                    'Fecha generacion',
                    'Total archivos',
                    'Total registros',
                    'Notas concatenadas',
                    'Compatibilidad MySQL'
                ],
                'Valor': [
                    f'{file_num + 1} de {total_files}',
                    f'{NOTE_SEPARATOR} ({SELECTED_SEPARATOR})',
                    len(chunk_data),
                    f'{start_idx + 1}-{end_idx}',
                    chunk_data['A'].min(),
                    chunk_data['A'].max(),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    total_files,
                    total_records,
                    len(multiple_notes),
                    'Optimizado para importación'
                ]
            }
            
            df_summary = pd.DataFrame(summary_data)
            df_summary.to_excel(writer, sheet_name='resumen', index=False)
        
        generated_files.append(output_file)
        print(f"Archivo {file_num + 1}/{total_files} generado: {output_file}")
        print(f"  Registros: {len(chunk_data)} (IDs: {chunk_data['A'].min()}-{chunk_data['A'].max()})")
    
    # === GUARDAR MAPEO ACTUALIZADO ===
    print(f"\n=== GENERANDO MAPEO ACTUALIZADO ===")
    
    mapping_file = f"{output_dir}/clinic_record_id_mapping_{SELECTED_SEPARATOR}.csv"
    
    mapping_data = []
    for _, row in grouped_notes.iterrows():
        mapping_data.append({
            'patient_date_key': row['patient_date_key'],
            'import_clinic_record_id': row['import_clinic_record_id'],
            'original_patient_id': row['original_patient_id'],
            'date': row['patient_date_key'].split('_')[1],
            'earliest_date': row['earliest_date'].strftime('%Y-%m-%d %H:%M:%S'),
            'note_count': row['note_count'],
            'separator_used': row['separator_used']
        })
    
    df_mapping = pd.DataFrame(mapping_data)
    df_mapping.to_csv(mapping_file, index=False)
    
    print(f"Mapeo guardado en: {mapping_file}")
    
    # === MOSTRAR EJEMPLOS ===
    print(f"\n=== EJEMPLOS CON SEPARADOR '{NOTE_SEPARATOR}' ===")
    
    # Mostrar ejemplos de notas concatenadas
    concatenated_examples = df_excel[df_excel['D'].str.contains(NOTE_SEPARATOR.replace('[', r'\[').replace(']', r'\]'), na=False)].head(3)
    
    for i, (_, row) in enumerate(concatenated_examples.iterrows(), 1):
        print(f"\nEjemplo {i} de nota concatenada:")
        print(f"  ID: {row['A']}")
        print(f"  Pet: {row['B']}")
        print(f"  Fecha: {row['C']}")
        print(f"  Nota: {row['D'][:150]}...")
        
        # Mostrar cómo se separaría de vuelta
        parts = row['D'].split(NOTE_SEPARATOR)
        print(f"  Párrafos separados: {len(parts)}")
        for j, part in enumerate(parts[:3], 1):  # Mostrar solo los primeros 3
            print(f"    {j}. {part[:50]}...")
    
    # === ESTADÍSTICAS FINALES ===
    print(f"\n=== ESTADÍSTICAS FINALES ===")
    print(f"✅ Separador usado: '{NOTE_SEPARATOR}' ({SELECTED_SEPARATOR})")
    print(f"✅ Archivos Excel generados: {total_files}")
    print(f"✅ Total registros procesados: {total_records}")
    print(f"✅ Rango de IDs: {CLINIC_RECORD_ID_START} - {CLINIC_RECORD_ID_START + total_records - 1}")
    print(f"✅ Registros con notas concatenadas: {len(multiple_notes)}")
    print(f"✅ Compatibilidad MySQL: Optimizada")
    
    print(f"\n📁 Archivos generados con separador '{SELECTED_SEPARATOR}':")
    for i, file_path in enumerate(generated_files, 1):
        print(f"  {i}. {file_path}")
    
    print(f"\n🔄 Para cambiar separador, edita SELECTED_SEPARATOR en línea 20")
    print(f"Opciones: {list(SEPARATOR_OPTIONS.keys())}")
    
    return generated_files, mapping_file

if __name__ == "__main__":
    generate_excel_import_template_apuntes_safe()
