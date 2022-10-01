import sys


class ButtonHandler:
    def press_a(self):
        print("Pressed A", file=sys.stderr)
        self.a()

    def press_b(self):
        print("Pressed B", file=sys.stderr)
        self.b()
        
    def press_c(self):
        print("Pressed C", file=sys.stderr)
        self.c()
        
    def press_d(self):
        print("Pressed D", file=sys.stderr)
        self.d()

    def a(self):
        ...
    def b(self):
        ...
    def c(self):
        ...
    def d(self):
        ...  