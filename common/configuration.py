import json
import os
import os.path
from util import fatal

 # Modules that need to be defined for the driver to work
expected_modules = ["oracle", "reporter", "control",
                 "model", "bootstrap", "source"]



class Configuration():
    def __init__(self,
                 user_configuration,
                 default_configuration = "default.conf"):

        # First load the default configuration
        self._conf = Configuration.load(default_configuration)

        # Now load the user configuration
        user_conf = Configuration.load(user_configuration)

        # Overwrite default configuration with user's one
        Configuration.overwrite(self._conf, user_conf)

        # Change and check modules paths
        self.check_modules()

        # Write live configuration to disk
        filename = "live_configuration.conf"
        self._conf["configuration_file"] = filename
        f = open(filename, "w")
        json.dump(self._conf, f, indent=2)
        f.write("\n")
        f.close()

    def check_modules(self):
        for module in expected_modules:
            modulepath = self["modules.{0}.executable"
                           .format(module)]
            modulepath = os.path.join(os.environ["DRIVERPATH"], modulepath)
            self._conf["modules"][module]["executable"] = modulepath

            if not os.path.isfile(modulepath):
                fatal("Module {0} could not be found".format(modulepath))
            if not os.access(modulepath, os.X_OK):
                fatal("Module {0} is not executable".format(modulepath))

    @staticmethod
    def load(filename):
        # Parse configuration
        try:
            f = open(filename, "r")
            conf = json.load(f)
            f.close()
        except ValueError, e:
            fatal("Problem parsing configuration file {0}:\n"
                  "  {1}".format(filename,e))
        except IOError:
            fatal("Could not open configuration file {0}"
                  .format(filename))
        return conf

    @staticmethod
    def overwrite(old_conf, new_conf):
        """
        Overwrite a previous configuration with a new one.  Existing
        configuration values not redefined by new_conf are preserved
        (which allows to merge different configurations together).

        The merged configuration is written to old_conf.
        """
        for key,value in new_conf.iteritems():
            if isinstance(value, dict) and key in old_conf:
                Configuration.overwrite(old_conf[key],
                                        value)
            else:
                old_conf[key] = value

    def __getitem__(self, key):
        subkeys = key.split(".")
        try:
            V = self._conf
            for sk in subkeys:
                V = V[sk]
            return V
        except KeyError:       
            fatal("Missing configuration parameter {0}"
                  .format(key))
