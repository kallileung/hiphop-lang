import re
from core import *
from hiphoperrors import hiphop_error

"""
<HHE> ::= <id>
        | open <filename> as <id>
        | save <id> as <filename>
        | apply <func> to <id>
        | apply-all [<funcs>] to <id>
        | save-macro [<funcs>] as <id>

<filename> ::= "<literal>"

<funcs> ::= <func>
        | <func>, <funcs>

<func> ::= <id> <nums>

<literal> ::= STRING

<nums> ::= 
         | <num> <nums>
"""

def is_open_expr(expr_str):
    # For one line of the program, if valid program return object,
    # otherwise False

    match_filename = re.findall('(?<=open ")(.*)(?=" as)', expr_str)
    match_id = re.findall('(?<=open ")*(?<=" as )(.*)$', expr_str)
    if (len(match_filename) != 1 or len(match_id) != 1):
        return hiphop_error("ParserError", -1, 'Invalid syntax for `open` expression.')
    else:
        return open_expr(match_filename[0], match_id[0])

def is_save_expr(expr_str):

    match_id = re.findall('(?<=save )(.*)(?= as)', expr_str)
    match_filename = re.findall('(?<=save ).*(?<= as ")(.*)"', expr_str)
    print("filename: {}; id: {}".format(match_filename[0], match_id[0]))
    if (len(match_filename) != 1 or len(match_id) != 1):
        return hiphop_error("ParserError", -1, 'Invalid syntax for `save` expression.')
    else:
        return save_expr(match_id[0], match_filename[0])

def is_apply_expr(expr_str):

    match = re.findall('(?<=apply )(.*)( to )(.*)', expr_str)
    if (len(match) != 1):
        return hiphop_error("ParserError", -1, 'Invalid syntax for `apply` expression.')
    match_func, _, match_id = match[0]
    match_function= match_func.split()
    match_funcname, match_args = match_function[0], match_function[1:]
    print("funcname: {}; args: {}; id: {}".format(match_funcname, match_args, match_id))
    return apply_expr(match_funcname, match_args, match_id)

def is_apply_all_expr(expr_str):

    match = re.findall('(?<=apply-all \[)(.*)] to (.*)', expr_str)
    if (len(match) != 1):
        return hiphop_error("ParserError", -1, 'Invalid syntax for `apply-all` expression.')
    match_funcs, match_id = match[0]
    lambda_funcs = []
    new_funcs = match_funcs.split(",")
    for new_func in new_funcs:
        lambda_funcs.append(make_lambda_func(new_func.strip()))
    return apply_all_expr(lambda_funcs, match_id)

def is_save_macro_expr(expr_str):

    match = re.findall('(?<=save-macro \[)(.*)] to (.*)', expr_str)
    if (len(match) != 1):
        return hiphop_error("ParserError", -1, 'Invalid syntax for `save-macro` expression.')
    match_funcs, match_id = match[0]
    return save_macro_expr(match_funcs, match_id)

class open_expr():

    def __init__(self, filename, id):

        self.filename = filename
        self.id = id

    def evaluate(self):
        openfile(self.filename, self.id)


class save_expr():

    def __init__(self, id, filename):

        self.id = id
        self.filename = filename

    def evaluate(self):
        savefile(self.id, self.filename)

