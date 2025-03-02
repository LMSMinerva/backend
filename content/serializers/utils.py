import random
import math
import itertools
import statistics
import numpy as np
import sympy
import datetime
import fractions
import re
import string

def validate_seleccion_body(body):
    """
    Validates that a 'seleccion' content body has the correct structure and can be processed.
    
    Args:
        body (dict): The body content to validate
        
    Returns:
        tuple: (is_valid, error_message) where is_valid is a boolean and error_message is None if valid
    """
    # Check if body is a dictionary
    if not isinstance(body, dict):
        return False, "Body must be a dictionary"
    
    # Check required keys
    required_keys = ["variables", "enunciado", "respuestas"]
    for key in required_keys:
        if key not in body:
            return False, f"Missing required key: '{key}'"
    
    # Validate variables is a string that can be executed
    if not isinstance(body["variables"], str):
        return False, "Variables must be a string containing Python code"
    
    # Try executing the variables code
    context = {
        # Random module functions
        "random": random.random,
        "randint": random.randint,
        "choice": random.choice,
        "choices": random.choices,
        "sample": random.sample,
        "uniform": random.uniform,
        "shuffle": random.shuffle,
        
        # Math module functions
        "sin": math.sin,
        "cos": math.cos,
        "tan": math.tan,
        "asin": math.asin,
        "acos": math.acos,
        "atan": math.atan,
        "atan2": math.atan2,
        "pi": math.pi,
        "e": math.e,
        "sqrt": math.sqrt,
        "log": math.log,
        "log10": math.log10,
        "exp": math.exp,
        "floor": math.floor,
        "ceil": math.ceil,
        "fabs": math.fabs,
        "factorial": math.factorial,
        "gcd": math.gcd,
        "degrees": math.degrees,
        "radians": math.radians,
        
        # Statistics functions
        "mean": statistics.mean,
        "median": statistics.median,
        "mode": statistics.mode,
        "stdev": statistics.stdev,
        "variance": statistics.variance,
        
        # Itertools functions
        "permutations": itertools.permutations,
        "combinations": itertools.combinations,
        "product": itertools.product,
        
        # NumPy basics
        "np": np,
        "array": np.array,
        "arange": np.arange,
        "linspace": np.linspace,
        
        # Sympy for symbolic math
        "symbols": sympy.symbols,
        "expand": sympy.expand,
        "factor": sympy.factor,
        "solve": sympy.solve,
        "sympify": sympy.sympify,
        
        # Date and time
        "datetime": datetime,
        "date": datetime.date,
        "timedelta": datetime.timedelta,
        
        # Fractions
        "Fraction": fractions.Fraction,
        
        # String operations
        "re": re,
        "string": string
    }
    
    try:
        exec(body["variables"], {}, context)
    except Exception as e:
        return False, f"Error in variables code: {str(e)}"
    
    # Validate enunciado is a string with valid expressions
    if not isinstance(body["enunciado"], str):
        return False, "Enunciado must be a string"
    
    # Extract expressions from enunciado
    pattern = r'\{([^{}]+)\}'
    expressions = re.findall(pattern, body["enunciado"])
    
    # Validate each expression in enunciado
    for expr in expressions:
        try:
            eval(expr, {}, context)
        except Exception as e:
            return False, f"Invalid expression '{expr}' in enunciado: {str(e)}"
    
    # Validate respuestas is a list
    if not isinstance(body["respuestas"], list):
        return False, "Respuestas must be a list"
    
    if len(body["respuestas"]) == 0:
        return False, "Respuestas cannot be empty"
    
    # Validate each respuesta
    for i, respuesta in enumerate(body["respuestas"]):
        # Check it's a list with at least 2 elements
        if not isinstance(respuesta, list) or len(respuesta) < 2:
            return False, f"Respuesta at index {i} must be a list with at least 2 elements"
        
        # Validate the last element is a boolean
        if len(respuesta) == 3 and not isinstance(respuesta[-1], bool):
            return False, f"The last element of respuesta at index {i} must be a boolean (correctness indicator)"
        
        # Validate the answer element is a string
        if len(respuesta) == 3 and not isinstance(respuesta[-2], str):
            return False, f"The text (second element) of respuesta at index {i} must be a string"
        
        # Extract and validate expressions in the response text
        expressions = re.findall(pattern, respuesta[-2])
        for expr in expressions:
            try:
                eval(expr, {}, context)
            except Exception as e:
                return False, f"Invalid expression '{expr}' in respuesta at index {i}: {str(e)}"
    
    # Check that at least one response is marked as correct
    has_correct = False
    for respuesta in body["respuestas"]:
        if respuesta[1]:
            has_correct = True
            break
    
    if not has_correct:
        return False, "At least one respuesta must be marked as correct"
    
    return True, None