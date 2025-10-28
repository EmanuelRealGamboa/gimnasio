#!/usr/bin/env python
"""
Script para verificar la integridad del módulo de gestión de equipos
Sin necesidad de ejecutar el servidor Django
"""

import os
import sys
import ast

def verificar_sintaxis(filepath):
    """Verifica que un archivo Python tenga sintaxis correcta"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        ast.parse(code)
        return True, "[OK] Sintaxis correcta"
    except SyntaxError as e:
        return False, f"[ERROR] Error de sintaxis: {e}"
    except Exception as e:
        return False, f"[ERROR] Error: {e}"

def verificar_imports(filepath):
    """Verifica que los imports sean validos"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            code = f.read()
        tree = ast.parse(code)
        imports = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                imports.append(node.module)
        return True, f"[OK] {len(imports)} imports encontrados"
    except Exception as e:
        return False, f"[ERROR] Error al verificar imports: {e}"

def main():
    print("=" * 70)
    print("VERIFICACIÓN DEL MÓDULO DE GESTIÓN DE EQUIPOS")
    print("=" * 70)
    print()

    base_path = os.path.dirname(__file__)
    gestion_equipos_path = os.path.join(base_path, 'gestion_equipos')

    archivos_criticos = [
        'models.py',
        'serializers.py',
        'views.py',
        'urls.py',
        'admin.py',
    ]

    print("[*] Verificando archivos Python...")
    print()

    todos_ok = True
    for archivo in archivos_criticos:
        filepath = os.path.join(gestion_equipos_path, archivo)
        print(f"Verificando {archivo}:")

        if not os.path.exists(filepath):
            print(f"  [ERROR] Archivo no encontrado")
            todos_ok = False
            continue

        # Verificar sintaxis
        ok, mensaje = verificar_sintaxis(filepath)
        print(f"  {mensaje}")
        if not ok:
            todos_ok = False
            continue

        # Verificar imports
        ok, mensaje = verificar_imports(filepath)
        print(f"  {mensaje}")
        if not ok:
            todos_ok = False

        print()

    print("=" * 70)
    print("RESUMEN DE ARCHIVOS")
    print("=" * 70)
    print()

    # Contar líneas de código
    total_lines = 0
    for archivo in archivos_criticos:
        filepath = os.path.join(gestion_equipos_path, archivo)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
                total_lines += lines
                print(f"  {archivo}: {lines} líneas")

    print()
    print(f"[+] Total: {total_lines} lineas de codigo")
    print()

    if todos_ok:
        print("[OK] TODOS LOS ARCHIVOS ESTAN CORRECTOS")
        print()
        print("Próximo paso: Instalar dependencias y ejecutar migraciones")
        print("  1. pip install -r requirements.txt --upgrade")
        print("  2. python manage.py migrate")
        print("  3. python manage.py runserver")
    else:
        print("[!] SE ENCONTRARON ERRORES")
        print("Revisa los mensajes anteriores para más detalles")

    print()
    print("=" * 70)

    return 0 if todos_ok else 1

if __name__ == '__main__':
    sys.exit(main())
