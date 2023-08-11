# Exam 1
```
$ kubectl get node -o json > json-mason.yaml
```
# Exam 2
```
$ kubectl create namespace exam-mason
```
# Exam 3
```
$ kubectl create deployment mason-deployment --image=nginx --replicas=2 -n exam-mason
```
# Exam 4
```
$ kubectl get deployment mason-deploymen -o custom-columns='DEPLOYMENT:.metadata.name','CONTAINER_IMAGE:.spec.template.spec.containers[*].image','READY_REPLICA:.status.readyReplicas','NAMESPACE:.metadata.namespace'
```
# Exam 5
```
$ kubectl create deployment nginx-deploy --image=nginx:1.16 --replicas=1
```
```
$ kubectl rollout history deployment/nginx-deploy -n exam-mason
deployment.apps/nginx-deploy
REVISION  CHANGE-CAUSE
1         <none>
```
```
$ kubectl set image deployment nginx-deploy -n exam-mason nginx=nginx:1.17
```
```
$ kubectl rollout history deployment nginx-deploy -n exam-mason
deployment.apps/nginx-deploy
REVISION  CHANGE-CAUSE
1         <none>
2         <none>
```
```
$ kubectl get deployment nginx-deploy -n exam-mason -o json
...
 "spec": {
                "containers": [
                    {
                        "image": "nginx:1.17",
...
```
# Exam 6
```yaml
apiVersion: v1
kind: Service
metadata:
  name: web-application
spec:
  type: NodePort
  selector:
    app.kubernetes.io/name: simple-webapp
  ports:
    - port: 8080
      targetPort: 8080
      nodePort: 30083
```
```
$ kubectl apply -f service.yaml -n exam-mason
```
# Exam 7
```
$ kubectl expose deployment nginx-deploy --name=mason-service --port=9090 -n exam-mason --type=ClusterIP
```
# Exam 8
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mason-deployment
  labels:
    app: nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: mason-pod
  template:
    metadata:
      labels:
        app: mason-pod
    spec:
      containers:
      - name: nginx
        image: nginx:1.17
        ports:
        - containerPort: 80
```
```
$ kubectl apply -f .\mason-deployment.yaml -n exam-mason
deployment.apps/mason-deployment created
```
replicas: 1로 변경  
```
$ kubectl apply -f .\mason-deployment.yaml -n exam-mason
deployment.apps/mason-deployment configured
```
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: mason-config
data:
  hello: "world"
  drink: "good"
  happy: "work"
```
```
$ kubectl apply -f configmap.yaml -n exam-mason
```
디플로이먼트에 값 추가
```
      volumes:
      - name: config
        configMap:
            name: mason-config
```
# Exam 9
```
$ kubectl exec -it pod/mason-deployment-7cd48c6767-jvbkl -n exam-mason echo "Hello World" > hello.txt
```
# Exam 10
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
  labels:
    app.kubernetes.io/name: MyApp
spec:
  containers:
  - name: myapp-container
    image: busybox:1.28
  initContainers:
  - name: init-myservice
    image: busybox:1.28
    command: ['sh', '-c', "sleep 20"] 
```
```
$ kubectl apply -f initContainer.yaml -n exam-mason
```
20초 전
```
NAME                                READY   STATUS     RESTARTS   AGE
mason-deployment-7cd48c6767-jvbkl   1/1     Running    0          12m
myapp-pod                           0/1     Init:0/1   0          12s
nginx-deploy-5c95467974-ls9wh       1/1     Running    0          58m
```
20초 후 
```
NAME                                READY   STATUS      RESTARTS     AGE
mason-deployment-7cd48c6767-jvbkl   1/1     Running     0            12m
myapp-pod                           0/1     Completed   1 (8s ago)   30s
nginx-deploy-5c95467974-ls9wh       1/1     Running     0            59m
```
