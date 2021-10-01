# flask-googleBigQuery-Docker-Kubernetes
## components:
1. source code for Flask application in Github
2. bulding the application, creating the container iamge image and running container image in AWS 
3. docker conaitner image in DockerHub
4. docker contianer image in Google Cloud Container Registry
5. Kunternetes cluster in GCK
docker, container image, running sql database on container flask api, mysql connector, 

```docker rm -f python-docker_mysqldb_1 python-docker_web_1; docker image rm python-docker_web;docker-compose up```

Push to docker hub in AWS Cloud9
- log in: ```docker login --username sxia1```
- tag local image and specify my dockerhub repo: <br>
    check image: ```docker images```  <br>
    should have:  <br>
    python-docker_web   latest  ##imageID <br>
    tag image with your DockerHub username + tagname:
    ```docker tag ##imageID sxia1/python-docker:tagname```

pull image in Google Cloud and upload to Google Cloud Contianer registry
- Enabled Container Registry in your project:
  ```gcloud services enable containerregistry.googleapis.com```
- Check if docker is installed: ```docker viersion```
- Log in to docker hub:
  ```docker login --username sxia1```
- Pull image ```docker pull sxia1/python-docker:latest```
- check image and find the imageID:
  ```docker images```
- add to Google container image registry of my project with projectID  _kubernetes-docker-327413_:

    ```docker tag 190365834180 gcr.io/kubernetes-docker-327413/python-docker```<br>
    ```docker push gcr.io/kubernetes-docker-327413/python-docker```
 - check Google Cloud contianer registry if this image is there


Google Cloud Kubernetes
 - enable Kubernetes API in GCP console 
 - create ckuster:<br>
    ```gcloud container clusters create docker-cloud-cluster```
 - get credentials and configures kubectl to use the cluster:<br>
    ```gcloud container clusters get-credentials docker-cloud-cluster```
 - Create the Deployment with container image:<br>
    depoyment name: give a kubernetes deployment name, **docker-server**<br>
    image: go into Google Cloud Contianer Registry and copy the container image name: <br>
              _gcr.io/kubernetes-docker-327413/python-docker@sha256:f2f5f16c2604d5e7ba3726933bc05e6964682087deab9bdf705dc2e354e35ab0:<tagname>_<br>
              the default <tagname> is _latest_<br>
    create command:<br>
    ```kubectl create deployment docker-server \
          --image=gcr.io/kubernetes-docker-327413/python-docker@sha256:f2f5f16c2604d5e7ba3726933bc05e6964682087deab9bdf705dc2e354e35ab0```
  
- Expose Kubernetes to the Internet:
  ```kubectl expose deployment docker-server --type LoadBalancer --port 80 --target-port 8080```
- Inspect running deployment pods: ```kubectl get pods``` <br>
- Inspect our server: ```kubectl get service docker-server```
  ![image](https://user-images.githubusercontent.com/39500675/135134418-0b26b3f7-d9ce-4cc2-b790-81b5c6b322ce.png)
- View our application:  ```http://EXTERNAL_IP```

 

