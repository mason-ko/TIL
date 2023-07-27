# 다루는 내용
- 다중 컨테이너 파드 생성
- 컨테이너 간 디스크 스토리지를 공유하기 위한 볼륨 생성
- 파드 내부에 깃 리포지터리 사용
- 파드에 GCE 퍼시스턴트 디스크와 같은 퍼시스턴트 스토리지 연결
- 사전 프로비저닝된 퍼시스턴트 스토리지
- 퍼시스턴트 스토리지의 동적 프로비저닝

# index
- [6.볼륨: 컨테이너에 디스크 스토리지 연결](#6볼륨-컨테이너에-디스크-스토리지-연결)
  - [6.1 볼륨 소개](#61-볼륨-소개)
  - [6.2 볼륨을 사용한 컨테이너 간 데이터 공유](#62-볼륨을-사용한-컨테이너-간-데이터-공유)
  - [6.3 워커 노드 파일시스템의 파일 접근](#63-워커-노드-파일시스템의-파일-접근)
  - [6.4 퍼시스턴트 스토리지 사용](#64-퍼시스턴트-스토리지-사용)
  - [6.5 기반 스토리지 기술과 파드 분리](#65-기반-스토리지-기술과-파드-분리)
  - [6.6 퍼시스턴트볼륨의 동적 프로비저닝](#66-퍼시스턴트볼륨의-동적-프로비저닝)
  - [6.7 요약](#67-요약)

### 들어가기전에
쿠버네티스에서 볼륨은 주로 데이터를 저장하고 공유하는 데 사용되는 기능입니다. 파드와 컨테이너의 라이프사이클과 독립적으로 지속되며, 여러 컨테이너 간에 데이터를 공유할 수 있게 해줍니다. 볼륨 마운트에 대해 이해하기 위해 먼저 알아두면 좋은 개념들이 있습니다.
* 파드의 라이프사이클과 볼륨의 라이프사이클: 파드의 모든 컨테이너는 동일한 라이프사이클을 공유하지만, 볼륨은 파드의 라이프사이클과는 독립적입니다. 즉, 파드가 삭제되더라도 볼륨의 데이터는 지속될 수 있습니다.
* Persistent Volumes (PV) 및 Persistent Volume Claims (PVC): Persistent Volumes(PV)는 클러스터의 저장소를 나타내는 API 리소스이며, Persistent Volume Claims(PVC)는 사용자에 의해 생성되어 PV를 요청하는 API 리소스입니다. PVC가 만들어지면, 쿠버네티스 스케줄러는 PVC의 요구사항을 만족하는 PV를 찾아 바인딩합니다.
* 볼륨 타입: 쿠버네티스는 다양한 유형의 볼륨을 지원합니다. 이들은 각각의 특징과 제한사항이 있으므로, 각 볼륨 타입의 특성과 사용 사례를 이해하는 것이 중요합니다. 일부 볼륨 타입에는 emptyDir, hostPath, nfs, persistentVolumeClaim, secret 등이 있습니다.
* Access Modes: 볼륨은 ReadWriteOnce (한 노드에서 읽기/쓰기), ReadOnlyMany (여러 노드에서 읽기 전용), ReadWriteMany (여러 노드에서 읽기/쓰기) 등 다양한 접근 모드를 가질 수 있습니다. 이러한 모드는 사용하는 저장소 타입과 애플리케이션의 요구사항에 따라 결정됩니다.
* Storage Class: 스토리지 클래스는 동적 볼륨 프로비저닝을 위한 방법을 제공합니다. 이는 관리자가 다양한 종류의 스토리지 (예: AWS EBS, Azure Disk, GCE Persistent Disk, Glusterfs 등) 및 그들의 세부 구성을 사전에 정의할 수 있게 해줍니다.
* 볼륨 마운트: 파드 내의 컨테이너는 볼륨을 특정 경로에 마운트하여 사용할 수 있습니다. 이는 볼륨의 데이터를 컨테이너에서 사용 가능하게 하며, 여러 컨테이너 간에 데이터를 공유할 수 있게 해줍니다.


# [6.볼륨: 컨테이너에 디스크 스토리지 연결](#index)
- 파드 내부의 각 컨테이너는 고유하게 분리된 파일 시스템을 가진다.
- 재시작 시 기존 데이터는 삭제됨.
- 새로운 컨테이너가 이전의 위치에서 계속되기를 원하거나, 실제 데이터의 디렉터리를 보존하고 싶을 때 볼륨을 사용.

> 볼륨을 사용하는 대표적인 케이스 
- **컨테이너 내 데이터 영속화**: Pod 삭제 및 재시작 시 컨테이너 내 데이터 유실 방지를 위해 (db, message queue, 등 statusful 애플리케이션 운영 가능)
- **여러 컨테이너 간 데이터 공유**: 여러 컨테이너 간 데이터를 공유해서 쉐어 시
- **시크릿 및 설정파일 공유**: secret, configmap 객체는 볼륨으로 마운트해서 애플리케이션 설정 등을 공유
- **로그 저장**: 애플리케이션 로그를 외부 시스템에 저장 및 수집
- **저장소 확장 및 이동**: 클러스터 내 스토리지 이동 또는 스토리지를 클러스터 외부 확장에 사용하여, 고가용성 및 재해복구 

## [6.1 볼륨 소개](#index)
독립적인 쿠버네티스 오브젝트가 아니므로 자체 생성 삭제 불가  
기본적으로 각 컨테이너는 잘 정의된 단일 책임을 가지고 있지만 각각 컨테이너 자체만으로는 큰 쓸모가 없다.  
공유 스토리지가 없으면 각 파드에서 공통적인 데이터를 제공할 수 없음, 그렇기 때문에 볼륨을 사용해야함.  

### 사용 가능한 볼륨 유형
- **emptyDir**: 일시적인 데이터를 저장하는데 사용하는 빈 디렉터리
- **hostPath**: 워커 노드의 파일시스템을 파드의 디렉터리로 마운트하는데 사용
- **gitRepo**: 깃 레포의 콘텐츠를 체크아웃해 초기화한 볼륨 ( 유지보수중단됨 - https://kubernetes.io/docs/concepts/storage/volumes/#gitrepo )
- **nfs**: NFS 공유를 파드에 마운트
- **gcePersistentDisk,awsElasticBlockStore,azureDisk**: 클라우드 제공자의 전용 스토리지 마운트
- **cinder, cephfs, iscsi, flocker, glusterfs, quobyte, rbd, flexVolume, vsphere Volume, photonPersistentDisk，scalelO**: 다른 유형의 네트워크 스토리지 마운트
- **configMap, secret, downwardAPI**: 쿠버네티스 리소스나 클러스터 정보를 파드에 노출하는데 사용되는 특별한 유형의 볼륨
- **persistentVolumeClaim**: 사전에 혹은 동적으로 프로비저닝된 퍼시스턴트 스토리지를 사용 

## [6.2 볼륨을 사용한 컨테이너 간 데이터 공유](#index)
### emptyDir 볼륨 사용
시작 시 빈 디렉터리로 시작  
파드가 삭제되면 볼륨의 콘텐츠도 삭제  
**동일파드에서 실행중인 컨테이너 간 파일 공유할때 유용**
단일 컨테이너에서도 임시 데이터를 디스크에 쓰는 목적에서 사용  
컨테이너의 파일시스템은 쓰기가 불가할수도있고 마운트된 볼륨에 쓰는것이 유일한 옵션일 수 있음  
### 파드 생성하기 
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: fortune
spec:
  containers:
  - image: luksa/fortune
    name: html-generator
    volumeMounts: # html이란 이름의 볼륨을 컨테이너의 /var/htdocs에 마운트 
    - name: html
      mountPath: /var/htdocs
  - image: nginx:alpine
    name: web-server
    volumeMounts: # 동일 볼륨을 /usr/share/nginx/html 에 마운트 
    - name: html
      mountPath: /usr/share/nginx/html
      readOnly: true
    ports:
    - containerPort: 80
      protocol: TCP
  volumes: # html이란 단일 emptyDir 볼륨을 위 컨테이너 두개에 마운트
  - name: html
    emptyDir: {}
```
### gitRepo
유지보수 중단으로 패스  
## [6.3 워커 노드 파일시스템의 파일 접근](#index)
대부분의 파드는 호스트 노드를 인식하지 못하므로 노드의 파일시스템에 있는 어떤파일에도 접근하면 안됨  
그러나 특정 시스템 레벨의 파드는 노드의 파일을 읽거나 할 때 사용  
### hostPath 볼륨 소개
사용하는 주요 케이스
- 노드의 서비스와 함께 동작하는 파드에 대한 데이터를 저장하거나 사용하는경우
- 쿠버네티스 애플리케이션을 개발할때
- 노드의 장치파일을 파드에서 사용해야하는 경우
- 주의사항: 노드의 파일시스템을 사용하기 때문에 파드가 다른 노드로 이동하면 원래 노드의 파일&디렉터리에 접근할 수 없다.
  그렇기 때문에 특정노드에 파드가 고정되어야하는 특수한 경우나, 모든 노드에 공통적으로 존재하는 파일이나 디렉터리에 접근해야하는 경우에 주로사용된다.

여러 파드가 동일 경로를 사용중이면 동일 파일 표시  
파드가 종료되도 콘텐츠는 삭제되지 않음 ( 데이터 유지 )  
물리적 저장소 단위는 노드 별로 달라지게 된다.  
![image](https://github.com/mason-ko/TIL/assets/30224146/14389cab-7579-4685-b140-e32119c50d9d)

+ 주의사항
+ hostPath 볼륨은 파드가 어떤 노드에 스케줄링 되느냐에 따라 민감하기 때문에(상태 유지가 필요한 파드는 스테이트풀셋 사용해야함) 일반적인 파드에 사용하는 것은 좋은 생각이 아님.
### hostPath 볼륨을 사용하는 시스템 파드 검사하기 
![image](https://github.com/mason-ko/TIL/assets/30224146/41085ef6-64b8-4ce9-b3e9-85ac71df5a59)
![image](https://github.com/mason-ko/TIL/assets/30224146/0c3dc11f-0d75-4fdf-9814-a304a57f7a53)

결국 노드의 시스템 파일에 읽기/쓰기 하는 경우에만 hostPath 볼륨을 사용해야하며 여러 파드에 걸쳐 데이터 보존용으로는 절대 사용 금지.

## [6.4 퍼시스턴트 스토리지 사용](#index)
사용하는 주요 케이스
- **상태 보존 애플리케이션**: 데이터베이스와 같은 상태 보존 애플리케이션은 데이터를 지속적으로 저장하고 읽어야 하므로 퍼시스턴트 스토리지가 필요합니다.
- **데이터 처리와 분석**: 대량의 데이터를 처리하거나 분석하는 애플리케이션은 일반적으로 퍼시스턴트 스토리지를 사용합니다. 이는 데이터를 안전하게 보존하고, 분석 결과를 저장하는 데 필요하기 때문입니다.
- **파일 저장과 공유**: 여러 서비스 또는 사용자간에 데이터를 공유하거나 저장해야 하는 경우에도 퍼시스턴트 스토리지를 사용합니다. 예를 들어, 사용자가 업로드한 파일을 저장하고, 서비스를 통해 이를 제공하는 경우 등입니다.
- **서비스 연속성 보장**: 일시적인 장애로 인해 파드가 중단되거나, 다른 노드로 이동하는 경우에도 데이터를 유지하기 위해 퍼시스턴트 스토리지를 사용합니다.
- **백업 및 복구**: 애플리케이션의 데이터를 백업하고, 필요한 경우 이를 복구하는데 퍼시스턴트 스토리지가 사용됩니다. 이는 데이터 손실을 방지하고, 서비스의 안정성을 높이는데 중요합니다.
- 이러한 케이스는 쿠버네티스의 장점 중 하나인 상태 없는 (stateless) 특성을 유지하면서도, 필요에 따라 상태를 유지(stateful)하는 데 필요한 데이터를 안정적으로 저장하고 관리할 수 있게 합니다.

여러 클러스터 노드에서 접근 필요 시 NAS 유형 사용  
### GCE 퍼시스턴트 디스크를 파드 볼륨으로 사용하기 
#### GCE 퍼시스턴트 디스크 생성하기 
클러스터 조회하기  
```
$ gcloud container clusters list
NAME ZONE MASTER_VERSION MASTER_IP . . .
kubia europe-westl-b 1.2.5 104.155.84.137 . . 
```
GCE 퍼시스턴트 디스크도 동일한 영역에 아래와 같이 생성한다.
```
$gcloud compute disks create --size=lGiB --zone=europe-westl-b mongodb 
```

#### GCE 퍼시스턴트 디스크 볼륨을 사용하는 파드 생성하기 
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mongodb 
spec:
  volumes:
  - name: mongodb-data
    gcePersistentDisk:
      pdName: mongodb
      fsType: ext4
  containers:
  - image: mongo
    name: mongodb
    volumeMounts:
    - name: mongodb-data
      mountPath: /data/db
    ports:
    - containerPort: 27017
      protocol: TCP
```
> Minikube 를 사용한다면 GCE 퍼시스턴트 디스크 대신 hostPath 볼륨으로 사용한다. mongo-pod-hostpath.yaml 참고 

볼륨을 mongoDB 내부에서 저장하는 데이터 경로에(/data/db) 마운트한다. 
![image](https://github.com/mason-ko/TIL/assets/30224146/8b43a795-49ee-4e31-aa94-d88a5fed2a33)

여기에서 의문점  
스케일을 늘려 여러 파드에 동일 경로를 마운트 했을 때 병렬적인 데이터 처리 시 일관성이 깨질 수 있다.  
그렇기 때문에 이 경우에는 StatefulSet 을 사용하여 PersistentVolumeClaim 로 마운트하여 사용  
access Mode는 ReadWriteOnce  

그렇다면 퍼시스턴트 볼륨 (PV) 와 퍼시스턴트 볼륨 클레임 (PVC) 의 차이는 뭘까  
- **Persistent Volume (PV)**: PV는 클러스터 내에서 사용할 수 있는 스토리지의 양을 나타내는 API 리소스입니다. 이는 디스크와 같은 물리적 또는 네트워크 연결 스토리지를 추상화한 것입니다. PV는 자체 수명주기를 가지고 있고, 클러스터 리소스로 간주됩니다.
- **Persistent Volume Claim (PVC)**: PVC는 사용자가 PV를 요청하는 방법입니다. 사용자는 PVC를 통해 특정 크기와 접근 모드를 가진 스토리지를 요청할 수 있습니다. PVC의 요청에 따라 쿠버네티스는 이를 충족하는 PV를 찾아 사용자에게 할당합니다.

## [6.5 기반 스토리지 기술과 파드 분리](#index)
쿠버네티스는 애플리케이션과 개발자로부터 인프라스트럭처의 세부 사항을 숨기는 것을 목표로 하고 있습니다.  
이러한 목표에 따르면, 애플리케이션 개발자는 기저에 어떤 종류의 스토리지 기술이나 물리 서버가 사용되는지 알 필요가 없습니다.  
인프라스트럭처 관련 처리는 클러스터 관리자의 책임이어야 합니다.  
### 퍼시스턴트볼륨과 퍼시스턴트볼륨클레임 소개 
![image](https://github.com/mason-ko/TIL/assets/30224146/5cfe64ba-880f-420b-9ab7-4e21917abeaf)
### 퍼시스턴트볼륨 생성 
위의 몽고 db 예제와 비교해보면, 이전과 달리 직접 클러스터 관리자의 역할로 GCE 퍼시스턴트 볼륨을 기반으로 한 퍼시스턴트 볼륨을 생성.  
그 후 퍼시스턴트볼륨을 클레임해서 파드에서 사용.
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: mongodb-pv
spec:
  capacity:  # pv 사이즈
    storage: 1Gi
  accessModes:
    - ReadWriteOnce # pv 접근 모드 
    - ReadOnlyMany
  persistentVolumeReclaimPolicy: Retain # 클레임 해제 후 퍼시스턴트 볼륨 유지
  gcePersistentDisk: # 퍼시스턴트 볼륨은 이전에 생성한 GCE 퍼시스턴트 디스크를 기반으로 함 
    pdName: mongodb
    fsType: ext4
```
> 미니큐브를 사용하는 경우 mongodb-pv-hostpath.yaml 파일로 PV 생성

persistentVolumeReclaimPolicy 옵션 
- Retain: 이 정책은 PV를 해제하고 관련 데이터를 보존합니다. PV는 여전히 API 서버에 존재하지만, 볼륨의 모든 리소스는 수동으로 해제해야 합니다. 이전 클레임에서 생성된 데이터에 접근하려면 동일한 PersistentVolumeClaim 객체를 사용해야 합니다.
- Delete: 이 정책은 PV를 해제하고 관련 스토리지 자산(예: AWS EBS, GCE PD, Azure Disk 또는 vSphere 파일)을 삭제합니다. 동적으로 프로비저닝된 볼륨에서 사용할 수 있으며, 스토리지 클래스에서 정의한 삭제 정책을 사용합니다.
- Recycle: 이 정책은 기본적으로 NFS와 같은 스토리지 볼륨을 단순히 삭제(rm -rf /thevolume/*)하고 다시 사용할 수 있게 합니다. 하지만 이 정책은 현재로서는 더 이상 권장되지 않으며, 대신 동적 프로비저닝을 사용하는 것이 좋습니다.


퍼시스턴트 볼륨 조회
```
$ kubectl get pv
```
<img width="540" alt="image" src="https://github.com/mason-ko/TIL/assets/30224146/cef307dd-99d5-4dd7-8d6e-d4e9e2047ebb">

### 퍼시스턴트볼륨클레임 생성을 통한 퍼시스턴트볼륨 요청 
#### PVC 생성 
kubectl create 로 쿠버네티스 api 에 게시  
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongodb-pvc # pvc의 이름으로 나중에 파드의 볼륨 요청할 때 사용 
spec:
  resources:
    requests:
      storage: 1Gi # 1기가 스토리지 요청 
  accessModes:
  - ReadWriteOnce # 읽기쓰기 
  storageClassName: "" # 이 부분은 동적 프로비저닝 절에서 배운다.
```

> storageClassName 필드는 사용할 PersistentVolume(PV)의 스토리지 클래스를 지정하는 데 사용됩니다.
> 스토리지 클래스를 이용하면, 각각의 PVC를 다른 유형의 스토리지(예: SSD, HDD, 고성능 스토리지, 등)와 연결할 수 있습니다.
> 빈 값일 경우 default 가 사용되며, 특정 스토리지 클래스에 default 라는 어노테이션으로 추가 및 지정 가능.

pvc 조회하기
```
$ kubectl get pvc
```
pvc 접근모드
- RWO(ReadWriteOnce): 단일 노드 읽기/쓰기
- ROX(ReadOnlyMany): 다수 노드 읽기
- RWX(ReadWriteMany): 다수 노드 읽기/쓰기
  
PV 바운드 상태가 되어 더이상 Available로 표시되지 않음.  
```
$ kubectl get pv
NAME CAPACITY ACCESSMODES STATUS CLAIM AGE
mongodb-pv lGi RWOj ROX Bound default/mongodb-pvc lm
```
#### 파드에서 PVC 사용하기 
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: mongodb 
spec:
  containers:
  - image: mongo
    name: mongodb
    volumeMounts:
    - name: mongodb-data
      mountPath: /data/db
    ports:
    - containerPort: 27017
      protocol: TCP
  volumes:
  - name: mongodb-data
    persistentVolumeClaim:
      claimName: mongodb-pvc # 위에서 생성했던 이름으로 PVC 참조
```
#### PV와 PVC 사용의 장점 이해하기 
<img width="668" alt="image" src="https://github.com/mason-ko/TIL/assets/30224146/89c398fe-b746-4e58-ad02-a3fecdc6b043">

GCE 퍼시스턴트 디스크 직접 사용 vs PV, PVC 사용하는 방법의 장단점
- 직접 사용하는 방법:
  - 장점:
간단하게 사용할 수 있습니다. PV나 PVC를 설정하거나 관리할 필요가 없습니다.
디스크와 파드 사이의 직접적인 연결을 통해 관리가 단순화됩니다.
  - 단점:
스토리지 관리에 대한 유연성이 떨어집니다. 예를 들어, 특정 스토리지 클래스나 스토리지 크기를 동적으로 변경하는 등의 작업이 어렵습니다.
쿠버네티스 환경에서의 이식성이 떨어집니다. 스토리지 구성이 파드에 직접 연결되어 있어, 다른 쿠버네티스 클러스터로 이동시키기 어렵습니다.
- PV와 PVC를 사용하는 방법:
  - 장점:
스토리지 관리에 대한 유연성이 크게 증가합니다. 스토리지 클래스를 통해 스토리지 타입을 쉽게 변경할 수 있으며, PVC를 통해 스토리지 크기를 동적으로 조절할 수 있습니다.
쿠버네티스 환경에서의 이식성이 좋습니다. 스토리지 구성이 파드에서 분리되어 있어, 동일한 스토리지 구성을 다른 쿠버네티스 클러스터에서도 쉽게 사용할 수 있습니다.
스토리지 리소스의 생명주기 관리가 간편해집니다. PV와 PVC를 사용하면 스토리지 리소스의 생성, 사용, 해제 등의 생명주기를 쿠버네티스 API를 통해 관리할 수 있습니다.
  - 단점:
PV와 PVC 설정과 관리에 대한 추가적인 작업이 필요합니다.
쿠버네티스의 스토리지 관련 개념과 작동 방식을 이해해야 합니다.
#### PVC 재사용 
파드와 PVC 삭제 후 PVC를 재생성 하면 클레임의 상태가 Pending 으로 표시된다.  
Kubernetes에서 퍼시스턴트 볼륨(PV)의 상태가 'Released'로 표시되면, 이전에 사용된 데이터가 남아 있는 상태를 나타냅니다.  
이 상태의 PV는 클러스터 관리자가 수동으로 볼륨을 비우지 않는 이상 새로운 클레임에 바인딩할 수 없습니다.  
이는 보안 문제를 일으킬 수 있습니다. 따라서, PV를 재사용하려면 관리자가 볼륨을 비우거나 재활용해야 합니다.  
이는 PV의 reclaim policy와 볼륨에 저장된 데이터의 성격에 따라 달라집니다.  
#### PV를 수동으로 다시 클레임 하기 
persistentVolumneClaimPolicy 를 Retain 으로 설정  
#### PV를 자동으로 다시 클레임하기
Recycle 은 볼륨의 콘텐츠를 삭제하고 볼륨이 다시 클레임 될 수 있도록 함  
- 다만 해당 옵션은 GCE 퍼시스턴트 디스크에서 사용불가 
Delete 정책은 기반 스토리지를 삭제
![image](https://github.com/mason-ko/TIL/assets/30224146/e0740f14-6c97-46c5-a07a-774ea23607c5)
## [6.6 퍼시스턴트볼륨의 동적 프로비저닝](#index)
동적 프로비저닝은 Kubernetes의 퍼시스턴트 볼륨(Persistent Volume, PV)을 관리하는 중요한 기능 중 하나입니다.  
이 기능은 사용자가 스토리지를 요청할 때마다 자동으로 스토리지를 생성하고 할당해주는 방식으로 작동합니다. 동적 프로비저닝의 사용은 여러 가지 이유로 중요합니다

1. **자원 최적화**: 동적 프로비저닝을 통해 사용자가 필요한 만큼의 스토리지를 즉시 할당받을 수 있습니다. 이는 공간 낭비를 최소화하고, 필요에 따라 스토리지를 확장하거나 축소할 수 있는 유연성을 제공합니다.
2. **자동화와 시간 절약**: 동적 프로비저닝을 사용하면, 사용자나 관리자가 수동으로 PV를 생성하고 관리할 필요가 없습니다. 스토리지 요청이 있을 때마다 시스템이 자동으로 PV를 생성하고 할당하기 때문에, 작업을 수행하는 데 필요한 시간과 노력을 크게 줄일 수 있습니다.
3. **데이터 보존과 보안**: 동적 프로비저닝은 각 요청에 대해 별도의 PV를 생성합니다. 이렇게 하면 각 사용자나 애플리케이션의 데이터를 격리시킬 수 있으므로, 데이터 보존과 보안을 향상시킬 수 있습니다.
4. **확장성**: 동적 프로비저닝은 클러스터가 확장될 때 특히 유용합니다. 사용자나 애플리케이션의 수가 늘어나면, 자동으로 필요한 만큼의 스토리지를 생성하고 할당할 수 있으므로, 스케일링이 더욱 간편해집니다.

### 스토리지클래스 리소스를 통한 사용 가능한 스토리지 유형 정의하기 
```yaml
apiVersion: storage.k8s.io/v1
kind: StorageClass
metadata:
  name: fast
provisioner: kubernetes.io/gce-pd # pv 프로비저닝을 위해 사용되는 볼륨 플러그인 
parameters:
  type: pd-ssd
```
### 특정스토리지클래스를 요청하는 PVC 정의 생성하기 
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mongodb-pvc 
spec:
  storageClassName: fast # 위에서 생성한 스토리지클래스, PVC는 사용자 정의 스토리지 클래스를 요청한다.
  resources:
    requests:
      storage: 100Mi
  accessModes:
    - ReadWriteOnce
```
## [6.7 요약](#index)
