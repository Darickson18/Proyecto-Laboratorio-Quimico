"""
Modelos del Sistema de Gestión de Laboratorio

Este módulo contiene las clases que representan las entidades
principales del sistema.

Classes:
    Reagent: Representa un reactivo
    Recipe: Representa una receta de experimento
    Experiment: Representa un experimento realizado
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from laboratory_system import Validator

class Reagent:
    """
    Representa un reactivo en el sistema.
    
    Attributes:
        name (str): Nombre del reactivo
        description (str): Descripción del reactivo
        cost (float): Costo por unidad
        category (str): Categoría del reactivo
        inventory (float): Cantidad en inventario
        unit (str): Unidad de medida
        min_threshold (float): Nivel mínimo de inventario
        expiry_date (datetime): Fecha de vencimiento
        location (str): Ubicación en el laboratorio
        safety_info (dict): Información de seguridad
    """
    
    def __init__(self, name: str, description: str, cost: float,
                 category: str, inventory: float, unit: str,
                 min_threshold: float, expiry_date: Optional[str] = None,
                 location: str = None, safety_info: Dict = None):
        """
        Inicializa un reactivo.
        
        Args:
            name: Nombre del reactivo
            description: Descripción del reactivo
            cost: Costo por unidad
            category: Categoría del reactivo
            inventory: Cantidad en inventario
            unit: Unidad de medida
            min_threshold: Nivel mínimo de inventario
            expiry_date: Fecha de vencimiento (opcional)
            location: Ubicación en el laboratorio (opcional)
            safety_info: Información de seguridad (opcional)
            
        Raises:
            ValueError: Si algún parámetro no es válido
        """
        # Validar parámetros
        Validator.validate_string(name, "name")
        Validator.validate_string(description, "description")
        Validator.validate_positive_number(cost, "cost")
        Validator.validate_string(category, "category")
        Validator.validate_positive_number(inventory, "inventory")
        Validator.validate_string(unit, "unit")
        Validator.validate_positive_number(min_threshold, "min_threshold")
        
        if expiry_date:
            Validator.validate_date_format(expiry_date, "expiry_date")
        
        # Asignar valores
        self.name = name
        self.description = description
        self.cost = cost
        self.category = category
        self.inventory = inventory
        self.unit = unit
        self.min_threshold = min_threshold
        self.expiry_date = datetime.strptime(expiry_date, "%Y-%m-%d") if expiry_date else None
        self.location = location or "Almacén general"
        self.safety_info = safety_info or {}
        
        # Historiales
        self.purchase_history = []
        self.usage_history = []
    
    def update_inventory(self, amount: float, reason: str = "") -> bool:
        """
        Actualiza el nivel de inventario.
        
        Args:
            amount: Cantidad a añadir (positivo) o restar (negativo)
            reason: Razón del cambio
            
        Returns:
            bool indicando si la actualización fue exitosa
        """
        new_inventory = self.inventory + amount
        if new_inventory < 0:
            return False
            
        self.inventory = new_inventory
        
        # Registrar transacción
        transaction = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "amount": amount,
            "reason": reason,
            "new_level": new_inventory
        }
        
        if amount > 0:
            self.purchase_history.append(transaction)
        else:
            self.usage_history.append(transaction)
            
        return True
    
    def is_expired(self) -> bool:
        """
        Verifica si el reactivo está vencido.
        
        Returns:
            bool indicando si el reactivo está vencido
        """
        if not self.expiry_date:
            return False
        return datetime.now() > self.expiry_date
    
    def is_low_stock(self) -> bool:
        """
        Verifica si el inventario está bajo el umbral mínimo.
        
        Returns:
            bool indicando si el inventario está bajo
        """
        return self.inventory <= self.min_threshold
    
    def to_dict(self) -> Dict:
        """
        Convierte el reactivo a un diccionario.
        
        Returns:
            Dict con los datos del reactivo
        """
        return {
            "name": self.name,
            "description": self.description,
            "cost": self.cost,
            "category": self.category,
            "inventory": self.inventory,
            "unit": self.unit,
            "min_threshold": self.min_threshold,
            "expiry_date": self.expiry_date.strftime("%Y-%m-%d") if self.expiry_date else None,
            "location": self.location,
            "safety_info": self.safety_info,
            "purchase_history": self.purchase_history,
            "usage_history": self.usage_history
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Reagent':
        """
        Crea una instancia de Reagent desde un diccionario.
        
        Args:
            data: Diccionario con los datos del reactivo
            
        Returns:
            Nueva instancia de Reagent
        """
        reagent = cls(
            name=data["name"],
            description=data["description"],
            cost=data["cost"],
            category=data["category"],
            inventory=data["inventory"],
            unit=data["unit"],
            min_threshold=data["min_threshold"],
            expiry_date=data["expiry_date"],
            location=data.get("location"),
            safety_info=data.get("safety_info", {})
        )
        reagent.purchase_history = data.get("purchase_history", [])
        reagent.usage_history = data.get("usage_history", [])
        return reagent

class Recipe:
    """
    Representa una receta de experimento.
    
    Attributes:
        name (str): Nombre de la receta
        objective (str): Objetivo del experimento
        reagents (dict): Reactivos necesarios y sus cantidades
        procedure (list): Lista de pasos del procedimiento
        expected_results (dict): Resultados esperados y sus rangos
    """
    
    def __init__(self, name: str, objective: str, reagents: Dict[str, float],
                 procedure: List[str], expected_results: Dict[str, Tuple[float, float]]):
        """
        Inicializa una receta.
        
        Args:
            name: Nombre de la receta
            objective: Objetivo del experimento
            reagents: Diccionario de reactivos y cantidades
            procedure: Lista de pasos del procedimiento
            expected_results: Diccionario de resultados esperados
            
        Raises:
            ValueError: Si algún parámetro no es válido
        """
        # Validar parámetros
        Validator.validate_string(name, "name")
        Validator.validate_string(objective, "objective")
        
        if not reagents:
            raise ValueError("La receta debe tener al menos un reactivo")
        
        if not procedure:
            raise ValueError("La receta debe tener al menos un paso")
        
        # Validar rangos de resultados esperados
        for measurement, (min_val, max_val) in expected_results.items():
            if min_val > max_val:
                raise ValueError(f"Rango inválido para {measurement}")
        
        self.name = name
        self.objective = objective
        self.reagents = reagents
        self.procedure = procedure
        self.expected_results = expected_results
    
    def validate_reagents(self, available_reagents: Dict[str, Reagent]) -> bool:
        """
        Valida que todos los reactivos necesarios estén disponibles.
        
        Args:
            available_reagents: Diccionario de reactivos disponibles
            
        Returns:
            bool indicando si todos los reactivos están disponibles
        """
        for reagent_name, required_amount in self.reagents.items():
            if reagent_name not in available_reagents:
                return False
            
            reagent = available_reagents[reagent_name]
            if reagent.inventory < required_amount or reagent.is_expired():
                return False
        
        return True
    
    def calculate_total_cost(self, available_reagents: Dict[str, Reagent]) -> float:
        """
        Calcula el costo total de los reactivos necesarios.
        
        Args:
            available_reagents: Diccionario de reactivos disponibles
            
        Returns:
            float con el costo total
            
        Raises:
            ValueError: Si algún reactivo no está disponible
        """
        total_cost = 0.0
        for reagent_name, amount in self.reagents.items():
            if reagent_name not in available_reagents:
                raise ValueError(f"Reactivo no disponible: {reagent_name}")
            
            reagent = available_reagents[reagent_name]
            total_cost += reagent.cost * amount
        
        return total_cost
    
    def to_dict(self) -> Dict:
        """
        Convierte la receta a un diccionario.
        
        Returns:
            Dict con los datos de la receta
        """
        return {
            "name": self.name,
            "objective": self.objective,
            "reagents": self.reagents,
            "procedure": self.procedure,
            "expected_results": self.expected_results
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Recipe':
        """
        Crea una instancia de Recipe desde un diccionario.
        
        Args:
            data: Diccionario con los datos de la receta
            
        Returns:
            Nueva instancia de Recipe
        """
        return cls(
            name=data["name"],
            objective=data["objective"],
            reagents=data["reagents"],
            procedure=data["procedure"],
            expected_results=data["expected_results"]
        )

class Experiment:
    """
    Representa un experimento realizado.
    
    Attributes:
        recipe (Recipe): Receta utilizada
        date (datetime): Fecha de realización
        responsible_people (list): Lista de responsables
        results (dict): Resultados obtenidos
        success (bool): Indicador de éxito
        cost (float): Costo total
    """
    
    def __init__(self, recipe: Recipe, responsible_people: List[str],
                 date: Optional[str] = None):
        """
        Inicializa un experimento.
        
        Args:
            recipe: Receta a utilizar
            responsible_people: Lista de responsables
            date: Fecha de realización (opcional)
            
        Raises:
            ValueError: Si algún parámetro no es válido
        """
        if not responsible_people:
            raise ValueError("Debe haber al menos un responsable")
        
        self.recipe = recipe
        self.responsible_people = responsible_people
        self.date = datetime.strptime(date, "%Y-%m-%d") if date else datetime.now()
        self.results = {}
        self.success = False
        self.cost = 0.0
        self.measurement_validations = {}
    
    def record_result(self, measurement: str, value: float,
                     raw_data: Dict = None) -> bool:
        """
        Registra y valida un resultado.
        
        Args:
            measurement: Nombre de la medición
            value: Valor obtenido
            raw_data: Datos crudos (opcional)
            
        Returns:
            bool indicando si el resultado es válido
        """
        self.results[measurement] = value
        
        if measurement in self.recipe.expected_results:
            min_val, max_val = self.recipe.expected_results[measurement]
            is_valid = min_val <= value <= max_val
            target = (min_val + max_val) / 2
            deviation = ((value - target) / target) * 100
            
            self.measurement_validations[measurement] = {
                "value": value,
                "is_valid": is_valid,
                "deviation": deviation,
                "raw_data": raw_data or {},
                "expected_range": (min_val, max_val)
            }
            
            return is_valid
        return True
    
    def validate_results(self) -> bool:
        """
        Valida todos los resultados del experimento.
        
        Returns:
            bool indicando si todos los resultados son válidos
        """
        if not self.results or not self.recipe.expected_results:
            return False
        
        for measurement, value in self.results.items():
            if measurement in self.recipe.expected_results:
                min_val, max_val = self.recipe.expected_results[measurement]
                if not (min_val <= value <= max_val):
                    return False
        return True
    
    def to_dict(self) -> Dict:
        """
        Convierte el experimento a un diccionario.
        
        Returns:
            Dict con los datos del experimento
        """
        return {
            "recipe": self.recipe.to_dict(),
            "responsible_people": self.responsible_people,
            "date": self.date.strftime("%Y-%m-%d"),
            "results": self.results,
            "success": self.success,
            "cost": self.cost,
            "measurement_validations": self.measurement_validations
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Experiment':
        """
        Crea una instancia de Experiment desde un diccionario.
        
        Args:
            data: Diccionario con los datos del experimento
            
        Returns:
            Nueva instancia de Experiment
        """
        recipe = Recipe.from_dict(data["recipe"])
        experiment = cls(
            recipe=recipe,
            responsible_people=data["responsible_people"],
            date=data["date"]
        )
        experiment.results = data["results"]
        experiment.success = data["success"]
        experiment.cost = data["cost"]
        experiment.measurement_validations = data.get("measurement_validations", {})
        return experiment 