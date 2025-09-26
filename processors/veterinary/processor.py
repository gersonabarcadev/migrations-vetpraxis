"""
Procesador específico para sistema Veterinary
"""
import pandas as pd
import sqlite3
from typing import Dict, Any, List
from pathlib import Path
import sys
import os

# Añadir el directorio padre al path para importar BaseProcessor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from processors import BaseProcessor


class VeterinaryProcessor(BaseProcessor):
    """Procesador específico para backups del sistema Veterinary"""
    
    def __init__(self, client_path: str):
        super().__init__(client_path)
        self.system_type = "veterinary"
    
    def process_raw_data(self) -> bool:
        """
        Procesa los datos raw del sistema Veterinary
        
        Returns:
            True si el procesamiento fue exitoso
        """
        try:
            # Buscar archivos SQL en raw_data
            sql_files = list(self.raw_data_path.glob("*.sql"))
            excel_files = list(self.raw_data_path.glob("*.xlsx"))
            
            if sql_files:
                return self._process_sql_backup(sql_files[0])
            elif excel_files:
                return self._process_excel_backup(excel_files[0])
            else:
                print("No se encontraron archivos SQL o Excel en raw_data")
                return False
                
        except Exception as e:
            print(f"Error procesando datos raw: {str(e)}")
            return False
    
    def _process_sql_backup(self, sql_file: Path) -> bool:
        """Procesa un backup SQL del sistema Veterinary"""
        try:
            # Crear una base de datos temporal en memoria
            conn = sqlite3.connect(':memory:')
            
            # Leer y ejecutar el archivo SQL
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
                # Ejecutar comandos SQL (esto es una simplificación)
                conn.executescript(sql_content)
            
            # Extraer tablas principales
            tables = ['clientes', 'mascotas', 'consultas', 'vacunas', 'procedimientos']
            
            for table in tables:
                try:
                    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
                    output_path = self.processed_path / f"{table}.csv"
                    df.to_csv(output_path, index=False, encoding='utf-8')
                except Exception as e:
                    print(f"Warning: No se pudo extraer tabla {table}: {str(e)}")
            
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error procesando SQL backup: {str(e)}")
            return False
    
    def _process_excel_backup(self, excel_file: Path) -> bool:
        """Procesa un backup Excel del sistema Veterinary"""
        try:
            # Leer todas las hojas del Excel
            excel_data = pd.read_excel(excel_file, sheet_name=None)
            
            # Guardar cada hoja como CSV
            for sheet_name, df in excel_data.items():
                output_path = self.processed_path / f"{sheet_name}.csv"
                df.to_csv(output_path, index=False, encoding='utf-8')
            
            return True
            
        except Exception as e:
            print(f"Error procesando Excel backup: {str(e)}")
            return False
    
    def generate_output_files(self) -> bool:
        """
        Genera archivos Excel en formato VetPraxis
        
        Returns:
            True si la generación fue exitosa
        """
        try:
            data_types = self.config.get('data_types', {})
            
            # Generar cada tipo de archivo si está habilitado
            if data_types.get('apuntes', False):
                self._generate_apuntes()
            
            if data_types.get('diagnosticos', False):
                self._generate_diagnosticos()
            
            if data_types.get('prescripciones', False):
                self._generate_prescripciones()
            
            if data_types.get('procedimientos', False):
                self._generate_procedimientos()
            
            if data_types.get('vacunas', False):
                self._generate_vacunas()
            
            return True
            
        except Exception as e:
            print(f"Error generando archivos de salida: {str(e)}")
            return False
    
    def _generate_apuntes(self):
        """Genera el archivo de apuntes/notas"""
        # Buscar archivo de consultas procesado
        consultas_file = self.processed_path / "consultas.csv"
        if consultas_file.exists():
            df = pd.read_csv(consultas_file)
            # Aquí iría la lógica de mapeo específica para apuntes
            # Por ahora, creamos un archivo de ejemplo
            output_file = self.output_path / "apuntes_import.xlsx"
            df.to_excel(output_file, index=False)
    
    def _generate_diagnosticos(self):
        """Genera el archivo de diagnósticos"""
        pass  # Implementar según estructura específica
    
    def _generate_prescripciones(self):
        """Genera el archivo de prescripciones"""
        pass  # Implementar según estructura específica
    
    def _generate_procedimientos(self):
        """Genera el archivo de procedimientos"""
        pass  # Implementar según estructura específica
    
    def _generate_vacunas(self):
        """Genera el archivo de vacunas"""
        vacunas_file = self.processed_path / "vacunas.csv"
        if vacunas_file.exists():
            df = pd.read_csv(vacunas_file)
            output_file = self.output_path / "vacunas_import.xlsx"
            df.to_excel(output_file, index=False)
    
    def validate_data(self) -> Dict[str, Any]:
        """
        Valida los datos procesados
        
        Returns:
            Diccionario con resultados de validación
        """
        results = {}
        
        # Contar registros en archivos procesados
        for csv_file in self.processed_path.glob("*.csv"):
            df = pd.read_csv(csv_file)
            results[f"registros_{csv_file.stem}"] = len(df)
        
        # Contar archivos de salida generados
        output_files = list(self.output_path.glob("*.xlsx"))
        results["archivos_salida_generados"] = len(output_files)
        
        # Validaciones adicionales
        results["validacion_exitosa"] = len(output_files) > 0
        
        return results
