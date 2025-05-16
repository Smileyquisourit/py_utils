#raise NotImplementedError("The ConfigHelper module isn't implemented yet ,but it will comme soon ;)")


# TODO list:
# ----------
# - Add UNSAFE exception when creating a config
# - __repr__ of ConfigVariable print <class str> (or int, float)
# - Add _doc or doc in ConfigVariable to explain a variable in the config (will be print as comment when
#       writting a config file) 
# - Change _NO_FALLBACK to a more elegant solution if possible, else see where to define it
# - Implement read and read_safe
#
# - Add supported type: bool (with 'on'/'off', 'True'/'False', 'true'/'false', 'yes'/'no')
# - Add interpolation for INI format configuration, with %{SECTION:NAME}s or %{NAME}s
# - Add verification logic for the name of a ConfigVariable and of a ConfigSection
#
# - Add generic type for the config classes, see https://docs.python.org/3/library/stdtypes.html#types-genericalias
# - see https://en.wikipedia.org/wiki/INI_file for more idea