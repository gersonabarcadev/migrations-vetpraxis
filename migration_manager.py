#!/usr/bin/env python3
"""
Script principal para administrar migraciones de clientes a VetPraxis
"""
import os
import sys
import argparse
from pathlib import Path
import json

# Añadir el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from processors.veterinary import VeterinaryProcessor
# from processors.qvet import QVetProcessor
# from processors.gvet import GVetProcessor
# from processors.cuvet import CuVetProcessor


class MigrationManager:
    """Administrador principal de migraciones"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent
        self.clients_path = self.project_root / "clients"
        
        # Mapeo de sistemas a procesadores
        self.processors = {
            'veterinary': VeterinaryProcessor,
            # 'qvet': QVetProcessor,
            # 'gvet': GVetProcessor,
            # 'cuvet': CuVetProcessor,
        }
    
    def list_clients(self):
        """Lista todos los clientes disponibles"""
        if not self.clients_path.exists():
            print("No existe la carpeta de clientes")
            return []
        
        clients = []
        for client_dir in self.clients_path.iterdir():
            if client_dir.is_dir():
                config_file = client_dir / "config.json"
                if config_file.exists():
                    with open(config_file, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                    clients.append({
                        'folder': client_dir.name,
                        'name': config.get('client_info', {}).get('name', 'Sin nombre'),
                        'system': config.get('source_system', {}).get('type', 'Desconocido')
                    })
        
        return clients
    
    def create_client(self, client_name: str, system_type: str):
        """
        Crea una nueva carpeta de cliente con estructura básica
        
        Args:
            client_name: Nombre del cliente (se convertirá en nombre de carpeta)
            system_type: Tipo de sistema (veterinary, qvet, gvet, cuvet)
        """
        # Crear nombre de carpeta seguro
        folder_name = f"{client_name.lower().replace(' ', '_')}_{system_type}"
        client_path = self.clients_path / folder_name
        
        # Crear estructura de carpetas
        for subdir in ['raw_data', 'processed', 'output', 'reports']:
            (client_path / subdir).mkdir(parents=True, exist_ok=True)
        
        # Crear archivo de configuración
        config = {
            "client_info": {
                "name": client_name,
                "contact": "",
                "subsidiary_id": "",
                "migration_date": ""
            },
            "source_system": {
                "type": system_type,
                "version": "",
                "database": "",
                "encoding": "utf-8"
            },
            "processing_config": {
                "batch_size": 1000,
                "validate_data": True,
                "generate_reports": True,
                "skip_empty_records": True
            },
            "field_mappings": {},
            "data_types": {
                "apuntes": True,
                "diagnosticos": True,
                "prescripciones": True,
                "procedimientos": True,
                "vacunas": True,
                "datos_control": False
            }
        }
        
        config_file = client_path / "config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        print(f"Cliente creado exitosamente en: {client_path}")
        print(f"Por favor, coloque los archivos del backup en: {client_path / 'raw_data'}")
        return str(client_path)
    
    def process_client(self, client_folder: str):
        """
        Procesa un cliente específico
        
        Args:
            client_folder: Nombre de la carpeta del cliente
        """
        client_path = self.clients_path / client_folder
        
        if not client_path.exists():
            print(f"Error: No existe el cliente {client_folder}")
            return False
        
        # Cargar configuración
        config_file = client_path / "config.json"
        if not config_file.exists():
            print(f"Error: No existe archivo de configuración para {client_folder}")
            return False
        
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        system_type = config.get('source_system', {}).get('type', '')
        
        if system_type not in self.processors:
            print(f"Error: Sistema {system_type} no soportado")
            print(f"Sistemas disponibles: {', '.join(self.processors.keys())}")
            return False
        
        # Crear procesador y ejecutar
        processor_class = self.processors[system_type]
        processor = processor_class(str(client_path))
        
        return processor.run_full_process()


def main():
    parser = argparse.ArgumentParser(description='Administrador de migraciones VetPraxis')
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando list
    subparsers.add_parser('list', help='Listar todos los clientes')
    
    # Comando create
    create_parser = subparsers.add_parser('create', help='Crear nuevo cliente')
    create_parser.add_argument('name', help='Nombre del cliente')
    create_parser.add_argument('system', choices=['veterinary', 'qvet', 'gvet', 'cuvet'],
                              help='Tipo de sistema de origen')
    
    # Comando process
    process_parser = subparsers.add_parser('process', help='Procesar cliente')
    process_parser.add_argument('client', help='Nombre de carpeta del cliente')
    
    args = parser.parse_args()
    
    manager = MigrationManager()
    
    if args.command == 'list':
        clients = manager.list_clients()
        if clients:
            print("Clientes disponibles:")
            print("-" * 80)
            for client in clients:
                print(f"Carpeta: {client['folder']}")
                print(f"Nombre: {client['name']}")
                print(f"Sistema: {client['system']}")
                print("-" * 40)
        else:
            print("No hay clientes configurados")
    
    elif args.command == 'create':
        manager.create_client(args.name, args.system)
    
    elif args.command == 'process':
        success = manager.process_client(args.client)
        if success:
            print("Procesamiento completado exitosamente")
            sys.exit(0)
        else:
            print("Error en el procesamiento")
            sys.exit(1)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
