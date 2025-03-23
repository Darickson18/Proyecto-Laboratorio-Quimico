"""
Sistema de Gestión de Laboratorio Interactivo

Este programa proporciona una interfaz interactiva de terminal para gestionar
un laboratorio científico, incluyendo reactivos, recetas y experimentos.
"""

import os
import json
import time
from datetime import datetime, timedelta

# Clases principales del sistema

class Validator:
    """Clase para validar datos de entrada"""
    
    @staticmethod
    def validate_string(value, field_name):
        """Valida que un valor sea una cadena no vacía."""
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"{field_name} debe ser una cadena no vacía")
        return value.strip()
    
    @staticmethod
    def validate_positive_number(value, field_name):
        """Valida que un valor sea un número positivo."""
        try:
            num = float(value)
            if num <= 0:
                raise ValueError
            return num
        except (ValueError, TypeError):
            raise ValueError(f"{field_name} debe ser un número positivo")
    
    @staticmethod
    def validate_date_format(date_str, field_name):
        """Valida que una fecha tenga el formato YYYY-MM-DD."""
        if not date_str:
            return None
        
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            raise ValueError(f"{field_name} debe tener el formato YYYY-MM-DD (ejemplo: 2023-12-31)")


class Reagent:
    """Clase que representa un reactivo en el laboratorio."""
    
    def __init__(self, name, description, cost, category, inventory, unit, 
                 min_threshold, expiry_date=None, location="Almacén general", 
                 safety_info=None):
        """Inicializa un nuevo reactivo."""
        self.name = Validator.validate_string(name, "Nombre")
        self.description = Validator.validate_string(description, "Descripción")
        self.cost = Validator.validate_positive_number(cost, "Costo")
        self.category = Validator.validate_string(category, "Categoría")
        self.inventory = Validator.validate_positive_number(inventory, "Inventario")
        self.unit = Validator.validate_string(unit, "Unidad")
        self.min_threshold = Validator.validate_positive_number(min_threshold, "Umbral mínimo")
        self.expiry_date = Validator.validate_date_format(expiry_date, "Fecha de vencimiento")
        self.location = Validator.validate_string(location, "Ubicación")
        self.safety_info = safety_info or {}
        self.purchase_history = []
        self.usage_history = []
        self.orders = []
    
    def is_low_stock(self):
        """Verifica si el reactivo está por debajo del umbral mínimo."""
        return self.inventory <= self.min_threshold
    
    def is_expired(self):
        """Verifica si el reactivo está vencido."""
        if not self.expiry_date:
            return False
        
        today = datetime.now().date()
        expiry = datetime.strptime(self.expiry_date, "%Y-%m-%d").date()
        return today >= expiry
    
    def days_until_expiry(self):
        """Calcula los días hasta la fecha de vencimiento."""
        if not self.expiry_date:
            return None
        
        today = datetime.now().date()
        expiry = datetime.strptime(self.expiry_date, "%Y-%m-%d").date()
        
        if today >= expiry:
            return 0
        
        return (expiry - today).days
    
    def update_inventory(self, amount, reason):
        """
        Actualiza el inventario del reactivo.
        
        Args:
            amount: Cantidad a añadir (positivo) o restar (negativo)
            reason: Razón del cambio
        """
        old_inventory = self.inventory
        self.inventory += amount
        
        # Registrar la transacción
        transaction = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "amount": amount,
            "old_level": old_inventory,
            "new_level": self.inventory,
            "reason": reason
        }
        
        if amount > 0:
            self.purchase_history.append(transaction)
        else:
            self.usage_history.append(transaction)
    
    def get_safety_info(self):
        """Obtiene la información de seguridad del reactivo."""
        return self.safety_info
    
    def to_dict(self):
        """Convierte el reactivo a un diccionario."""
        return {
            "name": self.name,
            "description": self.description,
            "cost": self.cost,
            "category": self.category,
            "inventory": self.inventory,
            "unit": self.unit,
            "min_threshold": self.min_threshold,
            "expiry_date": self.expiry_date,
            "location": self.location,
            "safety_info": self.safety_info,
            "purchase_history": self.purchase_history,
            "usage_history": self.usage_history,
            "orders": self.orders if hasattr(self, "orders") else []
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea un reactivo a partir de un diccionario."""
        reagent = cls(
            name=data["name"],
            description=data["description"],
            cost=data["cost"],
            category=data["category"],
            inventory=data["inventory"],
            unit=data["unit"],
            min_threshold=data["min_threshold"],
            expiry_date=data.get("expiry_date"),
            location=data.get("location", "Almacén general"),
            safety_info=data.get("safety_info", {})
        )
        
        reagent.purchase_history = data.get("purchase_history", [])
        reagent.usage_history = data.get("usage_history", [])
        reagent.orders = data.get("orders", [])
        
        return reagent


class Recipe:
    """Clase que representa una receta para un experimento."""
    
    def __init__(self, name, objective, reagents, expected_results, procedure=None):
        """Inicializa una nueva receta."""
        self.name = Validator.validate_string(name, "Nombre")
        self.objective = Validator.validate_string(objective, "Objetivo")
        
        if not isinstance(reagents, dict) or not reagents:
            raise ValueError("Reactivos debe ser un diccionario no vacío")
        self.reagents = reagents
        
        if not isinstance(expected_results, dict) or not expected_results:
            raise ValueError("Resultados esperados debe ser un diccionario no vacío")
        self.expected_results = expected_results
        
        self.procedure = procedure or []
    
    def validate_reagents(self, available_reagents):
        """
        Verifica si hay suficientes reactivos disponibles para esta receta.
        
        Args:
            available_reagents: Diccionario de reactivos disponibles
            
        Returns:
            bool: True si hay suficientes reactivos, False en caso contrario
        """
        for reagent_name, amount in self.reagents.items():
            if reagent_name not in available_reagents:
                return False
            
            reagent = available_reagents[reagent_name]
            if reagent.inventory < amount or reagent.is_expired():
                return False
        
        return True
    
    def calculate_total_cost(self, available_reagents):
        """
        Calcula el costo total de la receta.
        
        Args:
            available_reagents: Diccionario de reactivos disponibles
            
        Returns:
            float: Costo total
        """
        total_cost = 0.0
        for reagent_name, amount in self.reagents.items():
            if reagent_name not in available_reagents:
                raise ValueError(f"Reactivo '{reagent_name}' no disponible")
            
            reagent = available_reagents[reagent_name]
            total_cost += amount * reagent.cost
        
        return total_cost
    
    def to_dict(self):
        """Convierte la receta a un diccionario."""
        return {
            "name": self.name,
            "objective": self.objective,
            "reagents": self.reagents,
            "expected_results": {
                k: list(v) if isinstance(v, tuple) else v
                for k, v in self.expected_results.items()
            },
            "procedure": self.procedure
        }
    
    @classmethod
    def from_dict(cls, data):
        """Crea una receta a partir de un diccionario."""
        # Convertir listas a tuplas en expected_results
        expected_results = {}
        for k, v in data["expected_results"].items():
            if isinstance(v, list):
                expected_results[k] = tuple(v)
            else:
                expected_results[k] = v
        
        return cls(
            name=data["name"],
            objective=data["objective"],
            reagents=data["reagents"],
            expected_results=expected_results,
            procedure=data.get("procedure", [])
        )


class Experiment:
    """Clase que representa un experimento realizado."""
    
    def __init__(self, recipe, responsible_people):
        """Inicializa un nuevo experimento."""
        self.recipe = recipe
        self.date = datetime.now()
        self.responsible_people = responsible_people
        self.results = {}
        self.measurement_validations = {}
        self.success = False
        self.cost = 0.0
        self.notes = ""
    
    def record_result(self, measurement, value):
        """
        Registra un resultado y valida si está dentro del rango esperado.
        
        Args:
            measurement: Nombre de la medición
            value: Valor medido
            
        Returns:
            bool: True si el valor es válido, False en caso contrario
        """
        self.results[measurement] = value
        
        # Validar si está dentro del rango esperado
        expected = self.recipe.expected_results.get(measurement)
        if expected and isinstance(expected, tuple) and len(expected) == 2:
            min_val, max_val = expected
            is_valid = min_val <= value <= max_val
            expected_range = expected
        else:
            is_valid = True
            expected_range = None
        
        self.measurement_validations[measurement] = {
            "is_valid": is_valid,
            "expected_range": expected_range
        }
        
        return is_valid
    
    def validate_results(self):
        """
        Valida si todos los resultados están dentro de los rangos esperados.
        
        Returns:
            bool: True si todos los resultados son válidos, False en caso contrario
        """
        for measurement in self.recipe.expected_results:
            # Si falta alguna medición requerida, no es válido
            if measurement not in self.results:
                return False
            
            # Si alguna medición no es válida, no es válido
            validation = self.measurement_validations.get(measurement, {})
            if not validation.get("is_valid", False):
                return False
        
        return True
    
    def to_dict(self):
        """Convierte el experimento a un diccionario."""
        return {
            "recipe": self.recipe.to_dict(),
            "date": self.date.strftime("%Y-%m-%d"),
            "responsible_people": self.responsible_people,
            "results": self.results,
            "measurement_validations": self.measurement_validations,
            "success": self.success,
            "cost": self.cost,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Crea un experimento a partir de un diccionario.
        Nota: Requiere que la receta ya esté cargada.
        """
        recipe = Recipe.from_dict(data["recipe"])
        experiment = cls(recipe, data["responsible_people"])
        
        experiment.date = datetime.strptime(data["date"], "%Y-%m-%d")
        experiment.results = data["results"]
        experiment.measurement_validations = data["measurement_validations"]
        experiment.success = data["success"]
        experiment.cost = data["cost"]
        experiment.notes = data.get("notes", "")
        
        return experiment


class LaboratorySystem:
    """
    Clase principal que integra todas las funcionalidades del sistema.
    """
    def __init__(self):
        """Inicializa el sistema de laboratorio."""
        self.reagents = {}  # Diccionario de reactivos
        self.recipes = {}   # Diccionario de recetas
        self.experiments = []  # Lista de experimentos
        self.suppliers = {}  # Diccionario de proveedores
        self.researchers = {}  # Diccionario de investigadores
        
        # Crear directorio para visualizaciones y datos
        os.makedirs("plots", exist_ok=True)
        os.makedirs("data", exist_ok=True)
    
    def add_reagent(self, reagent):
        """Añade un reactivo al sistema."""
        self.reagents[reagent.name] = reagent
        return f"Reactivo añadido: {reagent.name}"
    
    def add_recipe(self, recipe):
        """Añade una receta al sistema."""
        self.recipes[recipe.name] = recipe
        return f"Receta añadida: {recipe.name}"
    
    def perform_experiment(self, recipe_name, responsible_people, measurements, notes=""):
        """Realiza un experimento."""
        if recipe_name not in self.recipes:
            return f"Error: Receta '{recipe_name}' no encontrada"
        
        recipe = self.recipes[recipe_name]
        
        # Verificar disponibilidad de reactivos
        for reagent_name, amount in recipe.reagents.items():
            if reagent_name not in self.reagents:
                return f"Error: Reactivo '{reagent_name}' no disponible"
            
            reagent = self.reagents[reagent_name]
            if reagent.inventory < amount:
                return f"Error: Inventario insuficiente de '{reagent_name}'"
            
            if reagent.is_expired():
                return f"Error: Reactivo '{reagent_name}' vencido"
        
        # Crear experimento
        experiment = Experiment(recipe, responsible_people)
        experiment.notes = notes
        
        # Registrar resultados
        for measurement, value in measurements.items():
            experiment.record_result(measurement, value)
        
        # Validar resultados
        experiment.success = experiment.validate_results()
        
        # Actualizar inventario
        for reagent_name, amount in recipe.reagents.items():
            self.reagents[reagent_name].update_inventory(
                -amount, f"Usado en experimento: {recipe_name}"
            )
        
        # Calcular costo
        experiment.cost = sum(
            self.reagents[reagent_name].cost * amount
            for reagent_name, amount in recipe.reagents.items()
        )
        
        # Añadir a la lista de experimentos
        self.experiments.append(experiment)
        
        result_message = f"Experimento realizado: {recipe_name}\n"
        result_message += f"Éxito: {'Sí' if experiment.success else 'No'}"
        
        return result_message, experiment
    
    def add_supplier(self, name, contact_info):
        """Añade un proveedor al sistema."""
        self.suppliers[name] = {
            "name": name,
            "contact_info": contact_info,
            "reagents": []
        }
        return f"Proveedor añadido: {name}"
    
    def associate_supplier_with_reagent(self, supplier_name, reagent_name):
        """Asocia un proveedor con un reactivo."""
        if supplier_name not in self.suppliers:
            return f"Error: Proveedor '{supplier_name}' no encontrado"
        
        if reagent_name not in self.reagents:
            return f"Error: Reactivo '{reagent_name}' no encontrado"
        
        if reagent_name not in self.suppliers[supplier_name]["reagents"]:
            self.suppliers[supplier_name]["reagents"].append(reagent_name)
            return f"Reactivo '{reagent_name}' asociado con proveedor '{supplier_name}'"
        
        return f"El reactivo '{reagent_name}' ya está asociado con el proveedor '{supplier_name}'"
    
    def place_order(self, reagent_name, quantity, supplier_name):
        """Registra un pedido de reactivo."""
        if reagent_name not in self.reagents:
            return f"Error: Reactivo '{reagent_name}' no encontrado"
        
        if supplier_name not in self.suppliers:
            return f"Error: Proveedor '{supplier_name}' no encontrado"
        
        order = {
            "order_id": f"ORD-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "reagent_name": reagent_name,
            "quantity": quantity,
            "supplier_name": supplier_name,
            "order_date": datetime.now().strftime("%Y-%m-%d"),
            "status": "pendiente",
            "expected_delivery": (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
        }
        
        # Añadir a historial de pedidos del reactivo
        self.reagents[reagent_name].orders.append(order)
        
        result = f"Pedido registrado: {order['order_id']}\n"
        result += f"Reactivo: {reagent_name}, Cantidad: {quantity}, Proveedor: {supplier_name}"
        
        return result, order
    
    def receive_order(self, order_id):
        """Registra la recepción de un pedido."""
        # Buscar el pedido en todos los reactivos
        for reagent_name, reagent in self.reagents.items():
            for order in reagent.orders:
                if order["order_id"] == order_id and order["status"] == "pendiente":
                    order["status"] = "recibido"
                    order["received_date"] = datetime.now().strftime("%Y-%m-%d")
                    
                    # Actualizar inventario
                    reagent.update_inventory(
                        order["quantity"],
                        f"Recepción de pedido {order_id}"
                    )
                    
                    result = f"Pedido recibido: {order_id}\n"
                    result += f"Reactivo: {reagent_name}, Cantidad: {order['quantity']}\n"
                    result += f"Nuevo inventario: {reagent.inventory} {reagent.unit}"
                    
                    return result
        
        return f"Error: Pedido '{order_id}' no encontrado o no pendiente"
    
    def get_low_stock_reagents(self):
        """Obtiene la lista de reactivos con bajo stock."""
        low_stock = [r for r in self.reagents.values() if r.is_low_stock()]
        return low_stock
    
    def get_expired_reagents(self):
        """Obtiene la lista de reactivos vencidos."""
        expired = [r for r in self.reagents.values() if r.is_expired()]
        return expired
    
    def get_inventory_report(self):
        """Genera un informe de inventario."""
        total_value = sum(r.inventory * r.cost for r in self.reagents.values())
        categories = set(r.category for r in self.reagents.values())
        
        report = {
            "total_reagents": len(self.reagents),
            "total_value": total_value,
            "categories": list(categories),
            "low_stock_count": len(self.get_low_stock_reagents()),
            "expired_count": len(self.get_expired_reagents())
        }
        
        return report
    
    def get_experiment_statistics(self):
        """Genera estadísticas de experimentos."""
        if not self.experiments:
            return {
                "total_experiments": 0,
                "success_rate": 0,
                "total_cost": 0,
                "average_cost": 0
            }
        
        total = len(self.experiments)
        successful = sum(1 for e in self.experiments if e.success)
        total_cost = sum(e.cost for e in self.experiments)
        
        stats = {
            "total_experiments": total,
            "success_rate": (successful / total) * 100,
            "total_cost": total_cost,
            "average_cost": total_cost / total
        }
        
        return stats
    
    def save_data(self, filename="data/laboratory_data.json"):
        """Guarda los datos del sistema en un archivo JSON."""
        data = {
            "reagents": {
                name: reagent.to_dict()
                for name, reagent in self.reagents.items()
            },
            "recipes": {
                name: recipe.to_dict()
                for name, recipe in self.recipes.items()
            },
            "experiments": [
                experiment.to_dict()
                for experiment in self.experiments
            ],
            "suppliers": self.suppliers
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return f"Datos guardados en: {filename}"
    
    def load_data(self, filename="data/laboratory_data.json"):
        """Carga los datos del sistema desde un archivo JSON."""
        if not os.path.exists(filename):
            return f"Archivo no encontrado: {filename}"
        
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Cargar reactivos
        self.reagents = {
            name: Reagent.from_dict(reagent_data)
            for name, reagent_data in data["reagents"].items()
        }
        
        # Cargar recetas
        self.recipes = {
            name: Recipe.from_dict(recipe_data)
            for name, recipe_data in data["recipes"].items()
        }
        
        # Cargar experimentos
        self.experiments = []
        for experiment_data in data["experiments"]:
            experiment = Experiment.from_dict(experiment_data)
            self.experiments.append(experiment)
        
        # Cargar proveedores
        self.suppliers = data.get("suppliers", {})
        
        result = f"Datos cargados desde: {filename}\n"
        result += f"Reactivos: {len(self.reagents)}\n"
        result += f"Recetas: {len(self.recipes)}\n"
        result += f"Experimentos: {len(self.experiments)}"
        
        return result
    
    def initialize_demo_data(self):
        """Inicializa el sistema con datos de ejemplo."""
        # Añadir proveedores
        suppliers = [
            {"name": "Sigma-Aldrich", "contact_info": "info@sigmaaldrich.com, +1-555-123-4567"},
            {"name": "Merck", "contact_info": "contacto@merck.com, +1-555-234-5678"},
            {"name": "Fisher Scientific", "contact_info": "soporte@fisher.com, +1-555-345-6789"},
            {"name": "VWR International", "contact_info": "ventas@vwr.com, +1-555-456-7890"}
        ]
        
        for supplier in suppliers:
            self.add_supplier(supplier["name"], supplier["contact_info"])
        
        # Añadir reactivos
        reagents = [
            {
                "name": "Ácido Sulfúrico",
                "description": "Ácido fuerte utilizado en diversas reacciones químicas",
                "cost": 15.50,
                "category": "Ácidos",
                "inventory": 2000,
                "unit": "mL",
                "min_threshold": 500,
                "expiry_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
                "location": "Almacén de ácidos",
                "safety_info": "Corrosivo. Usar guantes y gafas de protección.",
                "supplier": "Sigma-Aldrich"
            },
            {
                "name": "Hidróxido de Sodio",
                "description": "Base fuerte utilizada en neutralización",
                "cost": 12.75,
                "category": "Bases",
                "inventory": 1500,
                "unit": "g",
                "min_threshold": 300,
                "expiry_date": (datetime.now() + timedelta(days=730)).strftime("%Y-%m-%d"),
                "location": "Almacén de bases",
                "safety_info": "Corrosivo. Evitar contacto con piel y ojos.",
                "supplier": "Merck"
            },
            {
                "name": "Etanol",
                "description": "Solvente orgánico común",
                "cost": 8.25,
                "category": "Solventes",
                "inventory": 5000,
                "unit": "mL",
                "min_threshold": 1000,
                "expiry_date": (datetime.now() + timedelta(days=500)).strftime("%Y-%m-%d"),
                "location": "Almacén de solventes",
                "safety_info": "Inflamable. Mantener alejado de fuentes de calor.",
                "supplier": "Fisher Scientific"
            },
            {
                "name": "Cloruro de Sodio",
                "description": "Sal común utilizada en muchas preparaciones",
                "cost": 5.50,
                "category": "Sales",
                "inventory": 3000,
                "unit": "g",
                "min_threshold": 500,
                "expiry_date": (datetime.now() + timedelta(days=1825)).strftime("%Y-%m-%d"),
                "location": "Almacén general",
                "safety_info": "No tóxico. Sin precauciones especiales.",
                "supplier": "VWR International"
            },
            {
                "name": "Metanol",
                "description": "Alcohol de un solo carbono, solvente polar",
                "cost": 9.75,
                "category": "Solventes",
                "inventory": 200,
                "unit": "mL",
                "min_threshold": 500,
                "expiry_date": (datetime.now() + timedelta(days=365)).strftime("%Y-%m-%d"),
                "location": "Almacén de solventes",
                "safety_info": "Tóxico e inflamable. Usar en campana de extracción.",
                "supplier": "Sigma-Aldrich"
            },
            {
                "name": "Acetona",
                "description": "Solvente orgánico volátil",
                "cost": 7.80,
                "category": "Solventes",
                "inventory": 3500,
                "unit": "mL",
                "min_threshold": 800,
                "expiry_date": (datetime.now() + timedelta(days=730)).strftime("%Y-%m-%d"),
                "location": "Almacén de solventes",
                "safety_info": "Inflamable y volátil. Mantener contenedor cerrado.",
                "supplier": "Merck"
            }
        ]
        
        for reagent_data in reagents:
            supplier_name = reagent_data.pop("supplier")
            reagent = Reagent(**reagent_data)
            self.add_reagent(reagent)
            self.associate_supplier_with_reagent(supplier_name, reagent.name)
        
        # Añadir recetas
        recipes = [
            {
                "name": "Titulación Ácido-Base",
                "objective": "Determinar la concentración de una solución ácida o básica",
                "reagents": {
                    "Ácido Sulfúrico": 10,
                    "Hidróxido de Sodio": 5
                },
                "expected_results": {
                    "pH": (6.8, 7.2),
                    "volumen_gastado": (9.5, 10.5)
                },
                "procedure": [
                    "Preparar la bureta con NaOH",
                    "Añadir indicador a la solución de ácido",
                    "Titular hasta cambio de color",
                    "Registrar volumen gastado"
                ]
            },
            {
                "name": "Preparación de Buffer Fosfato",
                "objective": "Crear una solución buffer de pH 7.4",
                "reagents": {
                    "Etanol": 50,
                    "Cloruro de Sodio": 8.5
                },
                "expected_results": {
                    "pH": (7.3, 7.5),
                    "conductividad": (15.0, 18.0)
                },
                "procedure": [
                    "Disolver las sales en agua destilada",
                    "Ajustar el pH con ácido o base según sea necesario",
                    "Enrasar a volumen final",
                    "Filtrar la solución"
                ]
            }
        ]
        
        for recipe_data in recipes:
            recipe = Recipe(
                name=recipe_data["name"],
                objective=recipe_data["objective"],
                reagents=recipe_data["reagents"],
                expected_results=recipe_data["expected_results"],
                procedure=recipe_data["procedure"]
            )
            self.add_recipe(recipe)
        
        return "Datos de ejemplo inicializados correctamente"


# Funciones para el menú interactivo

def clear_screen():
    """Limpia la pantalla de la terminal."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title):
    """Imprime un encabezado para los menús."""
    clear_screen()
    print("=" * 60)
    print(f"{title:^60}")
    print("=" * 60)


def print_footer():
    """Imprime un pie de página para los menús."""
    print("\n" + "=" * 60)


def get_input(prompt, validator=None):
    """
    Solicita entrada al usuario con validación opcional.
    
    Args:
        prompt: Mensaje para mostrar al usuario
        validator: Función para validar la entrada
        
    Returns:
        La entrada del usuario validada
    """
    while True:
        value = input(prompt)
        if validator:
            try:
                return validator(value)
            except ValueError as e:
                print(f"Error: {e}")
        else:
            return value


def input_date(prompt):
    """Solicita una fecha en formato YYYY-MM-DD."""
    while True:
        date_str = input(prompt + " (YYYY-MM-DD, dejar en blanco para omitir): ")
        if not date_str:
            return None
        
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("Error: La fecha debe tener el formato YYYY-MM-DD (ejemplo: 2023-12-31)")


def input_float(prompt):
    """Solicita un número de punto flotante positivo."""
    while True:
        try:
            value = float(input(prompt))
            if value <= 0:
                print("Error: El valor debe ser positivo")
                continue
            return value
        except ValueError:
            print("Error: Debe ingresar un número válido")


def input_int(prompt):
    """Solicita un número entero positivo."""
    while True:
        try:
            value = int(input(prompt))
            if value <= 0:
                print("Error: El valor debe ser positivo")
                continue
            return value
        except ValueError:
            print("Error: Debe ingresar un número entero válido")


def input_yes_no(prompt):
    """Solicita una respuesta de sí o no."""
    while True:
        response = input(prompt + " (s/n): ").lower()
        if response in ('s', 'si', 'sí', 'y', 'yes'):
            return True
        elif response in ('n', 'no', 'not'):
            return False
        else:
            print("Error: Responda 's' para sí o 'n' para no")


def pause():
    """Pausa la ejecución hasta que el usuario presione Enter."""
    input("\nPresione Enter para continuar...")


# Menús principales

def menu_reagents(lab):
    """Menú para gestionar reactivos."""
    while True:
        print_header("GESTIÓN DE REACTIVOS")
        print("1. Añadir reactivo")
        print("2. Ver reactivos")
        print("3. Actualizar inventario")
        print("4. Gestionar proveedores")
        print("5. Realizar pedido")
        print("6. Recibir pedido")
        print("7. Generar informe de inventario")
        print("8. Ver reactivos con bajo stock")
        print("9. Ver reactivos vencidos")
        print("0. Volver al menú principal")
        
        option = input("\nSeleccione una opción: ")
        
        if option == "1":
            add_reagent(lab)
        elif option == "2":
            view_reagents(lab)
        elif option == "3":
            update_inventory(lab)
        elif option == "4":
            menu_suppliers(lab)
        elif option == "5":
            place_order(lab)
        elif option == "6":
            receive_order(lab)
        elif option == "7":
            inventory_report(lab)
        elif option == "8":
            view_low_stock(lab)
        elif option == "9":
            view_expired(lab)
        elif option == "0":
            break
        else:
            print("Opción no válida")
            pause()


def menu_recipes(lab):
    """Menú para gestionar recetas."""
    while True:
        print_header("GESTIÓN DE RECETAS")
        print("1. Añadir receta")
        print("2. Ver recetas")
        print("3. Validar receta")
        print("0. Volver al menú principal")
        
        option = input("\nSeleccione una opción: ")
        
        if option == "1":
            add_recipe(lab)
        elif option == "2":
            view_recipes(lab)
        elif option == "3":
            validate_recipe(lab)
        elif option == "0":
            break
        else:
            print("Opción no válida")
            pause()


def menu_experiments(lab):
    """Menú para gestionar experimentos."""
    while True:
        print_header("GESTIÓN DE EXPERIMENTOS")
        print("1. Realizar experimento")
        print("2. Ver experimentos")
        print("3. Ver estadísticas de experimentos")
        print("0. Volver al menú principal")
        
        option = input("\nSeleccione una opción: ")
        
        if option == "1":
            perform_experiment(lab)
        elif option == "2":
            view_experiments(lab)
        elif option == "3":
            experiment_statistics(lab)
        elif option == "0":
            break
        else:
            print("Opción no válida")
            pause()


def menu_suppliers(lab):
    """Menú para gestionar proveedores."""
    while True:
        print_header("GESTIÓN DE PROVEEDORES")
        print("1. Añadir proveedor")
        print("2. Ver proveedores")
        print("3. Asociar proveedor con reactivo")
        print("0. Volver al menú anterior")
        
        option = input("\nSeleccione una opción: ")
        
        if option == "1":
            add_supplier(lab)
        elif option == "2":
            view_suppliers(lab)
        elif option == "3":
            associate_supplier(lab)
        elif option == "0":
            break
        else:
            print("Opción no válida")
            pause()


# Funciones para gestionar reactivos

def add_reagent(lab):
    """Añade un nuevo reactivo al sistema."""
    print_header("AÑADIR REACTIVO")
    
    try:
        name = input("Nombre: ")
        description = input("Descripción: ")
        cost = input_float("Costo unitario: ")
        category = input("Categoría: ")
        inventory = input_float("Inventario inicial: ")
        unit = input("Unidad de medida (g, mL, L, etc.): ")
        min_threshold = input_float("Umbral mínimo: ")
        expiry_date = input_date("Fecha de vencimiento")
        location = input("Ubicación (dejar en blanco para 'Almacén general'): ") or "Almacén general"
        safety_info = input("Información de seguridad (dejar en blanco para omitir): ")
        
        reagent = Reagent(
            name=name,
            description=description,
            cost=cost,
            category=category,
            inventory=inventory,
            unit=unit,
            min_threshold=min_threshold,
            expiry_date=expiry_date,
            location=location,
            safety_info=safety_info
        )
        
        result = lab.add_reagent(reagent)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pause()


def view_reagents(lab):
    """Muestra la lista de reactivos."""
    print_header("REACTIVOS")
    
    if not lab.reagents:
        print("No hay reactivos registrados.")
    else:
        for name, reagent in lab.reagents.items():
            print(f"{name}:")
            print(f"  Descripción: {reagent.description}")
            print(f"  Costo: {reagent.cost}")
            print(f"  Categoría: {reagent.category}")
            print(f"  Inventario: {reagent.inventory} {reagent.unit}")
            print(f"  Umbral mínimo: {reagent.min_threshold}")
            print(f"  Fecha de vencimiento: {reagent.expiry_date}")
            print(f"  Ubicación: {reagent.location}")
            print(f"  Información de seguridad: {reagent.safety_info}")
            print()
    
    pause()


def update_inventory(lab):
    """Actualiza el inventario de un reactivo."""
    print_header("ACTUALIZAR INVENTARIO")
    
    reagent_name = input("Nombre del reactivo: ")
    if reagent_name not in lab.reagents:
        print(f"Error: Reactivo '{reagent_name}' no encontrado")
        return
    
    reagent = lab.reagents[reagent_name]
    
    print(f"Inventario actual de {reagent_name}: {reagent.inventory} {reagent.unit}")
    
    amount = input_float("Cantidad a añadir o restar: ")
    reason = input("Razón del cambio: ")
    
    reagent.update_inventory(amount, reason)
    
    print(f"Inventario actualizado: {reagent.inventory} {reagent.unit}")
    
    pause()


def view_low_stock(lab):
    """Muestra la lista de reactivos con bajo stock."""
    print_header("REACTIVOS CON BAJO STOCK")
    
    low_stock = lab.get_low_stock_reagents()
    if not low_stock:
        print("No hay reactivos con bajo stock.")
    else:
        for reagent in low_stock:
            print(f"{reagent.name}:")
            print(f"  Descripción: {reagent.description}")
            print(f"  Costo: {reagent.cost}")
            print(f"  Categoría: {reagent.category}")
            print(f"  Inventario: {reagent.inventory} {reagent.unit}")
            print(f"  Umbral mínimo: {reagent.min_threshold}")
            print(f"  Fecha de vencimiento: {reagent.expiry_date}")
            print(f"  Ubicación: {reagent.location}")
            print()
    
    pause()


def view_expired(lab):
    """Muestra la lista de reactivos vencidos."""
    print_header("REACTIVOS VENCIDOS")
    
    expired = lab.get_expired_reagents()
    if not expired:
        print("No hay reactivos vencidos.")
    else:
        for reagent in expired:
            print(f"{reagent.name}:")
            print(f"  Descripción: {reagent.description}")
            print(f"  Costo: {reagent.cost}")
            print(f"  Categoría: {reagent.category}")
            print(f"  Inventario: {reagent.inventory} {reagent.unit}")
            print(f"  Umbral mínimo: {reagent.min_threshold}")
            print(f"  Fecha de vencimiento: {reagent.expiry_date}")
            print(f"  Ubicación: {reagent.location}")
            print()
    
    pause()


def view_suppliers(lab):
    """Muestra la lista de proveedores."""
    print_header("PROVEEDORES")
    
    if not lab.suppliers:
        print("No hay proveedores registrados.")
    else:
        for name, supplier in lab.suppliers.items():
            print(f"{name}:")
            print(f"  Contacto: {supplier['contact_info']}")
            print(f"  Reactivos asociados: {', '.join(supplier['reagents'])}")
            print()
    
    pause()


def associate_supplier(lab):
    """Asocia un proveedor con un reactivo."""
    print_header("ASOCIAR PROVEEDOR CON REACTIVO")
    
    supplier_name = input("Nombre del proveedor: ")
    if supplier_name not in lab.suppliers:
        print(f"Error: Proveedor '{supplier_name}' no encontrado")
        return
    
    reagent_name = input("Nombre del reactivo: ")
    if reagent_name not in lab.reagents:
        print(f"Error: Reactivo '{reagent_name}' no encontrado")
        return
    
    result = lab.associate_supplier_with_reagent(supplier_name, reagent_name)
    print(result)
    
    pause()


def add_supplier(lab):
    """Añade un nuevo proveedor al sistema."""
    print_header("AÑADIR PROVEEDOR")
    
    name = input("Nombre: ")
    contact_info = input("Información de contacto: ")
    
    result = lab.add_supplier(name, contact_info)
    print(result)
    
    pause()


def place_order(lab):
    """Registra un nuevo pedido de reactivo."""
    print_header("REALIZAR PEDIDO")
    
    reagent_name = input("Nombre del reactivo: ")
    if reagent_name not in lab.reagents:
        print(f"Error: Reactivo '{reagent_name}' no encontrado")
        return
    
    quantity = input_float("Cantidad: ")
    supplier_name = input("Nombre del proveedor: ")
    
    result, order = lab.place_order(reagent_name, quantity, supplier_name)
    print(result)
    
    pause()


def receive_order(lab):
    """Registra la recepción de un pedido."""
    print_header("RECIBIR PEDIDO")
    
    order_id = input("ID del pedido: ")
    
    result = lab.receive_order(order_id)
    print(result)
    
    pause()


def inventory_report(lab):
    """Genera un informe de inventario."""
    print_header("INFORME DE INVENTARIO")
    
    report = lab.get_inventory_report()
    print(f"Total de reactivos: {report['total_reagents']}")
    print(f"Valor total del inventario: {report['total_value']}")
    print(f"Categorías: {', '.join(report['categories'])}")
    print(f"Reactivos con bajo stock: {report['low_stock_count']}")
    print(f"Reactivos vencidos: {report['expired_count']}")
    
    pause()


def view_experiments(lab):
    """Muestra la lista de experimentos."""
    print_header("EXPERIMENTOS")
    
    if not lab.experiments:
        print("No hay experimentos registrados.")
    else:
        for experiment in lab.experiments:
            print(f"{experiment.recipe.name} - Fecha: {experiment.date.strftime('%Y-%m-%d')}")
            print(f"Responsables: {', '.join(experiment.responsible_people)}")
            print()
    
    pause()


def experiment_statistics(lab):
    """Genera estadísticas de experimentos."""
    print_header("ESTADÍSTICAS DE EXPERIMENTOS")
    
    stats = lab.get_experiment_statistics()
    print(f"Total de experimentos: {stats['total_experiments']}")
    print(f"Porcentaje de éxito: {stats['success_rate']:.2f}%")
    print(f"Costo total: {stats['total_cost']}")
    print(f"Costo promedio: {stats['average_cost']}")
    
    pause()


def validate_recipe(lab):
    """Valida una receta."""
    print_header("VALIDAR RECETA")
    
    recipe_name = input("Nombre de la receta: ")
    if recipe_name not in lab.recipes:
        print(f"Error: Receta '{recipe_name}' no encontrada")
        return
    
    recipe = lab.recipes[recipe_name]
    
    # Verificar disponibilidad de reactivos
    available_reagents = {name: reagent for name, reagent in lab.reagents.items() if not reagent.is_expired()}
    if not recipe.validate_reagents(available_reagents):
        print("Error: No hay suficientes reactivos disponibles o algunos están vencidos")
        return
    
    # Calcular costo
    cost = recipe.calculate_total_cost(available_reagents)
    print(f"Costo total de la receta: {cost}")
    
    pause()


def add_recipe(lab):
    """Añade una nueva receta al sistema."""
    print_header("AÑADIR RECETA")
    
    try:
        name = input("Nombre: ")
        objective = input("Objetivo: ")
        reagents = {}
        while True:
            reagent_name = input("Nombre del reactivo (dejar en blanco para terminar): ")
            if not reagent_name:
                break
            amount = input_float(f"Cantidad de {reagent_name}: ")
            reagents[reagent_name] = amount
        
        expected_results = {}
        while True:
            measurement = input("Nombre de la medición (dejar en blanco para terminar): ")
            if not measurement:
                break
            value = input_float(f"Valor esperado para {measurement}: ")
            expected_results[measurement] = value
        
        procedure = []
        while True:
            step = input("Descripción del paso (dejar en blanco para terminar): ")
            if not step:
                break
            procedure.append(step)
        
        recipe = Recipe(name, objective, reagents, expected_results, procedure)
        result = lab.add_recipe(recipe)
        print(result)
    except Exception as e:
        print(f"Error: {e}")
    finally:
        pause()


def view_recipes(lab):
    """Muestra la lista de recetas."""
    print_header("RECETAS")
    
    if not lab.recipes:
        print("No hay recetas registradas.")
    else:
        for name, recipe in lab.recipes.items():
            print(f"{name}:")
            print(f"  Objetivo: {recipe.objective}")
            print(f"  Reactivos: {', '.join(recipe.reagents.keys())}")
            print(f"  Resultados esperados: {', '.join(f'{k}: {v}' for k, v in recipe.expected_results.items())}")
            print(f"  Procedimiento: {', '.join(recipe.procedure)}")
            print()
    
    pause()


def perform_experiment(lab):
    """Realiza un nuevo experimento."""
    print_header("REALIZAR EXPERIMENTO")
    
    recipe_name = input("Nombre de la receta: ")
    if recipe_name not in lab.recipes:
        print(f"Error: Receta '{recipe_name}' no encontrada")
        return
    
    recipe = lab.recipes[recipe_name]
    
    # Verificar disponibilidad de reactivos
    for reagent_name, amount in recipe.reagents.items():
        if reagent_name not in lab.reagents:
            print(f"Error: Reactivo '{reagent_name}' no disponible")
            return
        
        reagent = lab.reagents[reagent_name]
        if reagent.inventory < amount:
            print(f"Error: Inventario insuficiente de '{reagent_name}'")
            return
        
        if reagent.is_expired():
            print(f"Error: Reactivo '{reagent_name}' vencido")
            return
    
    # Solicitar información del experimento
    responsible_people = input("Responsables (separados por comas): ").split(',')
    measurements = {}
    while True:
        measurement = input("Nombre de la medición (dejar en blanco para terminar): ")
        if not measurement:
            break
        value = input_float(f"Valor medido para {measurement}: ")
        measurements[measurement] = value
    
    notes = input("Notas adicionales: ")
    
    # Realizar experimento
    result_message, experiment = lab.perform_experiment(recipe_name, responsible_people, measurements, notes)
    print(result_message)
    
    pause()


def main():
    """Función principal del programa."""
    lab = LaboratorySystem()
    
    # Inicializar con datos de ejemplo
    print("Inicializando sistema con datos de ejemplo...")
    lab.initialize_demo_data()
    print("Sistema inicializado correctamente con:")
    print(f"- Reactivos: {len(lab.reagents)}")
    print(f"- Recetas: {len(lab.recipes)}")
    print(f"- Proveedores: {len(lab.suppliers)}")
    print("\nBienvenido al Sistema de Gestión de Laboratorio Interactivo")
    print("\nPresione Enter para continuar...")
    input()
    
    while True:
        print_header("MENÚ PRINCIPAL")
        print("1. Gestionar reactivos")
        print("2. Gestionar recetas")
        print("3. Gestionar experimentos")
        print("4. Gestionar proveedores")
        print("5. Guardar datos")
        print("6. Cargar datos")
        print("0. Salir")
        
        option = input("\nSeleccione una opción: ")
        
        if option == "1":
            menu_reagents(lab)
        elif option == "2":
            menu_recipes(lab)
        elif option == "3":
            menu_experiments(lab)
        elif option == "4":
            menu_suppliers(lab)
        elif option == "5":
            filename = input("Nombre del archivo (data/laboratory_data.json): ") or "data/laboratory_data.json"
            result = lab.save_data(filename)
            print(result)
            pause()
        elif option == "6":
            filename = input("Nombre del archivo (data/laboratory_data.json): ") or "data/laboratory_data.json"
            result = lab.load_data(filename)
            print(result)
            pause()
        elif option == "0":
            break
        else:
            print("Opción no válida")
            pause()


if __name__ == "__main__":
    main()
