# Index
- [7장 컨피그맵과 시크릿: 애플리케이션 설정](#7장-컨피그맵과-시크릿-애플리케이션-설정)
  - [7.1 컨테이너화된 애플리케이션 설정](#71-컨테이너화된-애플리케이션-설정)
  - [7.2 컨테이너에 명령줄 인자 전달](#72-컨테이너에-명령줄-인자-전달)
    - [7.2.1 도커에서 명령어와 인자 정의](#721-도커에서-명령어와-인자-정의)
    - [7.2.2 쿠버네티스에서 명령과 인자 재정의](#722-쿠버네티스에서-명령과-인자-재정의)
  - [7.3 컨테이너의 환경변수 설정](#73-컨테이너의-환경변수-설정)
    - [7.3.1 컨테이너 정의에 환경변수 지정](#731-컨테이너-정의에-환경변수-지정)
    - [7.3.2 변숫값에서 다른 환경변수 참조](#732-변숫값에서-다른-환경변수-참조)
    - [7.3.3 하드코딩된 환경변수의 단점](#733-하드코딩된-환경변수의-단점)
  - [7.4 컨피그맵으로 설정 분리](#74-컨피그맵으로-설정-분리)
    - [7.4.1 컨피그맵소개](#741-컨피그맵소개)
    - [7.4.2 컨피그맵 생성](#742-컨피그맵-생성)
    - [7.4.3 컨피그맵 항목을 환경변수로 컨테이너에 전달](#743-컨피그맵-항목을-환경변수로-컨테이너에-전달)
    - [7.4.4 컨피그맵의 모든 항목을 한 번에 환경변수로 전달](#744-컨피그맵의-모든-항목을-한-번에-환경변수로-전달)
    - [7.4.5 컨피그맵 항목을 명령줄 인자로 전달](#745-컨피그맵-항목을-명령줄-인자로-전달)
    - [7.4.6 컨피그맵 볼륨을 사용해 컨피그맵 항목을 파일로 노출](#746-컨피그맵-볼륨을-사용해-컨피그맵-항목을-파일로-노출)
    - [7.4.7 애플리케이션을 재시작하지 않고 애플리케이션 설정 업데이트](#747-애플리케이션을-재시작하지-않고-애플리케이션-설정-업데이트)
  - [7.5 시크릿으로 민감한 데이터를 컨테이너에 전달](#75-시크릿으로-민감한-데이터를-컨테이너에-전달)
    - [7.5.1 시크릿소개](#751-시크릿소개)
    - [7.5.2 기본 토큰 시크릿 소개](#752-기본-토큰-시크릿-소개)
    - [7.5.3 시크릿 생성](#753-시크릿-생성)
    - [7.5.4 컨피그맵과 시크릿 비교](#754-컨피그맵과-시크릿-비교)
    - [7.5.5 파드에서 시크릿 사용](#755-파드에서-시크릿-사용)
    - [7.5.6 이미지를 가져올 때 사용하는 시크릿 이해](#756-이미지를-가져올-때-사용하는-시크릿-이해)
- [7.6 요약](#76-요약)


# 7장 컨피그맵과 시크릿: 애플리케이션 설정
# 다루는 내용
- 컨테이너의 주 프로세스 변경
- 애플리케이션에 명령줄 옵션 전달
- 애플리케이션에 노출되는 환경변수 설정
- 컨피그맵으로 애플리케이션 설정
- 시크릿으로 민감한 정보 전달

- **컨테이너의 주 프로세스**: 컨테이너는 시작 시 주 프로세스를 실행하며, 이 주 프로세스가 종료되면 컨테이너도 종료됩니다. 따라서 주 프로세스를 변경하는 것은 컨테이너의 수명주기와 밀접하게 연관되어 있습니다.
- **명령줄 옵션**: 이는 터미널 또는 콘솔에서 프로그램을 실행할 때 사용자가 프로그램에게 전달하는 추가적인 인수 또는 옵션입니다.
- **환경 변수**: 운영 체제에서 프로세스가 실행될 때 해당 프로세스가 참조할 수 있는 동적 값을 저장하는 데 사용됩니다. 애플리케이션 설정, 서비스 연결 문자열 등을 저장하는 데 자주 사용됩니다.
- **컨피그맵(ConfigMap)**: 쿠버네티스(Kubernetes)에서 사용되는 API 오브젝트로, 구성 세부 정보를 저장하는 데 사용됩니다. 환경변수, 커맨드라인 인수 등을 설정하는데 사용할 수 있습니다.
- **시크릿(Secret)**: 쿠버네티스에서 사용하는 API 오브젝트로, 민감한 정보(예: 암호, API 키 등)를 저장하고 관리하는 데 사용됩니다. 이는 암호화되어 안전하게 관리되며, 필요한 컨테이너에만 노출됩니다.
## 7.1 컨테이너화된 애플리케이션 설정
- 명령줄 인수 전달
- 각 컨테이너를 위한 사용자 정의 환경변수 지정
- 특수한 유형의 볼륨을 통해 설정 파일을 컨테이너에 마운트 
## 7.2 컨테이너에 명령줄 인자 전달
### 7.2.1 도커에서 명령어와 인자 정의

### ENTRYPOINT와 CMD의 이해 
Dockerfile에서 두개의 지침
- ENTRYPOINT는 컨테이너가 시작될 때 호출될 명령어
- CMD는 ENTRYPOINT에 전달되는 인자를 정의
CMD 명령어를 사용해 이미지가 실행될 때 실행할 명령어를 지정할 수 있지만, 올바른 방법은
ENTRYPOINT 명령어로 실행하고 기본 인자를 정의하려는 경우에만 CMD 를 지정

추가설명 
- ENTRYPOINT는 Docker 컨테이너가 시작될 때 항상 실행할 명령을 정의합니다.
- CMD는 Docker 컨테이너가 시작될 때 실행할 기본 명령을 정의합니다. 이 명령은 Docker run 명령어에 인자를 추가함으로써 덮어쓸 수 있습니다.
```yaml
FROM ubuntu:18.04
ENTRYPOINT ["/bin/echo", "Hello"]
CMD ["world"]
```
여기서 ENTRYPOINT는 /bin/echo hello 를 실행하고  
CMD 는 이 명령에 인자로 world 를 추가한다. 만약 Docker run 명령에 추가 인자를 제공한다면, 그 인자는 CMD에 정의된 world를 대체  
```
docker run <image> everyone
```
이 경우, 최종적으로 출력은 "hello everyone"  
ENTRYPOINT와 CMD는 둘다 exec(["executable","param1","param2"])과 shell 형식("executable param1 param2")을 지원합니다. 가능하면 exec 형식이 JSON 배열 형식을 사용하기에 더 안전하다.  

참고로 ENTRYPOINT와 CMD를 모두 Dockerfile에 정의하는경우 CMD는 ENTRYPOINT에 추가적인 인자를 제공하는것으로 간주.

#### 이미지에서 간격 설정 
fortuneloop.sh  
```yaml
# !/bin/bash
trap "exit" SIGINT
INTERVAL=$1
echo Configured to generate new fortune every $INTERVAL seconds mkdir -p /var/htdocs
while :
echo $(date) Writing fortune to /var/htdocs/index.html /usr/games/fortune > /var/htdocs/index.html
sleep ^INTERVAL
done
```
Dockerfile  
```yaml
FROM ubuntu:latest
RUN apt-get update ; apt-get -y install fortune
ADD fortuneloop.sh /bin/fortuneloop.sh 
ETNRYPOINT ["/bin/fortuneloop.sh"] # exec 형태의 ENTRYPOINT 명령 
CMD ["10"] # 실행할 때 사용할 기본 인자 
```
### 7.2.2 쿠버네티스에서 명령과 인자 재정의
```yaml
kind: Pod
spec:
  containers:
  - image: some/image
    command: ["/bin/command"]
    args: [Margl% "arg2", "arg3"]
```
대부분 사용자 정의 인자만 지정하고 명령을 재정의하는 경우는 거의 없다.  
이는 기본 명령을 재정의하면 컨테이너의 예상되는 행동을 변경할 수 있고 이는 문제를 일으킬수있다.  
예를 들어, 재정이된 명령이 컨테이너의 생명주기를 제대로 관리하지 못하면 컨테이너가 예기치 않게 종료되거나 문제를 일으킬 수 있기 때문.  
## 7.3 컨테이너의 환경변수 설정
### 7.3.1 컨테이너 정의에 환경변수 지정
```yaml
kind: Pod
spec:
  containers:
  - image: luksa/fortune:env
    env:               #환경변수 목록에 단일 변수 추가 
    - name: INTERVAL
      value: "30"
    name: html-generator
```
### 7.3.2 변숫값에서 다른 환경변수 참조
```yaml
env:
- name: FIRST_VAR
  value: "foo"
- name: SECOND_VAR
  value: "$(FIRST_VAR)bar"
```
SECOND_VAR 값은 foobar가 된다.
### 7.3.3 하드코딩된 환경변수의 단점
- 유연성 부족: 하드코딩된 환경 변수는 변경이 어렵습니다. 서비스가 확장되거나 변경되면서 환경 변수를 수정해야 할 수 있는데, 이는 새로운 이미지를 빌드하고 배포해야 하는 번거로움을 가져옵니다.
- 보안 이슈: 민감한 정보(예: 비밀번호, API 키 등)를 하드코딩하면 보안 위협이 될 수 있습니다. 이러한 정보는 쿠버네티스의 Secrets와 같은 보안 메커니즘을 통해 관리되어야 합니다.
- 환경 간 이동 어려움: 개발, 테스트, 프로덕션 등 다양한 환경에서 실행할 때, 각 환경에 맞게 환경 변수를 설정해야 합니다. 하드코딩된 환경 변수는 이를 어렵게 만듭니다.
- 코드와 설정의 분리 원칙 위반: 코드와 설정을 분리하는 것은 소프트웨어 개발의 일반적인 베스트 프랙티스입니다. 하드코딩된 환경 변수는 이 원칙을 위반하게 됩니다.
## 7.4 컨피그맵으로 설정 분리
### 7.4.1 컨피그맵소개
- 키/값으로 이루진 맵.
- 환경변수는 $(ENV_VAR) 구문을 사용해 명령줄 인수에서 참조할 수 있다.
- 쿠버네티스 rest api 호출해서 직접 읽을 수 있지만, 무관하게 유지.
- 독립적인 오브젝트에 설정을 포함하면, 각각 다른 환경에 관해 동일한 이름으로 여러 매니페스트를 유지 가능.
![image](https://github.com/mason-ko/TIL/assets/30224146/ebab08bc-a52f-4025-9f9d-f44ad0631e2c)
### 7.4.2 컨피그맵 생성
#### kubectl create configmap 명령 사용
sleep-inverval=25 라는 단일 항목을 가진 fortune-config 컨피그맵 생성  
생성 후 yaml 조회 가능  
```
$ kubectl create configmap fortune-config --from -literal=sleep-interval=25

$ kubectl get configmap fortune-config -o yaml
```
#### 파일 내용으로 컨피그맵 생성 
디스크에서 읽어 개별항목 지정  
키 이름 직접 지정  
--from-file 인수를 여러번 사용해 여러 파일 추가 가능  
```
$ kubectl create configmap my-config --from-file=config-file.conf

$ kubectl create configmap my-config --from-file=customkey=config-file.conf
```

#### 디렉터리에 있는 파일로 컨피그맵 생성 
```
$ kubectl create configmap my-config --from-file=/path/to/dir
```
#### 옵션들 
- --from-file=foo.json # 단일파일
- --from-file=bar=foobar.json # 사용자 정의 키 밑에 파일 저장
- --from-file=config-opts/ # 전체디렉터리
- --from-literal=some=thing # 문자열 값 
![image](https://github.com/mason-ko/TIL/assets/30224146/df8eecd2-28ab-4e7d-a529-3e9da03dc7c6)

### 7.4.3 컨피그맵 항목을 환경변수로 컨테이너에 전달
파드 yaml
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: fortune-env-from-configmap
spec:
  containers:
  - image: luksa/fortune:env
    env:
    - name: INTERVAL # INTERVAL 환경변수 설정 중 
      valueFrom:  # 고정 값을 설정하는 대신 컨피그맵 키에서 값을 가져와 초기화 
        configMapKeyRef:
          name: fortune-config # 참조하는 컨피그맵 이름 
          key: sleep-interval # 컨피그맵에서 해당 키 아래에 저장된 값으로 변수 설정 
```
#### 파드에 존재하지 않는 컨피그맵 참조 
ex) Error: configmap "my-config" not found
### 7.4.4 컨피그맵의 모든 항목을 한 번에 환경변수로 전달 
```yaml
spec:
  containers:
  - image: some-image
    envFrom: # env 대신 envFrom 속성 사용
    - prefix: CONFIG_ # 모든 환경변수는 CONFIG_ 접두사를 가짐
      configMapRef:
        name: my-config-map # my-config-map 이라는 컨피그맵 참조
    volumeMounts:
    - name: config-volume
      mountPath: /config  # 볼륨을 마운트할 경로 지정
  volumes:
  - name: config-volume
    configMap:
      name: my-config-map
```
### 7.4.5 컨피그맵 항목을 명령줄 인자로 전 달
![image](https://github.com/mason-ko/TIL/assets/30224146/4e4ae0a4-c82e-4a61-947d-56bce44708a0)
```yaml
apiVersion: vl
kind: Pod
metadata:
  name: fortune-angs-from-configmap
spec:
  containers:
  - image: luksa/fortune:args
    env:
    - name: INTERVAL
      valueFrom:
        configMapKeyRef:
          name: fortune-config
          key: sleep-interval
    args: ["$(INTERVAL)"] # $(ENV_NAME) 문법 사용 
```
### 7.4.6 컨피그맵 볼륨을 사용해 컨피그맵 항목을 파일로 노출
컨피맵은 모든 설정파일을 포함가능  
이 파일들을 컨테이너에 노출시키려면, 컨피그맵 볼륨 사용  
- 컨피그맵 오브젝트는 key-value형태로 저장하기때문에  ngnix 설정파일, yaml, 텍스트 등 다양한 형태의 설정파일이 될 수 있다.
#### 볼륨 안에 있는 컨피그맵 항목 사용 
Nginx 기준으로 설정파일 위치(/etc/nginx/ngix.conf) 에 맞게 마운트를 해야한다.  
![image](https://github.com/mason-ko/TIL/assets/30224146/009895f5-c4fd-46d7-9152-518812853173)
```yaml
apiVersion: vl
kind: Pod
metadata:
  name: fortune-configmap-volume
spec:
  containers:
  - image: nginx:alpine
    name: web-server
    volumeMounts:
    ...
    - name: config
      mountPath: /etc/nginx/conf.d # 컨피그맵 볼륨을 마운트하는 위치 
      readonly: true
    ...
  volumes:
  ...
  - name: config # 위의 볼륨 마운트의 name 과 일치해야함
    configMap:
      name: fortune-config # 이 볼륨은 fortune-config 컨피그맵을 참조한다.
...
```
#### 마운트된 컨피그맵 볼륨 내용 살펴보기 
```
$ kubectl exec fortune-configmap-volumne -c web-server ls /etc/nginx/config.d
```
#### 볼륨에 특정 컨피그맵 항목 노출 
```yaml
volumes:
- name: config
  configMap:
  name: fortune-config 
  items: # 볼륨에 포함할 항목을 조회해 선택 
  - key: my-nginx-cᄋnfig.conf # 해당 키 아래에 항목 포함 
    path: gzip.conf # 항목 값이 지정된 파일에 저장 
```
#### 디렉터리를 마운트할 때 디텍터리의 기존 파일을 숨기는 것 이해 
마운트시 마운트 된 디렉터리에 이 오브젝트의 모든 항목이 파일로 생성이되는데, 이때 해당 디렉터리에 이미 파일이 있었다면,  
이 파일들은 마운트에 의해 "숨겨진다"  
마운트된 파일 시스템이 기존 파일 시스템 위에 "덮어씌워지는" 것이기 때문에, 접근이 불가함  
예를 들어, /etc 에 컨피그맵을 마운트하면 원래있던 파일들을 볼 수 없게 됨으로써  
별도의 하위 디렉터리를 생성하여 마운트하는 것이 안전하다.
#### 디렉터리 안에 다른 파일을 숨기지 않고 개별 컨피그맵 항목을 파일로 마운트
volumeMount에 subPath 속성으로 파일이나 디렉터리 하나를 볼륨에 마운트 할 수 있다.
![image](https://github.com/mason-ko/TIL/assets/30224146/b1fa5761-169a-4f75-b8e2-ea2a66a0acb0)

```yaml
  containers:
  - image: some/image
    volumeMounts:
    - name: myvolume
      mountPath: /etc/someconfig.conf # 디렉터리가 아닌 파일 마운트
      subPath: myconfig.conf # 전체 볼륨을 마운트하는 대신 myconfig.conf 항목만 마운트 
```
#### 컨피그맵 볼륨 안에 있는 파일 권한 설정 
기본적으로 컨피그맵 볼륨의 모든 파일권한은 644(-rw-r-r--)  
defaultMode 속성을 설정해 변경 가능 
```yaml
volumes:
  - name: config
    configMap:
    name: fortune-config # 모든파일권한을
    defaultMode: "6600"  # -rw-rw----- 로 설정 
```
### 7.4.7 애플리케이션을 재시작하지 않고 애플리케이션 설정 업데이트
환경변수 또는 명령줄 인수를 사용할때는 프로세스 실행중 업데이트 불가.  
컨피그맵을 사용해 볼륨으로 노출하면 재시작 없이 업데이트 가능.  
- 단. golang 에서 환경변수로 읽을 때에는 해당되지 않고, 직접적으로 ConfigMap 볼륨으로 마운트한  
경로에 io로 접근했을 때 ( os.ReadFile ) 에만 가능하다.  
- 환경변수는 프로세스가 시작할 때 한번만 읽히기 때문에 환경변수로 사용시에는 재시작이 필요함.
## 7.5 시크릿으로 민감한 데이터를 컨테이너에 전달
### 7.5.1 시크릿소개
자격증명, 개인암호호 키와 같은 민감정보를 보관하고 시크릿이라는 별도 오브젝트를 제공.  
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secret-pod
spec:
  containers:
  - name: secret-container
    image: my-image
    volumeMounts:
    - name: secret-volume
      mountPath: "/etc/secret" # Secret을 마운트할 경로 지정
  volumes:
  - name: secret-volume
    secret:
      secretName: my-secret # 사용할 Secret 이름 지정
```
시크릿의 데이터 항목을 컨피그맵 처럼 환경변수로 사용 가능하며, env, envFrom 동일하게 사용 가능.  
시크릿고 컨피그맵의 차이는
- 데이터의 민감성: Secret 오브젝트는 민감한 데이터, 예를 들어 암호, OAuth 토큰, ssh 키 등을 저장하는 데 사용됩니다. 반면에 ConfigMap은 일반적인(non-sensitive) 설정 정보, 예를 들어 애플리케이션의 config 파일, shell 스크립트 등을 저장하는 데 사용됩니다.
- 데이터의 암호화: Kubernetes의 Secret은 기본적으로 etcd에 base64 인코딩된 형태로 저장됩니다. 이는 암호화가 아니라 인코딩이므로, 실제로는 plaintext로 저장되는 것과 동일합니다. 그러나 Kubernetes 1.7 이상에서는 etcd에 Secret을 암호화하여 저장하는 기능을 제공합니다. ConfigMap은 이러한 암호화 옵션이 없으며, 항상 plaintext로 저장됩니다.
- 사용 사례: ConfigMaps는 설정 파일이나 속성을 컨테이너화된 애플리케이션으로 전달하는데 사용되며, Secrets는 민감한/비밀 정보를 안전하게 전달하는데 사용됩니다.
- 크기 제한: Secret 오브젝트의 최대 크기는 1MiB입니다. 이 크기 제한은 API 서버와 kubelet 간의 메모리 사용량을 제한하는 데 사용됩니다. ConfigMap에는 이와 같은 크기 제한이 없습니다 (단, etcd에서 데이터를 읽고 쓰는 퍼포먼스가 제한 요인이 될 수 있습니다).
  
### 7.5.2 기본 토큰 시크릿 소개
```
$ kubectl get secrets
```
시크릿이 갖고 있는 세 가지 항목(ca.crt, namespace, token) 은 파드 안에서 쿠버네티스  
API 서버와 통신할 때 필요한 모든것을 나타낸다.  
- ca.crt: 이 파일은 쿠버네티스 클러스터의 CA(Certificate Authority) 인증서를 포함하고, 클러스터 내의 다른 서비스와 통신할 때 SSL/TLS를 사용하여 이들 서비스가 신뢰할 수 있는 서비스임을 증명하는 데 사용되는 인증서
- namespace: 이 파일은 현재 파드가 실행되고 있는 네임스페이스의 이름을 포함하고 있습니다. 파드가 어떤 네임스페이스에서 실행되고 있는지를 알아야 할 때 이 파일을 참조하면 됩니다.
- token: 이 파일은 Service Account 토큰을 포함하고 있다. 이 토큰은 쿠버네티스 API 서버에 대한 인증에 사용되며, 해당 Service Account 권한을 가진 사용자로써 API 서버에 요청을 보낼 수 있게 해줌. 이를 통해 Pods 는 자신의 권한 내에서 쿠버네티스 API를 사용할 수 있게 된다.
### 7.5.3 시크릿 생성
먼저 인증서와 개인 키 파일 생성.
```
$ openssl genrsa -out https.key 2048
$ openssl req -new -x509 -key https.key -out https.cert -days 3650 -subj
/CN=www•kubia-example•com
```
시크릿에 대한 foo 더미파일 안에 bar 문자열 저장  
```
$ echo bar > foo
```
이제 세가지 파일에서 시크릿을 만들 수 있다. 
```
$ kubectl create secret generic fortune-https --from-file=https.key --from-file=https.cert --from-file=foo

secret "fortune-https" created
```
--from-file=fortune-https 옵션 이용해 개별파일 대신 디렉터리 전체 포함 가능.
### 7.5.4 컨피그맵과 시크릿 비교
<img width="593" alt="image" src="https://github.com/mason-ko/TIL/assets/30224146/ce68c0a1-b11b-409c-8d95-96f83804b770">
시크릿 항목의 내용은 Base64 인코딩 문자열로 표시된다.  
#### stringData 필드 소개 
```yaml
kind: Secret
apiVersion: v1
stringData: # stringDat는 바이너리 데이터가 아닌 시크릿 데이터에 사용 할 수 있다.
  foo: plain text # plain text는 base64 인코딩 되지 않는것을 볼 수있다. 
```
### 7.5.5 파드에서 시크릿 사용
### 7.5.6 이미지를 가져올 때 사용하는 시크릿 이해
## 7.6 요 약