class apply_expr():

    def __init__(self, funcname, args, img):

        """
        funcname: function to call when expression is evaluated
        args: list of arguments going into the function
        img: img expression
        """

        self.funcname = funcname
        self.args = args
        self.img = img

    def evaluate(self):

        if (self.funcname == "blur"):
            if (len(self.args) != 1):
                return hiphop_error("InvalidFunctionError", -1, "Invalid number of arguments for `blur`")
            blur(self.img, int(self.args[0]))
        elif (self.funcname == "grayscale"):
            if (len(self.args) != 0):
                return hiphop_error("InvalidFunctionError", -1, "Invalid number of arguments for `grayscale`")
            grayscale(self.img)
        elif (self.funcname == "erode"):
            if (len(self.args) != 1):
                return hiphop_error("InvalidFunctionError", -1, "Invalid number of argments for `erode`")
            erode(self.img, int(self.args[0]))
        elif (self.funcname == "dilate"):
            if (len(self.args) != 1):
                return hiphop_error("InvalidFunctionError", -1, "Invalid number of argments for `erode`")
            dilate(self.img, int(self.args[0]))
        elif (self.funcname == "outline"):
            if (len(self.args) != 1):
                return hiphop_error("InvalidFunctionError", -1, "Invalid number of argments for `outline`")
            outline(self.img, int(self.args[0]))
        elif (self.funcname == "filtercolor"):
            if (len(self.args) != 6):
                return hiphop_error("InvalidFunctionError", -1, "Invalid number of arguments for `filtercolor lowR lowG lowB highR highG highB`")
            filtercolor(self.img, int(self.args[0]), int(self.args[1]), int(self.args[2]),
                                  int(self.args[3]), int(self.args[4]), int(self.args[5]))
        elif (self.funcname == "scale"):
            if (len(self.args) != 2):
                return hiphop_error("InvalidFunctionError", -1, "Invalid number of argments for `scale`")
            scale(self.img, float(self.args[0]), float(self.args[1]))
        elif (self.funcname == "crop"):
            if (len(self.args) != 4):
                return hiphop_error("InvalidFunctionError", -1, "Invalid number of arguments for `crop widthlow widthhigh heightlow heighthigh`")
            crop(self.img, float(self.args[0]), float(self.args[1]), float(self.args[2]), float(self.args[3]))
        elif (saved_macros.get_var(self.funcname) != -1):
            if len(self.args) != 0:
                return hiphop_error("InvalidFunctionError", -1, "Invalid number of arguments for `{}`".format(self.funcname))
            apply_all_expr(saved_macros.get_var(self.funcname), self.img).evaluate()
        else:
            return hiphop_error("InvalidFunctionError", -1, "Function name does not exist.")

class apply_all_expr():

    def __init__(self, apply_funcs, img):

        """
        apply_funcs: lambda functions
        img: img expression
        """

        self.apply_funcs = apply_funcs
        self.img = img 

    def evaluate(self):

        for func in self.apply_funcs:
            res = func(self.img)
            if (isinstance(res, hiphop_error)):
                return res

class save_macro_expr():

    def __init__(self, funcs, id):
        
        self.funcs = []

        # Parse the string of functions into lambda functions
        new_funcs = funcs.split(",")
        for new_func in new_funcs:
            self.funcs.append(make_lambda_func(new_func.strip()))

        self.id = id

    def evaluate(self):
        saved_macros.add_var(self.id, self.funcs)


def make_lambda_func(str):
    # From a string representation, creates a lambda function
    # ie. grayscale 50

    func_tokens = str.split(" ")
    funcname, func_args = func_tokens[0], func_tokens[1:]
    print("Making lambda function - funcname: {}, args: {}".format(funcname, func_args))

    if (funcname == "blur"):
        if (len(func_args) != 1):
            return hiphop_error("InvalidFunctionError", -1, "Invalid number of arguments for `blur`")
        return lambda img: blur(img, int(func_args[0]))
    elif (funcname == "grayscale"):
        if (len(func_args) != 0):
            return hiphop_error("InvalidFunctionError", -1, "Invalid number of arguments for `grayscale`")
        return lambda img: grayscale(img)
    else:
        return hiphop_error("InvalidFunctionError", -1, "Function name does not exist.")


class apply_funcs():

    def __init__(self, funcs_strings):
        """
        Parse string of functions and return list of lambda functions
        funcs_string: list of string representation of functions
        """
        self.apply_funcs = []
        for func_string in funcs_strings:
            self.apply_funcs.append(make_lambda_func(func_string))


class identifier():

    def __init__(self, boundvar):

        self.boundvar = boundvar

    def get_value(self):

        return self.boundvar
