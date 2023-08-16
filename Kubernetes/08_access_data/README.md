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
서비스와 파드에 관한 정보는 서비스 관련 환경변수나 DNS로 얻을 수 있다.  
그러나 애플리케이션이 다른 리소스의 정보가 필요하거나 가능한 한 최신 정보에 접근해야 하는 경우  
API 서버와 직접 통신해야 한다.
- 자동화 및 CI/CD: Continuous Integration / Continuous Deployment 파이프라인에서 자동화된 작업을 수행할 때 API 서버와 직접 통신이 필요할 수 있습니다. 예를 들면, 특정 리소스의 상태를 자동으로 확인하거나, 동적으로 리소스를 생성/변경/삭제하는 작업 등이 있습니다.
- 커스텀 스크립트 및 툴: kubectl의 기능만으로 충분하지 않은 경우나 특별한 작업을 위해 커스텀 스크립트나 툴을 개발할 때 API 서버와 직접 통신하는 것이 필요합니다.
- 응용 프로그램 통합: 쿠버네티스 클러스터 상태나 리소스 정보를 기반으로 동작하는 응용 프로그램을 개발할 때도 API 서버와의 직접 통신이 필요합니다.
- 커스텀 리소스 및 컨트롤러: 쿠버네티스에서 제공하지 않는 기능이나 리소스를 사용하기 위해 커스텀 리소스와 관련 컨트롤러를 개발할 때 API 서버와 직접 통신하는 방식으로 동작합니다.
- 고급 쿼리: kubectl로는 제한된 정보만을 제공받을 수 있을 때, API 서버로 직접 쿼리하여 필요한 데이터를 얻을 수 있습니다.


### 8.2.1 쿠버네티스 REST API 살펴보기 
```
$ kubectl cluster-info
$ kubectl proxy
$ curl localhost:8001
$ curl http://localhost:8001
$ curl http://localhost:8001/apis/batch/v1
$ curl http://localhost:8001/apis/batch/v1/jobs
$ curl http://localhost:8001/apis/batch/v1/namespaces/default/jobs/my-job
```

### 8.2.2 파드 내에서 API 서버와 통신 
파드 내부에서 API 서버와 통신하려면 
- API 서버의 위치를 찾아야한다.
- API 서버와 통신하고 있는지 확인해야 한다.
- API 서버로 인증해야 한다. 그렇지 않으면 볼 수도 없고 아무것도 할 수 없다.
#### API 서버와의 통신을 시도하기 위해 파드 실행 
API 주소 찾기 
```
$ kubectl get svc
```
#### 서버의 아이덴티티 검증 
curl --cacert /var/run/secrets/kubernetes.io/serviceaccount /ca.crt https://kubernetes  

CURL_CA_BUDNLE 환경변수를 사용하면 일일이 --cacert 를 지정 할 필요 없다.

#### API 서버로 인증 
토큰을 사용해 API 서버 액세스 
```
TOKEN=$(cat /var/run/secrets/kubernetes.io/serviceaccount/token)
```
<img width="608" alt="image" src="https://github.com/mason-ko/TIL/assets/30224146/ee81e9c3-4b06-4d88-9bf2-e95185f73b37">

#### 파드가 실행중인 네임스페이스 얻기 
<img width="499" alt="image" src="https://github.com/mason-ko/TIL/assets/30224146/5445625d-7de4-4fbb-900f-26bf2f8d222a">

#### 파드가 쿠버네티스와 통신하는 방법 정리 
- 애플리케이션은 API 서버의 인증서가 인증 기관으로부터 서명됐는지를 검증해야하며, 인증기관의 인증서는 ca.cart 파일에 있다.
- 애플리케이션은 token 파일의 내용을 Authorization HTTP 헤더에 Bearer 토큰으로 넣어 전송해서 자신을 인증해야 한다.
- namespace 파일은 파드의 네임스페이스 안에 있는 API 오브젝트의 CRUD 작업을 수행할 때 네임스페이스를 API 서버로 전달하는 데 사용해야 한다.

<img width="652" alt="image" src="https://github.com/mason-ko/TIL/assets/30224146/76d2d39d-3561-4939-b5b1-715a9fea7e74">

### 8.2.3 앰배서더 컨테이너를 이용한 API 서버 통신 간소화 
위 방법으로 일일이 다루는건 너무 복잡하다. 그래서 안소하게 하는 방법  
메인 컨테이너 옆의 앰배서더 컨테이너에서 kubectl proxy 를 실행하고 이를 통해 API 서버와 통신할 수있다.  
시크릿 볼륨에 있는 default-token 파일을 사용해 이를 수행한다.  
<img width="568" alt="image" src="https://github.com/mason-ko/TIL/assets/30224146/3df0169e-b365-461a-a68e-fba57fdaecb0">

#### 추가적인 앰배서더 컨테이너를 사용한 curl 파드 실행 
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: curl-with-ambassador
spec:
  containers:
  - name: main
    image: tutum/curl
    command: ["sleep", "9999999"]
  - name: ambassador                  # kubectl-proxy 이미지를 실행하는 
    image: luksa/kubectl-proxy:1.6.2  # 앰배서더 컨테이너 
```
### 8.2.4 클라이언트 라이브러리를 사용해 API 서버와 통신 
단순한 api 요청 이상을 수행하려면 쿠버네티스 api 클라이언트 라이브러리 중 하나를 사용하는 것이 좋다.  

- Golang: https://github.com/kubernetes/client—go
- Python: https://github.com/kubernetes-incubator/client-python/

### 정리
8장에서는 파드 내에서 실행되는 애플리케이션이 애플리케이션 자신, 다른 파드, 클러스터에 배포된 다른 구성 요소의 데이터를 얻는 방법을 살펴봤다.
- 파드의 이름, 네임스페이스 및 기타 메타데이터가 환경변수 또는 downward API 볼륨의 파일로 컨테이너 내부의 프로세스에 노출되는 방법





