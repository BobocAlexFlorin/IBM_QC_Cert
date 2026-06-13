@echo off
:: Create the directory structure
if not exist "data_tutorial\grid_stability" mkdir "data_tutorial\grid_stability"

:: Download the training dataset using curl
echo Downloading training dataset...
curl -L -s -o "data_tutorial\grid_stability\train.csv" "https://raw.githubusercontent.com/Qiskit/documentation/main/datasets/tutorials/grid_stability/train.csv"

:: Download the testing dataset
echo Downloading testing dataset...
curl -L -s -o "data_tutorial\grid_stability\test.csv" "https://raw.githubusercontent.com/Qiskit/documentation/main/datasets/tutorials/grid_stability/test.csv"

:: Print status and list the downloaded files
echo.
echo Dataset files downloaded:
dir "data_tutorial\grid_stability\*.csv"
pause