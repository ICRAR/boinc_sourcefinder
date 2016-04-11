!#bin/bash
echo "Installing Duchamp"

wget ftp://heasarc.gsfc.nasa.gov/software/fitsio/c/cfitsio3370.tar.gz
tar -xvf cfitsio3370.tar.gz
wget ftp://ftp.atnf.csiro.au/pub/software/wcslib/wcslib.tar.bz2
tar -xjvf wcslib.tar.bz2
wget http://www.atnf.csiro.au/people/Matthew.Whiting/Duchamp/downloads/Duchamp-1.6.1.tar.gz
tar -xzvf Duchamp-1.6.1.tar.gz

cd /root/cfitsio
./configure
make 
make install 

cd /root/wcslib-4.25
./configure --without-pgplot --with-cfitsioinc=/root/cfitsio --with-cfitsiolib=/root/cfitsio
make
mkdir /usr/local/share/man/man1
make install

export LD_LIBRARY_PATH=/usr/local/lib
cd /root/Duchamp-1.6.1
./configure --with-cfitsio=/root/cfitsio --without-pgplot
make
make install