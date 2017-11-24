from vpt.common import *
from vpt.settings import *

class FileStream:

    def __init__(self, folder, ftype="bin", annotations=None, normalize=False, ignore=False):

        self._folder = folder
        self._ftype = ftype
        self._fpaths = []
        self._annotations = annotations
        self._normalize = normalize
        self._ignore = ignore

        self._strip = annotations != None

        self.load_filenames()

        if self._ignore:
            assert annotations, "Stream set to ignore files without valid annotations but no annotations have been provided"


    def load_filenames(self):
        for root, dirs, files in os.walk(self._folder):
            for fname in files:
                if self._ftype in fname and "background" not in root:  # exclude folders with background in name
                    fpath = os.path.join(root, fname)

                    if self._strip:
                        try:
                            labels = (None, None)
                            if self._annotations != None:
                                key = getFileKey(fpath)
                                labels = self._annotations[key]
                                if self._ignore:
                                    if labels[0] in ANNOTATIONS and labels[1] in ANNOTATIONS:
                                        self._fpaths.append(fpath)
                                else:
                                    self._fpaths.append(fpath)
                        except Exception as e:
                            print ("Error Loading Files:", e)
                    else:
                        self._fpaths.append(fpath)

        print ("# Files Loaded:", len(self._fpaths))


    def img_generator(self):

        for fname in self._fpaths:
            try:
                yield load_depthmap(fname, normalize=self._normalize), fname
            except Exception as e:
                print ("Error Generating Image:", e)


    def get_fpaths(self):
        print ("Shape:", len(self._fpaths))
        return self._fpaths