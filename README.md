# flask-googleBigQuery-Docker-Kubernetes
![alt text](https://github.com/shufan1/flask-googleBigQuery-Docker/blob/main/showapplication.gif)

- Inspired by: https://colab.research.google.com/drive/1_BBcQWcgYXFyuThrEV_YwGzvn_UNcRNx#scrollTo=6GPlo51Z0LPU
## components:
1. source code for Flask application in Github
2. docker contianer image in Google Cloud Container Registry
3. Kunternetes cluster in GCK
![alt text](https://github.com/shufan1/flask-googleBigQuery-Docker/blob/main/blueprint.jpg?raw=true)

**Part I: Make and test Flask API locally**
- git clone this repo
- `make install`
- test if connecting to Google Big Query works: `pytest test.py  `
- Run Flask API locally: `python3 app.py`
- (If in Google Cloud Platform, can be deployed with Cloud Build and set up CD)

Troubleshooting:
If you get this following message when you run your python script calling BigQuery:<br>
   _"""<br>
   google.api_core.exceptions.BadRequest: 400 POST https://bigquery.googleapis.com/bigquery/v2/projects//jobs?prettyPrint=false: Invalid project ID ''. Project IDs must contain 6-63 lowercase letters, digits, or dashes. Some project IDs also include domain name separated by a colon. IDs must start with a letter and may not end with a dash.<br>
   """"_<br>
set ProjectID in your cloudshell. My project ID is kubernetes-docker-327413. You can find it under Project Info in GCP console and do this: <br>
 ```gcloud config set project kubernetes-docker-327413```
<hr>

**_If you want to make a Docker container and Kubernetes, continue_**

**Part II: Build Docker container image**
- Build image: ``` docker build --tag flask-docker .```
- check image: ```docker images```
![image](https://user-images.githubusercontent.com/39500675/135636101-670439bc-d400-4d53-a503-58039271d5d6.png)

- Test running image as container:<br>
  you might encounter "Invalid Project ID" error
  add project ID to bigquery client in app.py and rebuild the image:<br>
  ```client = bigquery.Client(project="kubernetes-docker-327413")```

**Part III: Push image to GoogleCloud Contianer Registry and Run image in Cloud Run"**
- Enabled Container Registry in your project:
  ```gcloud services enable containerregistry.googleapis.com```
- Authenticate docker request to Container Registry:
    ```gcloud auth configure-docker```
- Tag and push:
     ```docker tag <ImageID> gcr.io/kubernetes-docker-327413/python-docker```<br>
    ```docker push gcr.io/kubernetes-docker-327413/python-docker```
- Run pushed image with Cloud Run:
   Go into your cloud registry and see if the image is there. And connect to Cloud Run with a few clicks: <br>
   specify region : us-east1
 ![image](https://user-images.githubusercontent.com/39500675/135643367-fcf6a169-1af2-455f-809e-8aa4c26014ed.png)
- After deployment configuration finised in Cloud Run, check our application with the URL given.

**Part IV Google Cloud Kubernetes**
 - enable Kubernetes API in GCP console 
 - specify compute region and zone:<br>
   ```
   gcloud config set compute/region us-east1
   gcloud config set compute/zone us-east1-b
   ```
 - create ckuster:<br>
    ```gcloud container clusters create docker-cloud-cluster```
 - get credentials and configures kubectl to use the cluster:<br>
    ```gcloud container clusters get-credentials docker-cloud-cluster```
 - Create deployment with container image:<br>
    depoyment name: give a kubernetes deployment name, **docker-server**<br>
    image: go into Google Cloud Contianer Registry and copy the container image name: <br>
              _gcr.io/kubernetes-docker-327413/python-docker@sha256:3726913b526c0bad108881c85467c831162e0c6a7a9c462ae797abd25be0cab1_<br>
    create command:<br>
    ```
   kubectl create deployment docker-server \
          --image=gcr.io/kubernetes-docker-327413/python-docker@sha256:3726913b526c0bad108881c85467c831162e0c6a7a9c462ae797abd25be0cab1
   ```
  
- Expose Kubernetes to the Internet:
  ```kubectl expose deployment docker-server --type LoadBalancer --port 80 --target-port 8080```
- Inspect running deployment pods: ```kubectl get pods``` <br>
- Inspect our server: ```kubectl get service docker-server```
  ![image](https://user-images.githubusercontent.com/39500675/135646542-c8149269-b4ed-450a-bed3-15f2133ef180.png)
- View our application by curl or in the browser:  ```http://EXTERNAL_IP```
- At this point, you can see the main page but the application does not have access to BigQuery. Therefore any page with query task returns error. In the next section, I talk about how to fix this issue.


 **Side note: Enable BigQuery for Kubernetes**

 - create:<br>
   Follow the steps outlined here: https://cloud.google.com/kubernetes-engine/docs/tutorials/authenticating-to-cloud-platform#step_3_create_service_account_credentials<br>
   Instead of pub-sub: I named the key as kubernetesbigquery-key and specified Role as BigQueryAdmin. Dowload the key as a JSON file following the documentation.
 - upload the key JSON file to your project directory
 - create secret key in Kubernetes: 
       ```kubectl create secret generic kubernetesbigquery-key --from-file=key.json=kubernetes-docker-327413-ef9601a05d9a.json```<br>
   should be able to see the key in Kubernetes Engine >> Configuration
   ![image](https://user-images.githubusercontent.com/39500675/135668021-b2f1414f-31bd-49ab-b05f-0f7d48bc99c8.png)

 - modify the deployment specification in Kubernetes Engine consloe:
   Edit ```Workloads >> YAML```. At the right position and indentation level, carefully declare ```env```, ```volumeMounts``` and ```volumes```. 
 ```
apiVersion: apps/v1
kind: Deployment
metadata:
    ...
spec:
  ...
  template:
    ...
    spec:
      containers:
      - env:
        - name: GOOGLE_APPLICATION_CREDENTIALS
          value: /var/secrets/google/key.json
        image: gcr.io/kubernetes-docker-327413/python-docker@sha256:3726913b526c0bad108881c85467c831162e0c6a7a9c462ae797abd25be0cab1
        imagePullPolicy: IfNotPresent
        name: python-docker
        resources: {}
        terminationMessagePath: /dev/termination-log
        terminationMessagePolicy: File
        volumeMounts:
        - mountPath: /var/secrets/google
          name: google-cloud-key
      dnsPolicy: ClusterFirst
      restartPolicy: Always
      schedulerName: default-scheduler
      securityContext: {}
      terminationGracePeriodSeconds: 30
      volumes:
      - name: google-cloud-key
        secret:
          defaultMode: 420
          secretName: kubernetesbigquery-key
status:
  ...
````
- Save the edited YML file and it will automatically deploy
- Now we can view the application in browser !!!!
