echo off
echo 
echo "|---------------------------------|"
echo "|                                 |"
echo "|                                 |"
echo "|----------Click any key----------|"
echo "|                                 |"
echo "|                                 |"
echo "|---------------------------------|"
pause
python setup.py build
pause
echo "|---------------------------------|"
echo "|                                 |"
echo "|                                 |"
echo "|-Succesfully created executables-|"
echo "|                                 |"
echo "|                                 |"
echo "|---------------------------------|"
pause
echo "|---------------------------------|"
echo "|                                 |"
echo "|                                 |"
echo "|--------Creating installer-------|"
echo "|                                 |"
echo "|                                 |"
echo "|---------------------------------|"
pause
python setup.py bdist_msi
pause
echo "|---------------------------------|"
echo "|                                 |"
echo "|                                 |"
echo "|---Succesfully deployed Py1000---|"
echo "|                                 |"
echo "|                                 |"
echo "|---------------------------------|"
pause