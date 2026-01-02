"""
Extended Primitive Set for Genetic Programming

Adds much richer primitives beyond basic arithmetic:
- Data structure manipulation (lists, dicts, trees)
- String operations
- Advanced control flow (recursion, closures)
- External API calls
- Image/signal processing primitives
- Graph operations
"""

from enum import Enum
from typing import Any, Dict, List, Tuple, Callable, Optional
import math
import random


class ExtendedNodeType(Enum):
    """Extended node types for richer GP."""

    # ==== Data Structure Operations ====

    # Lists
    LIST_CREATE = "list_create"
    LIST_APPEND = "list_append"
    LIST_GET = "list_get"
    LIST_SET = "list_set"
    LIST_LEN = "list_len"
    LIST_SLICE = "list_slice"
    LIST_CONCAT = "list_concat"
    LIST_MAP = "list_map"
    LIST_FILTER = "list_filter"
    LIST_REDUCE = "list_reduce"
    LIST_SORT = "list_sort"
    LIST_REVERSE = "list_reverse"
    LIST_FIND = "list_find"

    # Dictionaries
    DICT_CREATE = "dict_create"
    DICT_GET = "dict_get"
    DICT_SET = "dict_set"
    DICT_HAS = "dict_has"
    DICT_KEYS = "dict_keys"
    DICT_VALUES = "dict_values"
    DICT_MERGE = "dict_merge"

    # Trees
    TREE_CREATE = "tree_create"
    TREE_LEFT = "tree_left"
    TREE_RIGHT = "tree_right"
    TREE_VALUE = "tree_value"
    TREE_INSERT = "tree_insert"
    TREE_TRAVERSE = "tree_traverse"

    # Stacks/Queues
    STACK_PUSH = "stack_push"
    STACK_POP = "stack_pop"
    QUEUE_ENQUEUE = "queue_enqueue"
    QUEUE_DEQUEUE = "queue_dequeue"

    # ==== Advanced Control Flow ====

    # Recursion
    RECURSIVE_CALL = "recursive_call"
    TAIL_CALL = "tail_call"
    MEMOIZE = "memoize"

    # Closures
    CLOSURE_CREATE = "closure_create"
    CLOSURE_CALL = "closure_call"
    CAPTURE_VAR = "capture_var"

    # Iteration
    FOR_EACH = "for_each"
    WHILE_DO = "while_do"
    DO_WHILE = "do_while"
    MAP_ITER = "map_iter"
    FILTER_ITER = "filter_iter"

    # Exceptions
    TRY_CATCH = "try_catch"
    THROW = "throw"
    ASSERT = "assert"

    # ==== String Operations ====

    STRING_CONCAT = "str_concat"
    STRING_SPLIT = "str_split"
    STRING_JOIN = "str_join"
    STRING_REPLACE = "str_replace"
    STRING_UPPER = "str_upper"
    STRING_LOWER = "str_lower"
    STRING_SUBSTR = "str_substr"
    STRING_LEN = "str_len"
    STRING_FIND = "str_find"
    STRING_FORMAT = "str_format"
    STRING_PARSE = "str_parse"

    # ==== Mathematical Extensions ====

    # Trigonometry
    SIN = "sin"
    COS = "cos"
    TAN = "tan"
    ASIN = "asin"
    ACOS = "acos"
    ATAN = "atan"
    ATAN2 = "atan2"

    # Advanced math
    EXP = "exp"
    LOG = "log"
    LOG10 = "log10"
    SQRT = "sqrt"
    ABS = "abs"
    CEIL = "ceil"
    FLOOR = "floor"
    ROUND = "round"

    # Statistics
    MIN = "min"
    MAX = "max"
    SUM = "sum"
    MEAN = "mean"
    MEDIAN = "median"
    STDDEV = "stddev"
    VARIANCE = "variance"

    # Linear algebra
    VECTOR_DOT = "vector_dot"
    VECTOR_CROSS = "vector_cross"
    VECTOR_NORM = "vector_norm"
    MATRIX_MUL = "matrix_mul"
    MATRIX_TRANSPOSE = "matrix_transpose"
    MATRIX_INVERSE = "matrix_inverse"

    # ==== Signal Processing ====

    FFT = "fft"
    IFFT = "ifft"
    CONVOLVE = "convolve"
    FILTER_LOWPASS = "filter_lowpass"
    FILTER_HIGHPASS = "filter_highpass"

    # ==== Image Processing (simplified) ====

    IMAGE_RESIZE = "image_resize"
    IMAGE_CROP = "image_crop"
    IMAGE_ROTATE = "image_rotate"
    IMAGE_FILTER = "image_filter"
    IMAGE_THRESHOLD = "image_threshold"
    IMAGE_EDGE_DETECT = "image_edge_detect"

    # ==== Graph Operations ====

    GRAPH_CREATE = "graph_create"
    GRAPH_ADD_NODE = "graph_add_node"
    GRAPH_ADD_EDGE = "graph_add_edge"
    GRAPH_NEIGHBORS = "graph_neighbors"
    GRAPH_SHORTEST_PATH = "graph_shortest_path"
    GRAPH_DFS = "graph_dfs"
    GRAPH_BFS = "graph_bfs"
    GRAPH_CONNECTED_COMPONENTS = "graph_connected_components"

    # ==== Pattern Matching ====

    REGEX_MATCH = "regex_match"
    REGEX_FIND_ALL = "regex_find_all"
    REGEX_REPLACE = "regex_replace"
    PATTERN_EXTRACT = "pattern_extract"

    # ==== Type Operations ====

    TYPE_OF = "type_of"
    IS_NUMBER = "is_number"
    IS_STRING = "is_string"
    IS_LIST = "is_list"
    CAST_INT = "cast_int"
    CAST_FLOAT = "cast_float"
    CAST_STRING = "cast_string"

    # ==== Parallel Operations ====

    PARALLEL_MAP = "parallel_map"
    PARALLEL_REDUCE = "parallel_reduce"
    ASYNC_CALL = "async_call"
    AWAIT = "await"

    # ==== External APIs (placeholders for extensibility) ====

    API_CALL = "api_call"
    HTTP_GET = "http_get"
    HTTP_POST = "http_post"
    FILE_READ = "file_read"
    FILE_WRITE = "file_write"


