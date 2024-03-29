# 1
```
kubectl create secret generic super-secret \
    --from-literal=username=mason \
    --from-literal=password='bob' -n exam-mason
```

```
apiVersion: v1
kind: Pod
metadata:
  name: pod-secrets-via-file
spec:
  containers:
  - name: pod-secrets-via-file
    image: redis
    volumeMounts:
    - name: foo
      mountPath: "/secret"
      readOnly: true
  volumes:
  - name: foo
    secret:
      secretName: super-secret
      optional: false
```

```
kebuctl apply -n exam-mason -f ./pod-secrets-via-file.yaml
```

```
apiVersion: v1
kind: Pod
metadata:
  name: pod-secrets-via-env
spec:
  containers:
  - name: pod-secrets-via-env
    image: redis
    env: 
      - name: CONFIDENTIAL
        valueFrom:
          secretKeyRef:
            name: super-secret
            key: password
            optional: false 
  restartPolicy: Never
```
```
kubectl apply -n exam-mason -f ./pod-secrets-via-env.yaml
```

# 2
```
kubectl run nginx --image=nginx --namespace=exam-mason --expose=true --port 5678
```
```
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: ping
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
spec:
  ingressClassName: nginx-example
  rules:
  - http:
      paths:
      - path: /hi
        pathType: Prefix
        backend:
          service:
            name: nginx
            port:
              number: 5678
```
```
kubectl apply -n exam-mason -f ./ingress.yaml
```
# 3

# 4 
```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.14.2
        ports:
        - containerPort: 80
```
```
kubectl scale deployment/nginx-deployment -n exam-mason --replicas=6
```
```
kubectl get all -n exam-mason | grep deployment
```
# 5

# 6


# 7
```
apiVersion: v1
kind: Pod
metadata:
  name: cpu-utilizer
spec:
  containers:
  - name: busybox
    image: busybox:1.28
  - name: nginx
    image: nginx:1.14.2
    ports:
    - containerPort: 80
```

```
kubectl apply -n exam-mason -f ./cpu-pod.yaml
```


# 8

