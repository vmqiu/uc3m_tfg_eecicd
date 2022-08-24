# demo_app

En este repositorio se almacenan los ficheros utilizado en demo_app.

Esta carpeta esta estructurado de la siguiente forma:
- **demo_app**
  - **final_demo_app**: es la versión final demo_app, con date_comp implementado.
  - **initial_demo_app**: es la versión inicial demo_app, sin date_comp implementado.
  - **docs**: documentación compilada de **final_demo_app**.

La estructura de carpetas que sigue demo_app es la siguiente:
- **demo_app**: ficheros de configuración, y Jenkinsfile.
  - **docs**: documentación generada con Sphinx.
  - **kubernetes**: ficheros relativos al despliegue de objetos Kubernetes.
  - **src**: carpeta donde se almacena el código fuente.
  

NOTA: al ser ejecutado en un entorno local, la IP varía, en este ejemplo se utiliza el IP del entorno local 192.168.0.20

# Actualización del sistema
~~~
sudo apt update
sudo apt upgrade -y
~~~

# Instalación de herramientas
## docker-compose, tmux, zsh, oh-my-zsh, Poetry
~~~

sudo apt-get install docker-compose-plugin -y

sudo apt-get install tmux -y

sudo apt-get install zsh -y
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"

curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python -
~~~

## Pyenv
~~~
git clone https://github.com/pyenv/pyenv.git ~/.pyenv

sudo apt-get update; sudo apt-get install make build-essential libssl-dev zlib1g-dev \
libbz2-dev libreadline-dev libsqlite3-dev wget curl llvm \
libncursesw5-dev xz-utils tk-dev libxml2-dev libxmlsec1-dev libffi-dev liblzma-dev -y

echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.zshrc
echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.zshrc
echo 'eval "$(pyenv init -)"' >> ~/.zshrc
exec "$SHELL"
~~~


## helm
~~~
curl https://baltocdn.com/helm/signing.asc | gpg --dearmor | sudo tee /usr/share/keyrings/helm.gpg > /dev/null
sudo apt-get install apt-transport-https --yes
echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/helm.gpg] https://baltocdn.com/helm/stable/debian/ all main" | sudo tee /etc/apt/sources.list.d/helm-stable-debian.list
sudo apt-get update
sudo apt-get install helm -y
helm version
~~~

# Hostname del servidor
Para la mantenibilidad del proyecto, se añade el IP 192.168.0.20 con los dominios.
~~~
echo "192.168.0.20 registry.eecicd.com jenkins.eecicd.com gitlab.eecicd.com eecicd.com" | sudo tee -a /etc/hosts
~~~

# Clonación del repositorio
Al utilizar Gitlab sin certificado, se debe clonar con la opción `http.sslVerify=false`.
~~~
git -c http.sslVerify=false clone https://gitlab.eecicd.com/jenkins/demo_app.git
cd demo_app
git config http.sslVerify "false"
~~~

# Instalación del entorno python
Se utilizará la versión 3.10.5, por lo que se instala con pyenv
~~~
pyenv install 3.10.5
pyenv global 3.10.5
~~~


# Instación de Poetry en el proyecto y adición de dependencias
Inicializar Poetry por primera vez
~~~
poetry init
~~~

Adición e instalación de dependencias
~~~
poetry add requests
poetry add Flask
poetry add Sphinx
poetry add furo

poetry install
~~~

Accedemos al entorno mediante
~~~
poetry shell
~~~

# Instalación de Sphinx en el proyecto
Inicializar Sphinx por primera vez
~~~
sphinx-quickstart docs
~~~

Para generar automáticamente la documentación de una carpeta
~~~
sphinx-apidoc -o docs/source/generated src
~~~

Para compilar la documentación 
~~~
sphinx-build -b html docs/source/ docs/build/html
~~~


# Comandos útiles
Exportar dependencias Poetry a requirements.txt
~~~
poetry export -f requirements.txt -o requirements.txt --without-hashes
~~~