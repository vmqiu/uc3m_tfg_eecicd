# Server

En esta carpeta se encuentran los ficheros utilizados para la creación del servidor, se parte de una imágen de VirtualBox proporcionado por el tutor Lisardo Prieto González. No obstante, con que el servidor contenga estas característica se puede continuar.

- Debian Server 11.3
- Docker Version 20.10.17


NOTA: al ser ejecutado en un entorno local, la IP varía, en este ejemplo se utiliza el IP del entorno local 192.168.0.20
# Actualización del sistema
~~~
sudo apt update
sudo apt upgrade -y
~~~

# Instalación de herramientas
## docker-compose, tmux, zsh, oh-my-zsh
~~~
sudo apt-get install zsh -y
sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
sudo apt-get install docker-compose-plugin -y
sudo apt-get install tmux -y
~~~

## kubectl
~~~
sudo apt-get update
sudo apt-get install -y apt-transport-https ca-certificates curl
sudo curl -fsSLo /usr/share/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/usr/share/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl
kubectl version --client --output=yaml 
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

# Minikube
## Instalación Minikube
~~~
curl -LO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64
sudo install minikube-linux-amd64 /usr/local/bin/minikube
~~~

## Creación del clúster Minikube
~~~
minikube start --cpus 4 --memory 8192 --insecure-registry="registry.eecicd.com:50000" 
minikube addons enable metrics-server
minikube addons enable ingress
minikube ssh "echo "192.168.0.20 registry.eecicd.com jenkins.eecicd.com gitlab.eecicd.com eecicd.com" | sudo tee -a /etc/hosts"
~~~

Cada vez que iniciamos minikube se debe ejecutar lo siguiente:

NOTA: Ejecutar en otra terminal con `tmux`, o ejecutar en segundo plano el comando `kubectl port-forward`  
~~~
minikube start
minikube ssh "echo "192.168.0.20 registry.eecicd.com jenkins.eecicd.com gitlab.eecicd.com eecicd.com" | sudo tee -a /etc/hosts"
kubectl port-forward --address 0.0.0.0 deployment/ingress-nginx-controller 8800:80 --namespace ingress-nginx
~~~


# Gitlab
~~~
docker compose up -d gitlab
~~~

Esperamos unos minutos 5-10m hasta que termine la instalación, y obtenemos la contraseña por defecto de `root`.
~~~
sudo docker exec -it gitlab grep 'Password:' /etc/gitlab/initial_root_password
~~~

La contraseña caduca a las 24 horas después de la creación, pasado estas horas, no se puede volver a obtener la contraseña sino que se debe resetear por el terminal con el siguiente comando.
~~~
sudo docker exec -it gitlab gitlab-rake "gitlab:password:reset[root]" # Resetear la contraseña de Root
~~~

Por defecto Gitlab bloquea las peticiones a la red local, por lo que hay que desactivar esta medida de seguridad.
~~~
Menu > Admin > Settings > Network > Outbound requests
~~~
# Docker Registry
~~~
docker compose up -d registry
~~~

# Jenkins
## Instalación Jenkins
Añadimos el repositorio Helm de Jenkins
~~~
helm repo add jenkins https://charts.jenkins.io
helm repo update
~~~

### (Opcional) Si no se utiliza el jenkins-values.yaml provisto
  ~~~
  helm show values jenkins/jenkins > jenkins-values.yaml
  ~~~

  Modificamos el fichero jenkins-values.yaml para añadir plugins, hostnames y variables de entorno para desactivar seguridad SSL de Git.
  ~~~
    installPlugins:
      - kubernetes:3697.v771155683e38
      - workflow-aggregator:581.v0c46fa_697ffd
      - git:4.11.4     
      - configuration-as-code:1429.v09b_044a_c93de
      - pipeline-stage-view:2.24           
      - docker-workflow:521.v1a_a_dd2073b_2e
      - gitlab-plugin:1.5.35
      - pipeline-utility-steps:2.13.0
  ~~~
  ~~~
    hostAliases: 
      - ip: "192.168.0.20"
        hostnames:
        - "gitlab.eecicd.com"
        - "eecicd.com"
        - "registry.eecicd.com"
        - "jenkins.eecicd.com"
  ~~~
  ~~~
    initContainerEnv:
      - name: GIT_SSL_NO_VERIFY
        value: "1"
    containerEnv:
      - name: GIT_SSL_NO_VERIFY
        value: "1"
  ~~~

Creamos el namespace jenkins e instalamos Jenkins
~~~
kubectl create namespace jenkins
helm install jenkins jenkins/jenkins -n jenkins -f jenkins-values.yaml
~~~

El Chart utilizado crea un Service Account sin acceso a kube-system, por lo que hay que conceder a Jenkins el rol de admin.
~~~
kubectl create clusterrolebinding jenkins --clusterrole cluster-admin --serviceaccount=jenkins:jenkins
~~~

Una vez que esten disponible los pods de Jenkins `kubectl wait --for=condition=ready pod/jenkins-0 -n jenkins --timeout=120s`, imprimimos la contraseña de admin.
~~~
kubectl exec --namespace jenkins -it svc/jenkins -c jenkins -- /bin/cat /run/secrets/additional/chart-admin-password && echo
~~~

Para acceder a Jenkins es necesario exponer el puerto del servicio con el siguiente comando:
~~~
kubectl port-forward --address 0.0.0.0 -n jenkins service/jenkins 8080:8080
~~~

