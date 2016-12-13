# Project Phase 2
# CMSC 671

#   Sabin Raj Tiwari
#   Shantanu Sengupta
#   Harsh Vashishta
#   Sushant Chaudhari

# References for the code
#   https://docs.python.org/
#   https://docs.python.org/2.7/tutorial/datastructures.html
#   https://docs.python.org/2/library/itertools.html#itertools.product
#   https://www.tutorialspoint.com/python/python_command_line_arguments.htm
#   http://stackoverflow.com/questions/1228299/change-one-character-in-a-string-in-python
#   http://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float-in-python


# Trivial functions to be used in the important test functions
# All require a nonempty string as the argument

def is_suit(s):
    """Test if parameter is one of Club, Diamond, Heart, Spade"""
    return s in "CDHS"

def is_color(s):
    """Test if parameter is one of Black or Red"""
    return s in "BR"

def is_value(s):
    """Test if parameter is a number or can be interpreted as a number"""
    s = str(s)
    # print s.isdigit() or (len(s) == 1 and s[0] in "AJQK");
    return s.isdigit() or (len(s) == 1 and s[0] in "AJQK")

def is_card(s):
    """Test if parameter is a value followed by a suit"""
    s = str(s);
    # print s;
    # print is_suit(s[-1]) and is_value(s[:len(s) - 1]);
    return is_suit(s[-1]) and is_value(s[:len(s) - 1])

def value_to_number(name):

    """Given the "value" part of a card, returns its numeric value"""
    values = [None, 'A', '2', '3', '4', '5', '6',
              '7', '8', '9', '10', 'J', 'Q', 'K']
    return values.index(name)

def number_to_value(number):
    """Given the numeric value of a card, returns its "value" name"""
    values = [None, 'A', '2', '3', '4', '5', '6',
              '7', '8', '9', '10', 'J', 'Q', 'K']
    return values[number]

# -------------------- Important functions

def suit(card):
    """Returns the suit of a card"""
    return card[-1]

def color(card):
    """Returns the color of a card"""
    return {'C':'B', 'D':'R', 'H':'R', 'S':'B'}.get(suit(card))

def value(card):
    """Returns the numeric value of a card or card value as an integer 1..13"""
    prefix = card[:len(card) - 1]
    names = {'A':1, 'J':11, 'Q':12, 'K':13}
    if prefix in names:
        return int(names.get(prefix))
    else:
        return int(prefix)

def is_royal(card):
    """Tests if a card is royalty (Jack, Queen, or King)"""
    return value(card) > 10

def equal(a, b):
    """Tests if two suits, two colors, two cards, or two values are equal."""
    return str(a) == str(b) # This is to allow comparisons with integers

def less(a, b):
    """Tests if a is less than b, where a and b are suits, cards,
       colors, or values. For suits: C < D < H < S. For colors,
       B < R. For cards, suits are considered first, then values.
       Values are compared numerically."""
    if is_card(a):
        if suit(a) != suit(b):
            return suit(a) < suit(b)
        else:
            return value(a) < value(b)
    elif is_value(a):
    	a = number_to_value(int(a));
    	b = number_to_value(int(b));

        return value_to_number(a) < value_to_number(b)
    else:
        return a < b

def greater(a, b):
    """The opposite of less"""
    return less(b, a)

def plus1(x):
    """Returns the next higher value, suit, or card in a suit;
       must be one. If a color, returns the other color"""
    if is_value(x):
        z = value_to_number(number_to_value(x))
    	
    
        return x+1;
    elif is_suit(x):
        if x == 'S':
            return 'C'
        return "CDHS"["CDHS".index(x) + 1]
    elif is_card(x):
        return number_to_value(value(x) + 1) + suit(x)
    elif is_color(x):
        return "BR"["BR".index(x) - 1]
    
def minus1(x):
    """Returns the next lower value, suit, or card in a suit;
       must be one. If a color, returns the other color"""
    if is_value(x):
        z = value_to_number(number_to_value(x))

        return x-1;
    elif is_suit(x):
        if x == 'C':
            return 'S';
        return "CDHS"["CDHS".index(x) - 1]
    elif is_card(x):
        return number_to_value(value(x) - 1) + suit(x)
    elif is_color(x):
        return "BR"["BR".index(x) - 1]

def even(card):
    """Tells if the card's numeric value is even"""
    return value(card) % 2 == 0

def odd(card):
    """Tells if the card's numeric value is odd"""
    return value(card) % 2 != 0

# -------------------- Lists of allowable functions

# These functions are declared so that logic can be supported;
# the actual implementation is in the 'evaluate' function
def andf(): pass
def orf():  pass
def notf(): pass
def iff():  pass

functions = [suit, color, value, is_royal, equal, less,
             greater, plus1, minus1, even, odd, andf,
             orf, notf, iff]

function_names = ['suit', 'color', 'value', 'is_royal',
                  'equal', 'equals', 'less', 'greater', 'plus1',
                  'minus1', 'even', 'odd', 'andf', 'orf',
                  'notf', 'iff', 'and', 'or', 'not', 'if']

