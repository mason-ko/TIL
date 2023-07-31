![image](https://github.com/mason-ko/TIL/assets/30224146/991c7bec-7bce-4915-abcf-574329489685)# Index
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
    - prefix: CONFIG_ # 모든 환경변수는 CONFIG_ 접두사를 가짐, 여기 configmap 에서 가져온 환경변수앞에 이 prefix를 붙인다는뜻 ex) FOO 는 CONFIG_FOO 가 됨 
    configMapRef:
      name: my-config-map # my-config-map 이라는 컨피그맵 참조 
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

### 7.4.7 애플리케이션을 재시작하지 않고 애플리케이션 설정 업데이트
## 7.5 시크릿으로 민감한 데이터를 컨테이너에 전달
### 7.5.1 시크릿소개
### 7.5.2 기본 토큰 시크릿 소개
### 7.5.3 시크릿 생성
### 7.5.4 컨피그맵과 시크릿 비교
### 7.5.5 파드에서 시크릿 사용
### 7.5.6 이미지를 가져올 때 사용하는 시크릿 이해
## 7.6 요 약