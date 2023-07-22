class FunctionDecorator:
    """
    Decorator of methods found in the SUL class.
    """

    def __init__(self, function, args=None):
        """
        Args:

            function: function of the class to be learned

            args: arguments to be passed to the function. Either a single argument, or a list of arguments if
                function has more than one parameter.
        """

        self.function = function
        self.args = None
        if args:
            self.args = [args] if not isinstance(args, (list, tuple)) else args

    def __repr__(self):
        if self.args:
            # print(f'{self.function.__name__}{self.args}')
            return f'{self.function.__name__}{self.args}'
        return self.function.__name__