## 간략 개요
- GKE 에서 관리하는 새로운 모드 ( 기존모드: 스탠다드 )
- VPA, HPA 를 통한 수평 확장, 수직 확장 설정 가능 ( 각각의 Min, Max 범위 설정 가능 )
- 커널 설정 관련된 부분들의 다수를 GKE 에서 자체적으로 관리하기때문에 마운트 등, 설정 불가능한 부분이 생김
- 비용이 스탠다드는 노드별로 지불이지만, 오토파일럿은 Pod 리소스 ( cpu, memory, temp storage) 별로 지불
- deployment 파일로 초기 replica 설정된 만큼 프로비저닝 되고, VPA, HPA 등 새로 생긴 쿠버네티스 오브젝트로 관리하는듯

## Reference
https://cloud.google.com/kubernetes-engine/docs/concepts/autopilot-overview
