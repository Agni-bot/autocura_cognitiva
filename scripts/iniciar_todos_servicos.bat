@echo off
REM Inicia todos os serviços do Sistema de Autocura Cognitiva em janelas separadas

start "Monitoramento" cmd /k python src\monitoramento.py
start "Diagnostico" cmd /k python src\diagnostico.py
start "Gerador de Acoes" cmd /k python src\gerador_acoes.py
start "Observabilidade" cmd /k python src\observabilidade\observabilidade.py

echo Todos os serviços foram iniciados em janelas separadas.
pause 