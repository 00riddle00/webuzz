# This is a traditional package since it is a directory and contains an
# __init__.py file. It is now called 'regular package', to distinguish it from
# 'namespace package' (see PEP 420 for that), which does not have an
# __init__.py.

# The __init__.py files are required to make Python treat the directories as
# containing 'regular packages'.

# A package can have modules (= Python files, basically*) inside, and/or
# another sub-packages.

# In the simplest case, __init__.py can just be an empty file, but it can also
# execute initialization code for the package.

# Depending on what we plan to do it is a good place to import public stuff
# from the modules in our package so people can simply use:
#
# `from our_package import whatever`
#
# instead of having to use:
#
# `from our_package.some_module import whatever`

# __init__.py file is basically a constructor for a package, just like the
# __init__ method in a class is a constructor for an object.

# * Actually, a module is an object that serves as an organizational unit of
#   Python code, which are loaded into Python by the process of importing. So a
#   package is also a module at the same time, since it can be imported. So we
#   can also say `submodules` instead of `sub-packages`.
