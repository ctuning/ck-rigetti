#! /bin/bash

#
# Installation script for Caffe.
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#

# PACKAGE_DIR
# INSTALL_DIR

echo "**************************************************************"
echo "Installing pyQuil package and its dependencies ..."

    # This is where pip2/pip3 will install the modules.
    # It has its own funny structure we don't control :
    #
PY_DEPS_TREE=${INSTALL_DIR}/py_deps

    # This is the link that *will* be pointing at the directory with modules.
    # However, because we want to use asterisk expansion, we will create
    # the link itself *after* PY_DEPS_TREE has been already populated.
    #
export PACKAGE_LIB_DIR=${INSTALL_DIR}/build

######################################################################################
echo ""
echo "Removing '${PY_DEPS_TREE}' ..."
rm -rf ${PY_DEPS_TREE} ${PACKAGE_LIB_DIR}

######################################################################################
echo "Installing pyQuil to '${PACKAGE_LIB_DIR}' ..."

${CK_PYTHON_BIN} -m pip install pyquil --prefix=${PY_DEPS_TREE} --no-cache-dir # --ignore-installed

if [ "${?}" != "0" ] ; then
  echo "Error: installation failed!"
  exit 1
fi

    # In order for the asterisk to expand properly,
    # we have to do it AFTER the directory tree has been populated:
    #
ln -s $PY_DEPS_TREE/lib/python*/site-packages ${PACKAGE_LIB_DIR}