# ----- Functions for creating, printing, and evaluating Trees

# Build a dictionary from function names to actual functions
to_function = {'and':andf, 'or':orf, 'not':notf, 'if':iff, 'equals':equal}
for f in functions:
    to_function[f.__name__] = f
    
def quote_if_needed(s):
    """If s is not a function, quote it"""
    function_names = map(lambda x: x.__name__, functions)
    return s if s in function_names else "'" + s + "'"

def scan(s):
    """This is an iterator for "tokens," where a token is a
       parenthesis or sequence of nonblank characters; commas
       and whitespace act as delimiters, and are discarded"""
    token = ''
    for ch in s:
        if ch.isspace():
            continue
        if ch in '(),':
            if token != '':
                yield token
                token = ''
            if ch != ',':
                yield ch
        else:
            token += ch
    if token != '':
        yield token
            
def tree(s):
    """Given a function in the usual "f(a, b)" notation, returns
       a Tree representation of that function, for example,
       equal(color(current),'R') becomes
       Tree(equal(Tree(color(current)),'R')) """
    tokens = list(scan(s))
    if len(tokens) == 1:
        return tokens[0]
    expr = ""
    functions = [] # a stack of functions
    args = []      # a stack of argument lists
    depth = 0
    for i in range(0, len(tokens) - 1):
        if tokens[i + 1] == '(':
            f = to_function[tokens[i]]
            depth += 1
        expr += tokens[i]
        if tokens[i] == ')':
            expr += ')'
            depth -= 1
    assert depth == 1, "*** Unmatched parentheses ***"
    return expr + '))'

def combine(f, args):
    """Makes a Tree from a function and a list of arguments"""
    if len(args) == 1:
        return Tree(f, args[0])
    elif len(args) == 2:
        return Tree(f, args[0], args[1])
    elif len(args) == 3:
        return Tree(f, args[0], args[1], args[2])
    else:
        raise Exception, "Incorrect arguments: {} {}".format(f, str(args))
    
def parse(s):
    """Converts a string representation of a rule into a Tree"""
    def parse2(s, i):
        if s[i] in function_names:
            f = to_function.get(s[i])
            assert s[i + 1] == "(", "No open parenthesis after " + s[i]
            (arg, i) = parse2(s, i + 2)
            args = [arg]
            while s[i] != ")":
                (arg, i) = parse2(s, i)
                args.append(arg)
            subtree = combine(f, args)
            return (subtree, i + 1)
        else:
            return (s[i], i + 1)
    return parse2(list(scan(s)), 0)[0]
        
class Tree:

    def __init__(self, root, first=None, second=None, third=None):
        """Create a new Tree; default is no children"""
        self.root = root
        assert root in functions
        if third == None:
            self.test = None
            self.left = first
            self.right = second
        else: # rearrange parameters so test can be put first
            self.test = first
            self.left = second
            self.right = third

    def __str__(self):
        """Provide a printable representation of this Tree"""
        if self.test != None: # it's an iff Tree
            return 'iff({}, {}, {})'.format(self.left, self.right, self.test)
        if self.left == None and self.right == None:
            return str(self.root)
        elif self.right == None:
            return '{}({})'.format(self.root.__name__, self.left)
        else:
            return '{}({}, {})'.format(self.root.__name__, self.left, self.right)

    def __repr__(self):
        s = "Tree("
        if self.root in functions:
            s += self.root.__name__
        else:
            str(self.root) + '!'
        if self.left != None:  s += ", " + repr(self.left)
        if self.right != None: s += ", " + repr(self.right)
        if self.test != None:  s += ", " + repr(self.test)
        return s + ")"
    
##    debugging = True
##    def evaluate(self, cards):
##        """For debugging, uncomment these lines and change
##           the name of evaluate (below) to evaluate"""
##        before = str(self)
##        after = self.evaluate2(cards)
##        if self.debugging: print "Tree: ", before, "-->", after
##        return after
    
    def evaluate(self, cards):
        """Evaluate this tree with the given card values"""
        def subeval(expr):
            if expr.__class__.__name__ == "Tree":
                return expr.evaluate(cards)
            else:
                if expr == "current":
                    return current
                elif expr == "previous":
                    return previous
                elif expr == "previous2":
                    return previous2
                else:
                    return expr
        try:
            (previous2, previous, current) = cards
            f = self.root
            if f not in functions:
                return f
            
            if f in [suit, color, value, is_royal, minus1, plus1, even, odd]:
                return f(subeval(self.left))
            
            elif f in [equal, less, greater]:
                return f(subeval(self.left), subeval(self.right))
            
            elif f == andf:
                if subeval(self.left):
                    return subeval(self.right)
                return False
            
            elif f == orf:
                if subeval(self.left):
                    return True
                return subeval(self.right)
            
            elif f == notf:
                return not subeval(self.left)
            
            elif f == iff:
                if subeval(self.test):
                    return subeval(self.left)
                else:
                    return subeval(self.right)
        except Exception as e:
            # print e
            # # print "Expression = ", self
            # # print " with cards =", cards
            raise