Accedemos a Jenkins a través de un navegador, y actualizamos los plugins.
~~~
Manage Jenkins > Manage Plugins (System Configuration)
~~~

# Conexión entre Gitlab y Jenkins
## Gitlab:
Crear un usuario llamado `jenkins`.
~~~
Menu > Admin > Overview > Users > New user
~~~

Generamos el access token, impersonamos el usuario jenkins a través del boton `Impersonate`. Marcamos la casilla `api`.
~~~
Impersonate > Profile (avatar) > Preferences > Access Tokens
~~~


## Jenkins:
Crear un usuario llamado `gitlab`
~~~
Manage Jenkins > Manage Users > Create User 
~~~

Iniciar sesión con el usuario para generar un API Token.   
~~~
Profile > Configure > API Token > Add new token
~~~

Conectar Jenkins con Gitlab:
~~~
Manage Jenkins > Configure System > Gitlab
Gitlab > Credentials > Add > Jenkins
~~~

# Creación repositorio, y commit inicial
Creamos un repositorio
~~~
Menu > Create new project > Create blank project
~~~

Por defecto el repositorio tiene protegido main, de forma que únicamente los que tienen el rol de Mantenedor pueden aprobar PR, y realizar push directo. Opcionalmente, se podría obligar a que solo se pueda aprobar PR solo si el proceso CI/CD ha sido exitoso.

Clonamos en nuestro sistema local, como se trata de un servidor sin firmar, tenemos que desactivar la protección de certificados de git. Luego, eliminamos `README.md`, ya que nuestro proyecto ya cuenta con `README.rst` y realizamos un commit inicial.
~~~
git -c http.sslVerify=false clone https://gitlab.eecicd.com/jenkins/demo_app.git
cd demo_app
git config http.sslVerify "false"
>Colocamos los ficheros de nuestro proyecto en la carpeta<
rm README.md
git commit -am "Initial commit"
git push
~~~ 

# Creación del pipeline:

~~~
Seleccionar Pipeline
Elegir GitLab Connection (viene seleccionado por defecto)
Marcar: 
  Build when a change is pushed to Gitlab.
  Opened Merge Request
Desmarcar:
  Approved Merge Requests (EE-only)
 Activar configuración avanzada: 
  Allowed Branches > Filter branches by regex
    Source Branch:
      (feature\/.+|hotfix\/.+|bugfix\/.+)
    Target Branch
      (main)
Pipeline
Definition > Pipeline from SCM
  SCM > Git
    Repository URL
    https://gitlab.eecicd.com/jenkins/demo_app.git
  Credentials
    Kind Username with password
  
  Branches to build:
    origin/${gitlabSourceBranch}
~~~

# Conexión Webhook y Pipeline

A continuación, acceder al proyecto donde implementar CI/CD y crear un Webhook.
~~~
Settings > Webhooks
~~~

La URL debe seguir la siguiente estructura:
~~~
http://JENKINS\_USER:API\_TOKEN@jenkins.eecicd.com:8080/project/PIPELINE\_NAME
~~~

Indicamos scope: `merge request`, y el URL debería quedar como:
~~~
http://gitlab:115d343a55836e7fec2b249735cf120589@jenkins.eecicd.com:8080/project/demo_app_pr_pipeline
~~~

A partir de aquí, cada vez que se abra un PR desde hotfix, feature o bugfix a main, se ejecutará el pipeline.


# Test de carga de Kubernetes
Al ejecutarse dentro de la VM, las peticiones se hacen a la IP de Ingress.

~~~
kubectl get ingress
~~~

El addonds metrics-server de Minikube tiene una tasa de refresco de 60s, para esta prueba lo modificaremos a 10s.
~~~
kubectl -n kube-system edit deployments.apps metrics-server
~~~
Dentro de `template`, buscamos el `args` `--metric-resolution=60s` y lo modificamos a `--metric-resolution=10s`

Ejecutamos un rollout para asegurarnos de que se apliquen los cambios
~~~
kubectl rollout restart deployment metrics-server -n kube-system
~~~

Para monitorizar los pods, y el HPA se utiliza
~~~
kubectl get pods -w
kubectl get hpa -w
~~~

Para ejecutar la carga, iniciamos un pod y enviamos peticiones en un bucle infinito.
~~~
kubectl run -it --rm load-generator --image=busybox /bin/sh
~~~

Ejecutamos dentro del pod el siguiente comando
~~~
while true; do wget -q -O- http://192.168.49.2/welcome_comp/; done 
~~~

Al terminar la prueba restauramos los 60s del metrics-server.


# Comandos útiles:
Escalar o desescalar objetos Kubernetes
~~~
kubectl scale type name --replicas=<new-replicas>
~~~

Actualizar un deployment con nueva configuración.
~~~
kubectl rollout restart deployment name -n namespace
~~~

Actualizar Jenkins tras modificar valores en jenkins-values.yaml
~~~
helm upgrade jenkins jenkins/jenkins -n jenkins -f jenkins-values.yaml
~~~

Comandos para la gestión de imagenes docker
~~~
curl -X GET http://registry.eecicd.com:50000/v2/_catalog
docker build -t welcome_comp -f src/welcome_comp/Dockerfile .
docker tag welcome_comp registry.eecicd.com:50000/welcome_comp
docker push registry.eecicd.com:50000/welcome_comp
~~~