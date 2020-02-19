import argparse
import os
import sys
import tempfile

from argparse import RawTextHelpFormatter
from logging import getLogger

import numpy as np

from mantidimaging.core.configs.functional_config import FunctionalConfig
from mantidimaging.core.configs.filter_registration import (register_filters_on_cli)


def grab_full_config(default_args=None):
    """
    Build the command line at runtime, by parsing all of the filters'
    parameter.

    Afterwards parses the arguments passed in from command line, updates the
    vales and creates the ReconstructionConfig.
    """
    # intentionally not importing with the whole module sometimes we don't want
    # to process the sys.argv arguments

    parser = argparse.ArgumentParser(description="Run image processing and tomographic reconstruction via "
                                     "third party tools",
                                     formatter_class=RawTextHelpFormatter)

    # this sets up the arguments in the parser, with defaults from the Config
    # file
    functional_args = FunctionalConfig()
    parser = functional_args._setup_parser(parser)

    # setup args for the filters
    register_filters_on_cli(parser)

    # generate a list of both default arguments and real arguments
    arg_list = default_args if default_args is not None else []
    arg_list += sys.argv[1:]

    # so parsing
    args = parser.parse_args(arg_list)

    # update the configs
    functional_args._update(args)

    # combine all of them together
    return ReconstructionConfig(functional_args, args)


class ReconstructionConfig(object):
    """
    Full configuration (pre-proc + tool/algorithm + post-proc.
    """
    def __init__(self, functional_config, args, special_args=True):
        """
        :param functional_config: The functional config,
                                  must be the class FunctionalConfig
        :param args: All of the arguments parsed by argparser
        :param funsafe: If funsafe the special arguments check will be skipped
        """
        # just some sanity checks
        assert isinstance(functional_config,
                          FunctionalConfig), "Functional config is invalid type. The script might be corrupted."

        self.func = functional_config
        self.args = args

        # THIS MUST BE THE LAST THING THIS FUNCTION DOES
        if special_args:
            self.handle_special_arguments()

    def handle_special_arguments(self):
        log = getLogger(__name__)

        if self.args.region_of_interest:
            if len(self.args.region_of_interest) != 4:
                raise ValueError("Not enough arguments provided for the Region of Interest!"
                                 " Expecting 4, but found {0}: {1}".format(len(self.args.region_of_interest),
                                                                           self.args.region_of_interest))

            self.args.region_of_interest = [int(val) for val in self.args.region_of_interest]

        if self.args.air_region:
            if len(self.args.air_region) != 4:
                raise ValueError("Not enough arguments provided for the Air Region "
                                 "Normalisation! Expecting 4, but found {0}: {1}".format(
                                     len(self.args.air_region), self.args.air_region))

            self.args.air_region = [int(val) for val in self.args.air_region]

        if (self.func.save_preproc or self.func.convert or self.func.aggregate) and not self.func.output_path:
            raise ValueError("An option was specified that requires an output directory, "
                             "but no output directory was given!\n"
                             "The options that require output directory are:\n"
                             "-s/--save-preproc, --convert, --aggregate")

        if self.func.cors is None and self.func.reconstruction:
            raise ValueError("If running a reconstruction a Center of " "Rotation MUST be provided")

        if self.func.cors and os.path.exists(self.func.cors[0]):
            # If the provided cors is a filename then load COR from file
            from mantidimaging.core.imopr.helper import load_cors_from_file
            cors = load_cors_from_file(self.func.cors[0])
            self.func.cors = []
            self.func.cor_slices = []
            for c in cors:
                self.func.cor_slices.append(int(c[0]))
                self.func.cors.append(float(c[1]))
        else:
            # Convert the centers of rotation (if provided) to floats
            if self.func.cors:
                self.func.cors = [float(cor) for cor in self.func.cors]

            # Convert the slices for the center of rotation centers of rotation
            # (if provided) to ints
            if self.func.cor_slices:
                self.func.cor_slices = \
                        [int(slice_id) for slice_id in self.func.cor_slices]

        if self.func.cors and self.func.cor_slices:
            len_cors = len(self.func.cors)
            len_cor_slices = len(self.func.cor_slices)
            if len_cors != len_cor_slices:
                raise ValueError("Centers of Rotation (len {0}) doesn't match length of "
                                 "Slice Indices (len {1})!".format(len_cors, len_cor_slices))

        log.debug("CORs: {}".format(self.func.cors))
        log.debug("COR slices: {}".format(self.func.cor_slices))

        # If the reconstruction is ran on already cropped images, then no ROI
        # should be provided, however if we have a ROI then the Centers of
        # Rotation will be inaccurate because the image has moved
        if self.func.cors and self.args.region_of_interest:
            # the COR is going to be related to the full image
            # as we are going to be cropping it, we subtract the crop
            left = self.args.region_of_interest[0]

            # subtract the move to the left to account for the crop from all
            # the CORs
            self.func.cors = [int(cor) - left for cor in self.func.cors]

        if self.func.indices:
            self.func.indices = [int(index) for index in self.func.indices]

            # if a single value is passed, assume we want from 0 up to the
            # passed value
            if len(self.func.indices) < 2:
                # start index 0, with step 1
                self.func.indices = [0, self.func.indices[0], 1]
            elif len(self.func.indices) == 2:
                # only add the step
                self.func.indices = [self.func.indices[0], self.func.indices[1], 1]
            elif len(self.func.indices) > 3:
                raise ValueError("Invalid amount of indices provided! Please use one of "
                                 "the formats --indices <end_idx>, --indices <start_idx> "
                                 "<end_idx>, --indices <start_idx> <end_idx> <step>")

        if self.func.split and not self.func.max_memory:
            raise ValueError("The --split flag was passed, but no " "--max-memory was specified!")

        # float16, uint16 data types produce exceptions
        # > float 16 - scipy median filter does not support it
        # > uint16 -  division is wrong, so all values become 0 and 1
        # could convert to float16, but then we'd have to go up to
        # float32 for the median filter anyway
        if self.func.data_dtype == 'float32':
            self.data_dtype = np.float32
        elif self.func.data_dtype == 'float64':
            self.data_dtype = np.float64

        if isinstance(self.func.process_list, list):
            # remove the list, we want a single string
            self.func.process_list = self.func.process_list[0]

    def __str__(self):
        return str(self.func) + str(self.args)

    @staticmethod
    def empty_init():
        """
        Create and return a ReconstructionConfig with all the default values.

        This function is provided here to create a config with the defaults,
        but not go through the hassle of importing every single config and
        then constructing it manually.
        This method does that for you!
        """
        # workaround to all the checks we've done

        parser = argparse.ArgumentParser()

        functional_args = FunctionalConfig()
        parser = functional_args._setup_parser(parser)

        # setup args for the filters
        register_filters_on_cli(parser)

        # get the OS's temp directory
        with tempfile.NamedTemporaryFile() as f:
            temp_dir = os.path.dirname(f.name)
        # pass in the mandatory arguments
        fake_args_list = ['--input-path', temp_dir, '--cors', '42']

        # parse the fake arguments
        fake_args = parser.parse_args(fake_args_list)

        # update the configs
        functional_args._update(fake_args)

        return ReconstructionConfig(functional_args, fake_args, special_args=False)
