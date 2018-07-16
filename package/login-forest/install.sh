#! /bin/bash

#
# CK installation script
#
# See CK LICENSE for licensing details.
# See CK COPYRIGHT for copyright details.
#

# PACKAGE_DIR
# INSTALL_DIR

cd ${INSTALL_DIR}

rm -f ${RIGETTI_LOGIN_FILE}
mv ${TMP_RIGETTI_LOGIN_FILE} ${RIGETTI_LOGIN_FILE}

exit 0