# Arity map for extended node types
EXTENDED_NODE_ARITY = {
    # Lists
    ExtendedNodeType.LIST_CREATE: 0,  # Variable args
    ExtendedNodeType.LIST_APPEND: 2,
    ExtendedNodeType.LIST_GET: 2,
    ExtendedNodeType.LIST_SET: 3,
    ExtendedNodeType.LIST_LEN: 1,
    ExtendedNodeType.LIST_SLICE: 3,
    ExtendedNodeType.LIST_CONCAT: 2,
    ExtendedNodeType.LIST_MAP: 2,
    ExtendedNodeType.LIST_FILTER: 2,
    ExtendedNodeType.LIST_REDUCE: 3,
    ExtendedNodeType.LIST_SORT: 1,
    ExtendedNodeType.LIST_REVERSE: 1,
    ExtendedNodeType.LIST_FIND: 2,

    # Dicts
    ExtendedNodeType.DICT_CREATE: 0,
    ExtendedNodeType.DICT_GET: 2,
    ExtendedNodeType.DICT_SET: 3,
    ExtendedNodeType.DICT_HAS: 2,
    ExtendedNodeType.DICT_KEYS: 1,
    ExtendedNodeType.DICT_VALUES: 1,
    ExtendedNodeType.DICT_MERGE: 2,

    # Trees
    ExtendedNodeType.TREE_CREATE: 3,  # value, left, right
    ExtendedNodeType.TREE_LEFT: 1,
    ExtendedNodeType.TREE_RIGHT: 1,
    ExtendedNodeType.TREE_VALUE: 1,
    ExtendedNodeType.TREE_INSERT: 2,
    ExtendedNodeType.TREE_TRAVERSE: 2,

    # Stacks/Queues
    ExtendedNodeType.STACK_PUSH: 2,
    ExtendedNodeType.STACK_POP: 1,
    ExtendedNodeType.QUEUE_ENQUEUE: 2,
    ExtendedNodeType.QUEUE_DEQUEUE: 1,

    # Control flow
    ExtendedNodeType.RECURSIVE_CALL: 2,
    ExtendedNodeType.TAIL_CALL: 2,
    ExtendedNodeType.MEMOIZE: 1,
    ExtendedNodeType.CLOSURE_CREATE: 2,
    ExtendedNodeType.CLOSURE_CALL: 2,
    ExtendedNodeType.CAPTURE_VAR: 1,
    ExtendedNodeType.FOR_EACH: 2,
    ExtendedNodeType.WHILE_DO: 2,
    ExtendedNodeType.DO_WHILE: 2,
    ExtendedNodeType.MAP_ITER: 2,
    ExtendedNodeType.FILTER_ITER: 2,
    ExtendedNodeType.TRY_CATCH: 2,
    ExtendedNodeType.THROW: 1,
    ExtendedNodeType.ASSERT: 2,

    # Strings
    ExtendedNodeType.STRING_CONCAT: 2,
    ExtendedNodeType.STRING_SPLIT: 2,
    ExtendedNodeType.STRING_JOIN: 2,
    ExtendedNodeType.STRING_REPLACE: 3,
    ExtendedNodeType.STRING_UPPER: 1,
    ExtendedNodeType.STRING_LOWER: 1,
    ExtendedNodeType.STRING_SUBSTR: 3,
    ExtendedNodeType.STRING_LEN: 1,
    ExtendedNodeType.STRING_FIND: 2,
    ExtendedNodeType.STRING_FORMAT: 2,
    ExtendedNodeType.STRING_PARSE: 1,

    # Math
    ExtendedNodeType.SIN: 1,
    ExtendedNodeType.COS: 1,
    ExtendedNodeType.TAN: 1,
    ExtendedNodeType.ASIN: 1,
    ExtendedNodeType.ACOS: 1,
    ExtendedNodeType.ATAN: 1,
    ExtendedNodeType.ATAN2: 2,
    ExtendedNodeType.EXP: 1,
    ExtendedNodeType.LOG: 1,
    ExtendedNodeType.LOG10: 1,
    ExtendedNodeType.SQRT: 1,
    ExtendedNodeType.ABS: 1,
    ExtendedNodeType.CEIL: 1,
    ExtendedNodeType.FLOOR: 1,
    ExtendedNodeType.ROUND: 1,

    # Statistics
    ExtendedNodeType.MIN: 2,
    ExtendedNodeType.MAX: 2,
    ExtendedNodeType.SUM: 1,
    ExtendedNodeType.MEAN: 1,
    ExtendedNodeType.MEDIAN: 1,
    ExtendedNodeType.STDDEV: 1,
    ExtendedNodeType.VARIANCE: 1,

    # Linear algebra
    ExtendedNodeType.VECTOR_DOT: 2,
    ExtendedNodeType.VECTOR_CROSS: 2,
    ExtendedNodeType.VECTOR_NORM: 1,
    ExtendedNodeType.MATRIX_MUL: 2,
    ExtendedNodeType.MATRIX_TRANSPOSE: 1,
    ExtendedNodeType.MATRIX_INVERSE: 1,

    # Signal processing
    ExtendedNodeType.FFT: 1,
    ExtendedNodeType.IFFT: 1,
    ExtendedNodeType.CONVOLVE: 2,
    ExtendedNodeType.FILTER_LOWPASS: 2,
    ExtendedNodeType.FILTER_HIGHPASS: 2,

    # Image processing
    ExtendedNodeType.IMAGE_RESIZE: 3,
    ExtendedNodeType.IMAGE_CROP: 5,
    ExtendedNodeType.IMAGE_ROTATE: 2,
    ExtendedNodeType.IMAGE_FILTER: 2,
    ExtendedNodeType.IMAGE_THRESHOLD: 2,
    ExtendedNodeType.IMAGE_EDGE_DETECT: 1,

    # Graph operations
    ExtendedNodeType.GRAPH_CREATE: 0,
    ExtendedNodeType.GRAPH_ADD_NODE: 2,
    ExtendedNodeType.GRAPH_ADD_EDGE: 3,
    ExtendedNodeType.GRAPH_NEIGHBORS: 2,
    ExtendedNodeType.GRAPH_SHORTEST_PATH: 3,
    ExtendedNodeType.GRAPH_DFS: 2,
    ExtendedNodeType.GRAPH_BFS: 2,
    ExtendedNodeType.GRAPH_CONNECTED_COMPONENTS: 1,

    # Pattern matching
    ExtendedNodeType.REGEX_MATCH: 2,
    ExtendedNodeType.REGEX_FIND_ALL: 2,
    ExtendedNodeType.REGEX_REPLACE: 3,
    ExtendedNodeType.PATTERN_EXTRACT: 2,

    # Type operations
    ExtendedNodeType.TYPE_OF: 1,
    ExtendedNodeType.IS_NUMBER: 1,
    ExtendedNodeType.IS_STRING: 1,
    ExtendedNodeType.IS_LIST: 1,
    ExtendedNodeType.CAST_INT: 1,
    ExtendedNodeType.CAST_FLOAT: 1,
    ExtendedNodeType.CAST_STRING: 1,

    # Parallel
    ExtendedNodeType.PARALLEL_MAP: 2,
    ExtendedNodeType.PARALLEL_REDUCE: 3,
    ExtendedNodeType.ASYNC_CALL: 1,
    ExtendedNodeType.AWAIT: 1,

    # External APIs
    ExtendedNodeType.API_CALL: 2,
    ExtendedNodeType.HTTP_GET: 1,
    ExtendedNodeType.HTTP_POST: 2,
    ExtendedNodeType.FILE_READ: 1,
    ExtendedNodeType.FILE_WRITE: 2,
}


