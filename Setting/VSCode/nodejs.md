# VS Code 로 Node js 실행시 resource maps error 

.vscode/launch.json 파일 configurations 내용에 아래 내용 추가
```
"resolveSourceMapLocations": [
  "${workspaceFolder}/**",
  "!**/node_modules/**"
],
```
  
VS Code Version 구버전에서는 잘 돌아간 거를 보아, 버전 올라가면서 resouce check 방식이 .map 파일을 사용하도록 바뀌었을거로 추정

참고: https://github.com/microsoft/vscode/issues/102042#issuecomment-656402933
