pip uninstall pre-commit

pip install --user pre-commit

Instalar nc para sus pruebas
sudo apt install netcat-traditional -y
para hacer pruebas al test del logger en code space facilmente
echo "Hello via nc" | nc -u 127.0.0.1 5514
para mandar la señal al taskmaster
pid=$(ps -ef | grep "[t]askmaster main.py" | awk '{print $2}') && kill -1 $pid
para abrir un server que escuche 
nc -u -l 5514
