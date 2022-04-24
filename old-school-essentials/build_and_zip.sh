#!/bin/bash

echo "Creating Characters"
python main.py 400

echo "Packaging"
cd output
tar -czf ../characters.tar.gz ./*
cd ..

echo "Removing Temp Files"
rm output/*
rmdir output