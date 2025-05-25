@echo on


:: Pythonのパス（必要に応じて書き換えてね）
set PYTHON=python

:: command_host.py を実行
%PYTHON% generate_network.py

pause
exit