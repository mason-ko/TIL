# 1

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: nginx-test1
spec:
  containers:
  - name: nginx
    image: nginx:1.14.2
    env:
    - name: var1
      value: val1
    ports:
    - containerPort: 80
```

```
$ kubectl apply -f ./simple-pod.yaml -n exam-mason
pod/nginx-test1 created

$ kubectl exec nginx-test1 -n exam-mason -- printenv | grep var1
var1=val1
```

# 2

```
$ kubectl exec nginx-test1 -n exam-mason ls | grep main.txt
```

# 3
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod2
  labels:
    app.kubernetes.io/name: MyApp
spec:
  containers:
  - name: myapp-container
    image: busybox:1.28
    command: ['sh', '-c', 'while true; do echo `Hi I am from Main container` >> /var/log/index.html; sleep 5; done']
    ports:
    - containerPort: 80
    volumeMounts:
    - mountPath: /var/log
      name: v1
  containers:
  - name: ngnix
    image: nginx:1.14.1
    volumeMounts:
    - mountPath: /usr/share/nginx/html
      name: v1
  volumes:
  - name: v1
    emptyDir:
      sizeLimit: 100Mi
```

```
$ kubectl apply -f ./3.yaml -n exam-mason
pod/myapp-pod2 created

$ kubectl get pods -n exam-mason | grep myapp-pod2
myapp-pod2                          1/1     Running    0          71s
```

# 4 

```
$ kubectl run busyboxpod-1 --image=busybox -n exam-mason --command -- sh "-c" "ls; sleep 3600;"
$ kubectl run busyboxpod-2 --image=busybox -n exam-mason --command -- sh "-c" "echo Hello World; sleep 3600;"
$ kubectl run busyboxpod-3 --image=busybox -n exam-mason --command -- sh "-c" "echo this is the third container; sleep 3600"

$ kubectl get pods -n exam-mason | grep busyboxpod
busyboxpod-1                        1/1     Running    0          46s
busyboxpod-2                        1/1     Running    0          22s
busyboxpod-3                        1/1     Running    0          21s

```

# 5

```
$ kubectl logs -f busyboxpod-1 -n exam-mason
$ kubectl logs -f busyboxpod-2 -n exam-mason
$ kubectl logs -f busyboxpod-3 -n exam-mason
```

# 6
# 7
# 8 
# 9

# 10

```
$ kubectl run redis --image=redis -n exam-mason --expose=true --port 6379
service/redis created
pod/redis created
```

# 11
```
$ kubectl delete pod redis --force=true -n exam-mason
warning: Immediate deletion does not wait for confirmation that the running resource has been terminated. The resource may continue to run on the cluster indefinitely.
pod "redis" force deleted
```

# 12 
# 13
# 14
# 15
