
### 맥에서 파일 업로드 시 파일명 분리되는 경우

보통 파일 업로드 시 받는 path 에 한글경로가 포함이 되어있을 때 발생

원인

한글을 처리하는 유니코드 정규화 방식이 맥과 윈도우가 다름

맥: NFD (Normalization Form Canonical Decomposition) 
윈도우: NFC (Normalization Form Canonical Composition) 


단순처리
```go
if path != "" {
	t := transform.Chain(norm.NFD, runes.Remove(runes.In(unicode.Mn)), norm.NFC)
	path, _, _ = transform.String(t, path)
}
```

참고: https://ko.wikipedia.org/wiki/%EC%9C%A0%EB%8B%88%EC%BD%94%EB%93%9C_%EB%93%B1%EA%B0%80%EC%84%B1