class ExtendedPrimitiveExecutor:
    """
    Executor for extended primitives.

    Provides implementations for all extended node types.
    """

    def __init__(self, safe_mode: bool = True):
        self.safe_mode = safe_mode
        self.memoization_cache: Dict[Tuple, Any] = {}

    def execute_extended(
        self,
        node_type: ExtendedNodeType,
        args: List[Any]
    ) -> Any:
        """Execute an extended primitive."""

        # Lists
        if node_type == ExtendedNodeType.LIST_CREATE:
            return []
        elif node_type == ExtendedNodeType.LIST_APPEND:
            lst, val = args
            if isinstance(lst, list):
                return lst + [val]
            return [val]
        elif node_type == ExtendedNodeType.LIST_GET:
            lst, idx = args
            if isinstance(lst, list) and isinstance(idx, (int, float)):
                idx = int(idx) % max(len(lst), 1)
                return lst[idx] if lst else 0
            return 0
        elif node_type == ExtendedNodeType.LIST_LEN:
            return len(args[0]) if isinstance(args[0], (list, str)) else 0
        elif node_type == ExtendedNodeType.LIST_MAP:
            lst, func = args
            if isinstance(lst, list) and callable(func):
                return [func(x) for x in lst]
            return lst
        elif node_type == ExtendedNodeType.LIST_FILTER:
            lst, func = args
            if isinstance(lst, list) and callable(func):
                return [x for x in lst if func(x)]
            return lst

        # Math
        elif node_type == ExtendedNodeType.SIN:
            return math.sin(float(args[0]))
        elif node_type == ExtendedNodeType.COS:
            return math.cos(float(args[0]))
        elif node_type == ExtendedNodeType.TAN:
            return math.tan(float(args[0]))
        elif node_type == ExtendedNodeType.EXP:
            try:
                return math.exp(min(100, float(args[0])))  # Prevent overflow
            except (OverflowError, ValueError, TypeError):
                # OverflowError: if exp result too large
                # ValueError: if invalid value
                # TypeError: if wrong type
                return 0.0
        elif node_type == ExtendedNodeType.LOG:
            try:
                return math.log(abs(float(args[0])) + 1e-10)
            except (ValueError, TypeError):
                # ValueError: if value is invalid for log
                # TypeError: if wrong type
                return 0.0
        elif node_type == ExtendedNodeType.SQRT:
            return math.sqrt(abs(float(args[0])))
        elif node_type == ExtendedNodeType.ABS:
            return abs(float(args[0]))

        # Statistics
        elif node_type == ExtendedNodeType.MIN:
            try:
                return min(float(args[0]), float(args[1]))
            except (ValueError, TypeError):
                # ValueError: if cannot convert to float
                # TypeError: if wrong type
                return 0.0
        elif node_type == ExtendedNodeType.MAX:
            try:
                return max(float(args[0]), float(args[1]))
            except (ValueError, TypeError):
                # ValueError: if cannot convert to float
                # TypeError: if wrong type
                return 0.0
        elif node_type == ExtendedNodeType.SUM:
            if isinstance(args[0], list):
                return sum(float(x) for x in args[0] if isinstance(x, (int, float)))
            return float(args[0])
        elif node_type == ExtendedNodeType.MEAN:
            if isinstance(args[0], list) and args[0]:
                vals = [float(x) for x in args[0] if isinstance(x, (int, float))]
                return sum(vals) / len(vals) if vals else 0.0
            return 0.0

        # Strings
        elif node_type == ExtendedNodeType.STRING_CONCAT:
            return str(args[0]) + str(args[1])
        elif node_type == ExtendedNodeType.STRING_LEN:
            return len(str(args[0]))
        elif node_type == ExtendedNodeType.STRING_UPPER:
            return str(args[0]).upper()
        elif node_type == ExtendedNodeType.STRING_LOWER:
            return str(args[0]).lower()

        # Dicts
        elif node_type == ExtendedNodeType.DICT_CREATE:
            return {}
        elif node_type == ExtendedNodeType.DICT_GET:
            d, key = args
            if isinstance(d, dict):
                return d.get(str(key), 0)
            return 0
        elif node_type == ExtendedNodeType.DICT_SET:
            d, key, val = args
            if isinstance(d, dict):
                result = d.copy()
                result[str(key)] = val
                return result
            return {str(key): val}

        # Type operations
        elif node_type == ExtendedNodeType.IS_NUMBER:
            return isinstance(args[0], (int, float))
        elif node_type == ExtendedNodeType.IS_STRING:
            return isinstance(args[0], str)
        elif node_type == ExtendedNodeType.IS_LIST:
            return isinstance(args[0], list)
        elif node_type == ExtendedNodeType.CAST_INT:
            try:
                return int(float(args[0]))
            except (ValueError, TypeError):
                # ValueError: if cannot convert to int
                # TypeError: if wrong type
                return 0
        elif node_type == ExtendedNodeType.CAST_FLOAT:
            try:
                return float(args[0])
            except (ValueError, TypeError):
                # ValueError: if cannot convert to float
                # TypeError: if wrong type
                return 0.0
        elif node_type == ExtendedNodeType.CAST_STRING:
            return str(args[0])

        # Default
        return 0.0

    def get_available_primitives(self) -> List[ExtendedNodeType]:
        """Get list of available extended primitives."""
        return list(ExtendedNodeType)

    def get_primitive_categories(self) -> Dict[str, List[ExtendedNodeType]]:
        """Get primitives grouped by category."""
        categories = {
            'lists': [],
            'dicts': [],
            'trees': [],
            'control_flow': [],
            'strings': [],
            'math': [],
            'statistics': [],
            'linear_algebra': [],
            'signal_processing': [],
            'image_processing': [],
            'graphs': [],
            'patterns': [],
            'types': [],
            'parallel': [],
            'external': []
        }

        for prim in ExtendedNodeType:
            name = prim.value
            if 'list_' in name:
                categories['lists'].append(prim)
            elif 'dict_' in name:
                categories['dicts'].append(prim)
            elif 'tree_' in name:
                categories['trees'].append(prim)
            elif name in ['for_each', 'while_do', 'recursive_call', 'closure_create']:
                categories['control_flow'].append(prim)
            elif 'str_' in name or 'string_' in name:
                categories['strings'].append(prim)
            elif name in ['sin', 'cos', 'tan', 'exp', 'log', 'sqrt', 'abs']:
                categories['math'].append(prim)
            elif name in ['min', 'max', 'sum', 'mean', 'median', 'stddev']:
                categories['statistics'].append(prim)
            elif 'vector_' in name or 'matrix_' in name:
                categories['linear_algebra'].append(prim)
            elif 'fft' in name or 'filter_' in name or 'convolve' in name:
                categories['signal_processing'].append(prim)
            elif 'image_' in name:
                categories['image_processing'].append(prim)
            elif 'graph_' in name:
                categories['graphs'].append(prim)
            elif 'regex_' in name or 'pattern_' in name:
                categories['patterns'].append(prim)
            elif 'is_' in name or 'cast_' in name or 'type_' in name:
                categories['types'].append(prim)
            elif 'parallel_' in name or 'async' in name or 'await' in name:
                categories['parallel'].append(prim)
            elif 'api_' in name or 'http_' in name or 'file_' in name:
                categories['external'].append(prim)

        return {k: v for k, v in categories.items() if v}
