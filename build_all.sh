#!/bin/bash

set -e
set -x

# git submodule update --init -f --recursive

# . build_client.sh

echo building SNAPPY
pushd caladan/apps/storage_service
pushd snappy
rm -rf build
mkdir build
pushd build

cmake -DSNAPPY_BUILD_TESTS=0 -DCMAKE_BUILD_TYPE=Release ..
make -j

popd
popd
popd

echo building CALADAN
for dir in caladan caladan/shim caladan/bindings/cc caladan/apps/storage_service caladan/apps/netbench; do
	make -C $dir
done

# TODO replace these direct paths
export SHENANGODIR=/users/estuhr/bw_artif/caladan

#### don't need? TODO
# echo building SILO
# pushd  silo
# ./silo.sh
# make
# popd

echo building MEMCACHED
pushd memcached
./autogen.sh
./configure --with-shenango=/users/estuhr/bw_artif/caladan
make
popd
#### don't need? TODO
# pushd memcached-linux
# ./autogen.sh
# ./configure
# make
# popd

echo building BOEHMGC
pushd boehmGC
./autogen.sh
./configure --prefix=/users/estuhr/bw_artif/boehmGC/build --enable-static --enable-large-config --enable-handle-fork=no --enable-dlopen=no --disable-java-finalization --enable-threads=shenango --enable-shared=no --with-shenango=/users/estuhr/bw_artif/caladan
make install
popd

echo building PARSEC
for p in x264 swaptions streamcluster; do
	parsec/bin/parsecmgmt -a build -p $p -c gcc-shenango
done

export GCDIR=/users/estuhr/bw_artif/boehmGC/build/
parsec/bin/parsecmgmt -a build -p swaptions -c gcc-shenango-gc
