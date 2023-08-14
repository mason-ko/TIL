# Index
- [8장 애플리케이션에서 파드 메타데이터와 그 외의 리소스에 액세스하기](#8장)
  - [8.1 Downward API로 메타데이터 전달](#81)
    - [8.1.1 사용 가능한 메타데이터 이해](#811)
    - [8.1.2 환경변수로 메타데이터 노출하기](#812)
    - [8.1.3 downwardAPI 볼륨에 파일로 메타데이터 전달](#813)
  - [8.2 쿠버네티스 API 서버와 통신하기](#82)
    - [8.2.1 쿠버네티스 REST API 살펴보기](#821)
    - [8.2.2 파드 내에서 API 서버와 통신](#822)
    - [8.2.3 앰배서더 컨테이너를 이용한 API 서버 통신 간소화](#823)
    - [8.2.4 클라이언트 라이브러리를 사용해 API 서버와 통신](#824)

# 8장 애플리케이션에서 파드 메타데이터와 그 외의 리소스에 액세스하기
## 8.1 Downward API로 메타데이터 전달 
Downward API는 쿠버네티스에서 컨ㅔ이너에 자신의 정보를 전달하는 메커니즘이며,  
주로 파드에 대한 정보를 파드 내의 컨테이너에게 알려주기 위해 사용된다.  
Downward API를 사용하면 파드의 필드를 컨테이너의 환경 변수나 파일로 주입 할 수 있다.
주요시나리오
- 환경변수로 파드정보 전달
- 파일로 파드정보 전달
### 8.1.1 사용 가능한 메타데이터 이해 
- 파드의 이름
- 파드의 IP 주소
- 파드가 속한 네임스페이스
- 파드가 실행 중인 노드의 이름
- 파드가 실행 중인 서비스 어카운트 이름
- 각 컨테이너의 CPU와 메모리 요청
- 각 컨테이너의 CPU와 메모리 제한
- 파드의 레이블
- 파드의 어노테이션
목록에 있는 대부분의 항목은 환경변수 또는 downwardAPI 볼륨으로 컨테이너에 전달될 수 있지만
레이블과 어노테이션은 볼륨으로만 노출될 수 있다. 일부 데이터는 다른 방법(OS에서직접)으로도 얻을 수 있지만, Downward API는 더 간단한 대안을 제공.

### 8.1.2 환경변수로 메타데이터 노출하기 
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: downward
spec:
  containers:
  - name: main
    image: busybox
    command: ["sleep", "9999999"]
    resources:
      requests:
        cpu: 15m
        memory: 100Ki
      limits:
        cpu: 100m
        memory: 4Mi
    env:
    - name: POD_NAME
      valueFrom:                       # 특정 값을 설정하는 대신 
        fieldRef:                      # 파드 매니페스트의 metadata.name을  
          fieldPath: metadata.name     # 참조한다.
    - name: POD_NAMESPACE
      valueFrom:
        fieldRef:
          fieldPath: metadata.namespace
    - name: POD_IP
      valueFrom:
        fieldRef:
          fieldPath: status.podIP
    - name: NODE_NAME
      valueFrom:
        fieldRef:
          fieldPath: spec.nodeName
    - name: SERVICE_ACCOUNT
      valueFrom:
        fieldRef:                            
          fieldPath: spec.serviceAccountName
    - name: CONTAINER_CPU_REQUEST_MILLICORES
      valueFrom:
        resourceFieldRef:                 # 컨테이너의 CPU/메모리 요청과 제한은
          resource: requests.cpu          # fieldRef 대신 resourceFieldRef사용
          divisor: 1m                     # 리소스 필드의 경우 제수(divisor)를 정의
    - name: CONTAINER_MEMORY_LIMIT_KIBIBYTES 
      valueFrom:
        resourceFieldRef:
          resource: limits.memory
          divisor: 1Ki
```
이 예제에서는 CPU 요청에 대한 제수를 1m(1밀리코어 또는 1000분의 1 CPU 코어)로 설정함.  
CPU 요청을 15m로 설정했기 때문에 환경변수 CONTAINER_CPU_REQUEST_MILLICORES는 15로 설정됨.  
마찬가지로 메모리 제한을 4Mi(4메비바이트)로 설정하고 제수를 1Ki(1키비바이트)로 설정했으므로  
CONTAINER_MEMORY_LIMIT_KIBIBYTES 는 4096으로 설정됨 
<img width="688" alt="image" src="https://github.com/mason-ko/TIL/assets/30224146/42c7a1f9-310e-4436-b5a5-ddec48bbd9d5">

파드 생성 후 환경변수로 확인
```
$ kubectl exec downward env
```

### 8.1.3 downwardAPI 볼륨에 파일로 메타데이터 전달 
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: downward
  labels:           # 이 레이블과 
    foo: bar
  annotations:      # 어노테이션은 downwardAPI 볼륨으로 노출된다. 
    key1: value1
    key2: |
      multi
      line
      value
spec:
  containers:
  - name: main
    image: busybox
    command: ["sleep", "9999999"]
    resources:
      requests:
        cpu: 15m
        memory: 100Ki
      limits:
        cpu: 100m
        memory: 4Mi
    volumeMounts:            
    - name: downward           # downward 볼륨은 
      mountPath: /etc/downward # /etc/downward 아래에 마운트한다.
  volumes:
  - name: downward     # downwardAPI 볼륨은
    downwardAPI:       # downward라는 이름으로 정의한다.
      items:
      - path: "podName"
        fieldRef:            # 파드의 이름(metadata.name 필드)은 podName 파일에 기록
          fieldPath: metadata.name
      - path: "podNamespace"
        fieldRef:
          fieldPath: metadata.namespace
      - path: "labels"
        fieldRef:   # 레이블은 /etc/downward/labels 파일에 기록
          fieldPath: metadata.labels
      - path: "annotations" 
        fieldRef:   # 어노테이션을 /etc/downward/annotations 파일에 기록
          fieldPath: metadata.annotations
      - path: "containerCpuRequestMilliCores"
        resourceFieldRef:
          containerName: main
          resource: requests.cpu
          divisor: 1m
      - path: "containerMemoryLimitBytes"
        resourceFieldRef:
          containerName: main
          resource: limits.memory
          divisor: 1
```

<img width="615" alt="image" src="https://github.com/mason-ko/TIL/assets/30224146/ab163907-5ee4-4d09-9362-bbeb8a27e001">
#### 볼륨 스펙에서 컨테이너 수준의 메타데이터 참조
```yaml
spec: 
  volumes:
  - name: downward 
    downwardAPI:
      items:
      - path: "containerCpuRequestMilliCores"
        resourceFieldRef:
          containerName: main # 컨테이너 이름이 반드시 지정돼야 한다.
          resource: requests.cpu
          divisor: 1m
```
#### Downward API 사용 시기 이해 
Downward API 로 하용 가능한 메타데이터는 상당히 제한적이므로, 더 많은 정보가 필요한 경우  
쿠버네티스 API 서버에서 직접 가져와야 한다.  
## 8.2 쿠버네티스 API 서버와 통신하기 
### 8.2.1 쿠버네티스 REST API 살펴보기 
### 8.2.2 파드 내에서 API 서버와 통신 
### 8.2.3 앰배서더 컨테이너를 이용한 API 서버 통신 간소화 
### 8.2.4 클라이언트 라이브러리를 사용해 API 서버와 통신 
