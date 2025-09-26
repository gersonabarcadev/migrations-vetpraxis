"""
Clase base para todos los procesadores de sistemas veterinarios
"""
from abc import ABC, abstractmethod
import json
import os
from typing import Dict, Any, List
import pandas as pd
from pathlib import Path


class BaseProcessor(ABC):
    """Clase base abstracta para procesadores de sistemas veterinarios"""
    
    def __init__(self, client_path: str):
        """
        Inicializa el procesador
        
        Args:
            client_path: Ruta a la carpeta del cliente
        """
        self.client_path = Path(client_path)
        self.config = self._load_config()
        self.raw_data_path = self.client_path / "raw_data"
        self.processed_path = self.client_path / "processed"
        self.output_path = self.client_path / "output"
        self.reports_path = self.client_path / "reports"
        
        # Crear carpetas si no existen
        for path in [self.processed_path, self.output_path, self.reports_path]:
            path.mkdir(exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Carga la configuración del cliente"""
        config_path = self.client_path / "config.json"
        if config_path.exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    @abstractmethod
    def process_raw_data(self) -> bool:
        """
        Procesa los datos raw del cliente
        
        Returns:
            True si el procesamiento fue exitoso, False en caso contrario
        """
        pass
    
    @abstractmethod
    def generate_output_files(self) -> bool:
        """
        Genera los archivos de salida en formato VetPraxis
        
        Returns:
            True si la generación fue exitosa, False en caso contrario
        """
        pass
    
    @abstractmethod
    def validate_data(self) -> Dict[str, Any]:
        """
        Valida los datos procesados
        
        Returns:
            Diccionario con resultados de validación
        """
        pass
    
    def generate_report(self, validation_results: Dict[str, Any]) -> str:
        """
        Genera un reporte de procesamiento
        
        Args:
            validation_results: Resultados de validación
            
        Returns:
            Ruta al archivo de reporte generado
        """
        report_path = self.reports_path / "processing_report.txt"
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"Reporte de Procesamiento - {self.config.get('client_info', {}).get('name', 'Cliente')}\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"Sistema origen: {self.config.get('source_system', {}).get('type', 'Desconocido')}\n")
            f.write(f"Fecha de procesamiento: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write("Resultados de validación:\n")
            f.write("-" * 40 + "\n")
            for key, value in validation_results.items():
                f.write(f"{key}: {value}\n")
        
        return str(report_path)
    
    def run_full_process(self) -> bool:
        """
        Ejecuta el proceso completo de migración
        
        Returns:
            True si todo el proceso fue exitoso
        """
        try:
            print(f"Iniciando procesamiento para {self.config.get('client_info', {}).get('name', 'Cliente')}")
            
            # Paso 1: Procesar datos raw
            print("Paso 1: Procesando datos raw...")
            if not self.process_raw_data():
                print("Error en el procesamiento de datos raw")
                return False
            
            # Paso 2: Generar archivos de salida
            print("Paso 2: Generando archivos de salida...")
            if not self.generate_output_files():
                print("Error en la generación de archivos de salida")
                return False
            
            # Paso 3: Validar datos
            print("Paso 3: Validando datos...")
            validation_results = self.validate_data()
            
            # Paso 4: Generar reporte
            print("Paso 4: Generando reporte...")
            report_path = self.generate_report(validation_results)
            print(f"Reporte generado en: {report_path}")
            
            print("Procesamiento completado exitosamente")
            return True
            
        except Exception as e:
            print(f"Error durante el procesamiento: {str(e)}")
            return False
