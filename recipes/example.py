import os

from cpl import core
from cpl import ui
from cpl.core import Msg


class Example(ui.PyRecipe):
    # Need to set values for all of these class variables.
    _name="example"
    _author="Anthony Horton"
    _copyright=""
    _description="Example of some basic data reduction processes. Expects a FrameSet containing a master dark frame, a master flat field frame, and some number of raw object frames to be processed. For each object frame it will subtract the master dark then divide by the flat field and save the resulting FITS file. It returns a FrameSet of the processed frames."
    _email="fakename@domain.org"
    _synopsis="Example of some basic data reduction processes."
    _version="1.0"
    
    def __init__(self):
        self.parameters = ui.ParameterList()

    def run(self, frameset, settings):
        # Update parameters from settings dict
        for key, value in settings.items():
            if key in self.parameters:
                self.parameters[key].value = value
            else:
                Msg.warning(self.name, f"Settings includes {key}:{value} but {self} has no parameter named {key}.")
  
        raw_frames = ui.FrameSet()
        dark_image = None
        flat_image = None
        processed_frames = ui.FrameSet()
    
        # Go through frames, check tag act accordingly.
        for frame in frameset:
            if frame.tag == "OBJECT":
                raw_frames.append(frame)
                Msg.debug(self.name, f"Got raw frame: {frame.file}.")
            elif frame.tag == "DARK":
                dark_image = core.Image.load(frame.file)
                Msg.info(self.name, f"Loaded dark frame {frame.file!r}.")
            elif frame.tag == "FLAT":
                flat_image = core.Image.load(frame.file)
                Msg.info(self.name, f"Loaded flat frame {frame.file!r}.")
            else:
                Msg.warning(self.name, f"Got frame {frame.file!r} with unexpected tag {frame.tag!r}, ignoring.")

        if not dark_image:
            raise DataNotFoundError("No dark frame in frameset.")
            
        if not flat_image:
            raise DataNotFoundError("No flat frame in frameset.")
        
        for frame in raw_frames:
            Msg.info(self.name, f"Processing {frame.file!r}...")
            Msg.debug(self.name, "Loading image.")
            raw_image = core.Image.load(frame.file)
            header = core.PropertyList.load(frame.file, 0)
            Msg.debug(self.name, "Dark subtracting...")
            raw_image.subtract(dark_image)
            Msg.debug(self.name, "Flat fielding...")
            raw_image.divide(flat_image)
            output_file = os.path.join("./products/", os.path.basename(frame.file))
            raw_image.save(output_file, header, core.io.CREATE)
            Msg.info(self.name, f"Saved processed file as {output_file!r}.")
            processed_frames.append(ui.Frame(file=output_file,
                                             tag="OBJECT",
                                             group=ui.Frame.FrameGroup.PRODUCT,
                                             level=ui.Frame.FrameLevel.INTERMEDIATE,
                                             type=ui.Frame.FrameType.IMAGE))
            processed_frames.sign_products()
            Msg.info(self.name, "Signed data products.")
            processed_frames.update_product_header()
            Msg.info(self.name, "FITS headers updated.")

        return processed_frames