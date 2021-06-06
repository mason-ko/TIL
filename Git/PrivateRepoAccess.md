## Https 경로의 private git repo 접근 에러 시

```
git config --global url."git@github.com:".insteadOf "https://github.com/"
```

위 옵션을 사용해서 https://github.com/ -> git@github.com:  으로 변경해서  
ssh 로 사용 가능


### 위의 케이스에서 Dockerfile 을 통한 container 내부에서 Module 접근 시 

```
git config --global url."https://{ACCESS_TOKEN}:x-oauth-basic@github.com/".insteadOf "https://github.com"
```

github 계정에서 Token 발급하여 해당 토큰을 넣는 방법으로 비공개 레포에 접근



### go private module 주소로 사용 시 go sum 실패 시 

1.13 이상의 go module 사용 시 private 모듈 사용시 문제가 발생하며

원인은 go get 명령 실행 시 golang proxy 체크섬 수행에서 에러가 발생함

그렇기 떄문에 아래 옵션 추가해야함!

ENV GOSUMDB=off
