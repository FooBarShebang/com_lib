#usr/bin/python3
"""
Module com_lib.check_dependencies

Performs the installation / dependencies checks. Attention: this module is
designed to be executable. All tests are run automatically upon import.
"""

__version__= '1.1.0.0'
__date__ = '30-09-2020'
__status__ = 'Production'

#actual imports

import sys
import os
import json
from importlib import import_module

MODULE_PATH = os.path.realpath(__file__)
LIB_FOLDER = os.path.dirname(MODULE_PATH)
LIB_NAME = os.path.basename(LIB_FOLDER)
ROOT_FOLDER = os.path.dirname(LIB_FOLDER)
CHECK_PATH = os.path.join(LIB_FOLDER, 'dependencies.json')

if not (ROOT_FOLDER in sys.path):
    sys.path.append(ROOT_FOLDER)

with open(CHECK_PATH, 'rt') as fFile:
    dictData = json.load(fFile)

#checks!

print('Dependencies checks for {}...'.format(LIB_NAME))

#+ Python version

dictCheck = dictData.get('python', None)

bExit = False

if not (dictCheck is None):
    iMajorReq = dictCheck['major']
    iMinorReq = dictCheck['minor']
    iMajorReal, iMinorReal, *rest = sys.version_info
    bCond1 = iMajorReal != iMajorReq
    bCond2 = iMinorReal < iMinorReq
    strRealVersion = '{}.{}'.format(iMajorReal, iMinorReal)
    strReqVersion = '{}.{}'.format(iMajorReq, iMinorReq)
    if bCond1:
        print('Required Python {}, whereas v{} is used.'.format(
                                                    iMajorReq, strRealVersion))
        bExit = True
    elif bCond2:
        print('Required Python version {} or newer, but v{} is used.'.format(
                                                strReqVersion, strRealVersion))
        bExit = True
    else:
        print('Python version check is passed.')
    if bExit:
        sys.exit(1)

#+ libraries

bOthers = False
bDO = False

for strKey in ['3rd_party', 'DO']:
    bFault = False
    dictCheck = dictData.get(strKey, None)
    if not (dictCheck is None):
        print('Checking the required {} libraries'.format(
                                                    strKey.replace('_', ' ')))
        for strModule, dictVersions in dictCheck.items():
            try:
                modImport = import_module(strModule)
                try:
                    print('Library "{}" version {} is found'.format(strModule,
                                                        modImport.__version__))
                    strlstSplitVersion = modImport.__version__.split('.')
                    iMajor = int(strlstSplitVersion[0])
                    iMinor = int(strlstSplitVersion[1])
                    bCond1 = iMajor < dictVersions["major"]
                    bCond2 = ((iMajor == dictVersions["major"]) and
                                            (iMinor < dictVersions["minor"]))
                    if bCond1 or bCond2:
                        strError = ' '.join(['This version is too old,'
                                                '>{}.{} is required'.format(
                                                        dictVersions["major"],
                                                        dictVersions["minor"])])
                        print(strError)
                        print('Install from "{}"'.format(dictVersions["path"]))
                        bFault = True
                except:
                    print('Library {} - no version found'.format(LIB_NAME))
                    bFault = True
            except ImportError:
                print('Library {} is not found'.format(strModule))
                print('Install from {}'.format(dictVersions["path"]))
                bFault = True
            if strKey == 'DO':
                try:
                    strCheckModule = '{}.check_dependencies'.format(strModule)
                    import_module(strCheckModule)
                except ImportError:
                    pass
        if bFault:
            if strKey == '3rd_party':
                bOthers = True
            elif strKey == 'DO':
                bDO = True

if bDO:
    print('Place the required DO libraries into folder "{}",'.format(
                                                                ROOT_FOLDER),
            'or into an arbitrary folder and add that folder into PYTHONPATH.')

if bOthers or bDO:
    print('Dependencies check is failed!')
    sys.exit(1)
else:
    print('Dependencies check is successful!')