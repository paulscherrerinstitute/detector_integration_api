VERSION=$1

user=git

git clone ${user}@git.psi.ch:sls_detectors_software/sls_detectors_package.git sls_detectors_package
cd sls_detectors_package

sh checkout.sh $user
sh gitall.sh checkout $VERSION

