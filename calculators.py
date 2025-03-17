"""
Calculadores del Sistema de Laboratorio

Este módulo contiene las clases para realizar cálculos
y validaciones de resultados experimentales.

Classes:
    ResultCalculator: Realiza cálculos de resultados experimentales
"""

import math
from typing import Dict, Tuple

class ResultCalculator:
    """
    Clase para realizar cálculos y validaciones de resultados experimentales.
    """
    
    @staticmethod
    def calculate_ph(h_concentration: float) -> float:
        """Calcula el pH a partir de la concentración de H+."""
        return -math.log10(h_concentration)
    
    @staticmethod
    def calculate_concentration(moles: float, volume_l: float) -> float:
        """Calcula la concentración en mol/L."""
        return moles / volume_l
    
    @staticmethod
    def calculate_yield(actual: float, theoretical: float) -> float:
        """Calcula el rendimiento porcentual."""
        return (actual / theoretical) * 100
    
    @staticmethod
    def calculate_purity(mass_real: float, mass_theoretical: float) -> float:
        """Calcula la pureza porcentual."""
        return (mass_real / mass_theoretical) * 100
    
    @staticmethod
    def evaluate_measurement(value: float, min_val: float, max_val: float) -> Tuple[bool, float]:
        """
        Evalúa si una medición está dentro del rango aceptable y calcula la desviación.
        
        Args:
            value: Valor medido
            min_val: Valor mínimo aceptable
            max_val: Valor máximo aceptable
            
        Returns:
            Tupla de (está_dentro_del_rango, porcentaje_de_desviación)
        """
        is_valid = min_val <= value <= max_val
        target = (min_val + max_val) / 2
        deviation = ((value - target) / target) * 100
        return is_valid, deviation 