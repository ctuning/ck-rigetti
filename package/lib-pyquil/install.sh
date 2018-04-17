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
EXTRA_PYTHON_SITE=${INSTALL_DIR}/python_deps_site

SHORT_PYTHON_VERSION=`${CK_ENV_COMPILER_PYTHON_FILE} -c 'import sys;print(sys.version[:3])'`
export PACKAGE_LIB_DIR="${EXTRA_PYTHON_SITE}/lib/python${SHORT_PYTHON_VERSION}/site-packages"
export PYTHONPATH=$PACKAGE_LIB_DIR:$PYTHONPATH

######################################################################################
echo ""
echo "Removing '${EXTRA_PYTHON_SITE}' ..."
rm -rf ${EXTRA_PYTHON_SITE}

######################################################################################
GIT_SRC_DIR=${INSTALL_DIR}/src
echo "Cloning pyQuil into ${GIT_SRC_DIR} ..."
git clone https://github.com/rigetticomputing/pyquil $GIT_SRC_DIR

######################################################################################
echo "Installing pyQuil to '${PACKAGE_LIB_DIR}' ..."

${CK_PYTHON_BIN} -m pip install $GIT_SRC_DIR -r $GIT_SRC_DIR/examples/requirements.txt --prefix=${EXTRA_PYTHON_SITE} --no-cache-dir # --ignore-installed

if [ "${?}" != "0" ] ; then
  echo "Error: installation failed!"
  exit 1
fi

    # Because we have to provide a fixed name via meta.json ,
    # and $PACKAGE_LIB_DIR depends on the Python version,
    # we solve it by creating a symbolic link with a fixed name.
    #
ln -s $PACKAGE_LIB_DIR ${INSTALL_DIR}/build
