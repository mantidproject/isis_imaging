import logging
import unittest


class ImporterTest(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(ImporterTest, self).__init__(*args, **kwargs)

        # force silent outputs
        from mantidimaging.core.configs.recon_config import (ReconstructionConfig)
        self.config = ReconstructionConfig.empty_init()
        self.config.func.log_level = logging.CRITICAL

    # that's the only supported tool right now, Astra is used through TomoPy
    def test_tomopy(self):
        from mantidimaging.core.tools.tomopy_tool import TomoPyTool
        from mantidimaging.core.tools import importer
        self.config.func.tool = 'tomopy'
        tool = importer.timed_import(self.config)
        assert isinstance(tool, TomoPyTool)

        tool = importer.do_importing('tomopy')
        assert isinstance(tool, TomoPyTool)

    def test_not_supported_tool(self):
        # not supported tool
        from mantidimaging.core.tools import importer
        self.config.func.tool = 'boop'
        self.assertRaises(ValueError, importer.timed_import, self.config)

        # invalid tool parameter
        self.config.func.tool = 42
        self.assertRaises(TypeError, importer.timed_import, self.config)


if __name__ == '__main__':
    unittest.main()
