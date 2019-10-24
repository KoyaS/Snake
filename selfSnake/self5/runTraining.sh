#!/bin/bash
chmod +x createGen.py
chmod +x selfSnakeCopy.py

python createGen.py
for i in {1..10}
do
   python selfSnakeCopy.py
done