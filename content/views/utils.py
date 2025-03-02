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

def process_visualization(body):
    """
    Process a 'seleccion' content body for visualization.
    
    Args:
        body (dict): The body content of a 'seleccion' type question
        
    Returns:
        dict: Processed body with variables resolved and any visualization enhancements
    """
    processed_body = {}

    # 1. Execute the variables code to create the variables in context
    variables_code = body.get("variables", "")
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

      # Custom formatter to evaluate expressions
    def evaluate_expressions(text):
        def replace_expr(match):
            expr = match.group(1)
            try:
                result = eval(expr, {}, context)
                return str(result)
            except Exception as e:
                raise ValueError(f"Failed to evaluate expression '{expr}': {str(e)}")
        
        # Find expressions in curly braces and evaluate them
        pattern = r'\{([^{}]+)\}'
        return re.sub(pattern, replace_expr, text)

    try:
        # Execute the variables code
        exec(variables_code, {}, context)
    except Exception as e:
        return {"error": f"Error processing variables: {str(e)}"}
    
    # 2. Process the enunciado with expression evaluation
    try:
        processed_body["enunciado"] = evaluate_expressions(body["enunciado"])
    except Exception as e:
        return {"error": f"Error formatting enunciado: {str(e)}"}
    
    # 3. Process each response text with expression evaluation
    processed_responses = []
    for resp in body.get("respuestas", []):
        try:
            # Each resp is [id, text]
            id_value = resp[0]
            text_value = evaluate_expressions(resp[1])
            processed_responses.append([id_value, text_value])
        except Exception as e:
            return {"error": f"Error formatting response text: {str(e)}"}
    
    processed_body["respuestas"] = processed_responses

    return processed_body

