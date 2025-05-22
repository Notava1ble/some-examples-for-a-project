from manim import *


class CreateCircle(Scene):
    def construct(self):
        circle = Circle()  # create a circle
        square = Square()  # create a square
        hello = Text("Hello")
        Goodbye = Text("Goodbye")
        circle.set_fill(PINK, opacity=0.5)  # set the color and transparency
        square.set_fill(BLUE, opacity=0.5)  # set the color and transparency
        self.wait(1)
        self.play(Create(circle))  # show the circle on screen
        self.wait(1)
        self.play(Transform(circle, square))  # show the circle on screen
        self.wait(1)
        self.play(Transform(circle, hello))  # show the circle on screen
        self.wait(1)
        self.play(Transform(circle, Goodbye))  # show the circle on screen
        self.wait(5)