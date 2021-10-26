import os

from cpl import core
from cpl.ui import PyRecipe, ParameterList, ParameterValue, ParameterRange, ParameterEnum


class HelloFITS(PyRecipe):
    # Need to set values for all of these class variables.
    _name="hellofits"
    _author="Anthony Horton"
    _copyright=""
    _description="A Hello World recipe that prints a greeting for each FITS file in the input FrameSet."
    _email="fakename@domain.org"
    _synopsis="Says hello to each FITS file."
    _version="1.0"
    
    # Only required method is run(), which takes a cpl.ui.FrameSet of input files and a Python
    # dictionary of recipe parameter name:value pairs, and returns a FrameSet of output files.
    def run(self, frameset, settings):
        for frame in frameset:
            print(f"Hello, {os.path.basename(frame.file)}!")

            
class HelloUser(PyRecipe):
    _name="hellouser"
    _author="Anthony Horton"
    _copyright=""
    _description="An example that includes parameters."
    _email="fakename@domain.org"
    _synopsis="Greets the user and lists the first N FITS files."
    _version="1.0"

    # Recipes are expected to store their settings as Parameters, in a ParameterList, as self.parameters
    def __init__(self):
        self.parameters = ParameterList((ParameterValue(name="hellouser.username",
                                                        context="hellouser",
                                                        description="User's name",
                                                        default="Unknown User"),
                                         ParameterRange(name="hellouser.nfits",
                                                        context="hellouser",
                                                        description="Number of FITS files to process.",
                                                        default=3,
                                                        min=1,
                                                        max=5),
                                         ParameterEnum(name="hellouser.reaction",
                                                       context="hellouser",
                                                       description="Reaction to the user.",
                                                       default="nice",
                                                       alternatives=("nice", "nasty"))))

    # Only required method is run(), which takes a cpl.ui.FrameSet of input files and a Python
    # dictionary of recipe parameter name:value pairs, and returns a FrameSet of output files.
    def run(self, frameset, settings):
        # Update parameters from settings dict
        for key, value in settings.items():
            try:
                self.parameters[key].value = value
            except KeyError:
                core.Msg.warning(self.name, f"Settings includes {key}:{value} but {self} has no parameter named {key}.")
        
        print(f"Hello, {self.parameters['hellouser.username'].value}, " +
              f"{self.parameters['hellouser.reaction'].value} to see you.\n")

        print(f"The first {self.parameters['hellouser.nfits'].value} FITS files are:\n")

        for i, frame in enumerate(frameset):
            if i >= self.parameters['hellouser.nfits'].value:
                break
            print(frame.file)
