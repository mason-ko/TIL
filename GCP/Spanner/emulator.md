# 설치

1. [Cloud SDK 설치.](https://cloud.google.com/sdk/install)
2. [Docker 설치.](https://docs.docker.com/docker-for-mac/install/)
3. 에뮬레이터 Run
```
gcloud emulators spanner start
```
4. 환경설정 변경
```
gcloud config configurations create emulator
gcloud config set auth/disable_credentials true
gcloud config set project your-project-id
gcloud config set api_endpoint_overrides/spanner http://localhost:9020/

export SPANNER_EMULATOR_HOST=localhost:9010
```

# 테스트 시 프로젝트가 변경되지 않았을 경우
환경변수 적용 확인 및 

vi ~/.zshrc. 
```
export SPANNER_EMULATOR_HOST=localhost:9010
```
추가





